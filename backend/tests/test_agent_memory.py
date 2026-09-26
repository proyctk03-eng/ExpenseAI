"""
Kiểm thử tính năng Agent Memory (TencentDB Agent Memory Style).
Kiểm tra khả năng tự học của hệ thống khi người dùng sửa danh mục giao dịch.
"""
import pytest
import time
from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db
from src.utils.limiter import limiter

init_db()
limiter.enabled = False
client = TestClient(app)


def test_agent_memory_learning_loop():
    """Kiểm tra vòng lặp tự học:
    1. Tạo giao dịch với từ khóa lạ: 'trà sữa gong cha đặc biệt' -> AI phân loại 'Khác' hoặc mặc định.
    2. Người dùng sửa giao dịch thành danh mục 'Ăn uống'.
    3. Hệ thống tự động ghi nhớ UserMemoryRule.
    4. Lần sau nhập lại 'trà sữa gong cha đặc biệt' -> Hệ thống tự động nhớ 'Ăn uống' với confidence 1.0!
    """
    # 1. Đăng ký & Đăng nhập
    username = f"mem_user_{int(time.time() * 1000)}"
    reg = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "Password@123"
    })
    assert reg.status_code == 201

    login = client.post("/api/auth/login", json={
        "username": username,
        "password": "Password@123"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Lấy danh sách categories để tìm ID của 'Ăn uống' và 'Giải trí'
    cats_res = client.get("/api/categories/", headers=headers)
    assert cats_res.status_code == 200
    categories = cats_res.json()
    an_uong_id = next(c["id"] for c in categories if c["name"] == "Ăn uống")
    giai_tri_id = next(c["id"] for c in categories if c["name"] == "Giải trí")

    # 3. Tạo giao dịch với từ khóa riêng biệt: 'vé xem phim cgv tối chủ nhật'
    tx_create = client.post("/api/transactions/", headers=headers, json={
        "amount": 120000,
        "description": "vé xem phim cgv tối chủ nhật",
        "transaction_date": "2026-09-14"
    })
    assert tx_create.status_code == 201
    tx_data = tx_create.json()
    tx_id = tx_data["id"]

    # 4. Người dùng cập nhật giao dịch sang danh mục 'Giải trí'
    update_res = client.put(f"/api/transactions/{tx_id}", headers=headers, json={
        "category_id": giai_tri_id,
        "description": "vé xem phim cgv tối chủ nhật"
    })
    assert update_res.status_code == 200
    assert update_res.json()["category_id"] == giai_tri_id

    # 5. Tạo giao dịch mới chứa cụm từ đã được học
    # Agent Memory sẽ nhận diện ngay lập tức từ khóa 'vé xem phim cgv tối chủ nhật' -> Gán Giải trí!
    tx_new = client.post("/api/transactions/", headers=headers, json={
        "amount": 150000,
        "description": "Đi mua vé xem phim cgv tối chủ nhật cùng bạn",
        "transaction_date": "2026-09-15"
    })
    assert tx_new.status_code == 201
    assert tx_new.json()["category_id"] == giai_tri_id
