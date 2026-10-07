"""Định nghĩa model Budget cho Quản lý Ngân sách cá nhân."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Numeric, String, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from .user import User
    from .category import Category


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("amount_limit > 0", name="chk_budget_amount_limit_positive"),
        UniqueConstraint("user_id", "category_id", "month", name="uq_budget_user_category_month"),
        Index("ix_budget_user_month", "user_id", "month"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)

    month: Mapped[str] = mapped_column(String(7), nullable=False)  # Định dạng 'YYYY-MM'
    amount_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    alert_threshold: Mapped[int] = mapped_column(default=80, nullable=False)  # % cảnh báo
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship()
    category: Mapped[Optional["Category"]] = relationship()

    @property
    def category_name(self) -> str:
        return self.category.name if self.category else "Tổng ngân sách"
