"""Router cho Quản lý Ngân sách (Budgets)."""
from datetime import date, datetime
import calendar
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Budget, Category, Transaction, User
from src.schemas.budget import BudgetCreate, BudgetResponse, BudgetSummaryResponse, BudgetUpdate
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


def _get_month_date_range(month_str: str):
    """Chuyển đổi chuỗi YYYY-MM sang (start_date, end_date)."""
    try:
        parts = month_str.split("-")
        year, month = int(parts[0]), int(parts[1])
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        return start_date, end_date
    except Exception:
        today = date.today()
        start_date = date(today.year, today.month, 1)
        _, last_day = calendar.monthrange(today.year, today.month)
        return start_date, date(today.year, today.month, last_day)


def _calculate_budget_spent(db: Session, user_id: int, category_id: Optional[int], start_date: date, end_date: date) -> float:
    """Tính toán số tiền thực tế đã chi tiêu trong tháng theo danh mục hoặc tổng."""
    query = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .select_from(Transaction)
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            func.coalesce(Category.type, "expense") == "expense",
        )
    )
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    total_spent = query.scalar() or 0.0
    return float(total_spent)


def _enrich_budget_response(budget: Budget, spent: float) -> BudgetResponse:
    limit = float(budget.amount_limit)
    remaining = max(0.0, limit - spent)
    pct = round((spent / limit) * 100, 1) if limit > 0 else 0.0

    if pct >= 100.0:
        stat = "exceeded"
    elif pct >= budget.alert_threshold:
        stat = "warning"
    else:
        stat = "safe"

    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        category_name=budget.category_name,
        month=budget.month,
        amount_limit=limit,
        alert_threshold=budget.alert_threshold,
        spent_amount=round(spent, 2),
        remaining_amount=round(remaining, 2),
        spent_percentage=pct,
        status=stat,
        created_at=budget.created_at,
    )


@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$", description="Tháng cần lấy (YYYY-MM)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách hạn mức ngân sách của người dùng theo tháng kèm tiến độ chi tiêu thực tế."""
    target_month = month or date.today().strftime("%Y-%m")
    start_date, end_date = _get_month_date_range(target_month)

    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id, Budget.month == target_month)
        .order_by(Budget.category_id.is_(None).desc(), Budget.id.asc())
        .all()
    )

    results = []
    for b in budgets:
        spent = _calculate_budget_spent(db, current_user.id, b.category_id, start_date, end_date)
        results.append(_enrich_budget_response(b, spent))

    return results


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tạo mới hoặc cập nhật hạn mức ngân sách."""
    if budget_in.category_id:
        category = db.query(Category).filter(Category.id == budget_in.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Danh mục không tồn tại")
        if category.type != "expense":
            raise HTTPException(status_code=400, detail="Chỉ có thể đặt ngân sách cho danh mục Chi tiêu")

    # Kiểm tra xem đã có budget cho user + category + month này chưa (Upsert)
    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.category_id == budget_in.category_id,
            Budget.month == budget_in.month,
        )
        .first()
    )

    if existing:
        existing.amount_limit = budget_in.amount_limit
        existing.alert_threshold = budget_in.alert_threshold
        db.commit()
        db.refresh(existing)
        budget = existing
    else:
        budget = Budget(
            user_id=current_user.id,
            category_id=budget_in.category_id,
            month=budget_in.month,
            amount_limit=budget_in.amount_limit,
            alert_threshold=budget_in.alert_threshold,
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)

    start_date, end_date = _get_month_date_range(budget.month)
    spent = _calculate_budget_spent(db, current_user.id, budget.category_id, start_date, end_date)
    return _enrich_budget_response(budget, spent)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xóa một mục hạn mức ngân sách."""
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Hạn mức ngân sách không tồn tại")

    db.delete(budget)
    db.commit()
    return None


@router.get("/summary", response_model=BudgetSummaryResponse)
def get_budget_summary(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tổng quan ngân sách toàn diện theo tháng."""
    target_month = month or date.today().strftime("%Y-%m")
    start_date, end_date = _get_month_date_range(target_month)

    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id, Budget.month == target_month)
        .all()
    )

    enriched_budgets = []
    total_budget = 0.0
    for b in budgets:
        spent = _calculate_budget_spent(db, current_user.id, b.category_id, start_date, end_date)
        enriched = _enrich_budget_response(b, spent)
        enriched_budgets.append(enriched)
        if b.category_id is None:
            total_budget = float(b.amount_limit)

    # Nếu không có budget tổng, tính tổng của các budget danh mục
    if total_budget == 0.0:
        total_budget = sum(float(b.amount_limit) for b in budgets if b.category_id is not None)

    # Tổng chi tiêu thực tế trong tháng của user
    total_spent = _calculate_budget_spent(db, current_user.id, None, start_date, end_date)
    total_remaining = max(0.0, total_budget - total_spent)
    overall_pct = round((total_spent / total_budget) * 100, 1) if total_budget > 0 else 0.0

    if overall_pct >= 100.0:
        overall_status = "exceeded"
    elif overall_pct >= 80.0:
        overall_status = "warning"
    else:
        overall_status = "safe"

    return BudgetSummaryResponse(
        month=target_month,
        total_budget=round(total_budget, 2),
        total_spent=round(total_spent, 2),
        total_remaining=round(total_remaining, 2),
        overall_percentage=overall_pct,
        overall_status=overall_status,
        budgets=enriched_budgets,
    )
