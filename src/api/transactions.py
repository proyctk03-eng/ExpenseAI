"""API quản lý giao dịch tích hợp AI, tối ưu hóa chống trùng lặp (Idempotency Guard) và xử lý ngoại lệ toàn diện."""
from datetime import date, datetime, timedelta, timezone
import logging
import threading
import time
from typing import List, Optional, Set, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Transaction, User, Category, AIPrediction
from src.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from src.utils.dependencies import require_permission
from src.services.ai_classifier import AIClassifier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["transactions"])
ai_classifier = AIClassifier()

# Bộ khóa in-flight để ngăn chặn request đồng thời (Double-Submit Protection)
_in_flight_signatures: Set[Tuple[int, float, str, str]] = set()
_in_flight_lock = threading.Lock()


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    all_users: bool = False,
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
    if all_users and current_user.has_permission("*:*"):
        query = db.query(Transaction)
    else:
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if search:
        query = query.filter(Transaction.description.ilike(f"%{search.strip()}%"))
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    return query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("transaction:create")),
):
    """Tạo giao dịch mới, tự động phân loại bằng AI và chống insert trùng lặp (Idempotency)."""
    norm_desc = (tx_in.description or "").strip()
    norm_amount = round(float(tx_in.amount), 2)
    norm_date_str = str(tx_in.transaction_date)
    signature = (current_user.id, norm_amount, norm_desc, norm_date_str)

    # 1. Cơ chế chống trùng lặp cấp độ in-flight (khi người dùng click dồn dập trong tích tắc)
    acquired = False
    try:
        with _in_flight_lock:
            if signature in _in_flight_signatures:
                is_duplicate_in_flight = True
            else:
                _in_flight_signatures.add(signature)
                acquired = True
                is_duplicate_in_flight = False

        # Nếu một request giống hệt đang được xử lý, đợi request đó hoàn tất rồi trả về kết quả
        if is_duplicate_in_flight:
            logger.info("Request trùng lặp đang in-flight cho user %s, chờ kết quả...", current_user.id)
            for _ in range(20):  # Chờ tối đa 4 giây
                time.sleep(0.2)
                with _in_flight_lock:
                    if signature not in _in_flight_signatures:
                        break

            # Kiểm tra xem giao dịch đã được commit bởi request trước chưa
            recent_threshold = datetime.now(timezone.utc) - timedelta(seconds=20)
            existing_tx = (
                db.query(Transaction)
                .filter(
                    Transaction.user_id == current_user.id,
                    Transaction.amount == tx_in.amount,
                    Transaction.description == norm_desc,
                    Transaction.transaction_date == tx_in.transaction_date,
                    Transaction.created_at >= recent_threshold,
                )
                .order_by(Transaction.id.desc())
                .first()
            )
            if existing_tx:
                logger.warning("Phát hiện giao dịch in-flight lặp lại (id=%s). Trả về 409 Conflict.", existing_tx.id)
                raise HTTPException(status_code=409, detail="Giao dịch trùng lặp vừa được tạo. Vui lòng không gửi lại liên tục.")

        # 2. Cơ chế Idempotency Guard dựa trên Database (Cửa sổ 5 giây)
        recent_threshold = datetime.now(timezone.utc) - timedelta(seconds=5)
        existing_duplicate = (
            db.query(Transaction)
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.amount == tx_in.amount,
                Transaction.description == norm_desc,
                Transaction.transaction_date == tx_in.transaction_date,
                Transaction.created_at >= recent_threshold,
            )
            .order_by(Transaction.id.desc())
            .first()
        )

        if existing_duplicate:
            logger.warning("Phát hiện giao dịch lặp lại từ user %s trong 5s (id=%s). Trả về 409 Conflict.", current_user.id, existing_duplicate.id)
            raise HTTPException(status_code=409, detail="Giao dịch trùng lặp vừa được tạo. Vui lòng không gửi lại liên tục.")

        # 3. Phân loại danh mục bằng AI hoặc Heuristics (Bọc an toàn)
        category_id = tx_in.category_id
        ai_pred_data = None

        if not category_id:
            try:
                result = ai_classifier.classify(norm_desc, user_id=current_user.id, db=db)
                pred_cat_name = result.get("category", "Khác")
                pred_type = result.get("type", "expense")
                ai_pred_data = result
            except Exception as e:
                logger.exception("Ngoại lệ khi gọi AI Classifier, tự động fallback danh mục mặc định: %s", e)
                pred_cat_name = "Khác"
                pred_type = "expense"
                ai_pred_data = {"category": "Khác", "confidence": 0.5, "type": "expense"}

            # Tìm kiếm danh mục sẵn có của user hoặc hệ thống
            try:
                category = (
                    db.query(Category)
                    .filter(
                        (Category.user_id == current_user.id) | (Category.user_id.is_(None)),
                        Category.name == pred_cat_name,
                    )
                    .first()
                )

                if not category:
                    category = Category(name=pred_cat_name, type=pred_type, user_id=current_user.id)
                    db.add(category)
                    db.flush()

                category_id = category.id
            except Exception as e:
                logger.warning("Không thể tự động gán Category ID cho giao dịch: %s", e)
                category_id = None

        # 4. Lưu giao dịch vào Database
        new_tx = Transaction(
            amount=tx_in.amount,
            description=norm_desc,
            transaction_date=tx_in.transaction_date,
            category_id=category_id,
            user_id=current_user.id,
        )
        db.add(new_tx)
        db.flush()

        # Lưu dự đoán AI nếu có
        if ai_pred_data:
            try:
                ai_pred = AIPrediction(
                    transaction_id=new_tx.id,
                    predicted_category=ai_pred_data.get("category", "Khác"),
                    confidence=float(ai_pred_data.get("confidence", 0.9)),
                )
                db.add(ai_pred)
            except Exception as e:
                logger.warning("Không thể lưu AIPrediction: %s", e)

        db.commit()
        db.refresh(new_tx)
        return new_tx

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Lỗi nghiêm trọng khi tạo giao dịch cho user %s: %s", current_user.id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi lưu giao dịch. Vui lòng kiểm tra lại thông tin và thử lại."
        )
    finally:
        if acquired:
            with _in_flight_lock:
                _in_flight_signatures.discard(signature)


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
                rule = (
                    db.query(UserMemoryRule)
                    .filter(
                        UserMemoryRule.user_id == current_user.id,
                        UserMemoryRule.keyword_pattern == keyword,
                    )
                    .first()
                )
                if rule:
                    rule.category_id = tx_in.category_id
                    rule.frequency += 1
                else:
                    new_rule = UserMemoryRule(
                        user_id=current_user.id,
                        keyword_pattern=keyword,
                        category_id=tx_in.category_id,
                        frequency=1,
                    )
                    db.add(new_rule)
        except Exception as e:
            logger.warning("Không thể lưu kinh nghiệm Agent Memory: %s", e)

    if tx_in.amount is not None:
        tx.amount = tx_in.amount
    if tx_in.description is not None:
        tx.description = tx_in.description.strip()
    if tx_in.category_id is not None:
        tx.category_id = tx_in.category_id
    if tx_in.transaction_date is not None:
        tx.transaction_date = tx_in.transaction_date

    try:
        db.commit()
        db.refresh(tx)
        return tx
    except Exception as e:
        db.rollback()
        logger.exception("Lỗi cập nhật giao dịch %d: %s", tx_id, e)
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
    except Exception as e:
        db.rollback()
        logger.exception("Lỗi xóa giao dịch %d: %s", tx_id, e)
        raise HTTPException(status_code=500, detail="Lỗi xóa giao dịch")
