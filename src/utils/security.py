"""Mô-đun bảo mật: hash mật khẩu và tạo JWT token."""
import logging

import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

from src.config import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp với hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        logger.warning("Lỗi kiểm tra mật khẩu")
        return False


def get_password_hash(password: str) -> str:
    """Tạo bcrypt hash cho mật khẩu."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Tạo JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta) -> str:
    """Tạo JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
