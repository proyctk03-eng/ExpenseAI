import json
import logging
import httpx
from typing import Dict, Any

from openai import OpenAI
from src.config import GEMINI_API_KEY, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class AIVisionService:
    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-4o-mini"
        
        # Prefer Gemini 1.5 Flash for vision
        if GEMINI_API_KEY and GEMINI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=GEMINI_API_KEY,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    timeout=30.0,
                    max_retries=1,
                )
                self.model = "gemini-1.5-flash"
                self.is_available = True
                logger.info("AIVisionService initialized with Google Gemini (%s)", self.model)
            except Exception as e:
                logger.warning("Could not init Gemini vision client: %s", e)
                
        elif OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    timeout=30.0,
                    max_retries=1,
                )
                self.model = "gpt-4o-mini"
                self.is_available = True
                logger.info("AIVisionService initialized with OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Could not init OpenAI vision client: %s", e)

    def scan_receipt(self, base64_image_data: str, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        if not self.is_available or not self.client:
            return {"error": "AI Vision is not configured."}
            
        try:
            with open("src/prompts/vision_prompt.txt", "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except Exception as e:
            logger.error("Could not read vision_prompt.txt: %s", e)
            return {"error": "Lỗi cấu hình AI (Thiếu file prompt)."}

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
                return data
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Vision API: %s", content)
                return {"error": "Could not parse AI response"}
                
        except Exception as e:
            logger.exception("Vision API error: %s", e)
            return {"error": str(e)}
