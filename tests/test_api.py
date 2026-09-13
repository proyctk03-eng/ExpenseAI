"""
Bộ Test toàn diện cho hệ thống ExpenseAI.
Bao gồm: Xác thực, CRUD giao dịch, phân loại AI, báo cáo thống kê,
bảo mật, xử lý lỗi, và hiệu năng.
"""
import pytest
import time
from fastapi.testclient import TestClient
from src.main import app
from src.utils.limiter import limiter

# Vô hiệu hóa rate limit khi chạy kiểm thử
limiter.enabled = False

client = TestClient(app)


# =============================================
# HELPER: Đăng ký + đăng nhập lấy token
# =============================================
def create_test_user():
    """Tạo user test và trả về headers có Bearer token."""
    username = f"test_{int(time.time() * 1000)}"
    email = f"{username}@test.com"

    res = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": "Test@123"
    })
    assert res.status_code == 201, f"Register failed: {res.text}"

    res_login = client.post("/api/auth/login", json={
        "username": username,
        "password": "Test@123"
    })
    assert res_login.status_code == 200, f"Login failed: {res_login.text}"

    token = res_login.json()["access_token"]
    client.cookies.clear()
    return {"Authorization": f"Bearer {token}"}, username


# =============================================
# 1. KIỂM TRA API GỐC
# =============================================
class TestAPIRoot:
    """Kiểm tra endpoint gốc hoạt động."""

    def test_api_root_returns_200(self):
        """TC-01: GET /api trả về status 200."""
        res = client.get("/api")
        assert res.status_code == 200

    def test_api_root_response_format(self):
        """TC-02: GET /api trả về đúng cấu trúc JSON."""
        res = client.get("/api")
        data = res.json()
        assert data["status"] == "success"
        assert "message" in data
        assert "docs_url" in data

    def test_docs_page_accessible(self):
        """TC-03: Trang Swagger /docs trả về 200."""
        res = client.get("/docs")
        assert res.status_code == 200


# =============================================
# 2. KIỂM TRA ĐĂNG KÝ (Register)
# =============================================
class TestRegister:
    """Kiểm tra chức năng đăng ký tài khoản."""

    def test_register_success(self):
        """TC-04: Đăng ký thành công với thông tin hợp lệ."""
        username = f"reg_{int(time.time() * 1000)}"
        res = client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "Pass123"
        })
        assert res.status_code == 201

    def test_register_duplicate_username(self):
        """TC-05: Đăng ký trùng username phải bị từ chối."""
        username = f"dup_{int(time.time() * 1000)}"
        client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "Pass123"
        })
        # Đăng ký lại cùng username
        res2 = client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}_2@test.com",
            "password": "Pass123"
        })
        assert res2.status_code in [400, 409, 422]

    def test_register_missing_fields(self):
        """TC-06: Đăng ký thiếu trường bắt buộc phải trả lỗi 422."""
        res = client.post("/api/auth/register", json={
            "username": "nopass"
        })
        assert res.status_code == 422

    def test_register_invalid_email(self):
        """TC-07: Đăng ký email sai định dạng phải trả lỗi."""
        res = client.post("/api/auth/register", json={
            "username": f"bad_email_{int(time.time())}",
            "email": "not-an-email",
            "password": "Pass123"
        })
        assert res.status_code == 422

    def test_register_short_password(self):
        """TC-08: Đăng ký mật khẩu quá ngắn (<6 ký tự) phải bị từ chối."""
        res = client.post("/api/auth/register", json={
            "username": f"short_{int(time.time())}",
            "email": f"short_{int(time.time())}@test.com",
            "password": "12"
        })
        assert res.status_code == 422


# =============================================
# 3. KIỂM TRA ĐĂNG NHẬP (Login)
# =============================================
class TestLogin:
    """Kiểm tra chức năng đăng nhập."""

    def test_login_success(self):
        """TC-09: Đăng nhập đúng thông tin trả về access_token."""
        headers, _ = create_test_user()
        assert "Authorization" in headers

    def test_login_wrong_password(self):
        """TC-10: Đăng nhập sai mật khẩu phải bị từ chối."""
        headers, username = create_test_user()
        res = client.post("/api/auth/login", json={
            "username": username,
            "password": "WrongPassword"
        })
        assert res.status_code in [401, 400]

    def test_login_nonexistent_user(self):
        """TC-11: Đăng nhập user không tồn tại phải bị từ chối."""
        res = client.post("/api/auth/login", json={
            "username": "user_khong_ton_tai_99999",
            "password": "whatever"
        })
        assert res.status_code in [401, 400, 404]

    def test_login_returns_valid_token(self):
        """TC-12: Token trả về phải dùng được để truy cập API bảo vệ."""
        headers, _ = create_test_user()
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200
        assert "username" in res.json()


