"""Unit & Integration tests cho Module Quản lý Ngân sách (Budget Management)."""
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient

from src.database import SessionLocal
from src.main import app
from src.models import Category, User, Role, Budget
from src.utils.security import create_access_token, get_password_hash

client = TestClient(app)


@pytest.fixture
def user_token():
    """Tạo JWT token cho tài khoản người dùng bình thường."""
    db = SessionLocal()
    user = db.query(User).filter(User.username != "admin").first()
    if not user:
        user = User(
            username="budget_user_test",
            email="budget_user@example.com",
            hashed_password=get_password_hash("password123"),
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


def test_create_and_get_budget(user_token):
    """Kiểm thử tạo mới và lấy danh sách ngân sách."""
    headers = {"Authorization": f"Bearer {user_token}", "X-CSRF-Token": "test-token"}
    cookies = {"csrftoken": "test-token"}

    # 1. Tạo budget
    payload = {
        "month": "2026-11",
        "amount_limit": 10000000.0,
        "alert_threshold": 80,
    }
    res = client.post("/api/budgets/", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 201
    data = res.json()
    assert data["month"] == "2026-11"
    assert data["amount_limit"] == 10000000.0
    assert data["status"] in ["safe", "warning", "exceeded"]
    budget_id = data["id"]

    # 2. Lấy danh sách ngân sách tháng 2026-11
    res_get = client.get("/api/budgets/?month=2026-11", headers=headers, cookies=cookies)
    assert res_get.status_code == 200
    budgets = res_get.json()
    assert len(budgets) >= 1
    found = any(b["id"] == budget_id for b in budgets)
    assert found is True

    # 3. Lấy tổng quan ngân sách summary
    res_summary = client.get("/api/budgets/summary?month=2026-11", headers=headers, cookies=cookies)
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["month"] == "2026-11"
    assert summary["total_budget"] >= 10000000.0

    # 4. Xóa budget
    res_del = client.delete(f"/api/budgets/{budget_id}", headers=headers, cookies=cookies)
    assert res_del.status_code == 204


def test_create_budget_invalid_category(user_token):
    """Không thể tạo budget cho danh mục không tồn tại hoặc danh mục thu nhập."""
    headers = {"Authorization": f"Bearer {user_token}", "X-CSRF-Token": "test-token"}
    cookies = {"csrftoken": "test-token"}

    payload = {
        "month": "2026-11",
        "amount_limit": 5000000.0,
        "category_id": 999999,  # Không tồn tại
    }
    res = client.post("/api/budgets/", json=payload, headers=headers, cookies=cookies)
    assert res.status_code == 404


def test_budgets_web_page_render():
    """Kiểm thử route Web /budgets render trang HTML thành công."""
    res = client.get("/budgets")
    assert res.status_code == 200
    assert "Quản lý Ngân sách" in res.text
    assert "overallProgressBar" in res.text

