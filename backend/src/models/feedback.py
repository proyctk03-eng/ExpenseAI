"""Định nghĩa models cho hệ thống Phản hồi (Feedback Ticket System)."""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from .user import User


class FeedbackTicket(Base):
    """Ticket phản hồi từ người dùng."""
    __tablename__ = "feedback_tickets"
    __table_args__ = (
        Index("ix_feedback_user_id", "user_id"),
        Index("ix_feedback_status", "status"),
        Index("ix_feedback_topic", "topic"),
        Index("ix_feedback_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str] = mapped_column(String(50), nullable=False, default="other")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="feedback_tickets")
    replies: Mapped[List["TicketReply"]] = relationship(back_populates="ticket", cascade="all, delete-orphan", order_by="TicketReply.created_at")

    # --- Topic choices ---
    # bug        : Báo lỗi
    # feature    : Đóng góp tính năng
    # complaint  : Khiếu nại
    # other      : Khác

    # --- Status choices ---
    # pending      : Chưa xử lý
    # in_progress  : Đang xử lý
    # resolved     : Đã giải quyết
    # rejected     : Từ chối


class TicketReply(Base):
    """Phản hồi (trả lời) trong một ticket."""
    __tablename__ = "ticket_replies"
    __table_args__ = (
        Index("ix_reply_ticket_id", "ticket_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("feedback_tickets.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ticket: Mapped["FeedbackTicket"] = relationship(back_populates="replies")
    user: Mapped["User"] = relationship()
