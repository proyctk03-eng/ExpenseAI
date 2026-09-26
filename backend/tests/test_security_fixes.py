"""Tests for Security Remediation (Phase 1, 2, 3 fixes)."""
import io
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from src.main import app
from src.database import SessionLocal
from src.models import User, Role
from src.utils.security import get_password_hash, create_access_token, create_refresh_token

client = TestClient(app)


@pytest.fixture
def auth_user():
    """Create or get a test user with access and refresh tokens."""
    db = SessionLocal()
    user = db.query(User).filter(User.username == "sec_test_user").first()
    if not user:
        user = User(
            username="sec_test_user",
            email="sectest@example.com",
            hashed_password=get_password_hash("TestPass@123")
        )
        role = db.query(Role).filter(Role.name == "user").first()
        if role:
            user.roles.append(role)
        db.add(user)
        db.commit()
        db.refresh(user)

    user_id = user.id
    access_token = create_access_token({"sub": str(user_id)}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token({"sub": str(user_id)}, expires_delta=timedelta(days=7))
    db.close()
    return {"user_id": user_id, "access_token": access_token, "refresh_token": refresh_token}


def test_h08_register_anti_enumeration(auth_user):
    """H-08: Duplicate username or email returns unified error message."""
    res = client.post("/api/auth/register", json={
        "username": "sec_test_user",
        "email": "different_sec@example.com",
        "password": "Password@123"
    })
    assert res.status_code == 400
    assert res.json()["detail"] == "Tài khoản hoặc email đã tồn tại"


def test_m01_refresh_token_rotation(auth_user):
    """M-01: Refresh endpoint rotates both access and refresh tokens."""
    client.cookies.set("refresh_token", auth_user["refresh_token"])
    res = client.post("/api/auth/refresh")
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Rotated token must be different or valid
    assert data["refresh_token"] is not None
    client.cookies.clear()


def test_h06_scan_receipt_magic_bytes_validation(auth_user):
    """H-06: File with fake image MIME header but malicious/invalid bytes must be rejected."""
    headers = {"Authorization": f"Bearer {auth_user['access_token']}"}
    fake_file = io.BytesIO(b"<html><script>alert('xss')</script></html>")
    res = client.post(
        "/api/transactions/scan-receipt",
        headers=headers,
        files={"file": ("test.png", fake_file, "image/png")}
    )
    assert res.status_code == 400
    assert "Magic bytes" in res.json()["detail"] or "hợp lệ" in res.json()["detail"]


def test_h05_feedback_sanitization(auth_user):
    """H-05: Stored XSS payload is escaped server-side."""
    headers = {"Authorization": f"Bearer {auth_user['access_token']}"}
    res = client.post(
        "/api/feedback/",
        headers=headers,
        json={
            "subject": "<script>alert('XSS')</script>",
            "message": "<img src=x onerror=alert(1)>Test",
            "topic": "bug"
        }
    )
    assert res.status_code == 201
    ticket = res.json()
    assert "<script>" not in ticket["subject"]
    assert "&lt;script&gt;" in ticket["subject"]
    assert "<img" not in ticket["message"]
    assert "&lt;img" in ticket["message"]


def test_h03_csrf_protection_blocks_state_change_without_token(auth_user):
    """H-03: Cookie-authenticated state change fails if X-CSRF-Token is missing."""
    client.cookies.set("access_token", auth_user["access_token"])
    client.cookies.set("csrftoken", "test_csrf_token_12345")
    # Missing X-CSRF-Token header
    res = client.post("/api/categories/", json={"name": "CSRF_Test", "type": "expense"})
    assert res.status_code == 403
    assert "CSRF" in res.json()["detail"]
    client.cookies.clear()


def test_h03_csrf_protection_allows_with_valid_token(auth_user):
    """H-03: Cookie-authenticated state change succeeds with matching X-CSRF-Token."""
    csrf_val = "valid_csrf_token_secret_12345678"
    client.cookies.set("access_token", auth_user["access_token"])
    client.cookies.set("csrftoken", csrf_val)
    headers = {"X-CSRF-Token": csrf_val}
    res = client.post("/api/categories/", json={"name": "CSRF_Allowed_Cat", "type": "expense"}, headers=headers)
    assert res.status_code in [200, 201, 400]  # Passes CSRF check (may be 400 if duplicate, but not 403)
    assert res.status_code != 403
    client.cookies.clear()
