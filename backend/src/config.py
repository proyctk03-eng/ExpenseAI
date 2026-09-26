"""
Module nạp và quản lý các biến cấu hình toàn cục từ file .env.
Bất kỳ cấu hình nào thay đổi theo môi trường (Dev/Prod) đều nên đặt ở đây.
"""
import os
import secrets
import logging
from dotenv import load_dotenv

_config_logger = logging.getLogger("expenseai.config")

# Tìm và nạp các biến môi trường từ file .env vào os.environ
load_dotenv()

# --- Các biến môi trường bắt buộc ---
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./expense_db.sqlite"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- SECRET_KEY: KHÔNG dùng hardcoded fallback (S1 Security Fix) ---
_env_secret = os.getenv("SECRET_KEY", "").strip()
if _env_secret:
    SECRET_KEY = _env_secret
else:
    # Dev mode: tạo key ngẫu nhiên mỗi lần khởi động (token sẽ hết hạn khi restart)
    SECRET_KEY = secrets.token_hex(32)
    _config_logger.warning(
        "SECRET_KEY chưa được cấu hình trong biến môi trường! "
        "Đang sử dụng key ngẫu nhiên (tất cả JWT token sẽ bị vô hiệu hóa khi restart). "
        "Hãy đặt SECRET_KEY trong file .env cho production."
    )

# --- Redis Configuration (Lazy Init để tránh crash khi import) ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"

_redis_client = None

def _get_redis_client():
    """Lazy-init Redis client để tránh crash khi Redis chưa sẵn sàng."""
    global _redis_client
    if _redis_client is None:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
    return _redis_client


# Backward-compatible proxy
class _RedisProxy:
    """Proxy object cho lazy Redis client access."""
    def __getattr__(self, name):
        return getattr(_get_redis_client(), name)

redis_client = _RedisProxy()

# --- Các biến môi trường có giá trị mặc định ---
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Môi trường chạy app: 'development' hoặc 'production'
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# --- Kiểm tra tính hợp lệ của cấu hình lúc khởi động trong production ---
if ENVIRONMENT == "production":
    missing_keys = []
    if not os.getenv("DATABASE_URL"):
        missing_keys.append("DATABASE_URL")
    if not os.getenv("SECRET_KEY"):
        missing_keys.append("SECRET_KEY")
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY hoặc GEMINI_API_KEY")

    if missing_keys:
        error_msg = f"LỖI KHỞI ĐỘNG (Production): Thiếu các cấu hình biến môi trường sau: {', '.join(missing_keys)}"
        raise ValueError(error_msg)
