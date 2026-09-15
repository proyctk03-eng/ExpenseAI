"""
Thiết lập kết nối cơ sở dữ liệu sử dụng SQLAlchemy 2.0.
"""
import os
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from src.config import DATABASE_URL

# Tự động thay đổi URL nếu đang dùng SQLite để tương thích với async
async_db_url = DATABASE_URL
if async_db_url.startswith("sqlite://"):
    async_db_url = async_db_url.replace("sqlite://", "sqlite+aiosqlite://")

connect_args = {"check_same_thread": False} if "sqlite" in async_db_url else {}
engine = create_async_engine(async_db_url, pool_pre_ping=True, connect_args=connect_args)

# Sync engine dành cho các script Init/Seed lúc khởi động ứng dụng
sync_engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

if "sqlite" in async_db_url:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma_async(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()
        
    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma_sync(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_default_rbac(db: Session) -> None:
    from src.models.rbac import Role, Permission
    permissions_data = [
        {"name": "*:*", "resource": "all", "action": "all"},
        {"name": "transaction:create", "resource": "transaction", "action": "create"},
        {"name": "transaction:read", "resource": "transaction", "action": "read"},
        {"name": "transaction:update", "resource": "transaction", "action": "update"},
        {"name": "transaction:delete", "resource": "transaction", "action": "delete"},
        {"name": "category:create", "resource": "category", "action": "create"},
        {"name": "category:read", "resource": "category", "action": "read"},
        {"name": "category:update", "resource": "category", "action": "update"},
        {"name": "category:delete", "resource": "category", "action": "delete"},
        {"name": "report:read", "resource": "report", "action": "read"}
    ]
    perm_map = {}
    for p_data in permissions_data:
        p = db.query(Permission).filter(Permission.name == p_data["name"]).first()
        if not p:
            p = Permission(**p_data)
            db.add(p)
            db.flush()
        perm_map[p_data["name"]] = p

    roles_data = [
        {"name": "admin", "description": "Toàn quyền hệ thống", "perms": ["*:*"]},
        {"name": "user", "description": "Người dùng cơ bản", "perms": [
            "transaction:create", "transaction:read", "transaction:update", "transaction:delete",
            "category:create", "category:read", "category:update", "category:delete", "report:read"
        ]},
        {"name": "viewer", "description": "Chỉ xem", "perms": ["transaction:read", "category:read", "report:read"]}
    ]
    for r_data in roles_data:
        r = db.query(Role).filter(Role.name == r_data["name"]).first()
        if not r:
            r = Role(name=r_data["name"], description=r_data["description"])
            db.add(r)
            db.flush()
        r.permissions = [perm_map[p_name] for p_name in r_data["perms"] if p_name in perm_map]
    db.commit()

def seed_default_categories(db: Session) -> None:
    from src.models import Category
    if not db.query(Category).filter(Category.user_id.is_(None)).first():
        default_categories = [
            {"name": "Lương", "type": "income", "color": "#10B981"},
            {"name": "Thưởng", "type": "income", "color": "#34D399"},
            {"name": "Thu nhập khác", "type": "income", "color": "#6EE7B7"},
            {"name": "Ăn uống", "type": "expense", "color": "#F43F5E"},
            {"name": "Di chuyển", "type": "expense", "color": "#FBBF24"},
            {"name": "Học tập", "type": "expense", "color": "#60A5FA"},
            {"name": "Giải trí", "type": "expense", "color": "#A78BFA"},
            {"name": "Sinh hoạt", "type": "expense", "color": "#F472B6"},
            {"name": "Mua sắm", "type": "expense", "color": "#34D399"},
            {"name": "Khác", "type": "expense", "color": "#9CA3AF"},
        ]
        for cat in default_categories:
            db.add(Category(name=cat["name"], type=cat["type"], color=cat.get("color"), user_id=None, is_system=True))
        db.commit()

def seed_default_feedback(db: Session) -> None:
    from datetime import datetime, timedelta, timezone
    from src.models import FeedbackTicket, TicketReply, User
    from src.models.rbac import Role
    from src.utils.security import get_password_hash

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user_role = db.query(Role).filter(Role.name == "user").first()

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(username="admin", email="admin@expenseai.com", hashed_password=get_password_hash("admin123"))
        db.add(admin)
        db.flush()
    if admin_role and admin_role not in admin.roles:
        admin.roles.append(admin_role)

    sinhvien = db.query(User).filter(User.username == "sinhvien").first()
    if not sinhvien:
        sinhvien = User(username="sinhvien", email="sinhvien@university.edu.vn", hashed_password=get_password_hash("123456"))
        db.add(sinhvien)
        db.flush()
    if user_role and user_role not in sinhvien.roles:
        sinhvien.roles.append(user_role)
    db.commit()

def init_db() -> None:
    from src.models import User, Category, Transaction, AIPrediction, UserMemoryRule
    from src.models.rbac import Role, Permission, UserRole, RolePermission
    from src.models.feedback import FeedbackTicket, TicketReply
    Base.metadata.create_all(bind=sync_engine)
    with SessionLocal() as db:
        try:
            seed_default_rbac(db)
            seed_default_categories(db)
            seed_default_feedback(db)
        except Exception:
            db.rollback()
