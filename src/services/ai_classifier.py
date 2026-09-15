"""Service AI phân loại giao dịch tự động tích hợp Caching và Heuristics Engine."""
import json
import logging
import re
import time
from typing import Optional, Dict, Any

import httpx
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

from src.config import OPENAI_API_KEY, GEMINI_API_KEY

import asyncio
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    "Ăn uống", "Di chuyển", "Mua sắm", "Hóa đơn", "Giải trí", 
    "Sức khỏe", "Giáo dục", "Tiền bố mẹ gửi", "Lương part-time", 
    "Học bổng", "Thu nhập", "Nhà cửa", "Cá nhân", "Khác", "Chưa phân loại"
]

class CategoryResponse(BaseModel):
    category: str
    confidence: float = Field(default=0.95)
    type: str = Field(default="expense")

# Từ điển quy chuẩn tiếng Việt với độ tin cậy cao
VIETNAMESE_HEURISTICS = [
    {
        "category": "Thu nhập",
        "type": "income",
        "keywords": [
            "lương", "thu nhập", "thưởng", "bố mẹ gửi", "tiền gửi", "học bổng",
            "bán đồ", "cổ tức", "lãi tiết kiệm", "hoàn tiền", "trợ cấp", "nhận chuyển khoản"
        ]
    },
    {
        "category": "Ăn uống",
        "type": "expense",
        "keywords": [
            "phở", "cơm", "bún", "bánh mì", "hủ tiếu", "mì tôm", "bánh canh",
            "ăn sáng", "ăn trưa", "ăn tối", "uống nước", "cà phê", "cafe", "trà sữa",
            "highlands", "starbucks", "phúc long", "the coffee house",
            "lotteria", "kfc", "mcdonald", "nhậu", "buffet", "lẩu", "nướng",
            "gà rán", "trái cây", "hoa quả", "quán ăn"
        ]
    },
    {
        "category": "Di chuyển",
        "type": "expense",
        "keywords": [
            "xăng", "đổ xăng", "xe buýt", "bus", "grab", "be", "gojek", "taxi",
            "vé tàu", "vé máy bay", "gửi xe", "rửa xe", "bảo dưỡng xe", "thay nhớt",
            "vá xe", "sửa xe", "phí cầu đường", "bot"
        ]
    },
    {
        "category": "Hóa đơn",
        "type": "expense",
        "keywords": [
            "tiền điện", "tiền nước", "tiền mạng", "internet", "wifi", "tiền trọ",
            "tiền phòng", "hóa đơn", "nạp tiền điện thoại", "viettel", "vinaphone",
            "mobifone", "truyền hình cáp", "phí chung cư", "phí dịch vụ", "rác"
        ]
    },
    {
        "category": "Mua sắm",
        "type": "expense",
        "keywords": [
            "shopee", "tiki", "lazada", "tiktok shop", "mua sắm", "quần áo",
            "giày", "dép", "mỹ phẩm", "siêu thị", "winmart", "coopmart",
            "bách hóa xanh", "chợ", "tạp hóa", "đồ gia dụng"
        ]
    },
    {
        "category": "Giải trí",
        "type": "expense",
        "keywords": [
            "xem phim", "cgv", "bhd", "lotte cinema", "karaoke", "du lịch",
            "bida", "game", "nạp game", "steam", "netflix", "spotify",
            "bar", "pub", "hội chợ", "vé tham quan"
        ]
    },
    {
        "category": "Sức khỏe",
        "type": "expense",
        "keywords": [
            "thuốc", "tiệm thuốc", "nhà thuốc", "pharmacity", "long châu",
            "khám bệnh", "bệnh viện", "nha khoa", "bác sĩ", "xét nghiệm",
            "vitamin", "khẩu trang", "bảo hiểm y tế"
        ]
    },
    {
        "category": "Giáo dục",
        "type": "expense",
        "keywords": [
            "học phí", "sách", "vở", "khóa học", "tài liệu", "giáo trình",
            "dụng cụ học tập", "thi cử", "chứng chỉ", "tiếng anh"
        ]
    },
]


