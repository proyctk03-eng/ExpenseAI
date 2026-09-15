"""Service AI tư vấn tài chính tích hợp Caching, Backoff Retry và Chuyên gia tài chính ngoại tuyến."""
import hashlib
import json
import logging
import sys
import time
from typing import Dict, Any, Optional

import httpx
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

from src.config import GEMINI_API_KEY, OPENAI_API_KEY

logger = logging.getLogger(__name__)


import asyncio

class AIAdviceService:
    """Gọi Gemini hoặc OpenAI API để sinh lời khuyên tài chính, kèm bộ nhớ đệm Redis và Fallback thông minh."""

    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-3.5-turbo"
        self._cache_ttl = 86400  # 24 giờ

        # Ưu tiên sử dụng Google Gemini nếu có GEMINI_API_KEY
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
                logger.info("AIAdviceService khởi tạo thành công với mô hình Google Gemini (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo Gemini client trong AIAdviceService: %s", e)

        # Fallback sang OpenAI nếu có OPENAI_API_KEY hợp lệ
        if not self.is_available and OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    timeout=15.0,
                    max_retries=1,
                )
                self.model = "gpt-3.5-turbo"
                self.is_available = True
                logger.info("AIAdviceService khởi tạo thành công với OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo OpenAI trong AIAdviceService: %s", e)

    def _compute_hash(self, summary_data: dict) -> str:
        """Tạo khóa băm MD5 duy nhất cho bộ dữ liệu tài chính."""
        dumped = json.dumps(summary_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(dumped.encode("utf-8")).hexdigest()

    def _generate_rule_based_advice(self, summary_data: dict) -> str:
        """Hệ thống phân tích tài chính chuyên gia quy chuẩn (Rule-based Financial Advisor).
        Áp dụng Quy tắc 50/30/20 và phân tích cơ cấu chi tiêu.
        """
        income_dict = summary_data.get("income", {})
        expense_dict = summary_data.get("expense", {})

        total_income = sum(income_dict.values())
        total_expense = sum(expense_dict.values())
        balance = total_income - total_expense

        # Sắp xếp danh mục chi tiêu theo thứ tự giảm dần
        sorted_expenses = sorted(expense_dict.items(), key=lambda x: x[1], reverse=True)
        top_cats = sorted_expenses[:2]
        top_cats_desc = ", ".join([f"{name} ({amt:,.0f} ₫)" for name, amt in top_cats]) if top_cats else "chưa có"

        if total_income == 0 and total_expense > 0:
            return (
                f"⚠️ **Cảnh báo dòng tiền**: 3 tháng qua bạn đã chi tiêu tổng cộng {total_expense:,.0f} ₫ "
                f"nhưng chưa ghi nhận khoản thu nhập nào. Hạng mục chi nhiều nhất là {top_cats_desc}. "
                f"Hãy nhanh chóng bổ sung ghi chép thu nhập và cắt giảm chi tiêu không thiết yếu."
            )

        if total_income > 0:
            savings_rate = (balance / total_income) * 100
        else:
            savings_rate = 0.0

        if balance < 0:
            deficit = abs(balance)
            top_cat_pct = (sorted_expenses[0][1] / total_expense * 100) if (sorted_expenses and total_expense > 0) else 0
            return (
                f"⚠️ **Cảnh báo thâm hụt**: Trong 3 tháng qua bạn đang chi vượt thu {deficit:,.0f} ₫ "
                f"(Tổng thu: {total_income:,.0f} ₫, Tổng chi: {total_expense:,.0f} ₫). "
                f"Danh mục chiếm tỷ trọng lớn nhất là {sorted_expenses[0][0]} ({top_cat_pct:.1f}%). "
                f"Lời khuyên: Cắt giảm ngay 15-20% chi phí ở danh mục này và hạn chế phát sinh chi tiêu mới để cân đối dòng tiền."
            )

        if savings_rate >= 25.0:
            return (
                f"🌟 **Quản lý tài chính xuất sắc**: Tỷ lệ tích lũy của bạn đạt {savings_rate:.1f}% "
                f"với số dư thặng dư +{balance:,.0f} ₫ (Tổng thu: {total_income:,.0f} ₫). "
                f"Khuyến nghị chuẩn 50/30/20: Tiếp tục duy trì phong độ, trích lập ít nhất 20% vào quỹ khẩn cấp 3-6 tháng sinh hoạt "
                f"hoặc kênh đầu tư an toàn sinh lời."
            )

        if savings_rate > 0:
            return (
                f"💡 **Cần tối ưu tích lũy**: Bạn đang có thặng dư tài chính +{balance:,.0f} ₫, "
                f"nhưng tỷ lệ tích lũy mới đạt {savings_rate:.1f}% (mục tiêu lý tưởng là ≥20%). "
                f"Các khoản chi lớn nhất hiện tại: {top_cats_desc}. "
                f"Gợi ý: Đặt hạn mức chi tiêu hàng tuần cho nhóm này để nâng tỷ lệ tích lũy lên mức 20% trong tháng tới."
            )

        return (
            f"📊 **Cân đối thu chi**: Thu nhập và chi tiêu của bạn đang ở mức hòa vốn ({total_income:,.0f} ₫). "
            f"Để tránh rủi ro khi có biến cố, hãy áp dụng nguyên tắc 'Trả cho bản thân trước' — trích ít nhất 10% thu nhập "
            f"vào tài khoản tiết kiệm ngay khi có nguồn thu."
        )

    async def get_advice(self, summary_data: dict, force_refresh: bool = False) -> str:
        """Phân tích dữ liệu chi tiêu và đưa ra lời khuyên với Redis Cache 24 giờ, Retry và Heuristic Fallback."""
        from src.config import redis_client
        hash_key = self._compute_hash(summary_data)
        cache_key = f"advice:{hash_key}"

        # Kiểm tra Cache
        if not force_refresh:
            try:
                cached_str = await redis_client.get(cache_key)
                if cached_str:
                    logger.info("Trả về kết quả AI Advice từ Redis Cache (0ms, 0 quota)")
                    return cached_str
            except Exception as e:
                logger.warning("Lỗi Redis Cache: %s", e)

        # Nếu không có LLM client khả dụng -> kích hoạt Rule-Based Financial Advisor
        if not self.is_available or not self.client:
            advice = self._generate_rule_based_advice(summary_data)
            try:
                await redis_client.set(cache_key, advice, ex=self._cache_ttl)
            except Exception:
                pass
            return advice

        try:
            with open("src/prompts/financial_advice_prompt.txt", "r", encoding="utf-8") as f:
                prompt = f.read().strip()
        except Exception as e:
            logger.error("Could not read financial_advice_prompt.txt: %s", e)
            return "Lỗi cấu hình AI (Thiếu file prompt tư vấn)."

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                async def _call_api():
                    return await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=[
                            {"role": "system", "content": prompt},
                            {
                                "role": "user",
                                "content": f"Dữ liệu 3 tháng qua: {json.dumps(summary_data, ensure_ascii=False)}",
                            },
                        ],
                        temperature=0.6,
                    )
                    
                response = await asyncio.wait_for(_call_api(), timeout=5.0)
                content = response.choices[0].message.content
                advice_text = (content or "").strip()
                
                try:
                    await redis_client.set(cache_key, advice_text, ex=self._cache_ttl)
                except Exception:
                    pass
                return advice_text

            except RateLimitError as e:
                logger.warning("Gemini/OpenAI Rate Limit trong AI Advice (lần thử %d/%d): %s", attempt + 1, max_attempts, e)
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.5)
                else:
                    break
            except (APITimeoutError, APIConnectionError, asyncio.TimeoutError) as e:
                logger.warning("Gemini/OpenAI Timeout trong AI Advice (lần thử %d/%d): %s", attempt + 1, max_attempts, e)
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break
            except Exception as e:
                logger.exception("Lỗi không xác định khi gọi AI Advice: %s", e)
                break

        # Kích hoạt Fallback Chuyên gia Tài chính ngoại tuyến chất lượng cao
        logger.info("Kích hoạt Chuyên gia Tài chính Ngoại tuyến do Gemini API đang quá tải")
        advice = self._generate_rule_based_advice(summary_data)
        try:
            await redis_client.set(cache_key, advice, ex=self._cache_ttl)
        except Exception:
            pass
        return advice
