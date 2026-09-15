"""API xin tư vấn tài chính từ AI."""
from datetime import date, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Transaction, Category, User
from src.utils.dependencies import get_current_user
from src.services.ai_advice import AIAdviceService
from src.services.ai_behavior import AIBehaviorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/advice", tags=["advice"])
advice_service = AIAdviceService()
behavior_service = AIBehaviorService()


@router.post("/")
def get_financial_advice(
    force_refresh: bool = Query(False, description="Bắt buộc làm mới không dùng cache"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy lời khuyên tài chính cá nhân hóa từ AI dựa trên 90 ngày qua."""
    three_months_ago = date.today() - timedelta(days=90)

    # Truy vấn cơ sở trong 90 ngày qua
    base_query = (
        db.query(Category.name, Category.type, func.sum(Transaction.amount))
        .join(Transaction)
        .filter(Transaction.transaction_date >= three_months_ago)
    )

    # Ưu tiên lấy dữ liệu của chính user
    user_results = (
        base_query.filter(Transaction.user_id == current_user.id)
        .group_by(Category.name, Category.type)
        .all()
    )

    # Nếu là Admin và chưa có giao dịch cá nhân, phân tích tổng hợp hệ thống
    if not user_results and (current_user.is_admin or current_user.has_permission("*:*")):
        results = base_query.group_by(Category.name, Category.type).all()
    else:
        results = user_results

    summary = {"income": {}, "expense": {}}
    for cat_name, cat_type, total in results:
        summary[cat_type][cat_name] = float(total)

    if not summary["expense"] and not summary["income"]:
        raise HTTPException(
            status_code=400,
            detail="Chưa có đủ dữ liệu giao dịch trong 3 tháng qua để AI phân tích. Hãy thêm các giao dịch thu chi của bạn!"
        )

    advice = advice_service.get_advice(summary, force_refresh=force_refresh)
    return {"advice": advice}

@router.get("/behavior")
def analyze_user_behavior(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Phân tích hành vi tiêu dùng từ 50 giao dịch gần nhất."""
    # Lấy 50 giao dịch gần nhất
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(50)
        .all()
    )
    
    if not transactions:
        raise HTTPException(status_code=400, detail="Chưa có đủ dữ liệu giao dịch để phân tích hành vi.")
        
    # Sắp xếp lại theo chiều thuận thời gian để AI dễ nhận diện chuỗi
    transactions.reverse()
    
    log_lines = []
    for tx in transactions:
        amount_str = f"{tx.amount:,.0f}đ"
        cat = tx.category_name if tx.category_name else "Khác"
        # Chỉ lấy expense để phân tích hành vi tiêu dùng
        if tx.category_type == "expense":
            log_lines.append(f"[{tx.transaction_date}] {cat}: {tx.description} ({amount_str})")
            
    if len(log_lines) < 5:
        raise HTTPException(status_code=400, detail="Cần ít nhất 5 giao dịch chi tiêu để phân tích hành vi.")
        
    log_str = "\n".join(log_lines)
    analysis = behavior_service.analyze_behavior(log_str)
    
    return {"analysis": analysis}
