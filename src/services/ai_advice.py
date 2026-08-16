"""Service AI tư vấn tài chính."""
import json
import logging

import httpx
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

from src.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


class AIAdviceService:
    """Gọi OpenAI API để sinh lời khuyên tài chính."""

    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(timeout=15.0),
            max_retries=2,
        )

    def get_advice(self, summary_data: dict) -> str:
        """Phân tích dữ liệu chi tiêu và đưa ra lời khuyên."""
        prompt = (
            "Bạn là chuyên gia tư vấn tài chính. Dựa trên dữ liệu tổng hợp 3 tháng qua, "
            "hãy đưa ra lời khuyên tài chính cá nhân ngắn gọn (dưới 200 chữ), thực tế."
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Dữ liệu 3 tháng qua: {json.dumps(summary_data, ensure_ascii=False)}"},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except (APITimeoutError, APIConnectionError) as e:
            logger.warning("AI API timeout/connection error: %s", e)
            return "Hệ thống AI đang phản hồi chậm. Vui lòng thử lại sau ít phút."
        except RateLimitError:
            logger.warning("AI API rate limit hit")
            return "Hệ thống đang quá tải. Vui lòng thử lại sau."
        except Exception as e:
            logger.exception("Lỗi không xác định khi gọi AI")
            return "Không thể kết nối AI. Vui lòng thử lại sau."
