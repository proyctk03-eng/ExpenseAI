from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    start_date: date
    end_date: date
    currency: str = "VND"

class MonthlyComparison(BaseModel):
    labels: List[str]
    income: List[float]
    expense: List[float]

class CategoryBreakdown(BaseModel):
    labels: List[str]
    data: List[float]
    colors: List[str]
