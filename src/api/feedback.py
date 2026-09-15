"""API quản lý phản hồi (Feedback Ticket System)."""
import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from src.database import get_db
from src.models import FeedbackTicket, TicketReply, User
from src.schemas.feedback import (
    FeedbackCreate, FeedbackResponse, FeedbackDetailResponse,
    FeedbackStatusUpdate, ReplyCreate, ReplyResponse,
)
from src.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feedback", tags=["feedback"])


def _ticket_to_response(ticket: FeedbackTicket) -> dict:
    """Chuyển đổi FeedbackTicket ORM thành dict phù hợp FeedbackResponse."""
    return {
        "id": ticket.id,
        "user_id": ticket.user_id,
        "username": ticket.user.username,
        "subject": ticket.subject,
        "message": ticket.message,
        "topic": ticket.topic,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "reply_count": len(ticket.replies),
    }


def _reply_to_response(reply: TicketReply) -> dict:
    """Chuyển đổi TicketReply ORM thành dict phù hợp ReplyResponse."""
    return {
        "id": reply.id,
        "ticket_id": reply.ticket_id,
        "user_id": reply.user_id,
        "username": reply.user.username,
        "is_admin": reply.user.is_admin,
        "message": reply.message,
        "created_at": reply.created_at,
    }


# ──────────────────────────────────────────────
#  User: Tạo phản hồi mới
# ──────────────────────────────────────────────
@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Người dùng tạo ticket phản hồi mới."""
    ticket = FeedbackTicket(
        user_id=current_user.id,
        subject=data.subject,
        message=data.message,
        topic=data.topic,
        status="pending",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    logger.info("User %s created feedback ticket #%d", current_user.username, ticket.id)
    return _ticket_to_response(ticket)


# ──────────────────────────────────────────────
#  Admin: Lấy danh sách tất cả tickets (có filter)
# ──────────────────────────────────────────────
@router.get("/", response_model=List[FeedbackResponse])
def get_all_feedback(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = Query(None, alias="status"),
    topic: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin: Lấy danh sách toàn bộ tickets với bộ lọc thông minh."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền truy cập")

    query = db.query(FeedbackTicket)

    if status_filter:
        query = query.filter(FeedbackTicket.status == status_filter)
    if topic:
        query = query.filter(FeedbackTicket.topic == topic)
    if search:
        query = query.filter(FeedbackTicket.subject.ilike(f"%{search}%"))
    if start_date:
        query = query.filter(sa_func.date(FeedbackTicket.created_at) >= start_date)
    if end_date:
        query = query.filter(sa_func.date(FeedbackTicket.created_at) <= end_date)

    tickets = query.order_by(FeedbackTicket.created_at.desc()).offset(skip).limit(limit).all()
    return [_ticket_to_response(t) for t in tickets]


# ──────────────────────────────────────────────
#  Admin: Thống kê tổng quan
# ──────────────────────────────────────────────
@router.get("/stats")
def get_feedback_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thống kê số lượng ticket theo trạng thái."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền truy cập")

    total = db.query(sa_func.count(FeedbackTicket.id)).scalar() or 0
    pending = db.query(sa_func.count(FeedbackTicket.id)).filter(FeedbackTicket.status == "pending").scalar() or 0
    in_progress = db.query(sa_func.count(FeedbackTicket.id)).filter(FeedbackTicket.status == "in_progress").scalar() or 0
    resolved = db.query(sa_func.count(FeedbackTicket.id)).filter(FeedbackTicket.status == "resolved").scalar() or 0
    rejected = db.query(sa_func.count(FeedbackTicket.id)).filter(FeedbackTicket.status == "rejected").scalar() or 0

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "rejected": rejected,
    }


# ──────────────────────────────────────────────
#  User: Xem tickets của mình
# ──────────────────────────────────────────────
@router.get("/my", response_model=List[FeedbackResponse])
def get_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Người dùng xem danh sách tickets đã gửi."""
    tickets = (
        db.query(FeedbackTicket)
        .filter(FeedbackTicket.user_id == current_user.id)
        .order_by(FeedbackTicket.created_at.desc())
        .all()
    )
    return [_ticket_to_response(t) for t in tickets]


# ──────────────────────────────────────────────
#  Xem chi tiết ticket + replies
# ──────────────────────────────────────────────
@router.get("/{ticket_id}", response_model=FeedbackDetailResponse)
def get_feedback_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xem chi tiết ticket kèm toàn bộ lịch sử phản hồi."""
    ticket = db.query(FeedbackTicket).filter(FeedbackTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket")

    # Chỉ admin hoặc chủ ticket mới được xem
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền xem ticket này")

    return {
        "id": ticket.id,
        "user_id": ticket.user_id,
        "username": ticket.user.username,
        "subject": ticket.subject,
        "message": ticket.message,
        "topic": ticket.topic,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "replies": [_reply_to_response(r) for r in ticket.replies],
    }


# ──────────────────────────────────────────────
#  Admin: Cập nhật trạng thái ticket
# ──────────────────────────────────────────────
@router.put("/{ticket_id}/status", response_model=FeedbackResponse)
def update_feedback_status(
    ticket_id: int,
    data: FeedbackStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin: Cập nhật trạng thái xử lý của ticket."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền cập nhật trạng thái")

    ticket = db.query(FeedbackTicket).filter(FeedbackTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket")

    ticket.status = data.status
    db.commit()
    db.refresh(ticket)
    logger.info("Admin %s updated ticket #%d status to %s", current_user.username, ticket_id, data.status)
    return _ticket_to_response(ticket)


# ──────────────────────────────────────────────
#  Gửi phản hồi (reply) trong ticket
# ──────────────────────────────────────────────
@router.post("/{ticket_id}/reply", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
def create_reply(
    ticket_id: int,
    data: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gửi phản hồi (trả lời) trong một ticket. Cả admin và chủ ticket đều có thể reply."""
    ticket = db.query(FeedbackTicket).filter(FeedbackTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket")

    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền phản hồi ticket này")

    reply = TicketReply(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=data.message,
    )
    db.add(reply)

    # Tự động chuyển trạng thái nếu admin trả lời ticket pending
    if current_user.is_admin and ticket.status == "pending":
        ticket.status = "in_progress"

    db.commit()
    db.refresh(reply)
    logger.info("User %s replied to ticket #%d", current_user.username, ticket_id)
    return _reply_to_response(reply)
