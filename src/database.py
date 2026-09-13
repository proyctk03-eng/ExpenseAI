"""
Thiết lập kết nối cơ sở dữ liệu sử dụng SQLAlchemy 2.0.
"""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
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
    default_categories = [
        {"name": "Lương", "type": "income"},
        {"name": "Thưởng", "type": "income"},
        {"name": "Thu nhập khác", "type": "income"},
        {"name": "Ăn uống", "type": "expense"},
        {"name": "Di chuyển", "type": "expense"},
        {"name": "Học tập", "type": "expense"},
        {"name": "Giải trí", "type": "expense"},
        {"name": "Sinh hoạt", "type": "expense"},
        {"name": "Mua sắm", "type": "expense"},
        {"name": "Khác", "type": "expense"},
    ]
    for cat in default_categories:
        exists = db.query(Category).filter(
            Category.user_id.is_(None),
            Category.name == cat["name"]
        ).first()
        if not exists:
            db.add(Category(name=cat["name"], type=cat["type"], user_id=None))
    db.commit()

def init_db() -> None:
    from src.models import User, Category, Transaction, AIPrediction  # noqa: F401
    from src.models.rbac import Role, Permission, UserRole, RolePermission  # noqa: F401
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        try:
            seed_default_rbac(db)
            seed_default_categories(db)
        except Exception:
            db.rollback()


