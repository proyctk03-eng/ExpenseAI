"""Service AI phân loại giao dịch tự động."""
import json
import logging

import httpx
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

from src.config import OPENAI_API_KEY, GEMINI_API_KEY

logger = logging.getLogger(__name__)


class AIClassifier:
    """Phân loại giao dịch vào danh mục bằng Gemini hoặc OpenAI."""

    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-3.5-turbo"

        # Ưu tiên sử dụng Google Gemini nếu có GEMINI_API_KEY
        if GEMINI_API_KEY and GEMINI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=GEMINI_API_KEY,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    http_client=httpx.Client(timeout=15.0),
                    max_retries=2,
                )
                self.model = "gemini-3.6-flash"
                self.is_available = True
                logger.info("AIClassifier khởi tạo thành công với mô hình Google Gemini (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo Gemini client trong AIClassifier: %s", e)

        # Fallback sang OpenAI nếu có OPENAI_API_KEY hợp lệ
        if not self.is_available and OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    http_client=httpx.Client(timeout=15.0),
                    max_retries=2,
                )
                self.model = "gpt-3.5-turbo"
                self.is_available = True
                logger.info("AIClassifier khởi tạo thành công với OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo OpenAI client trong AIClassifier: %s", e)

    def classify(self, description: str, user_id: int = None, db = None) -> dict:
        """Phân loại mô tả giao dịch và trả về {category, confidence, type}.
        Tầng 1 (L1 Fact Memory - TencentDB Agent Memory style): Tra cứu kinh nghiệm cá nhân.
        Tầng 2 (Deep AI): Gọi OpenAI API.
        Tầng 3 (Heuristic Fallback): Phân loại từ điển nội bộ.
        """
        # Tầng 1: Tra cứu bộ nhớ người dùng (L1 Fact Memory)
        if user_id and db:
            try:
                from src.models.user_memory_rule import UserMemoryRule
                rules = db.query(UserMemoryRule).filter(UserMemoryRule.user_id == user_id).order_by(UserMemoryRule.frequency.desc()).all()
                desc_lower = description.lower()
                for rule in rules:
                    if rule.keyword_pattern.lower() in desc_lower:
                        cat_name = rule.category.name if rule.category else "Khác"
                        cat_type = getattr(rule.category, "type", "expense") if rule.category else "expense"
                        return {
                            "category": cat_name,
                            "confidence": 1.0,
                            "type": cat_type,
                            "source": "user_memory"
                        }
            except Exception as e:
                logger.warning("Lỗi tra cứu UserMemoryRule: %s", e)

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
                model=self.model,
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