class AIClassifier:
    """Phân loại giao dịch vào danh mục bằng Gemini hoặc OpenAI, có Cache Redis & Rule Heuristics."""

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
                logger.info("AIClassifier khởi tạo thành công với mô hình Google Gemini (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo Gemini client trong AIClassifier: %s", e)

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
                logger.info("AIClassifier khởi tạo thành công với OpenAI (%s)", self.model)
            except Exception as e:
                logger.warning("Không thể khởi tạo OpenAI client trong AIClassifier: %s", e)

    def _normalize_text(self, text: str) -> str:
        """Chuẩn hóa chuỗi mô tả để tra cứu cache và so khớp từ khóa."""
        return re.sub(r"\s+", " ", (text or "").strip().lower())

    def _match_heuristics(self, desc_norm: str) -> Optional[dict]:
        """So khớp với bộ từ điển quy chuẩn tiếng Việt mở rộng."""
        for rule in VIETNAMESE_HEURISTICS:
            for kw in rule["keywords"]:
                # Tìm từ khóa dưới dạng ranh giới từ hoặc cụm từ
                pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
                if re.search(pattern, desc_norm):
                    return {
                        "category": rule["category"],
                        "confidence": 0.95,
                        "type": rule["type"],
                        "source": "heuristic_dictionary"
                    }
        return None

    async def classify(self, description: str, user_id: Optional[int] = None, db = None) -> Dict[str, Any]:
        """Phân loại mô tả giao dịch theo kiến trúc 5 tầng bền vững:"""
        from src.config import redis_client
        desc_norm = self._normalize_text(description)
        if not desc_norm:
            return {"category": "Khác", "confidence": 0.0, "type": "expense", "source": "default"}

        # Tầng 1: Tra cứu bộ nhớ người dùng (L1 Fact Memory)
        if user_id and db:
            try:
                from sqlalchemy import select
                from src.models.user_memory_rule import UserMemoryRule
                
                # Check if db is async session or sync session
                if hasattr(db, 'execute'):
                    stmt = select(UserMemoryRule).filter(UserMemoryRule.user_id == user_id).order_by(UserMemoryRule.frequency.desc())
                    res = await db.execute(stmt)
                    rules = res.scalars().all()
                else:
                    rules = (
                        db.query(UserMemoryRule)
                        .filter(UserMemoryRule.user_id == user_id)
                        .order_by(UserMemoryRule.frequency.desc())
                        .all()
                    )
                    
                for rule in rules:
                    if rule.keyword_pattern and rule.keyword_pattern.lower() in desc_norm:
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

        # Tầng 2: Redis Cache (TTL 24 giờ)
        cache_key = f"classifier:{desc_norm}"
        try:
            cached_str = await redis_client.get(cache_key)
            if cached_str:
                logger.info("Trả về kết quả AI Classifier từ Redis Cache")
                return json.loads(cached_str)
        except Exception as e:
            logger.warning("Lỗi Redis Cache: %s", e)

        # Tầng 3: High-Confidence Heuristics Engine (Phân loại cực nhanh cho 85%+ chi tiêu thường nhật)
        heuristic_res = self._match_heuristics(desc_norm)
        if heuristic_res:
            try:
                await redis_client.set(cache_key, json.dumps(heuristic_res), ex=self._cache_ttl)
            except Exception:
                pass
            return heuristic_res

        # Nếu không có LLM client khả dụng -> dùng heuristic dự phòng
        if not self.is_available or not self.client:
            fallback_res = {"category": "Khác", "confidence": 0.5, "type": "expense", "source": "offline_fallback"}
            return fallback_res

        # Tầng 4: Gọi Gemini / OpenAI LLM cho các mô tả phức tạp, kèm Retry Exponential Backoff
        try:
            with open("src/prompts/classification_prompt.txt", "r", encoding="utf-8") as f:
                prompt = f.read().strip()
        except Exception as e:
            logger.error("Could not read classification_prompt.txt: %s", e)
            return {"category": "Chưa phân loại", "confidence": 0.0, "type": "expense", "source": "missing_prompt"}

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                # Wrap API call with asyncio.wait_for for strict timeout
                async def _call_api():
                    return await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": description},
                        ],
                        temperature=0.1,
                    )
                
                response = await asyncio.wait_for(_call_api(), timeout=2.5)
                content = response.choices[0].message.content
                
                # Parse JSON
                parsed_json = json.loads(content)
                
                # Guardrails (Chống ảo giác) bằng Pydantic
                try:
                    ai_result = CategoryResponse(**parsed_json)
                    if ai_result.category not in VALID_CATEGORIES:
                        logger.warning("Guardrail: Category '%s' không hợp lệ, chuyển về 'Khác'", ai_result.category)
                        ai_result.category = "Khác"
                        ai_result.confidence = 0.5
                except Exception as ve:
                    logger.warning("Guardrail: Pydantic validation failed: %s, fallback to Chưa phân loại", ve)
                    ai_result = CategoryResponse(category="Chưa phân loại", confidence=0.0)

                parsed_dict = ai_result.model_dump()
                parsed_dict["source"] = "gemini_api"

                # Lưu vào Redis Cache
                try:
                    await redis_client.set(cache_key, json.dumps(parsed_dict), ex=self._cache_ttl)
                except Exception:
                    pass
                return parsed_dict

            except asyncio.TimeoutError:
                logger.warning("Gemini API Timeout (asyncio.wait_for 2.5s) (lần thử %d/%d)", attempt + 1, max_attempts)
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break
            except Exception as e:
                logger.exception("Lỗi gọi AI Classifier (lần thử %d/%d): %s", attempt + 1, max_attempts, e)
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0)
                else:
                    break

        # Tầng 5: Graceful Heuristic Fallback khi API quá tải hoặc lỗi
        logger.info("Kích hoạt Graceful Fallback cho mô tả '%s'", description)
        fallback_res = {
            "category": "Chưa phân loại",
            "confidence": 0.0,
            "type": "expense",
            "source": "fallback_after_overload"
        }
        try:
            await redis_client.set(cache_key, json.dumps(fallback_res), ex=self._cache_ttl)
        except Exception:
            pass
        return fallback_res
