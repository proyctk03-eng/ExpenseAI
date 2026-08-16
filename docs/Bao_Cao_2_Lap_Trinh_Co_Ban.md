# BÁO CÁO BÀI KIỂM TRA SỐ 2: LẬP TRÌNH CƠ BẢN
**Kính gửi:** Giảng viên hướng dẫn môn học
**Dự án:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Thành viên:** Nguyễn Tuấn Đạt (Trưởng nhóm), Phàn Ngọc Anh (Phó nhóm) - Nhóm 02

*Kính thưa Thầy/Cô, nhóm chúng em xin phép trình bày báo cáo phần Lập trình cơ bản cho dự án như sau:*

---

### 1. Cấu trúc dự án hợp lý
Dự án được chúng em phân tách chặt chẽ theo chuẩn thiết kế MVC hiện đại:
- `src/api/`: Chứa các router điều hướng logic.
- `src/models/`: Định nghĩa CSDL (SQLAlchemy).
- `src/schemas/`: Ràng buộc dữ liệu vào/ra (Pydantic).
- `src/services/`: Nơi chứa mã nguồn gọi AI.
- `src/templates/`: Giao diện HTML hiển thị cho người dùng.
- Thư mục `docs/`, `tests/`, `scripts/`: Chứa tài liệu báo cáo, file test và data mẫu.

### 2. Xây dựng chức năng đăng nhập và phân quyền
- Tại `src/api/auth.py`, chúng em sử dụng `OAuth2PasswordBearer` và băm mật khẩu với thư viện `passlib`.
- Để bảo mật, các Endpoint được bảo vệ bằng Dependency `Depends(get_current_user)`, ngăn chặn truy cập trái phép.

### 3. Hoàn thiện CRUD nghiệp vụ chính
- Chức năng thêm, sửa, đọc, xóa giao dịch được lập trình đầy đủ tại `src/api/transactions.py`.
- Đặc biệt, khi thêm giao dịch, hệ thống tự động liên kết với Danh mục tương ứng. Mọi thao tác đều hoạt động chính xác và an toàn.

### 4. Xây dựng chức năng tìm kiếm và lọc
- Dựa theo yêu cầu, chúng em đã nâng cấp Endpoint `GET /transactions/` để hỗ trợ đa tham số: `search` (từ khóa mô tả), `start_date` (từ ngày), `end_date` (đến ngày) và `category_id`.
- Chức năng lọc đã được tích hợp mượt mà vào thanh công cụ (Filter Bar) trên giao diện web `transactions.html`.

### 5. Xây dựng thống kê/báo cáo cơ bản
- Tại `src/api/reports.py`, thay vì dùng vòng lặp Python gây tốn RAM, chúng em đã áp dụng phương pháp tối ưu là sử dụng `func.sum()` của SQLAlchemy để Database tự cộng dồn. 
- Dữ liệu trả về dạng JSON được đẩy trực tiếp lên biểu đồ Chart.js ở Dashboard.

### 6. Thiết kế giao diện rõ ràng, dễ sử dụng
- Giao diện được thiết kế hoàn thiện bằng Bootstrap 5.
- Form nhập liệu mở dưới dạng Modal Popup, nút xóa có cảnh báo Confirm. Hệ thống Responsive hiển thị rất tốt trên điện thoại di động.

### 7. Kết nối và thao tác CSDL ổn định
- Database kết nối cực kỳ ổn định.
- Chúng em có viết sẵn file `scripts/seed_data.py` tự động sinh tài khoản và 50 giao dịch đẹp mắt phục vụ việc Thầy/Cô chạy demo lập tức.

### 8. Xử lý lỗi cơ bản
- Mọi thao tác lưu, xóa DB đều được nhóm đặt trong khối `try...except`. Nếu có sự cố, hệ thống sẽ gọi `db.rollback()` để bảo toàn dữ liệu, tuyệt đối không bị sập (crash) server.
- Nếu người dùng nhập sai dữ liệu, Pydantic Schema sẽ bắt lỗi 422 Unprocessable Entity.

### 9. Minh chứng sử dụng AI khi lập trình
- Chúng em đã sử dụng AI như một người hướng dẫn để tìm hiểu cách viết Middleware JWT và cấu hình SQLAlchemy an toàn. Code do AI cung cấp đều được nhóm em tinh chỉnh lại (đưa key vào .env) và lưu lại minh chứng đầy đủ tại thư mục `docs/`.

### 10. Quản lý mã nguồn và tài liệu chạy thử
- Nhóm đã tạo file `.gitignore` để làm sạch mã nguồn.
- File `.env.example` tạo mẫu bảo mật API Key thay vì hardcode.
- File `Dockerfile` và `docker-compose.yml` có sẵn, giúp Thầy/Cô gõ đúng 1 lệnh là có thể chạy web lên. Mọi hướng dẫn chi tiết đều nằm trong `README.md`.

*Nhóm 02 trân trọng cảm ơn Thầy/Cô!*
