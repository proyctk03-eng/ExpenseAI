from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["income", "expense"]

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[Literal["income", "expense"]] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str
    user_id: Optional[int]
    model_config = ConfigDict(from_attributes=True)
