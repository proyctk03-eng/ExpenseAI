import logging
import httpx

from openai import OpenAI, RateLimitError
from src.config import GEMINI_API_KEY, OPENAI_API_KEY
from src.utils.ai_key_manager import gemini_key_manager

logger = logging.getLogger(__name__)

class AIBehaviorService:
    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-3.5-turbo"
        self._provider = "offline"
        
        # Ưu tiên sử dụng Google Gemini nếu có key
        if gemini_key_manager.has_keys:
            client = gemini_key_manager.get_client(timeout=15.0, max_retries=1)
            if client:
                self.client = client
                self.model = "gemini-3.5-flash-lite"
                self.is_available = True
                self._provider = "gemini"
                logger.info("AIBehaviorService initialized with Google Gemini (%s)", self.model)
                
        elif OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    timeout=15.0,
                    max_retries=1,
                )
                self.model = "gpt-3.5-turbo"
                self.is_available = True
                self._provider = "openai"
                logger.info("AIBehaviorService initialized with OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Could not init OpenAI behavior client: %s", e)

    def _failover_to_next_client(self, reason: str = "") -> bool:
        """Tự động chuyển sang key dự phòng tiếp theo hoặc OpenAI khi gặp RateLimit/Quota."""
        if self._provider == "gemini":
            has_backup = gemini_key_manager.mark_current_key_exhausted(reason)
            if has_backup:
                new_client = gemini_key_manager.get_client(timeout=15.0, max_retries=1)
                if new_client:
                    self.client = new_client
                    logger.info("AIBehaviorService switched to backup Gemini key.")
                    return True

            if OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
                try:
                    self.client = OpenAI(api_key=OPENAI_API_KEY, timeout=15.0, max_retries=1)
                    self.model = "gpt-3.5-turbo"
                    self._provider = "openai"
                    logger.warning("All Gemini keys exhausted, AIBehaviorService falling back to OpenAI.")
                    return True
                except Exception as e:
                    logger.error("Could not init OpenAI fallback: %s", e)
        return False

    def analyze_behavior(self, transactions_log: str) -> str:
        if not self.is_available or not self.client:
            return "Tính năng phân tích hành vi đang tạm thời bị vô hiệu hóa do thiếu cấu hình AI."
            
        if not transactions_log.strip():
            return "Không có đủ dữ liệu giao dịch để AI có thể phân tích hành vi."

        try:
            with open("src/prompts/behavior_prompt.txt", "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except Exception as e:
            logger.error("Could not read behavior_prompt.txt: %s", e)
            return "Lỗi cấu hình AI (Thiếu file prompt hành vi)."

        prompt = system_prompt.format(transactions=transactions_log)

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                content = response.choices[0].message.content
                return (content or "").strip()
            except RateLimitError as e:
                logger.warning("Rate limit in analyze_behavior (attempt %d/%d): %s", attempt + 1, max_attempts, e)
                if self._failover_to_next_client(str(e)):
                    continue
                break
            except Exception as e:
                logger.exception("Behavior API error (attempt %d/%d): %s", attempt + 1, max_attempts, e)
                err_msg = str(e).lower()
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg or "unauthorized" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                break

        return "Hệ thống AI đang tạm thời nâng cấp, vui lòng thử lại sau."
