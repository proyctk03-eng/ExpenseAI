"""Unit & Integration tests cho Hệ thống Xử lý Phản hồi (Feedback Ticket System)."""
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, SessionLocal
from src.models import User, Role, FeedbackTicket, TicketReply
from src.utils.security import get_password_hash, create_access_token

client = TestClient(app)

@pytest.fixture
def admin_token():
    """Tạo JWT token cho tài khoản admin."""
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin_test",
            email="admintest@example.com",
            hashed_password=get_password_hash("admin123")
        )
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            admin.roles.append(admin_role)
        db.add(admin)
        db.commit()
        db.refresh(admin)
    token = create_access_token({"sub": str(admin.id)}, expires_delta=timedelta(minutes=30))
    db.close()
    return token

@pytest.fixture
def user_token():
    """Tạo JWT token cho tài khoản người dùng bình thường."""
    db = SessionLocal()
    user = db.query(User).filter(User.username != "admin").first()
    if not user:
        user = User(
            username="normal_user_test",
            email="usertest@example.com",
            hashed_password=get_password_hash("user123")
        )
        user_role = db.query(Role).filter(Role.name == "user").first()
        if user_role:
            user.roles.append(user_role)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(minutes=30))
    db.close()
    return token

def test_user_can_create_feedback(user_token):
    """Người dùng bình thường có thể tạo ticket phản hồi."""
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {
        "subject": "Kiểm thử tạo phản hồi từ Pytest",
        "message": "Nội dung phản hồi kiểm thử tự động hệ thống.",
        "topic": "bug"
    }
    resp = client.post("/api/feedback/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["subject"] == payload["subject"]
    assert data["topic"] == "bug"
    assert data["status"] == "pending"
    assert "id" in data

def test_admin_can_get_stats(admin_token):
    """Admin có thể lấy thống kê tổng quan các tickets."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/feedback/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "pending" in data
    assert "in_progress" in data
    assert "resolved" in data
    assert "rejected" in data
    assert data["total"] >= 1

def test_normal_user_cannot_access_admin_stats(user_token):
    """Người dùng thường không được phép truy cập endpoint thống kê admin."""
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = client.get("/api/feedback/stats", headers=headers)
    assert resp.status_code == 403

def test_admin_can_filter_tickets(admin_token):
    """Admin có thể lấy danh sách và lọc tickets theo trạng thái, chủ đề."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/feedback/?status=pending", headers=headers)
    assert resp.status_code == 200
    tickets = resp.json()
    assert isinstance(tickets, list)
    for t in tickets:
        assert t["status"] == "pending"

def test_admin_can_update_status(admin_token):
    """Admin có thể chuyển trạng thái ticket."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Lấy ticket đầu tiên
    res = client.get("/api/feedback/", headers=headers)
    assert res.status_code == 200
    tickets = res.json()
    assert len(tickets) > 0
    t_id = tickets[0]["id"]

    # Cập nhật thành in_progress
    resp = client.put(f"/api/feedback/{t_id}/status", json={"status": "in_progress"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"

def test_reply_flow(admin_token, user_token):
    """Luồng trao đổi tin nhắn phản hồi giữa Admin và User."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_user = {"Authorization": f"Bearer {user_token}"}

    # User tạo ticket mới
    create_resp = client.post("/api/feedback/", json={
        "subject": "Hỏi về tính năng mới",
        "message": "Khi nào tính năng này sẵn sàng?",
        "topic": "feature"
    }, headers=headers_user)
    assert create_resp.status_code == 201
    ticket_id = create_resp.json()["id"]

    # Admin gửi câu trả lời
    reply_resp = client.post(f"/api/feedback/{ticket_id}/reply", json={
        "message": "Tính năng sẽ có trong tuần tới bạn nhé."
    }, headers=headers_admin)
    assert reply_resp.status_code == 201
    assert reply_resp.json()["is_admin"] is True

    # User xem chi tiết ticket
    detail_resp = client.get(f"/api/feedback/{ticket_id}", headers=headers_user)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["replies"]) >= 1
    assert detail["replies"][-1]["message"] == "Tính năng sẽ có trong tuần tới bạn nhé."

def test_support_page_renders_html():
    """Trang /support trả về mã HTTP 200 và chứa các thành phần giao diện mới."""
    resp = client.get("/support")
    assert resp.status_code == 200
    assert "Xử lý phản hồi" in resp.text
    assert "communicationModal" in resp.text
    assert "filterCard" in resp.text
