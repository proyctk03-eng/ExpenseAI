from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database import get_db
from src.models import User, Transaction, Category
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    # Kiểm tra quyền admin
    if not current_user.is_admin and not current_user.has_permission("*:*"):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập chức năng Quản trị.")
    return current_user

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """Lấy danh sách tất cả người dùng và số lượng giao dịch của họ."""
    from sqlalchemy import func as sa_func
    from sqlalchemy.orm import joinedload

    # Gộp 1 truy vấn duy nhất thay vì N+1 vòng lặp count
    rows = (
        db.query(User, sa_func.count(Transaction.id).label("tx_count"))
        .outerjoin(Transaction, Transaction.user_id == User.id)
        .options(joinedload(User.roles))
        .group_by(User.id)
        .all()
    )
    result = []
    for u, tx_count in rows:
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
    
    # Outer join để không bỏ sót giao dịch chưa phân loại (mặc định expense), gom thành 1 query
    cat_type = func.coalesce(Category.type, "expense")
    vol_rows = (
        db.query(cat_type, func.sum(Transaction.amount))
        .select_from(Transaction)
        .outerjoin(Category, Transaction.category_id == Category.id)
        .group_by(cat_type)
        .all()
    )
    totals = {"income": 0.0, "expense": 0.0}
    for ctype, val in vol_rows:
        totals[ctype] = float(val or 0)
    
    return {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_volume": float(totals["income"] + totals["expense"]),
        "total_income": totals["income"],
        "total_expense": totals["expense"]
    }