# =============================================
# 4. KIỂM TRA BẢO MẬT (Security)
# =============================================
class TestSecurity:
    """Kiểm tra bảo mật hệ thống."""

    def test_access_without_token(self):
        """TC-13: Truy cập API bảo vệ không có token phải bị 401/403."""
        client.cookies.clear()
        res = client.get("/api/transactions/")
        assert res.status_code in [401, 403]

    def test_access_with_invalid_token(self):
        """TC-14: Truy cập API bảo vệ với token giả phải bị từ chối."""
        client.cookies.clear()
        res = client.get("/api/transactions/", headers={
            "Authorization": "Bearer fake.token.here"
        })
        assert res.status_code in [401, 403]

    def test_user_cannot_see_other_user_data(self):
        """TC-15: User A không thể xem giao dịch của User B."""
        headers_a, _ = create_test_user()
        headers_b, _ = create_test_user()

        # User A tạo giao dịch
        client.post("/api/transactions/", json={
            "amount": 50000, "description": "Riêng tư A",
            "transaction_date": "2026-08-10"
        }, headers=headers_a)

        # User B truy vấn
        res_b = client.get("/api/transactions/", headers=headers_b)
        assert res_b.status_code == 200
        for tx in res_b.json():
            assert "Riêng tư A" not in tx["description"]


# =============================================
# 5. KIỂM TRA GIAO DỊCH (Transactions CRUD)
# =============================================
class TestTransactions:
    """Kiểm tra CRUD giao dịch."""

    def test_create_transaction(self):
        """TC-16: Tạo giao dịch thành công."""
        headers, _ = create_test_user()
        res = client.post("/api/transactions/", json={
            "amount": 35000,
            "description": "Ăn phở sáng",
            "transaction_date": "2026-08-15"
        }, headers=headers)
        assert res.status_code == 201
        assert res.json()["description"] == "Ăn phở sáng"

    def test_create_transaction_missing_fields(self):
        """TC-17: Tạo giao dịch thiếu trường bắt buộc phải lỗi 422."""
        headers, _ = create_test_user()
        res = client.post("/api/transactions/", json={
            "amount": 10000
        }, headers=headers)
        assert res.status_code == 422

    def test_list_transactions(self):
        """TC-18: Lấy danh sách giao dịch trả về mảng."""
        headers, _ = create_test_user()
        client.post("/api/transactions/", json={
            "amount": 20000, "description": "Test list",
            "transaction_date": "2026-08-15"
        }, headers=headers)
        res = client.get("/api/transactions/", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        assert len(res.json()) >= 1

    def test_delete_transaction(self):
        """TC-19: Xóa giao dịch thành công."""
        headers, _ = create_test_user()
        res_create = client.post("/api/transactions/", json={
            "amount": 99000, "description": "Sẽ bị xóa",
            "transaction_date": "2026-08-15"
        }, headers=headers)
        tx_id = res_create.json()["id"]

        res_del = client.delete(f"/api/transactions/{tx_id}", headers=headers)
        assert res_del.status_code in [200, 204]

    def test_delete_nonexistent_transaction(self):
        """TC-20: Xóa giao dịch không tồn tại phải trả lỗi 404."""
        headers, _ = create_test_user()
        res = client.delete("/api/transactions/999999", headers=headers)
        assert res.status_code == 404

    def test_search_transactions(self):
        """TC-21: Tìm kiếm giao dịch theo mô tả."""
        headers, _ = create_test_user()
        client.post("/api/transactions/", json={
            "amount": 45000, "description": "Bún bò Huế đặc biệt",
            "transaction_date": "2026-08-15"
        }, headers=headers)
        res = client.get("/api/transactions/?search=bún+bò", headers=headers)
        assert res.status_code == 200
        results = res.json()
        assert len(results) >= 1
        assert any("bún bò" in tx["description"].lower() for tx in results)

    def test_filter_by_date_range(self):
        """TC-22: Lọc giao dịch theo khoảng ngày."""
        headers, _ = create_test_user()
        client.post("/api/transactions/", json={
            "amount": 30000, "description": "Trong khoảng ngày",
            "transaction_date": "2026-08-10"
        }, headers=headers)
        res = client.get(
            "/api/transactions/?start_date=2026-08-01&end_date=2026-08-31",
            headers=headers
        )
        assert res.status_code == 200
        assert len(res.json()) >= 1


# =============================================
# 6. KIỂM TRA BÁO CÁO THỐNG KÊ (Reports)
# =============================================
class TestReports:
    """Kiểm tra chức năng báo cáo thống kê."""

    def test_summary_report(self):
        """TC-23: Báo cáo tổng hợp trả về đúng cấu trúc."""
        headers, _ = create_test_user()
        client.post("/api/transactions/", json={
            "amount": 100000, "description": "Thu nhập test",
            "transaction_date": "2026-08-15"
        }, headers=headers)
        res = client.get("/api/reports/summary", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "balance" in data

    def test_category_report(self):
        """TC-24: Báo cáo theo danh mục trả về mảng."""
        headers, _ = create_test_user()
        res = client.get("/api/reports/by_category", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)


# =============================================
# 7. KIỂM TRA AI TƯ VẤN (AI Advice)
# =============================================
class TestAIAdvice:
    """Kiểm tra chức năng AI tư vấn tài chính."""

    def test_ai_advice_endpoint(self):
        """TC-25: Endpoint AI advice phải trả về response (dù có hoặc không có dữ liệu)."""
        headers, _ = create_test_user()
        res = client.post("/api/advice/", headers=headers)
        assert res.status_code in [200, 400, 422]

    def test_ai_advice_without_auth(self):
        """TC-26: AI advice không có token phải bị từ chối."""
        client.cookies.clear()
        res = client.post("/api/advice/")
        assert res.status_code in [401, 403]


# =============================================
# 8. KIỂM TRA TRANG WEB (Web Pages)
# =============================================
class TestWebPages:
    """Kiểm tra các trang giao diện web trả về HTML."""

    def test_login_page(self):
        """TC-27: Trang /login phải trả về 200 và HTML."""
        res = client.get("/login")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]

    def test_register_page(self):
        """TC-28: Trang /register phải trả về 200 và HTML."""
        res = client.get("/register")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]

    def test_dashboard_page(self):
        """TC-29: Trang dashboard / phải trả về 200."""
        res = client.get("/")
        assert res.status_code == 200

    def test_transactions_page(self):
        """TC-30: Trang /transactions phải trả về 200."""
        res = client.get("/transactions")
        assert res.status_code == 200


