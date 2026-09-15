"""Định nghĩa model User."""
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from .transaction import Transaction
    from .category import Category
    from .rbac import Role
    from .feedback import FeedbackTicket

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    categories: Mapped[List["Category"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["Role"]] = relationship(secondary="user_roles", back_populates="users")
    feedback_tickets: Mapped[List["FeedbackTicket"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self) -> bool:
        return self.username == "admin" or any(r.name == "admin" for r in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """Kiểm tra user có quyền truy cập resource cụ thể không"""
        for role in self.roles:
            for perm in role.permissions:
                if perm.name == permission_name or perm.name == "*:*":
                    return True
        return False
