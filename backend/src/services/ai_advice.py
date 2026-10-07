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
        self.async_client = None
        self.model = "gpt-3.5-turbo"
        self._cache_ttl = 86400  # 24 giờ
        self._provider = "rule_based"

        # Ưu tiên sử dụng Google Gemini nếu có key khả dụng
        if gemini_key_manager.has_keys:
            client = gemini_key_manager.get_client(timeout=15.0, max_retries=1)
            async_client = gemini_key_manager.get_async_client(timeout=15.0, max_retries=1)
            if client and async_client:
                self.client = client
                self.async_client = async_client
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
                from openai import AsyncOpenAI
                self.async_client = AsyncOpenAI(
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
                new_async_client = gemini_key_manager.get_async_client(timeout=15.0, max_retries=1)
                if new_client and new_async_client:
                    self.client = new_client
                    self.async_client = new_async_client
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
                f"**Cảnh báo dòng tiền**: 3 tháng qua bạn đã chi tiêu tổng cộng {total_expense:,.0f} ₫ "
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
                f"**Cảnh báo thâm hụt**: Trong 3 tháng qua bạn đang chi vượt thu {deficit:,.0f} ₫ "
                f"(Tổng thu: {total_income:,.0f} ₫, Tổng chi: {total_expense:,.0f} ₫). "
                f"Danh mục chiếm tỷ trọng lớn nhất là {sorted_expenses[0][0]} ({top_cat_pct:.1f}%). "
                f"Lời khuyên: Cắt giảm ngay 15-20% chi phí ở danh mục này và hạn chế phát sinh chi tiêu mới để cân đối dòng tiền."
            )

        if savings_rate >= 25.0:
            return (
                f"**Quản lý tài chính xuất sắc**: Tỷ lệ tích lũy của bạn đạt {savings_rate:.1f}% "
                f"với số dư thặng dư +{balance:,.0f} ₫ (Tổng thu: {total_income:,.0f} ₫). "
                f"Khuyến nghị chuẩn 50/30/20: Tiếp tục duy trì phong độ, trích lập ít nhất 20% vào quỹ khẩn cấp 3-6 tháng sinh hoạt "
                f"hoặc kênh đầu tư an toàn sinh lời."
            )

        if savings_rate > 0:
            return (
                f"**Cần tối ưu tích lũy**: Bạn đang có thặng dư tài chính +{balance:,.0f} ₫, "
                f"nhưng tỷ lệ tích lũy mới đạt {savings_rate:.1f}% (mục tiêu lý tưởng là ≥20%). "
                f"Các khoản chi lớn nhất hiện tại: {top_cats_desc}. "
                f"Gợi ý: Đặt hạn mức chi tiêu hàng tuần cho nhóm này để nâng tỷ lệ tích lũy lên mức 20% trong tháng tới."
            )

        return (
            f"**Cân đối thu chi**: Thu nhập và chi tiêu của bạn đang ở mức hòa vốn ({total_income:,.0f} ₫). "
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
                        max_tokens=800,
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

    async def stream_chat_with_context(self, user_message: str, summary_data: dict, history: list[dict] = None):
        """Thực hiện chat trực tiếp dưới dạng stream (Generator)."""
        if not self.is_available or not self.async_client:
            # Fallback
            yield "data: " + json.dumps({"content": self._generate_rule_based_advice(summary_data)}) + "\n\n"
            yield "data: [DONE]\n\n"
            return

        system_prompt = (
            "Bạn là Trợ lý tài chính thông minh của ExpenseAI. "
            "Nhiệm vụ của bạn là giải đáp chính xác, đúng trọng tâm câu hỏi của người dùng "
            "dựa trên dữ liệu tài chính thu chi thực tế của họ và các nguyên tắc quản lý tài chính chuẩn mực. "
            "Bạn được cung cấp dữ liệu chi tiết theo từng tháng trong 6 tháng gần nhất (monthly_breakdown).\n\n"
            "QUY TẮC BẮT BUỘC:\n"
            "1. Trả lời trực tiếp vào câu hỏi, tính toán chính xác và đưa ra kết quả ngay.\n"
            "2. Tuyệt đối KHÔNG sử dụng công thức LaTeX ($$...$$ hay $...$). Viết phép tính bằng văn bản thông thường (ví dụ: 31 ngày x 100.000 = 3.100.000 VNĐ).\n"
            "3. Tuyệt đối KHÔNG thêm bất kỳ biểu tượng cảm xúc (emoji) nào, đặc biệt là 💡, 📊, 💰, ⚠️, 👋 hay các biểu tượng trang trí khác.\n"
            "4. KHÔNG tự ý đưa thêm mục lời khuyên, mẹo vặt hay nhận xét ngoài lề nếu người dùng không yêu cầu. Trả lời ngắn gọn, chuẩn xác, đúng số liệu, không trang trí cầu kỳ."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Dữ liệu tài chính: {json.dumps(summary_data, ensure_ascii=False)}"},
            {"role": "assistant", "content": "Tôi đã ghi nhận đầy đủ dữ liệu tài chính. Tôi sẵn sàng giải đáp!"},
        ]

        if history:
            for msg in history[-20:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
        for attempt in range(max_attempts):
            try:
                # Dùng AsyncOpenAI client với tham số stream=True
                stream = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True,
                )
                
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield "data: " + json.dumps({"content": content}) + "\n\n"
                        
                yield "data: [DONE]\n\n"
                return

            except RateLimitError as e:
                logger.warning("RateLimit trong stream_chat_with_context (lần thử %d): %s", attempt + 1, e)
                if self._failover_to_next_client(str(e)):
                    continue
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break
            except Exception as e:
                logger.exception("Lỗi gọi stream_chat_with_context: %s", e)
                err_msg = str(e).lower()
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                break

        # Fallback
        fallback_msg = self._generate_intelligent_chat_reply(user_message, summary_data)
        yield "data: " + json.dumps({"content": fallback_msg}) + "\n\n"
        yield "data: [DONE]\n\n"

    async def chat_with_context(self, user_message: str, summary_data: dict, history: list[dict] = None) -> str:
        """Thực hiện chat trực tiếp dựa trên bối cảnh dữ liệu tài chính của người dùng.
        
        Args:
            user_message: Tin nhắn mới nhất của người dùng
            summary_data: Dữ liệu thu chi tổng hợp 3 tháng
            history: Lịch sử hội thoại trước đó [{"role": "user"|"assistant", "content": "..."}]
        """
        if not self.is_available or not self.client:
            # Fallback: trả lời dựa trên rule-based nếu AI không khả dụng
            return self._generate_rule_based_advice(summary_data)

        system_prompt = (
            "Bạn là Trợ lý tài chính thông minh của ExpenseAI. "
            "Nhiệm vụ của bạn là giải đáp chính xác, đúng trọng tâm câu hỏi của người dùng "
            "dựa trên dữ liệu tài chính thu chi thực tế của họ và các nguyên tắc quản lý tài chính chuẩn mực. "
            "Bạn được cung cấp dữ liệu chi tiết theo từng tháng trong 6 tháng gần nhất (monthly_breakdown), "
            "bao gồm tổng thu, tổng chi, số dư, tỷ lệ tiết kiệm và chi tiết từng danh mục cho mỗi tháng. "
            "Khi người dùng hỏi về bất kỳ tháng cụ thể nào hoặc yêu cầu tính toán, hãy tra cứu dữ liệu và tính toán chính xác.\n\n"
            "QUY TẮC BẮT BUỘC:\n"
            "1. Trả lời trực tiếp vào câu hỏi, tính toán chính xác và đưa ra kết quả ngay.\n"
            "2. Tuyệt đối KHÔNG sử dụng công thức LaTeX ($$...$$ hay $...$). Viết phép tính bằng văn bản thông thường (ví dụ: 31 ngày x 100.000 = 3.100.000 VNĐ).\n"
            "3. Tuyệt đối KHÔNG thêm bất kỳ biểu tượng cảm xúc (emoji) nào, đặc biệt là 💡, 📊, 💰, ⚠️, 👋 hay các biểu tượng trang trí khác.\n"
            "4. KHÔNG tự ý đưa thêm mục lời khuyên, mẹo vặt hay nhận xét ngoài lề nếu người dùng không yêu cầu. Trả lời ngắn gọn, chuẩn xác, đúng số liệu, không trang trí cầu kỳ."
        )

        # Xây dựng chuỗi hội thoại đầy đủ: system → dữ liệu → lịch sử → câu hỏi mới
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Dữ liệu tài chính (chi tiết theo từng tháng và tổng quan): {json.dumps(summary_data, ensure_ascii=False)}"},
            {"role": "assistant", "content": "Tôi đã ghi nhận đầy đủ dữ liệu tài chính chi tiết theo từng tháng của bạn. Tôi sẵn sàng giải đáp, phân tích chi tiêu từng tháng và tư vấn cho bạn!"},
        ]

        # Thêm lịch sử hội thoại (giới hạn 20 tin nhắn gần nhất)
        if history:
            for msg in history[-20:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        # Thêm câu hỏi hiện tại
        messages.append({"role": "user", "content": user_message})

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
        for attempt in range(max_attempts):
            try:
                async def _call_api():
                    return await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000,
                    )
                    
                response = await asyncio.wait_for(_call_api(), timeout=20.0)
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
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg or "not_found" in err_msg or "404" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                break

        # Fallback: trả lời dựa trên bộ suy luận thông minh đa chiều nếu AI không khả dụng
        logger.info("Kích hoạt Fallback phân tích thông minh cho chat_with_context")
        return self._generate_intelligent_chat_reply(user_message, summary_data)

    def _generate_intelligent_chat_reply(self, user_message: str, summary_data: dict) -> str:
        """Trả lời thông minh dựa trên phân tích dữ liệu đa chiều khi LLM ngoại tuyến hoặc fallback."""
        import re
        msg = user_message.lower().strip()
        monthly = summary_data.get("monthly_breakdown", {})
        available_months = summary_data.get("available_months", [])
        analytics = summary_data.get("analytics", {})
        mom = summary_data.get("month_over_month", {})

        # 0. Xử lý tính toán chi phí hàng ngày trong tháng nếu có
        # Ví dụ: "tháng 12 ngày nào tôi cũng ăn 100k cơm thì tổng tôi ăn hết bao nhiêu"
        m_calc = re.search(r"tháng\s*(\d{1,2})", msg)
        if m_calc and any(w in msg for w in ["mỗi ngày", "ngày nào", "hàng ngày", "1 ngày"]) and any(w in msg for w in ["tổng", "hết bao nhiêu", "tất cả", "bao nhiêu"]):
            month_val = int(m_calc.group(1))
            if 1 <= month_val <= 12:
                import calendar
                from datetime import datetime
                curr_year = datetime.now().year
                days_in_m = calendar.monthrange(curr_year, month_val)[1]
                
                # Bỏ qua phần "tháng X" để lấy đúng số tiền chi tiêu
                sub_msg = msg[:m_calc.start()] + " " + msg[m_calc.end():]
                cost_match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(k|nghìn|ngàn|tr|triệu|000\b)?", sub_msg)
                if cost_match:
                    num_val = float(cost_match.group(1).replace(",", "."))
                    unit = (cost_match.group(2) or "").lower()
                    if unit in ["k", "nghìn", "ngàn", "000"]:
                        daily_cost = num_val * 1000
                    elif unit in ["tr", "triệu"]:
                        daily_cost = num_val * 1000000
                    elif num_val < 1000:
                        daily_cost = num_val * 1000
                    else:
                        daily_cost = num_val
                    
                    total_cost = days_in_m * daily_cost
                    formatted_daily = f"{int(daily_cost):,}".replace(",", ".")
                    formatted_total = f"{int(total_cost):,}".replace(",", ".")
                    return (
                        f"Tháng {month_val} có {days_in_m} ngày.\n"
                        f"Nếu mỗi ngày chi {formatted_daily} VNĐ, tổng số tiền chi trong tháng {month_val} là:\n"
                        f"{days_in_m} ngày x {formatted_daily} VNĐ = {formatted_total} VNĐ"
                    )

        # 1. Chào hỏi
        if any(g in msg for g in ["chào", "hello", "hi ", "hi!", "alo", "hey"]) or msg in ["hi", "chào"]:
            return (
                "**Xin chào! Tôi là Trợ lý tài chính ExpenseAI.**\n\n"
                "Tôi có thể hỗ trợ bạn theo dõi và phân tích chi tiêu:\n"
                "- Phân tích chi tiêu từng tháng (VD: 'Tháng 8 chi tiêu thế nào?', 'Chi tiết tháng này')\n"
                "- So sánh giữa các tháng (VD: 'So sánh tháng này với tháng trước')\n"
                "- Tìm xu hướng và cực trị (VD: 'Tháng nào tôi chi tiêu nhiều nhất?', 'Bình quân mỗi tháng tiêu bao nhiêu?')\n"
                "- Tư vấn ngân sách và tiết kiệm theo chuẩn 50/30/20.\n\n"
                "Bạn muốn tìm hiểu thông tin tài chính nào?"
            )

        # 2. Câu hỏi về tháng nhiều nhất / cao nhất
        if any(k in msg for k in ["nhiều nhất", "cao nhất", "lớn nhất", "đỉnh điểm"]):
            if any(w in msg for w in ["chi", "tiêu", "xài"]):
                highest_exp = analytics.get("highest_expense_month")
                if highest_exp:
                    m_str = highest_exp["month"]
                    amt = highest_exp["amount"]
                    m_detail = monthly.get(m_str, {})
                    top_cats = sorted(m_detail.get("categories", {}).get("expense", {}).items(), key=lambda x: x[1], reverse=True)[:2]
                    top_txt = f" (chi nhiều nhất cho: {', '.join([f'**{c}** ({a:,.0f} ₫)' for c, a in top_cats])})" if top_cats else ""
                    return f"**Tháng chi tiêu nhiều nhất** của bạn là **Tháng {m_str}** với tổng chi **{amt:,.0f} ₫**{top_txt}."
            if any(w in msg for w in ["thu", "kiếm", "lương"]):
                highest_inc = analytics.get("highest_income_month")
                if highest_inc:
                    return f"**Tháng có thu nhập cao nhất** là **Tháng {highest_inc['month']}** với tổng thu **{highest_inc['amount']:,.0f} ₫**."

        # 3. Câu hỏi về tháng ít nhất / thấp nhất
        if any(k in msg for k in ["ít nhất", "thấp nhất", "tiết kiệm nhất"]):
            lowest_exp = analytics.get("lowest_expense_month")
            if lowest_exp:
                return f"**Tháng chi tiêu thấp nhất** của bạn là **Tháng {lowest_exp['month']}** với tổng chi chỉ **{lowest_exp['amount']:,.0f} ₫**."

        # 4. Câu hỏi về trung bình / bình quân
        if any(k in msg for k in ["trung bình", "bình quân"]):
            avg_exp = analytics.get("average_monthly_expense", 0)
            avg_inc = analytics.get("average_monthly_income", 0)
            total_m = analytics.get("total_tracked_months", len(available_months))
            return (
                f"**Thống kê bình quân ({total_m} tháng theo dõi gần nhất):**\n"
                f"*   **Chi tiêu trung bình:** {avg_exp:,.0f} ₫/tháng\n"
                f"*   **Thu nhập trung bình:** {avg_inc:,.0f} ₫/tháng\n"
                f"*   **Số dư tích lũy bình quân:** {avg_inc - avg_exp:+,.0f} ₫/tháng."
            )

        # 5. So sánh các tháng
        if "so sánh" in msg or ("tháng này" in msg and "tháng trước" in msg):
            if mom:
                c_m = mom.get("current_month")
                p_m = mom.get("previous_month")
                e_diff = mom.get("expense_diff", 0)
                e_pct = mom.get("expense_pct_change", 0)
                trend = f"**tăng +{e_pct:.1f}%** (+{e_diff:,.0f} ₫)" if e_diff > 0 else f"**giảm {abs(e_pct):.1f}%** (-{abs(e_diff):,.0f} ₫)"
                return (
                    f"**So sánh chi tiêu Tháng {c_m} so với Tháng {p_m}:**\n"
                    f"*   Chi tiêu {trend}.\n"
                    f"*   Thu nhập thay đổi: **{mom.get('income_diff', 0):+,.0f} ₫** ({mom.get('income_pct_change', 0):+.1f}%)."
                )

        # 6. Hỏi về tháng cụ thể (ví dụ: "tháng 8", "tháng 9", "08/2026", "2026-08")
        match_m = re.search(r"tháng\s*(\d{1,2})", msg)
        if match_m:
            m_num = int(match_m.group(1))
            matched_key = None
            for k in available_months:
                if k.endswith(f"-{m_num:02d}"):
                    matched_key = k
                    break
            if matched_key and matched_key in monthly:
                # Tìm tháng trước liền kề nếu có
                prev_data = None
                idx = available_months.index(matched_key)
                if idx + 1 < len(available_months):
                    prev_data = monthly.get(available_months[idx + 1])
                return self._generate_rule_based_monthly_advice(matched_key, monthly[matched_key], prev_data)
            else:
                return (
                    f"ℹ️ Bạn chưa có dữ liệu giao dịch cho **Tháng {m_num}**.\n"
                    f"Các tháng hiện có dữ liệu: {', '.join([f'Tháng {m}' for m in available_months]) if available_months else 'Chưa có giao dịch'}."
                )

        # 7. Hỏi về "tháng này" hoặc "tháng hiện tại"
        if "tháng này" in msg or "tháng hiện tại" in msg:
            curr_m = summary_data.get("current_month")
            if curr_m and curr_m in monthly:
                prev_data = None
                if len(available_months) >= 2 and available_months[0] == curr_m:
                    prev_data = monthly.get(available_months[1])
                return self._generate_rule_based_monthly_advice(curr_m, monthly[curr_m], prev_data)

        # Fallback chung sang chuyên gia phân tích 50/30/20
        return self._generate_rule_based_advice(summary_data)

    def _generate_rule_based_monthly_advice(self, month: str, month_data: dict, prev_month_data: dict = None) -> str:
        """Hệ thống phân tích tài chính chuyên gia ngoại tuyến theo từng tháng."""
        income = month_data.get("income", 0.0)
        expense = month_data.get("expense", 0.0)
        balance = income - expense
        categories = month_data.get("categories", {}).get("expense", {})

        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_cats = sorted_cats[:3]
        top_str = ", ".join([f"**{c}** ({a:,.0f} ₫)" for c, a in top_cats]) if top_cats else "Chưa có"

        savings_rate = (balance / income * 100) if income > 0 else 0.0

        comparison_text = ""
        if prev_month_data:
            p_exp = prev_month_data.get("expense", 0.0)
            if p_exp > 0:
                diff = expense - p_exp
                pct = (diff / p_exp) * 100
                if diff > 0:
                    comparison_text = f"\n*   **So với tháng trước:** Chi tiêu **tăng +{pct:.1f}%** (+{diff:,.0f} ₫). Cần kiểm tra lại các khoản chi lớn."
                else:
                    comparison_text = f"\n*   **So với tháng trước:** Chi tiêu **giảm {abs(pct):.1f}%** (-{abs(diff):,.0f} ₫). Xu hướng quản lý rất tích cực!"

        return (
            f"### Báo cáo Tài chính Tháng {month}\n"
            f"*   **Tổng thu nhập:** {income:,.0f} ₫\n"
            f"*   **Tổng chi tiêu:** {expense:,.0f} ₫\n"
            f"*   **Số dư ròng:** {'+' if balance >= 0 else ''}{balance:,.0f} ₫ (Tỷ lệ tiết kiệm: {savings_rate:.1f}%)\n"
            f"*   **Khoản chi nhiều nhất:** {top_str}{comparison_text}"
        )

    async def get_monthly_advice(self, month: str, month_data: dict, prev_month_data: dict = None, force_refresh: bool = False) -> str:
        """Phân tích chuyên sâu cho một tháng cụ thể bằng AI, kèm Redis Cache."""
        from src.config import CACHE_ENABLED, redis_client
        cache_payload = {"month": month, "current": month_data, "prev": prev_month_data}
        hash_key = self._compute_hash(cache_payload)
        cache_key = f"advice_month:{month}:{hash_key}"

        if CACHE_ENABLED and not force_refresh:
            try:
                cached_str = await redis_client.get(cache_key)
                if cached_str:
                    logger.info("Trả về kết quả Monthly AI Advice từ Redis Cache")
                    return cached_str
            except Exception as e:
                logger.warning("Lỗi Redis Cache: %s", e)

        if not self.is_available or not self.client:
            return self._generate_rule_based_monthly_advice(month, month_data, prev_month_data)

        prompt = (
            f"Bạn là Chuyên gia tư vấn tài chính ExpenseAI. Dưới đây là dữ liệu thu chi chi tiết của Tháng {month}:\n"
            f"{json.dumps(month_data, ensure_ascii=False)}\n"
        )
        if prev_month_data:
            prompt += f"Dữ liệu tháng trước liền kề để so sánh:\n{json.dumps(prev_month_data, ensure_ascii=False)}\n"

        prompt += (
            f"\nHãy đưa ra bản phân tích chuyên sâu cho Tháng {month} (khoảng 150-250 từ) bằng Markdown:\n"
            f"1. **Đánh giá tổng quan tháng {month}**: Thu, chi, số dư, tỷ lệ tiết kiệm theo chuẩn 50/30/20.\n"
            f"2. **Phân tích danh mục trọng yếu**: Nhóm chi lớn nhất, các điểm cần chú ý.\n"
            f"3. **So sánh với tháng trước** (nếu có dữ liệu): Chi tiêu tăng hay giảm bao nhiêu (%, số tiền) và nhận xét.\n"
            f"4. **Khuyến nghị hành động**: 2 gợi ý cụ thể để tối ưu cho tháng tới. Tuyệt đối không dùng LaTeX hay biểu tượng cảm xúc emoji."
        )

        max_attempts = max(2, gemini_key_manager.total_keys + 1)
        for attempt in range(max_attempts):
            try:
                async def _call_api():
                    return await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "Chuyên gia tài chính ExpenseAI. Phân tích chi tiết và đưa ra lời khuyên thực tế bằng tiếng Việt."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.6,
                        max_tokens=800,
                    )

                response = await asyncio.wait_for(_call_api(), timeout=20.0)
                advice_text = (response.choices[0].message.content or "").strip()

                if CACHE_ENABLED:
                    try:
                        await redis_client.set(cache_key, advice_text, ex=self._cache_ttl)
                    except Exception:
                        pass
                return advice_text

            except RateLimitError as e:
                logger.warning("Rate limit trong monthly advice (lần %d): %s", attempt + 1, e)
                if self._failover_to_next_client(str(e)):
                    continue
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break
            except Exception as e:
                logger.exception("Lỗi gọi monthly advice: %s", e)
                err_msg = str(e).lower()
                if "quota" in err_msg or "exhausted" in err_msg or "429" in err_msg or "not_found" in err_msg or "404" in err_msg:
                    if self._failover_to_next_client(str(e)):
                        continue
                break

        return self._generate_rule_based_monthly_advice(month, month_data, prev_month_data)


