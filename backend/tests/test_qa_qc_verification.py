"""
Bộ kiểm thử QA/QC chuyên sâu (Quality Assurance & Automation Testing Suite).
Bao gồm:
1. Static & UI Analysis: Kiểm tra 100% không có raw emoji trong tất cả templates giao diện.
2. Web Route Health: Kiểm tra tính sẵn sàng của tất cả 8 trang giao diện Web cốt lõi.
3. Form Validation & Boundary Tests: Kiểm tra chặn số tiền âm, số tiền bằng 0, hoặc vượt ngưỡng 1 nghìn tỷ VNĐ.
4. Vietnamese Accent Verification: Xác nhận các từ khóa điều hướng cốt lõi hiển thị tiếng Việt có dấu chuẩn xác.
5. Concurrency & Double-Submit Protection: Xác minh cờ chống gửi lặp trong template giao diện.
6. Feedback & Communication Hub: Kiểm thử luồng gửi và phản hồi ticket hỗ trợ.
"""
import os
import re
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import SessionLocal
from src.models import User, Role, FeedbackTicket, TicketReply
from src.utils.security import get_password_hash, create_access_token


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def qa_user():
    """Tạo người dùng mẫu phục vụ bộ test QA/QC."""
    db = SessionLocal()
    try:
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(name="user", description="Người dùng")
            db.add(user_role)
            db.commit()

        user = db.query(User).filter(User.username == "qa_tester").first()
        if not user:
            user = User(
                username="qa_tester",
                email="tester@expenseai.local",
                hashed_password=get_password_hash("TesterPassword123!"),
            )
            user.roles.append(user_role)
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=1))
        return {"user": user, "token": token}
    finally:
        db.close()


def test_all_html_templates_zero_raw_emojis():
    """Kiểm tra toàn bộ thư mục frontend/templates đảm bảo 0 biểu tượng raw emoji Unicode."""
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates")
    assert os.path.exists(templates_dir), "Thư mục frontend/templates phải tồn tại"

    emoji_pattern = re.compile(
        "["
        "\U0001F000-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U00002600-\U000026FF"
        "\U00002B50"
        "\U0000231A-\U000023F3"
        "\U000023E9-\U000023FA"
        "]+",
        flags=re.UNICODE
    )

    violations = []
    for root, _, files in os.walk(templates_dir):
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as fh:
                    for line_idx, line in enumerate(fh, 1):
                        matches = emoji_pattern.findall(line)
                        if matches:
                            violations.append(f"{f}:{line_idx} chứa emoji {matches}")

    assert len(violations) == 0, f"Tìm thấy emoji trong templates: {violations}"


def test_web_routes_render_html(client):
    """Kiểm tra toàn bộ các trang giao diện Web người dùng trả về HTTP 200 và text/html."""
    routes = [
        "/",
        "/login",
        "/register",
        "/transactions",
        "/stats",
        "/budgets",
        "/settings",
        "/feedback",
    ]
    for route in routes:
        res = client.get(route)
        assert res.status_code == 200, f"Route {route} trả về status {res.status_code}"
        assert "text/html" in res.headers.get("content-type", "")
        assert len(res.text) > 100, f"Nội dung route {route} quá ngắn hoặc rỗng"


