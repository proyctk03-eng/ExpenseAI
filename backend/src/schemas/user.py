"""Schemas cho module xác thực người dùng."""
import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """S3 Fix: Enforce strong password policy."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ HOA (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ thường (a-z)")
        if not re.search(r"[0-9]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ số (0-9)")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/~`]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%...)")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    roles: List[str] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        """S3 Fix: Enforce strong password policy for password change."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ HOA (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ thường (a-z)")
        if not re.search(r"[0-9]", v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 chữ số (0-9)")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/~`]", v):
            raise ValueError("Mật khẩu mới phải chứa ít nhất 1 ký tự đặc biệt")
        return v
