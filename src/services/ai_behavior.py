import logging
import httpx

from openai import OpenAI
from src.config import GEMINI_API_KEY, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class AIBehaviorService:
    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-3.5-turbo"
        
        # Prefer Gemini for text analysis
        if GEMINI_API_KEY and GEMINI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=GEMINI_API_KEY,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    timeout=15.0,
                    max_retries=1,
                )
                self.model = "gemini-1.5-flash"
                self.is_available = True
                logger.info("AIBehaviorService initialized with Google Gemini (%s)", self.model)
            except Exception as e:
                logger.warning("Could not init Gemini behavior client: %s", e)
                
        elif OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    timeout=15.0,
                    max_retries=1,
                )
                self.model = "gpt-3.5-turbo"
                self.is_available = True
                logger.info("AIBehaviorService initialized with OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Could not init OpenAI behavior client: %s", e)

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
        except Exception as e:
            logger.exception("Behavior API error: %s", e)
            return "Hệ thống AI đang tạm thời nâng cấp, vui lòng thử lại sau."
