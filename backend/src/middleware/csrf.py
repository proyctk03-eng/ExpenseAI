"""CSRF Protection Middleware — Double-Submit Cookie Pattern."""
import secrets
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import ENVIRONMENT

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
EXEMPT_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/demo-login",
    "/api/auth/logout",
    "/api/auth/csrf-token",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/static",
)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware bảo vệ CSRF dựa trên cơ chế Double-Submit Cookie:
    - Trình duyệt lưu `csrftoken` trong cookie (non-httpOnly).
    - Frontend đọc cookie và gửi lại qua header `X-CSRF-Token` trên các state-changing request (POST/PUT/DELETE).
    - Server so khớp giá trị giữa cookie và header.
    - Miễn trừ cho các request dùng Authorization header độc lập (không dựa vào cookie session).
    """

    async def dispatch(self, request: Request, call_next):
        # Kiểm tra CSRF cho các phương thức thay đổi trạng thái
        if request.method not in SAFE_METHODS:
            path = request.url.path
            is_exempt = any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES)
            
            # Chỉ yêu cầu CSRF khi request có cookie xác thực (ambient credentials)
            has_cookie_auth = bool(request.cookies.get("access_token"))
            has_auth_header = bool(request.headers.get("authorization"))

            # Nếu dùng cookie auth và không nằm trong danh sách miễn trừ
            if has_cookie_auth and not is_exempt and not has_auth_header:
                csrf_cookie = request.cookies.get("csrftoken")
                csrf_header = request.headers.get("x-csrf-token")

                if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header):
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF verification failed: Thiếu hoặc sai CSRF token."}
                    )

        response = await call_next(request)

        # Đảm bảo client luôn có `csrftoken` cookie
        if "csrftoken" not in request.cookies:
            token = secrets.token_hex(32)
            response.set_cookie(
                key="csrftoken",
                value=token,
                httponly=False,  # JavaScript cần đọc được để gắn vào header X-CSRF-Token
                samesite="lax",
                secure=(ENVIRONMENT == "production"),
                path="/",
            )

        return response
