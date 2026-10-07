"""
Pytest configuration và global fixtures cho ExpenseAI.
Đảm bảo database và dữ liệu mặc định (RBAC, schema) được khởi tạo trước khi test chạy.
"""
import os
import pytest
from src.database import init_db
from src.utils.limiter import limiter

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Khởi tạo toàn bộ database tables và RBAC roles/permissions trước khi chạy test."""
    # Đảm bảo Gemini failover tests có mock keys ngay cả khi không có .env (CI environment)
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "mock-api-key-for-testing":
        os.environ.setdefault("GEMINI_API_KEY", "mock-gemini-primary-key-for-ci-testing-1234567890")
        os.environ.setdefault("GEMINI_API_KEY_BACKUP", "mock-gemini-backup-key-for-ci-testing-0987654321")
        # Reload key manager với mock keys
        from src.utils.ai_key_manager import gemini_key_manager
        gemini_key_manager.reload_keys()

    limiter.enabled = False
    init_db()
    yield

