"""Kiểm thử tự động cho cơ chế chống trùng lặp (Idempotency) và tối ưu luồng AI (Cache, Heuristics, Fallback)."""
import time
from fastapi.testclient import TestClient
import pytest

from src.main import app
from src.services.ai_classifier import AIClassifier
from src.services.ai_advice import AIAdviceService
from tests.test_api import create_test_user

client = TestClient(app)


class TestDeduplicationGuard:
    """Kiểm tra cơ chế chặn chèn trùng lặp giao dịch (Idempotency Guard)."""

    def test_prevent_duplicate_transaction_in_short_window(self):
        """Gửi cùng 1 giao dịch nhiều lần liên tiếp chỉ sinh ra 1 bản ghi duy nhất trong DB."""
        headers, user = create_test_user()
        payload = {
            "amount": 75000,
            "description": "Cà phê gặp khách hàng sáng",
            "transaction_date": "2026-09-15"
        }

        # Request 1: Tạo mới
        res1 = client.post("/api/transactions/", json=payload, headers=headers)
        assert res1.status_code == 201
        tx1 = res1.json()
        tx1_id = tx1["id"]

        # Request 2: Ngay lập tức gửi lại cùng payload (mô phỏng double click hoặc lag)
        res2 = client.post("/api/transactions/", json=payload, headers=headers)
        assert res2.status_code == 409
        assert "trùng lặp" in res2.json()["detail"].lower()

        # Kiểm tra danh sách giao dịch chỉ có đúng 1 bản ghi
        list_res = client.get("/api/transactions/?search=Cà+phê+gặp+khách", headers=headers)
        assert list_res.status_code == 200
        records = [tx for tx in list_res.json() if tx["id"] == tx1_id]
        assert len(records) == 1

    def test_allow_different_transactions(self):
        """Các giao dịch khác số tiền hoặc mô tả vẫn được tạo bình thường."""
        headers, _ = create_test_user()
        res1 = client.post("/api/transactions/", json={
            "amount": 30000,
            "description": "Bánh mì pate sáng",
            "transaction_date": "2026-09-15"
        }, headers=headers)
        assert res1.status_code == 201

        res2 = client.post("/api/transactions/", json={
            "amount": 50000,
            "description": "Bún chả trưa",
            "transaction_date": "2026-09-15"
        }, headers=headers)
        assert res2.status_code == 201
        assert res1.json()["id"] != res2.json()["id"]


class TestAIClassifierOptimization:
    """Kiểm tra hiệu năng và độ chính xác của bộ phân loại AI tích hợp Heuristics & Cache."""

    def test_heuristics_fast_classification(self):
        """Từ điển tiếng Việt mở rộng phải phân loại chính xác các khoản chi tiêu phổ biến mà không tốn quota LLM."""
        classifier = AIClassifier()

        cases = [
            ("Ăn bát phở bò tái chín", "Ăn uống", "expense"),
            ("Đổ xăng xe máy Petrolimex", "Di chuyển", "expense"),
            ("Thanh toán tiền điện EVN", "Hóa đơn", "expense"),
            ("Mua sắm quần áo trên Shopee", "Mua sắm", "expense"),
            ("Vé xem phim CGV tối thứ 7", "Giải trí", "expense"),
            ("Mua thuốc tại Pharmacity", "Sức khỏe", "expense"),
            ("Đóng học phí đại học", "Giáo dục", "expense"),
            ("Nhận lương tháng 9", "Thu nhập", "income"),
        ]

        for desc, expected_cat, expected_type in cases:
            start_t = time.time()
            res = classifier.classify(desc)
            elapsed = time.time() - start_t

            assert res["category"] == expected_cat, f"Mô tả '{desc}' phân loại sai: {res}"
            assert res["type"] == expected_type
            assert res["confidence"] >= 0.9
            assert elapsed < 0.05, f"Heuristics phải phản hồi dưới 50ms, thực tế: {elapsed*1000:.1f}ms"

    def test_classifier_cache(self):
        """Gọi phân loại 2 lần cùng một mô tả phải lấy từ cache trong tích tắc."""
        classifier = AIClassifier()
        desc = "Đặt trà sữa phúc long thơm ngon"
        res1 = classifier.classify(desc)
        assert res1["category"] == "Ăn uống"

        # Lần 2 phải lấy từ cache
        start_t = time.time()
        res2 = classifier.classify(desc)
        elapsed = time.time() - start_t

        assert res2["category"] == res1["category"]
        assert elapsed < 0.005, "Lấy từ Cache phải dưới 5ms"


class TestAIAdviceOptimization:
    """Kiểm tra Cache và Fallback chuyên gia tài chính ngoại tuyến."""

    def test_advice_cache_and_speed(self):
        """Lời khuyên tài chính phải được cache, các lần gọi sau không tốn quota và phản hồi tức thì."""
        service = AIAdviceService()
        sample_data = {
            "income": {"Lương": 15000000.0},
            "expense": {"Ăn uống": 5000000.0, "Tiền trọ": 3000000.0, "Di chuyển": 1000000.0}
        }

        advice1 = service.get_advice(sample_data)
        assert advice1 is not None and len(advice1) > 20

        # Lần 2: Kiểm tra cache
        start_t = time.time()
        advice2 = service.get_advice(sample_data)
        elapsed = time.time() - start_t

        assert advice2 == advice1
        assert elapsed < 0.01, f"Lấy từ Cache phải dưới 10ms, thực tế: {elapsed*1000:.1f}ms"

    def test_rule_based_fallback_financial_engine(self):
        """Khi API không khả dụng hoặc bị quá tải, bộ quy tắc tài chính phải sinh lời khuyên chuẩn 50/30/20."""
        service = AIAdviceService()
        
        # Trường hợp thâm hụt (chi tiêu vượt thu nhập)
        deficit_data = {
            "income": {"Lương": 8000000.0},
            "expense": {"Ăn uống": 6000000.0, "Mua sắm": 4000000.0}
        }
        advice_deficit = service._generate_rule_based_advice(deficit_data)
        assert "thâm hụt" in advice_deficit.lower() or "chi vượt thu" in advice_deficit.lower()
        assert "Ăn uống" in advice_deficit

        # Trường hợp quản lý tốt (thặng dư > 25%)
        surplus_data = {
            "income": {"Lương": 20000000.0},
            "expense": {"Ăn uống": 5000000.0, "Nhà ở": 4000000.0}
        }
        advice_surplus = service._generate_rule_based_advice(surplus_data)
        assert "50/30/20" in advice_surplus
        assert "tích lũy" in advice_surplus.lower() or "tiết kiệm" in advice_surplus.lower()
