"""
Entry point chính của hệ thống.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import ENVIRONMENT
from src.database import init_db
from src.api import advice, auth, categories, reports, transactions, web, dashboard, feedback
from src.utils.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from src.middleware.logging import APILoggingMiddleware

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("expenseai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if ENVIRONMENT == "development":
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error("Lỗi khởi tạo DB: %s", e)
    yield


app = FastAPI(
    title="Expense Manager AI",
    description="Hệ thống API quản lý chi tiêu cá nhân thông minh, tích hợp phân loại và tư vấn tự động bằng AI.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(APILoggingMiddleware)

# CORS - thu hẹp theo môi trường
ALLOWED_ORIGINS = (
    ["http://localhost:8000", "http://localhost:3000", "http://127.0.0.1:8000"]
    if ENVIRONMENT == "development"
    else ["https://yourdomain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Đăng ký các router
app.include_router(web.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(advice.router)
app.include_router(feedback.router)


@app.get("/api")
def read_root():
    return {
        "status": "success",
        "message": "Welcome to Expense Manager AI API!",
        "docs_url": "/docs",
    }
