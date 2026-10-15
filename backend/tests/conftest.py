"""
Pytest configuration và global fixtures cho ExpenseAI.
Đảm bảo database và dữ liệu mặc định (RBAC, schema) được khởi tạo trước khi test chạy.
"""
import os

# Đảm bảo các biến môi trường cần thiết được khởi tạo trước khi bất kỳ module nào được import
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "mock-api-key-for-testing":
    os.environ["GEMINI_API_KEY"] = "mock-gemini-primary-key-for-ci-testing-1234567890"
if not os.getenv("GEMINI_API_KEY_BACKUP") or os.getenv("GEMINI_API_KEY_BACKUP") == "mock-api-key-for-testing":
    os.environ["GEMINI_API_KEY_BACKUP"] = "mock-gemini-backup-key-for-ci-testing-0987654321"
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "mock-ci-secret-key-32-chars-long-for-testing"

import pytest
import src.config as app_config
from src.database import init_db
from src.utils.limiter import limiter
from src.utils.ai_key_manager import gemini_key_manager

# Đồng bộ trực tiếp vào app_config và reload key manager
if not app_config.GEMINI_API_KEY or app_config.GEMINI_API_KEY == "mock-api-key-for-testing":
    app_config.GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
if not app_config.GEMINI_API_KEY_BACKUP or app_config.GEMINI_API_KEY_BACKUP == "mock-api-key-for-testing":
    app_config.GEMINI_API_KEY_BACKUP = os.environ["GEMINI_API_KEY_BACKUP"]
gemini_key_manager.reload_keys()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Khởi tạo toàn bộ database tables và RBAC roles/permissions trước khi chạy test."""
    limiter.enabled = False
    init_db()
    yield
