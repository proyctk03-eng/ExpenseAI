"""Schemas Pydantic cho Quản lý Ngân sách (Budget)."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Định dạng YYYY-MM")
    amount_limit: float = Field(..., gt=0, description="Hạn mức ngân sách tối đa")
    category_id: Optional[int] = Field(None, description="ID danh mục (None = Tổng ngân sách)")
    alert_threshold: int = Field(default=80, ge=10, le=100, description="Ngưỡng cảnh báo %")


class BudgetUpdate(BaseModel):
    amount_limit: Optional[float] = Field(None, gt=0)
    alert_threshold: Optional[int] = Field(None, ge=10, le=100)


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int] = None
    category_name: str
    month: str
    amount_limit: float
    alert_threshold: int
    spent_amount: float = 0.0
    remaining_amount: float = 0.0
    spent_percentage: float = 0.0
    status: str = "safe"  # safe, warning, exceeded
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetSummaryResponse(BaseModel):
    month: str
    total_budget: float
    total_spent: float
    total_remaining: float
    overall_percentage: float
    overall_status: str
    budgets: list[BudgetResponse]
