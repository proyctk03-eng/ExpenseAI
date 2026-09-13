"""
Pytest configuration và global fixtures cho ExpenseAI.
Đảm bảo database và dữ liệu mặc định (RBAC, schema) được khởi tạo trước khi test chạy.
"""
import pytest
from src.database import init_db
from src.utils.limiter import limiter

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Khởi tạo toàn bộ database tables và RBAC roles/permissions trước khi chạy test."""
    limiter.enabled = False
    init_db()
    yield
