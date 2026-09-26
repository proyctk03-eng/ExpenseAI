"""Định nghĩa model cho RBAC (Role-Based Access Control)."""
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from .user import User

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # admin, user, viewer
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permissions", back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship(
        secondary="user_roles", back_populates="roles"
    )

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. transaction:create
    resource: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. transaction
    action: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. create, read, update, delete, manage

    roles: Mapped[List["Role"]] = relationship(
        secondary="role_permissions", back_populates="permissions"
    )

class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
