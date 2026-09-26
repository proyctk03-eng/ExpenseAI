"""Pydantic schemas cho hệ thống Phản hồi (Feedback Tickets)."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Feedback Ticket Schemas ---

class FeedbackCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    topic: str = Field("other", pattern=r"^(bug|feature|complaint|other)$")


class FeedbackStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(pending|in_progress|resolved|rejected)$")


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    username: str
    subject: str
    message: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    reply_count: int = 0
    model_config = ConfigDict(from_attributes=True)


# --- Reply Schemas ---

class ReplyCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


class ReplyResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    username: str
    is_admin: bool = False
    message: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FeedbackDetailResponse(BaseModel):
    """Chi tiết ticket kèm danh sách phản hồi."""
    id: int
    user_id: int
    username: str
    subject: str
    message: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    replies: List[ReplyResponse] = []
    model_config = ConfigDict(from_attributes=True)
