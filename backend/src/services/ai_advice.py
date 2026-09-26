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
from src.utils.ai_key_manager import gemini_key_manager

logger = logging.getLogger(__name__)


import asyncio

class AIAdviceService:
    """Gọi Gemini hoặc OpenAI API để sinh lời khuyên tài chính, kèm bộ nhớ đệm Redis, Failover Multi-Key và Fallback thông minh."""

    def __init__(self):
        self.is_available = False
        self.client = None
        self.model = "gpt-3.5-turbo"
        self._cache_ttl = 86400  # 24 giờ
        self._provider = "rule_based"

        # Ưu tiên sử dụng Google Gemini nếu có key khả dụng
        if gemini_key_manager.has_keys:
            client = gemini_key_manager.get_client(timeout=15.0, max_retries=1)
            if client:
                self.client = client
                self.model = "gemini-3.5-flash-lite"
                self.is_available = True
                self._provider = "gemini"
                logger.info("AIAdviceService khởi tạo thành công với mô hình Google Gemini (%s)", self.model)

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
                self._provider = "openai"
                logger.info("AIAdviceService khởi tạo thành công với OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo OpenAI trong AIAdviceService: %s", e)

    def _failover_to_next_client(self, reason: str = "") -> bool:
        """Tự động chuyển đổi sang Gemini API key dự phòng tiếp theo hoặc OpenAI khi gặp lỗi Quota/RateLimit."""
        if self._provider == "gemini":
            has_backup = gemini_key_manager.mark_current_key_exhausted(reason)
            if has_backup:
                new_client = gemini_key_manager.get_client(timeout=15.0, max_retries=1)
                if new_client:
                    self.client = new_client
                    logger.info("AIAdviceService đã chuyển đổi sang Gemini API key dự phòng thành công.")
                    return True

            # Nếu hết toàn bộ Gemini keys, thử chuyển sang OpenAI
            if OPENAI_API_KEY and OPENAI_API_KEY != "mock-api-key-for-testing":
                try:
                    self.client = OpenAI(api_key=OPENAI_API_KEY, timeout=15.0, max_retries=1)
                    self.model = "gpt-3.5-turbo"
                    self._provider = "openai"
                    logger.warning("Đã hết toàn bộ Gemini keys, AIAdviceService chuyển sang dùng OpenAI.")
                    return True
                except Exception as e:
                    logger.error("Không thể khởi tạo OpenAI fallback: %s", e)

        return False

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
        from src.config import CACHE_ENABLED, redis_client
        hash_key = self._compute_hash(summary_data)
        cache_key = f"advice:{hash_key}"

        # Kiểm tra Cache
        if CACHE_ENABLED and not force_refresh:
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
            if CACHE_ENABLED:
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

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
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
                        max_tokens=500,
                    )
                    
                response = await asyncio.wait_for(_call_api(), timeout=15.0)
                content = response.choices[0].message.content
                advice_text = (content or "").strip()
                
                if CACHE_ENABLED:
                    try:
                        await redis_client.set(cache_key, advice_text, ex=self._cache_ttl)
                    except Exception:
                        pass
                return advice_text

            except RateLimitError as e:
                logger.warning("Gemini/OpenAI Rate Limit trong AI Advice (lần thử %d/%d): %s", attempt + 1, max_attempts, e)
                if self._failover_to_next_client(str(e)):
                    continue
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
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
                err_msg = str(e).lower()
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg or "unauthorized" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                break

        # Kích hoạt Fallback Chuyên gia Tài chính ngoại tuyến chất lượng cao
        logger.info("Kích hoạt Chuyên gia Tài chính Ngoại tuyến do Gemini API đang quá tải")
        advice = self._generate_rule_based_advice(summary_data)
        if CACHE_ENABLED:
            try:
                await redis_client.set(cache_key, advice, ex=self._cache_ttl)
            except Exception:
                pass
        return advice

    async def chat_with_context(self, user_message: str, summary_data: dict) -> str:
        """Thực hiện chat trực tiếp dựa trên bối cảnh dữ liệu tài chính của người dùng."""
        if not self.is_available or not self.client:
            # Fallback: trả lời dựa trên rule-based nếu AI không khả dụng
            return self._generate_rule_based_advice(summary_data)

        system_prompt = "Trợ lý tài chính ExpenseAI. Trả lời ngắn gọn bằng tiếng Việt dựa trên dữ liệu thu chi."

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
        for attempt in range(max_attempts):
            try:
                async def _call_api():
                    return await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Dữ liệu: {json.dumps(summary_data, ensure_ascii=False)}\n\nCâu hỏi: {user_message}"},
                        ],
                        temperature=0.7,
                        max_tokens=300,
                    )
                    
                response = await asyncio.wait_for(_call_api(), timeout=15.0)
                return (response.choices[0].message.content or "").strip()

            except RateLimitError as e:
                logger.warning("RateLimit trong chat_with_context (lần thử %d): %s", attempt + 1, e)
                if self._failover_to_next_client(str(e)):
                    continue
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break
            except (APITimeoutError, APIConnectionError, asyncio.TimeoutError) as e:
                logger.warning("Timeout trong chat_with_context (lần thử %d): %s", attempt + 1, e)
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break
            except Exception as e:
                logger.exception("Lỗi không xác định khi gọi chat_with_context: %s", e)
                err_msg = str(e).lower()
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                break

        # Fallback: trả lời dựa trên rule-based thay vì trả về lỗi
        logger.info("Kích hoạt Fallback rule-based cho chat_with_context")
        return self._generate_rule_based_advice(summary_data)


