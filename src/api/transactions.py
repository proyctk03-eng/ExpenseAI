"""API quản lý giao dịch tích hợp AI."""
import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Transaction, User, Category, AIPrediction
from src.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from src.utils.dependencies import get_current_user, require_permission
from src.services.ai_classifier import AIClassifier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["transactions"])
ai_classifier = AIClassifier()


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("transaction:read")),
):
    """Lấy danh sách giao dịch với bộ lọc."""
    if current_user.has_permission("*:*"):
        query = db.query(Transaction)
    else:
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("transaction:create")),
):
    """Tạo giao dịch mới, tự động phân loại bằng AI nếu không chọn danh mục."""
    try:
        category_id = tx_in.category_id
        ai_pred_data = None

        if not category_id:
            result = ai_classifier.classify(tx_in.description, user_id=current_user.id, db=db)
            pred_cat_name = result["category"]
            pred_type = result.get("type", "expense")

            category = db.query(Category).filter(
                (Category.user_id == current_user.id) | (Category.user_id.is_(None)),
                Category.name == pred_cat_name
            ).first()

            if not category:
                category = Category(name=pred_cat_name, type=pred_type, user_id=current_user.id)
                db.add(category)
                db.flush()

            category_id = category.id
            ai_pred_data = result

        new_tx = Transaction(
            amount=tx_in.amount,
            description=tx_in.description,
            transaction_date=tx_in.transaction_date,
            category_id=category_id,
            user_id=current_user.id,
        )
        db.add(new_tx)
        db.flush()

        if ai_pred_data:
            ai_pred = AIPrediction(
                transaction_id=new_tx.id,
                predicted_category=ai_pred_data["category"],
                confidence=ai_pred_data["confidence"],
            )
            db.add(ai_pred)

        db.commit()
        db.refresh(new_tx)
        return new_tx

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Lỗi khi tạo giao dịch cho user %s", current_user.id)
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi khi tạo giao dịch. Vui lòng thử lại.")


@router.put("/{tx_id}", response_model=TransactionResponse)
def update_transaction(
    tx_id: int,
    tx_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("transaction:update")),
):
    """Cập nhật giao dịch và ghi nhận kinh nghiệm học hỏi (Agent Memory)."""
    if current_user.has_permission("*:*"):
        tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    else:
        tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == current_user.id).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

    # Học hỏi từ người dùng: Nếu user đổi danh mục khác danh mục cũ, ghi nhận vào UserMemoryRule
    if tx_in.category_id is not None and tx_in.category_id != tx.category_id:
        try:
            from src.models.user_memory_rule import UserMemoryRule
            keyword = (tx_in.description or tx.description or "").strip().lower()
            if len(keyword) >= 2:
                rule = db.query(UserMemoryRule).filter(
                    UserMemoryRule.user_id == current_user.id,
                    UserMemoryRule.keyword_pattern == keyword
                ).first()
                if rule:
                    rule.category_id = tx_in.category_id
                    rule.frequency += 1
                else:
                    new_rule = UserMemoryRule(
                        user_id=current_user.id,
                        keyword_pattern=keyword,
                        category_id=tx_in.category_id,
                        frequency=1
                    )
                    db.add(new_rule)
        except Exception as e:
            logger.warning("Không thể lưu kinh nghiệm Agent Memory: %s", e)

    if tx_in.amount is not None:
        tx.amount = tx_in.amount
    if tx_in.description is not None:
        tx.description = tx_in.description
    if tx_in.category_id is not None:
        tx.category_id = tx_in.category_id
    if tx_in.transaction_date is not None:
        tx.transaction_date = tx_in.transaction_date

    try:
        db.commit()
        db.refresh(tx)
        return tx
    except Exception:
        db.rollback()
        logger.exception("Lỗi cập nhật giao dịch %d", tx_id)
        raise HTTPException(status_code=500, detail="Lỗi cập nhật giao dịch")


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("transaction:delete")),
):
    """Xóa giao dịch."""
    if current_user.has_permission("*:*"):
        tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    else:
        tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == current_user.id).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

    try:
        db.delete(tx)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Lỗi xóa giao dịch %d", tx_id)
        raise HTTPException(status_code=500, detail="Lỗi xóa giao dịch")
