import json
import logging
import httpx
from typing import Dict, Any

from openai import OpenAI, RateLimitError
from src.config import GEMINI_API_KEY, OPENAI_API_KEY
from src.utils.ai_key_manager import gemini_key_manager

logger = logging.getLogger(__name__)

class AIVisionService:
    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-4o-mini"
        self._provider = "offline"
        
        # Ưu tiên sử dụng Google Gemini nếu có key
        if gemini_key_manager.has_keys:
            client = gemini_key_manager.get_client(timeout=30.0, max_retries=1)
            if client:
                self.client = client
                self.model = "gemini-3.5-flash-lite"
                self.is_available = True
                self._provider = "gemini"
                logger.info("AIVisionService initialized with Google Gemini (%s)", self.model)
                
        elif OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    timeout=30.0,
                    max_retries=1,
                )
                self.model = "gpt-4o-mini"
                self.is_available = True
                self._provider = "openai"
                logger.info("AIVisionService initialized with OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Could not init OpenAI vision client: %s", e)

    def _failover_to_next_client(self, reason: str = "") -> bool:
        """Tự động chuyển sang key dự phòng tiếp theo hoặc OpenAI khi gặp RateLimit/Quota."""
        if self._provider == "gemini":
            has_backup = gemini_key_manager.mark_current_key_exhausted(reason)
            if has_backup:
                new_client = gemini_key_manager.get_client(timeout=30.0, max_retries=1)
                if new_client:
                    self.client = new_client
                    logger.info("AIVisionService switched to backup Gemini key.")
                    return True

            if OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
                try:
                    self.client = OpenAI(api_key=OPENAI_API_KEY, timeout=30.0, max_retries=1)
                    self.model = "gpt-4o-mini"
                    self._provider = "openai"
                    logger.warning("All Gemini keys exhausted, AIVisionService falling back to OpenAI.")
                    return True
                except Exception as e:
                    logger.error("Could not init OpenAI fallback: %s", e)
        return False

    def scan_receipt(self, base64_image_data: str, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        if not self.is_available or not self.client:
            return {"error": "AI Vision is not configured."}
            
        try:
            with open("src/prompts/vision_prompt.txt", "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except Exception as e:
            logger.error("Could not read vision_prompt.txt: %s", e)
            return {"error": "Lỗi cấu hình AI (Thiếu file prompt)."}

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": system_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.0
                )
                
                content = response.choices[0].message.content
                # Cleanup markdown formatting if any
                content = (content or "").replace("```json", "").replace("```", "").strip()
                
                try:
                    data = json.loads(content)
                    return data if isinstance(data, dict) else {}
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from Vision API: %s", content)
                    return {"error": "Could not parse AI response"}
                    
            except RateLimitError as e:
                logger.warning("Rate limit in scan_receipt (attempt %d/%d): %s", attempt + 1, max_attempts, e)
                if self._failover_to_next_client(str(e)):
                    continue
                return {"error": "Hệ thống AI nhận diện hóa đơn đang quá tải, vui lòng thử lại sau ít phút."}
            except Exception as e:
                logger.exception("Vision API error (attempt %d/%d): %s", attempt + 1, max_attempts, e)
                err_msg = str(e).lower()
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg or "unauthorized" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                return {"error": str(e)}

        return {"error": "Hệ thống AI nhận diện hóa đơn đang quá tải, vui lòng thử lại sau ít phút."}
