from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src.models import User, Transaction, Category
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    # Kiểm tra quyền admin
    if not current_user.is_admin and "admin" not in [r.name for r in current_user.roles]:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập chức năng Quản trị.")
    return current_user

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """Lấy danh sách tất cả người dùng và số lượng giao dịch của họ."""
    users = db.query(User).all()
    result = []
    for u in users:
        tx_count = db.query(Transaction).filter(Transaction.user_id == u.id).count()
        roles = [r.name for r in u.roles]
        if u.is_admin and "admin" not in roles:
            roles.append("admin")
            
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "roles": roles,
            "transaction_count": tx_count,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return result

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """Lấy thống kê tổng quan của hệ thống."""
    total_users = db.query(User).count()
    total_transactions = db.query(Transaction).count()
    
    total_income = db.query(func.sum(Transaction.amount)).join(Category).filter(Category.type == "income").scalar() or 0
    total_expense = db.query(func.sum(Transaction.amount)).join(Category).filter(Category.type == "expense").scalar() or 0
    
    return {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_volume": float(total_income + total_expense),
        "total_income": float(total_income),
        "total_expense": float(total_expense)
    }
