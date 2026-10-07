"""API Dashboard: tổng thu, tổng chi, biểu đồ."""
import logging
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import User, Transaction, Category
from src.schemas.dashboard import DashboardSummary, MonthlyComparison, CategoryBreakdown
from src.utils.dependencies import require_permission, DateRange, get_date_range

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _user_filter(current_user: User):
    """Trả về filter theo user_id nếu không phải admin."""
    if current_user.has_permission("*:*"):
        return []
    return [Transaction.user_id == current_user.id]


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    date_range: DateRange = Depends(get_date_range),
    current_user: User = Depends(require_permission("report:read")),
    db: Session = Depends(get_db),
):
    """Lấy tổng thu, tổng chi và số dư."""
    base = [
        Transaction.transaction_date >= date_range.start,
        Transaction.transaction_date <= date_range.end,
        *_user_filter(current_user),
    ]

    # outerjoin: bao gồm giao dịch chưa phân loại (category_id = NULL)
    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(Category.type == "income", *base)
        .scalar()
    )
    expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(func.coalesce(Category.type, "expense") == "expense", *base)
        .scalar()
    )

    total_inc = float(income)
    total_exp = float(expense)
    has_data = (total_inc > 0 or total_exp > 0)
    latest_month = None
    if not has_data:
        latest_tx = (
            db.query(Transaction.transaction_date)
            .filter(*_user_filter(current_user))
            .order_by(Transaction.transaction_date.desc())
            .first()
        )
        if latest_tx and latest_tx[0]:
            latest_month = latest_tx[0].strftime("%Y-%m")

    return DashboardSummary(
        total_income=total_inc,
        total_expense=total_exp,
        balance=total_inc - total_exp,
        start_date=date_range.start,
        end_date=date_range.end,
        has_data=has_data,
        latest_active_month=latest_month,
    )


@router.get("/available-months")
def get_available_months(
    current_user: User = Depends(require_permission("report:read")),
    db: Session = Depends(get_db),
):
    """Lấy danh sách các tháng có dữ liệu giao dịch của người dùng."""
    from sqlalchemy import extract
    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("y"),
            extract("month", Transaction.transaction_date).label("m"),
            func.count(Transaction.id).label("cnt")
        )
        .filter(*_user_filter(current_user))
        .group_by("y", "m")
        .order_by(extract("year", Transaction.transaction_date).desc(), extract("month", Transaction.transaction_date).desc())
        .all()
    )
    months = []
    for y, m, cnt in rows:
        m_str = f"{int(y):04d}-{int(m):02d}"
        months.append({"month": m_str, "label": f"Tháng {int(m):02d}/{int(y)}", "count": int(cnt)})
    return months


@router.get("/monthly-comparison", response_model=MonthlyComparison)
def get_monthly_comparison(
    current_user: User = Depends(require_permission("report:read")),
    db: Session = Depends(get_db),
):
    """Lấy dữ liệu thu/chi 6 tháng gần nhất (gộp 1 query)."""
    from datetime import timedelta
    from sqlalchemy import extract

    today = date.today()
    six_months_ago = today.replace(day=1) - timedelta(days=150)

    base = [Transaction.transaction_date >= six_months_ago, *_user_filter(current_user)]

    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("y"),
            extract("month", Transaction.transaction_date).label("m"),
            func.coalesce(Category.type, "expense").label("ctype"),
            func.sum(Transaction.amount),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(*base)
        .group_by("y", "m", "ctype")
        .order_by("y", "m")
        .all()
    )

    monthly: dict = {}
    for year, month, cat_type, total in rows:
        key = f"{int(year)}-{int(month):02d}"
        monthly.setdefault(key, {"income": 0.0, "expense": 0.0})
        monthly[key][cat_type] = float(total)

    labels = sorted(monthly.keys())
    return MonthlyComparison(
        labels=labels,
        income=[monthly[k]["income"] for k in labels],
        expense=[monthly[k]["expense"] for k in labels],
    )


@router.get("/category-breakdown", response_model=CategoryBreakdown)
def get_category_breakdown(
    date_range: DateRange = Depends(get_date_range),
    current_user: User = Depends(require_permission("report:read")),
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            func.coalesce(Category.name, "Chưa phân loại").label("cname"),
            func.sum(Transaction.amount).label("total"),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(
            func.coalesce(Category.type, "expense") == "expense",
            Transaction.transaction_date >= date_range.start,
            Transaction.transaction_date <= date_range.end,
            *_user_filter(current_user),
        )
        .group_by("cname")
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    palette = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#3B82F6", "#10B981"]
    return CategoryBreakdown(
        labels=[r[0] for r in results],
        data=[float(r[1]) for r in results],
        colors=[palette[i % len(palette)] for i in range(len(results))],
    )
