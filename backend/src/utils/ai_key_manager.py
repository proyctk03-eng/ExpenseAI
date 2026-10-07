"""
Module quản lý danh sách Google Gemini API Keys và tự động Failover toàn hệ thống.
Khi một API Key hết quota / token (lỗi 429 hoặc Resource Exhausted),
hệ thống sẽ lập tức chuyển đổi sang API Key dự phòng mà không làm gián đoạn trải nghiệm người dùng.
"""
import logging
from typing import List, Optional
from openai import OpenAI

from src.config import get_gemini_api_keys, OPENAI_API_KEY

logger = logging.getLogger(__name__)


class GeminiKeyManager:
    """Singleton quản lý xoay vòng và dự phòng khóa Google Gemini API toàn hệ thống."""

    def __init__(self):
        self._keys: List[str] = get_gemini_api_keys()
        self._current_index: int = 0
        self._exhausted_keys: set = set()

    def reload_keys(self) -> None:
        """Tải lại danh sách key từ cấu hình."""
        self._keys = get_gemini_api_keys()
        self._current_index = 0
        self._exhausted_keys.clear()

    @property
    def has_keys(self) -> bool:
        """Kiểm tra có ít nhất 1 Gemini key khả dụng hay không."""
        return len(self._keys) > 0

    @property
    def current_key(self) -> Optional[str]:
        """Trả về API Key hiện tại đang hoạt động."""
        if not self._keys:
            return None
        return self._keys[self._current_index]

    @property
    def current_key_index(self) -> int:
        """Trả về index của key đang hoạt động (0 là primary, 1 là backup 1...)."""
        return self._current_index

    @property
    def total_keys(self) -> int:
        """Tổng số API keys được cấu hình."""
        return len(self._keys)

    def get_client(self, timeout: float = 15.0, max_retries: int = 1) -> Optional[OpenAI]:
        """Khởi tạo OpenAI-compatible client cho Google Gemini sử dụng key hiện tại."""
        key = self.current_key
        if not key:
            return None
        try:
            return OpenAI(
                api_key=key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=timeout,
                max_retries=max_retries,
            )
        except Exception as e:
            logger.warning("Không thể tạo client với Gemini key #%d: %s", self._current_index + 1, e)
            return None

    def get_async_client(self, timeout: float = 15.0, max_retries: int = 1):
        """Khởi tạo AsyncOpenAI-compatible client cho Google Gemini sử dụng key hiện tại."""
        from openai import AsyncOpenAI
        key = self.current_key
        if not key:
            return None
        try:
            return AsyncOpenAI(
                api_key=key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=timeout,
                max_retries=max_retries,
            )
        except Exception as e:
            logger.warning("Không thể tạo async client với Gemini key #%d: %s", self._current_index + 1, e)
            return None

    def mark_current_key_exhausted(self, reason: str = "") -> bool:
        """Đánh dấu key hiện tại hết hạn hoặc hết quota và chuyển sang key dự phòng tiếp theo.
        Trả về True nếu còn key dự phòng khả dụng, False nếu đã hết toàn bộ Gemini keys.
        """
        if self.current_key:
            self._exhausted_keys.add(self.current_key)
            masked_key = self.current_key[:6] + "..." + self.current_key[-4:] if len(self.current_key) > 10 else "***"
            logger.warning(
                "Gemini API Key #%d (%s) hết quota hoặc gặp sự cố (%s). Đang kích hoạt key dự phòng...",
                self._current_index + 1,
                masked_key,
                reason or "Rate limit / Quota exceeded",
            )

        # Tìm key tiếp theo chưa bị đánh dấu hết hạn
        for idx in range(len(self._keys)):
            if self._keys[idx] not in self._exhausted_keys:
                self._current_index = idx
                masked_new = self._keys[idx][:6] + "..." + self._keys[idx][-4:] if len(self._keys[idx]) > 10 else "***"
                logger.info(
                    "Đã tự động chuyển đổi sang Gemini API Key dự phòng #%d (%s) thành công.",
                    self._current_index + 1,
                    masked_new,
                )
                return True

        logger.error("TOÀN BỘ (%d) Google Gemini API Keys đã hết token/quota! Sẽ kích hoạt fallback nếu có.", len(self._keys))
        return False


# Singleton instance dùng chung toàn ứng dụng
gemini_key_manager = GeminiKeyManager()