def test_transaction_boundary_amount_validation(client, qa_user):
    """Kiểm tra xử lý lỗi biên số tiền giao dịch: Chặn số âm, bằng 0, và số vượt ngưỡng 1 nghìn tỷ."""
    headers = {"Authorization": f"Bearer {qa_user['token']}"}

    # 1. Số tiền âm
    res_negative = client.post("/api/transactions/", json={
        "amount": -50000,
        "description": "Thử nghiệm số âm",
        "transaction_date": "2026-10-15"
    }, headers=headers)
    assert res_negative.status_code == 422, "Hệ thống phải chặn số tiền âm với mã 422"

    # 2. Số tiền bằng 0
    res_zero = client.post("/api/transactions/", json={
        "amount": 0,
        "description": "Thử nghiệm số 0",
        "transaction_date": "2026-10-15"
    }, headers=headers)
    assert res_zero.status_code == 422, "Hệ thống phải chặn số tiền bằng 0"

    # 3. Số tiền vượt ngưỡng 1 nghìn tỷ VNĐ
    res_overflow = client.post("/api/transactions/", json={
        "amount": 1000000000001,
        "description": "Thử nghiệm vượt ngưỡng",
        "transaction_date": "2026-10-15"
    }, headers=headers)
    assert res_overflow.status_code == 422, "Hệ thống phải chặn số tiền vượt ngưỡng cho phép"

    # 4. Số tiền hợp lệ
    res_valid = client.post("/api/transactions/", json={
        "amount": 75000,
        "description": "Cà phê sáng kiểm thử QA",
        "transaction_date": "2026-10-15"
    }, headers=headers)
    assert res_valid.status_code in (200, 201), "Số tiền hợp lệ phải lưu thành công"


def test_vietnamese_accented_ui_labels():
    """Kiểm tra các template giao diện cốt lõi có đầy đủ từ khóa tiếng Việt có dấu chuẩn."""
    base_tpl = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates", "base.html")
    assert os.path.exists(base_tpl)
    with open(base_tpl, "r", encoding="utf-8") as f:
        content = f.read()

    expected_keywords = [
        "Giao dịch",
        "Thống kê",
        "Ngân sách",
        "Cài đặt",
        "Xử lý phản hồi",
        "Đăng xuất",
    ]
    for kw in expected_keywords:
        assert kw in content, f"Từ khóa giao diện tiếng Việt '{kw}' phải xuất hiện trong base.html"


def test_double_submit_protection_flags():
    """Kiểm tra các template có gắn cờ kiểm soát ngăn double-submit dồn dập từ phía người dùng."""
    tpl_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates")

    # Kiểm tra transaction_form.html
    with open(os.path.join(tpl_dir, "transaction_form.html"), "r", encoding="utf-8") as f:
        tf_content = f.read()
    assert "isTxSubmitting" in tf_content, "transaction_form.html phải có biến isTxSubmitting để chặn gửi lặp"

    # Kiểm tra budgets.html
    with open(os.path.join(tpl_dir, "budgets.html"), "r", encoding="utf-8") as f:
        bg_content = f.read()
    assert "isBudgetSubmitting" in bg_content, "budgets.html phải có biến isBudgetSubmitting để chặn gửi lặp"


def test_feedback_ticket_flow(client, qa_user):
    """Kiểm thử luồng gửi phản hồi và gửi tin nhắn trả lời trong Feedback Hub."""
    headers = {"Authorization": f"Bearer {qa_user['token']}"}

    # 1. Tạo ticket phản hồi mới
    ticket_payload = {
        "subject": "Kiểm thử tự động QA Feedback Hub",
        "topic": "bug",
        "message": "Nội dung phản hồi tự động kiểm tra hệ thống thông suốt."
    }
    res_create = client.post("/api/feedback/", json=ticket_payload, headers=headers)
    assert res_create.status_code in (200, 201), f"Tạo ticket thất bại: {res_create.text}"
    ticket_data = res_create.json()
    ticket_id = ticket_data.get("id")
    assert ticket_id is not None

    # 2. Gửi phản hồi vào hội thoại của ticket
    reply_payload = {
        "message": "Người dùng bổ sung thông tin xác nhận lỗi đã rõ ràng."
    }
    res_reply = client.post(f"/api/feedback/{ticket_id}/reply", json=reply_payload, headers=headers)
    assert res_reply.status_code in (200, 201), f"Gửi tin nhắn phản hồi thất bại: {res_reply.text}"
    reply_data = res_reply.json()
    assert reply_data.get("message") == reply_payload["message"]
