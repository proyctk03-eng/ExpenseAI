"""Service AI tư vấn tài chính."""
import json
import logging

import httpx
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

from src.config import OPENAI_API_KEY, GEMINI_API_KEY

logger = logging.getLogger(__name__)


class AIAdviceService:
    """Gọi Gemini hoặc OpenAI API để sinh lời khuyên tài chính."""

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
                logger.info("AIAdviceService khởi tạo thành công với mô hình Google Gemini (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo Gemini client trong AIAdviceService: %s", e)

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
                logger.info("AIAdviceService khởi tạo thành công với OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo OpenAI trong AIAdviceService: %s", e)

    def get_advice(self, summary_data: dict) -> str:
        """Phân tích dữ liệu chi tiêu và đưa ra lời khuyên."""
        if not self.is_available or not self.client:
            expense_total = sum(summary_data.get("expense", {}).values())
            income_total = sum(summary_data.get("income", {}).values())
            balance = income_total - expense_total
            if balance > 0:
                return f"Bạn đang kiểm soát tài chính tốt với số dư tích lũy +{balance:,.0f} ₫. Hãy trích tối thiểu 20% vào quỹ tiết kiệm khẩn cấp!"
            elif balance < 0:
                return f"Cảnh báo: Bạn đang chi vượt thu {-balance:,.0f} ₫. Hãy rà soát lại các danh mục chi tiêu lớn như Ăn uống và Giải trí để cân đối ngân sách."
            else:
                return "Chi tiêu của bạn đang ở mức vừa đủ so với thu nhập. Hãy cân nhắc lập kế hoạch ngân sách cụ thể cho các tháng tới."
        prompt = (
            "Bạn là chuyên gia tư vấn tài chính. Dựa trên dữ liệu tổng hợp 3 tháng qua, "
            "hãy đưa ra lời khuyên tài chính cá nhân ngắn gọn (dưới 200 chữ), thực tế."
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
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
