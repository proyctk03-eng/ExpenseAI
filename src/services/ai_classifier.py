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
        self.is_available = bool(OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing")
        if self.is_available:
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    http_client=httpx.Client(timeout=15.0),
                    max_retries=2,
                )
            except Exception as e:
                logger.warning("Không thể khởi tạo OpenAI client: %s", e)
                self.is_available = False
                self.client = None
        else:
            self.client = None

    def classify(self, description: str) -> dict:
        """Phân loại mô tả giao dịch và trả về {category, confidence, type}."""
        if not self.is_available or not self.client:
            # Fallback heuristic cơ bản
            desc_lower = description.lower()
            if any(k in desc_lower for k in ["lương", "thu nhập", "thưởng", "bố mẹ gửi", "tiền gửi", "học bổng"]):
                return {"category": "Thu nhập", "confidence": 0.8, "type": "income"}
            if any(k in desc_lower for k in ["phở", "cơm", "bún", "ăn", "uống", "cà phê", "trà sữa"]):
                return {"category": "Ăn uống", "confidence": 0.8, "type": "expense"}
            if any(k in desc_lower for k in ["xăng", "xe", "grab", "be", "xe buýt"]):
                return {"category": "Di chuyển", "confidence": 0.8, "type": "expense"}
            return {"category": "Khác", "confidence": 0.0, "type": "expense"}

        prompt = (
            "Bạn là chuyên gia phân loại tài chính cá nhân. Hãy phân loại giao dịch sau vào một "
            "trong các danh mục: Ăn uống, Di chuyển, Mua sắm, Hóa đơn, Giải trí, Sức khỏe, Giáo dục, "
            "Tiền bố mẹ gửi, Lương part-time, Học bổng, Khác. Xác định loại là 'expense' (chi tiêu) hoặc 'income' (thu nhập). "
            'Chỉ trả về JSON duy nhất có dạng: {"category": "...", "confidence": 0.95, "type": "expense"}.'
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
