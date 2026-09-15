"""API quản lý giao dịch tích hợp AI, tối ưu hóa chống trùng lặp (Idempotency Guard) và xử lý ngoại lệ toàn diện."""
from datetime import date, datetime, timedelta, timezone
import logging
import threading
import time
import asyncio
from typing import List, Optional, Set, Tuple

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database import get_async_db
from src.models import Transaction, User, Category, AIPrediction
from src.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from src.utils.dependencies import require_permission
from src.utils.limiter import limiter
from src.services.ai_classifier import AIClassifier
from src.services.ai_vision import AIVisionService
import base64

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["transactions"])
ai_classifier = AIClassifier()
ai_vision = AIVisionService()

_in_flight_signatures: Set[Tuple[int, float, str, str]] = set()
_in_flight_lock = threading.Lock()

from fastapi import BackgroundTasks
from src.database import AsyncSessionLocal

async def process_receipt_background(base64_str: str, mime_type: str, user_id: int):
    try:
        # Chạy tác vụ gọi API AI Vision đồng bộ trên một thread khác để không block event loop
        result = await asyncio.to_thread(ai_vision.scan_receipt, base64_str, mime_type)
        if "error" in result:
            logger.error("Lỗi AI Vision background: %s", result["error"])
            return

        async with AsyncSessionLocal() as db:
            norm_desc = result.get("description", "Hóa đơn tự động")
            amount = result.get("amount", 0)
            tx_date_str = result.get("date", str(date.today()))
            try:
                tx_date = datetime.strptime(tx_date_str, "%Y-%m-%d").date()
            except:
                tx_date = date.today()

            # Sử dụng AI Classifier để phân loại
            cat_res = await ai_classifier.classify(norm_desc, user_id=user_id)
            pred_cat_name = cat_res.get("category", "Khác")
            pred_type = cat_res.get("type", "expense")

            stmt_cat = select(Category).filter(
                (Category.user_id == user_id) | (Category.user_id.is_(None)),
                Category.name == pred_cat_name,
            )
            res_cat = await db.execute(stmt_cat)
            category = res_cat.scalars().first()

            if not category:
                category = Category(name=pred_cat_name, type=pred_type, user_id=user_id)
                db.add(category)
                await db.flush()

            new_tx = Transaction(
                amount=amount,
                description=norm_desc,
                transaction_date=tx_date,
                category_id=category.id,
                user_id=user_id,
            )
            db.add(new_tx)
            await db.flush()
            
            ai_pred = AIPrediction(
                transaction_id=new_tx.id,
                predicted_category=cat_res.get("category", "Khác"),
                confidence=float(cat_res.get("confidence", 0.9)),
            )
            db.add(ai_pred)

            await db.commit()
            logger.info("Đã lưu hóa đơn tự động thành công cho user %d", user_id)

    except Exception as e:
        logger.exception("Lỗi process_receipt_background: %s", e)