# =============================================
# 9. KIỂM TRA XỬ LÝ LỖI (Error Handling)
# =============================================
class TestErrorHandling:
    """Kiểm tra xử lý lỗi và edge cases."""

    def test_invalid_endpoint(self):
        """TC-31: Truy cập URL không tồn tại phải trả về 404."""
        res = client.get("/api/khong-ton-tai")
        assert res.status_code == 404

    def test_invalid_json_body(self):
        """TC-32: Gửi body không phải JSON hợp lệ phải trả lỗi."""
        headers, _ = create_test_user()
        res = client.post("/api/transactions/",
                          content="this is not json",
                          headers={**headers, "Content-Type": "application/json"})
        assert res.status_code == 422

    def test_negative_zero_amount(self):
        """TC-33: Tạo giao dịch với amount = 0 phải bị từ chối hoặc xử lý."""
        headers, _ = create_test_user()
        res = client.post("/api/transactions/", json={
            "amount": 0,
            "description": "Amount zero",
            "transaction_date": "2026-08-15"
        }, headers=headers)
        # Amount 0 nên bị từ chối (constraint amount > 0)
        assert res.status_code in [400, 422]

    def test_very_long_description(self):
        """TC-34: Mô tả rất dài phải được xử lý (không crash server)."""
        headers, _ = create_test_user()
        long_desc = "A" * 5000
        res = client.post("/api/transactions/", json={
            "amount": 10000,
            "description": long_desc,
            "transaction_date": "2026-08-15"
        }, headers=headers)
        # Phải không crash (trả 201 hoặc 422)
        assert res.status_code in [201, 422]

    def test_special_characters_in_search(self):
        """TC-35: Tìm kiếm với ký tự đặc biệt không crash."""
        headers, _ = create_test_user()
        res = client.get(
            "/api/transactions/?search=%27%3BDROP+TABLE+users%3B--",
            headers=headers
        )
        assert res.status_code == 200
