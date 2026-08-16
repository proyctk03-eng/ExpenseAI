from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    category_id: Optional[int] = None
    transaction_date: date

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    amount: float
    description: str
    transaction_date: date
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
