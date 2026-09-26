"""Định nghĩa model AIPrediction."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from .transaction import Transaction

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    predicted_category: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transaction: Mapped["Transaction"] = relationship(back_populates="ai_prediction")
