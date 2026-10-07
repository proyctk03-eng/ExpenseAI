"""Dependency injection cho FastAPI: xác thực và phân quyền."""
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Callable

from fastapi import Depends, HTTPException, Query, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from src.config import SECRET_KEY, ALGORITHM
from src.database import get_db
from src.models import User

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Giải mã JWT token từ Header Authorization hoặc Cookie và trả về User hiện tại."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực chứng chỉ",
    )
    
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        else:
            raise credentials_exception
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_permission(required_permission: str) -> Callable:
    """
    Dependency kiểm tra quyền truy cập.
    Ví dụ: require_permission("transaction:create")
    """
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Không có quyền truy cập. Yêu cầu quyền: {required_permission}"
            )
        return current_user
    return dependency


@dataclass
class DateRange:
    """Dải ngày được parse từ query params."""
    start: date
    end: date


def get_date_range(
    time_range: str = Query("this_month"),
    start_date: str | None = None,
    end_date: str | None = None,
) -> DateRange:
    """Dependency chuyển đổi time_range thành cặp (start_date, end_date), hỗ trợ cả YYYY-MM và last_month."""
    import calendar
    today = date.today()
    last_month_end = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    ranges = {
        "today": (today, today),
        "this_week": (today - timedelta(days=today.weekday()), today),
        "this_month": (today.replace(day=1), today),
        "last_month": (last_month_start, last_month_end),
        "this_year": (today.replace(month=1, day=1), today),
        "all_time": (date(2000, 1, 1), today),
    }
    if time_range in ranges:
        return DateRange(*ranges[time_range])

    # Hỗ trợ định dạng tháng cụ thể 'YYYY-MM'
    if "-" in time_range and len(time_range) == 7:
        try:
            parts = time_range.split("-")
            y, m = int(parts[0]), int(parts[1])
            _, last_day = calendar.monthrange(y, m)
            return DateRange(date(y, m, 1), date(y, m, last_day))
        except Exception:
            pass

    # custom
    return DateRange(
        start=datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else today.replace(day=1),
        end=datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else today,
    )
