"""API báo cáo thống kê."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from src.database import get_db
from src.models import Transaction, Category, User
from src.utils.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/summary")
def get_summary(month: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(require_permission("report:read"))):
    target_date = date.fromisoformat(month + "-01") if month else date.today()
    
    base_filter_income = [Category.type == "income", extract('year', Transaction.transaction_date) == target_date.year, extract('month', Transaction.transaction_date) == target_date.month]
    base_filter_expense = [Category.type == "expense", extract('year', Transaction.transaction_date) == target_date.year, extract('month', Transaction.transaction_date) == target_date.month]
    
    if not current_user.has_permission("*:*"):
        base_filter_income.append(Transaction.user_id == current_user.id)
        base_filter_expense.append(Transaction.user_id == current_user.id)
        
    income = db.query(func.sum(Transaction.amount)).join(Category).filter(*base_filter_income).scalar() or 0
    expense = db.query(func.sum(Transaction.amount)).join(Category).filter(*base_filter_expense).scalar() or 0
                        
    return {"month": target_date.strftime("%Y-%m"), "total_income": float(income), "total_expense": float(expense), "balance": float(income - expense)}

@router.get("/by_category")
def get_by_category(month: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(require_permission("report:read"))):
    target_date = date.fromisoformat(month + "-01") if month else date.today()
    
    base_filter = [
        extract('year', Transaction.transaction_date) == target_date.year,
        extract('month', Transaction.transaction_date) == target_date.month
    ]
    if not current_user.has_permission("*:*"):
        base_filter.append(Transaction.user_id == current_user.id)
        
    results = db.query(Category.name, Category.type, func.sum(Transaction.amount).label("total"))\
                .join(Transaction).filter(*base_filter)\
                .group_by(Category.name, Category.type).order_by(func.sum(Transaction.amount).desc()).all()
                
    return [{"category": r[0], "type": r[1], "total": float(r[2])} for r in results]
@router.get("/monthly_trend")
def get_monthly_trend(db: Session = Depends(get_db), current_user: User = Depends(require_permission("report:read"))):
    today = date.today()
    results = []
    
    for i in range(5, -1, -1):
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
            
        base_filter_income = [Category.type == "income", extract('year', Transaction.transaction_date) == target_year, extract('month', Transaction.transaction_date) == target_month]
        base_filter_expense = [Category.type == "expense", extract('year', Transaction.transaction_date) == target_year, extract('month', Transaction.transaction_date) == target_month]
        
        if not current_user.has_permission("*:*"):
            base_filter_income.append(Transaction.user_id == current_user.id)
            base_filter_expense.append(Transaction.user_id == current_user.id)
            
        income = db.query(func.sum(Transaction.amount)).join(Category).filter(*base_filter_income).scalar() or 0
        expense = db.query(func.sum(Transaction.amount)).join(Category).filter(*base_filter_expense).scalar() or 0
                            
        results.append({
            "month": f"{target_month:02d}/{target_year}",
            "income": float(income),
            "expense": float(expense)
        })
        
    return results