@router.post("/scan-receipt", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def scan_receipt(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("transaction:create"))
):
    """Trích xuất thông tin hóa đơn từ ảnh upload bằng AI Vision chạy ngầm."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file hình ảnh.")
        
    try:
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Kích thước ảnh quá lớn (Tối đa 5MB).")
            
        base64_str = base64.b64encode(contents).decode("utf-8")
        
        # Đẩy tác vụ nặng vào BackgroundTasks
        background_tasks.add_task(process_receipt_background, base64_str, file.content_type, current_user.id)
        
        return {
            "status": "processing", 
            "message": "Hệ thống đang phân tích hóa đơn ngầm, kết quả sẽ có sau ít giây."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Lỗi khi upload hóa đơn: %s", e)
        raise HTTPException(status_code=500, detail="Lỗi khi xử lý hình ảnh hóa đơn.")


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    all_users: bool = False,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission("transaction:read")),
):
    """Lấy danh sách giao dịch với bộ lọc (Async)."""
    stmt = select(Transaction).options(joinedload(Transaction.category))
    
    if not (all_users and current_user.has_permission("*:*")):
        stmt = stmt.filter(Transaction.user_id == current_user.id)

    if search:
        stmt = stmt.filter(Transaction.description.ilike(f"%{search.strip()}%"))
    if start_date:
        stmt = stmt.filter(Transaction.transaction_date >= start_date)
    if end_date:
        stmt = stmt.filter(Transaction.transaction_date <= end_date)
    if category_id:
        stmt = stmt.filter(Transaction.category_id == category_id)

    stmt = stmt.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_transaction(
    request: Request,
    tx_in: TransactionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission("transaction:create")),
):
    """Tạo giao dịch mới (Async)."""
    norm_desc = (tx_in.description or "").strip()
    norm_amount = round(float(tx_in.amount), 2)
    norm_date_str = str(tx_in.transaction_date)
    signature = (current_user.id, norm_amount, norm_desc, norm_date_str)

    acquired = False
    try:
        with _in_flight_lock:
            if signature in _in_flight_signatures:
                is_duplicate_in_flight = True
            else:
                _in_flight_signatures.add(signature)
                acquired = True
                is_duplicate_in_flight = False

        if is_duplicate_in_flight:
            logger.info("Request trùng lặp đang in-flight cho user %s", current_user.id)
            for _ in range(20):
                await asyncio.sleep(0.2)
                with _in_flight_lock:
                    if signature not in _in_flight_signatures:
                        break

            recent_threshold = datetime.now(timezone.utc) - timedelta(seconds=20)
            stmt = select(Transaction).filter(
                Transaction.user_id == current_user.id,
                Transaction.amount == tx_in.amount,
                Transaction.description == norm_desc,
                Transaction.transaction_date == tx_in.transaction_date,
                Transaction.created_at >= recent_threshold,
            ).order_by(Transaction.id.desc())
            
            result = await db.execute(stmt)
            existing_tx = result.scalars().first()
            if existing_tx:
                raise HTTPException(status_code=409, detail="Giao dịch trùng lặp.")

        recent_threshold = datetime.now(timezone.utc) - timedelta(seconds=5)
        stmt = select(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.amount == tx_in.amount,
            Transaction.description == norm_desc,
            Transaction.transaction_date == tx_in.transaction_date,
            Transaction.created_at >= recent_threshold,
        ).order_by(Transaction.id.desc())
        
        result = await db.execute(stmt)
        existing_duplicate = result.scalars().first()
        if existing_duplicate:
            raise HTTPException(status_code=409, detail="Giao dịch trùng lặp.")

        category_id = tx_in.category_id
        ai_pred_data = None

        if not category_id:
            try:
                res = ai_classifier.classify(norm_desc, user_id=current_user.id)
                pred_cat_name = res.get("category", "Khác")
                pred_type = res.get("type", "expense")
                ai_pred_data = res
            except Exception as e:
                logger.exception("Lỗi AI: %s", e)
                pred_cat_name = "Khác"
                pred_type = "expense"
                ai_pred_data = {"category": "Khác", "confidence": 0.5, "type": "expense"}

            try:
                stmt_cat = select(Category).filter(
                    (Category.user_id == current_user.id) | (Category.user_id.is_(None)),
                    Category.name == pred_cat_name,
                )
                res_cat = await db.execute(stmt_cat)
                category = res_cat.scalars().first()

                if not category:
                    category = Category(name=pred_cat_name, type=pred_type, user_id=current_user.id)
                    db.add(category)
                    await db.flush()

                category_id = category.id
            except Exception as e:
                logger.warning("Không gán được Category: %s", e)
                category_id = None

        new_tx = Transaction(
            amount=tx_in.amount,
            description=norm_desc,
            transaction_date=tx_in.transaction_date,
            category_id=category_id,
            user_id=current_user.id,
        )
        db.add(new_tx)
        await db.flush()

        if ai_pred_data:
            ai_pred = AIPrediction(
                transaction_id=new_tx.id,
                predicted_category=ai_pred_data.get("category", "Khác"),
                confidence=float(ai_pred_data.get("confidence", 0.9)),
            )
            db.add(ai_pred)

        await db.commit()
        await db.refresh(new_tx)
        
        stmt_refresh = select(Transaction).options(joinedload(Transaction.category)).filter(Transaction.id == new_tx.id)
        res_refresh = await db.execute(stmt_refresh)
        return res_refresh.scalars().first()

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("Lỗi tạo giao dịch: %s", e)
        raise HTTPException(status_code=500, detail="Lỗi tạo giao dịch.")
    finally:
        if acquired:
            with _in_flight_lock:
                _in_flight_signatures.discard(signature)


@router.put("/{tx_id}", response_model=TransactionResponse)
async def update_transaction(
    tx_id: int,
    tx_in: TransactionUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission("transaction:update")),
):
    """Cập nhật giao dịch (Async)."""
    stmt = select(Transaction).options(joinedload(Transaction.category)).filter(Transaction.id == tx_id)
    if not current_user.has_permission("*:*"):
        stmt = stmt.filter(Transaction.user_id == current_user.id)
        
    result = await db.execute(stmt)
    tx = result.scalars().first()

    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

    if tx_in.category_id is not None and tx_in.category_id != tx.category_id:
        try:
            from src.models.user_memory_rule import UserMemoryRule
            keyword = (tx_in.description or tx.description or "").strip().lower()
            if len(keyword) >= 2:
                stmt_rule = select(UserMemoryRule).filter(
                    UserMemoryRule.user_id == current_user.id,
                    UserMemoryRule.keyword_pattern == keyword,
                )
                res_rule = await db.execute(stmt_rule)
                rule = res_rule.scalars().first()
                
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
            logger.warning("Lỗi Agent Memory: %s", e)

    if tx_in.amount is not None: tx.amount = tx_in.amount
    if tx_in.description is not None: tx.description = tx_in.description.strip()
    if tx_in.category_id is not None: tx.category_id = tx_in.category_id
    if tx_in.transaction_date is not None: tx.transaction_date = tx_in.transaction_date

    try:
        await db.commit()
        await db.refresh(tx)
        return tx
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi cập nhật giao dịch")


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    tx_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission("transaction:delete")),
):
    """Xóa giao dịch (Async)."""
    stmt = select(Transaction).filter(Transaction.id == tx_id)
    if not current_user.has_permission("*:*"):
        stmt = stmt.filter(Transaction.user_id == current_user.id)
        
    result = await db.execute(stmt)
    tx = result.scalars().first()

    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

    try:
        await db.delete(tx)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi xóa giao dịch")
