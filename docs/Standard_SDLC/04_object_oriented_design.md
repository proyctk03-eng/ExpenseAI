# THIẾT KẾ HƯỚNG ĐỐI TƯỢNG VÀ KIẾN TRÚC (OOD)
**Tên ứng dụng:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Nhóm:** 02 (Trưởng nhóm: Nguyễn Tuấn Đạt, Phó nhóm: Phàn Ngọc Anh)
**Giai đoạn:** Tuần 4-5 (Bài KT 1)

---

## 1. MÔ HÌNH KIẾN TRÚC TỔNG QUAN
Hệ thống tuân thủ kiến trúc **Client-Server** kết hợp thiết kế **Micro-layer** cho Backend:
- **Presentation Layer (Frontend):** Jinja2 Templates + Bootstrap 5. Gọi API thông qua JS Fetch.
- **Controller/Router Layer (`src/api/`):** Nơi tiếp nhận Request HTTP, kiểm tra Token JWT. Gồm: `auth.py`, `transactions.py`, `reports.py`.
- **Service/Logic Layer (`src/services/`):** Xử lý logic nặng, đặc biệt là tương tác với OpenAI API (`ai_service.py`).
- **Data Access Layer (`src/models/`):** SQLAlchemy ORM ánh xạ các đối tượng Python xuống Database quan hệ.
- **Schema Layer (`src/schemas/`):** Pydantic models đảm nhận validate dữ liệu (Tránh SQL Injection & dữ liệu rác).

## 2. THIẾT KẾ CÁC LỚP ĐỐI TƯỢNG CHÍNH (DOMAIN CLASSES)

### Lớp User
- **Thuộc tính:** `id` (int), `username` (string), `password_hash` (string), `role` (string)
- **Phương thức:** `verify_password()`, `get_transactions()`

### Lớp Category
- **Thuộc tính:** `id` (int), `name` (string), `type` (Enum: IN/OUT), `user_id` (int)

### Lớp Transaction
- **Thuộc tính:** `id` (int), `amount` (float), `description` (string), `date` (datetime), `category_id` (int), `user_id` (int)
- **Phương thức:** Lớp này đại diện cho Entity vật lý, việc xử lý CRUD được tách riêng qua Repository Pattern hoặc trực tiếp tại Router do sử dụng FastAPI.

### Lớp AIPrediction
- **Thuộc tính:** `id` (int), `tx_id` (int), `predicted_category` (string), `confidence` (float)

## 3. LUỒNG DỮ LIỆU CHÍNH (SEQUENCE FLOW)
**Ví dụ: Luồng thêm giao dịch (Tự động phân loại bằng AI)**
1. `User` nhập chuỗi "Đổ xăng 50k" trên giao diện Web.
2. `Client` gọi `POST /transactions` gửi lên `{"description": "Đổ xăng 50k", "amount": 50000}`.
3. `API Router` kiểm tra Token. Token hợp lệ.
4. `API Router` gọi hàm `ai_service.predict_category(description)`.
5. `AIService` gọi API OpenAI GPT-3.5 với prompt JSON giới hạn.
6. `OpenAI` trả về `{"category": "Đi lại", "confidence": 0.95}`.
7. `API Router` tìm `category_id` khớp với "Đi lại" trong Database.
8. `API Router` tạo mới `Transaction` và gán `category_id` vừa tìm.
9. Dùng `db.commit()` để lưu đồng thời `Transaction` và `AIPrediction` (Đảm bảo tính nguyên tử - Atomicity).
10. Trả về thành công 200 OK. Frontend cập nhật bảng.
