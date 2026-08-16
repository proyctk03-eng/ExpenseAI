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

def init_db() -> None:
    from src.models import User, Category, Transaction, AIPrediction  # noqa: F401
    Base.metadata.create_all(bind=engine)
