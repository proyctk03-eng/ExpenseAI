"""Model UserMemoryRule - Lưu trữ quy tắc bộ nhớ học được từ người dùng (TencentDB Agent Memory L1 Fact Memory)."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base


class UserMemoryRule(Base):
    """Quy tắc bộ nhớ cục bộ học được từ phản hồi / chỉnh sửa của người dùng."""
    __tablename__ = "user_memory_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword_pattern: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="memory_rules")
    category = relationship("Category")
