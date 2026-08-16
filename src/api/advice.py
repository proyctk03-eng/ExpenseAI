"""API xin tư vấn tài chính từ AI."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy import func

from src.database import get_db
from src.models import Transaction, Category, User
from src.utils.dependencies import get_current_user
from src.services.ai_advice import AIAdviceService

router = APIRouter(prefix="/api/advice", tags=["advice"])
advice_service = AIAdviceService()

@router.post("/")
def get_financial_advice(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    three_months_ago = date.today() - timedelta(days=90)
    
    results = db.query(Category.name, Category.type, func.sum(Transaction.amount))\
                .join(Transaction).filter(Transaction.user_id == current_user.id, Transaction.transaction_date >= three_months_ago)\
                .group_by(Category.name, Category.type).all()
                
    summary = {"income": {}, "expense": {}}
    for cat_name, cat_type, total in results:
        summary[cat_type][cat_name] = float(total)
        
    if not summary["expense"] and not summary["income"]:
        raise HTTPException(status_code=400, detail="Không đủ dữ liệu giao dịch trong 3 tháng qua để AI phân tích.")
        
    advice = advice_service.get_advice(summary)
    return {"advice": advice}
