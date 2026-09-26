import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_request")

class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.4f}s"
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(
                f"{request.method} {request.url.path} - "
                f"ERROR: {str(e)} - {process_time:.4f}s"
            )
            raise e
