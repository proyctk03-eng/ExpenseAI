"""
Module nạp và quản lý các biến cấu hình toàn cục từ file .env.
Bất kỳ cấu hình nào thay đổi theo môi trường (Dev/Prod) đều nên đặt ở đây.
"""
import os
from dotenv import load_dotenv

# Tìm và nạp các biến môi trường từ file .env vào os.environ
load_dotenv()

# --- Các biến môi trường bắt buộc ---
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Các biến môi trường có giá trị mặc định ---
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Môi trường chạy app: 'development' hoặc 'production'
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# --- Kiểm tra tính hợp lệ của cấu hình lúc khởi động ---
missing_keys = []
if not DATABASE_URL:
    missing_keys.append("DATABASE_URL")
if not SECRET_KEY:
    missing_keys.append("SECRET_KEY")
if not OPENAI_API_KEY:
    missing_keys.append("OPENAI_API_KEY")

if missing_keys:
    error_msg = f"LỖI KHỞI ĐỘNG: Thiếu các cấu hình biến môi trường sau: {', '.join(missing_keys)}"
    raise ValueError(error_msg)
