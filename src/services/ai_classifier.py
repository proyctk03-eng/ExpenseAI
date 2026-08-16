"""Service AI phân loại giao dịch tự động."""
import json
import logging

import httpx
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

from src.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


class AIClassifier:
    """Phân loại giao dịch vào danh mục bằng OpenAI."""

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("Thiếu OPENAI_API_KEY")
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(timeout=15.0),
            max_retries=2,
        )

    def classify(self, description: str) -> dict:
        """Phân loại mô tả giao dịch và trả về {category, confidence}."""
        prompt = (
            "Bạn là chuyên gia phân loại chi tiêu. Hãy phân loại giao dịch sau vào một "
            "trong các danh mục: Ăn uống, Di chuyển, Mua sắm, Hóa đơn, Giải trí, Sức khỏe, "
            "Giáo dục, Khác. Chỉ trả về JSON duy nhất có dạng "
            '{"category": "...", "confidence": 0.95}.'
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": description},
                ],
                temperature=0.0,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except (APITimeoutError, APIConnectionError) as e:
            logger.warning("AI Classification timeout: %s", e)
            return {"category": "Khác", "confidence": 0.0}
        except RateLimitError:
            logger.warning("AI rate limit hit during classification")
            return {"category": "Khác", "confidence": 0.0}
        except Exception as e:
            logger.exception("AI Classification Error")
            return {"category": "Khác", "confidence": 0.0}
