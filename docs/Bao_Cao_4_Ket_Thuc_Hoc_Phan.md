# BÁO CÁO SỐ 4: TỔNG KẾT BẢO VỆ ĐỒ ÁN (THI KẾT THÚC HỌC PHẦN)
**Kính gửi:** Hội đồng chấm thi / Thầy Cô giảng viên
**Dự án:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Thành viên:** Nguyễn Tuấn Đạt (Trưởng nhóm), Phàn Ngọc Anh (Phó nhóm) - Nhóm 02

*Kính thưa Hội đồng và Thầy/Cô, chúng em xin trình bày báo cáo kỹ thuật tổng kết cho toàn bộ vòng đời phát triển dự án của nhóm:*

---

### 1. Hoàn thiện chức năng hệ thống
Sau nhiều tuần phát triển, nhóm chúng em đã xây dựng thành công và hoàn thiện toàn vẹn hệ thống. Các chức năng từ Quản trị tài khoản, CRUD danh mục, CRUD giao dịch, Thống kê biểu đồ đến AI phân loại và AI tư vấn tài chính đều hoạt động ổn định và đáp ứng 100% mục tiêu ban đầu đề ra.

### 2. Chất lượng kiến trúc và mã nguồn
Hệ thống được nhóm thiết kế theo kiến trúc Controller-Service chuẩn mực:
- Phân rã module khoa học: `models`, `schemas`, `services`, `api`.
- Mã nguồn Python tuân thủ khắt khe chuẩn PEP8, có Type Hinting đầy đủ, giúp dự án sạch sẽ, dễ bảo trì và mở rộng trong tương lai.

### 3. Chất lượng cơ sở dữ liệu
- CSDL quan hệ với cấu trúc 4 bảng được chuẩn hóa, quản trị qua ORM `SQLAlchemy`. Khóa chính, khóa ngoại liên kết logic chặt chẽ.
- Chúng em cũng cung cấp sẵn script `init_db.py` và `seed_data.py` tự tạo mẫu dữ liệu thực tế giúp Thầy/Cô thuận tiện trong việc chấm điểm.

### 4. Chất lượng giao diện và trải nghiệm người dùng
- Giao diện Web được nhóm xây dựng bằng Bootstrap, có tính phản hồi (Responsive) cao.
- Có Dashboard tổng quan vẽ biểu đồ bằng Chart.js.
- Trang Lịch sử giao dịch hỗ trợ thanh Bộ lọc (Filter) đa tiêu chí, kết nối với backend qua Fetch API vô cùng mượt mà.

### 5. Chất lượng chức năng AI
- AI được ứng dụng giải quyết xuất sắc Core Value (Giá trị cốt lõi): Xóa bỏ sự lười biếng, tốn thời gian khi phân loại danh mục bằng tay của con người.
- Độ chính xác của AI được kiểm soát chặt chẽ bằng System Prompt và cấu trúc dữ liệu JSON cứng.

### 6. Bảo mật, quyền riêng tư và đạo đức AI
- **Bảo mật ứng dụng:** Mật khẩu băm Bcrypt, Token JWT. Khóa ngoại ngăn chặn tuyệt đối lỗi bảo mật leo thang đặc quyền (IDOR) giữa những người dùng khác nhau.
- **Đạo đức AI:** Chúng em đảm bảo thuật toán chỉ gửi các con số tổng gộp lên OpenAI, tránh triệt để tình trạng lộ lọt chi tiết giao dịch nhạy cảm của người sử dụng.

### 7. Hiệu năng và độ ổn định
- Nhờ đẩy việc xử lý toán học sang CSDL (dùng hàm Aggregate của SQL), Endpoint Thống kê tốn cực ít bộ nhớ của hệ thống.
- Các giao dịch có nhúng AI đều được đưa vào khối nguyên tử Database (`try...rollback`). Nếu API AI chậm/lỗi, giao dịch vẫn lưu thành công với cờ (flag) mặc định.

### 8. Triển khai và đóng gói
- Toàn bộ source code đã được nhóm gói gọn bằng Docker (`Dockerfile` Multi-stage).
- Tích hợp `docker-compose.yml`. Thầy cô chỉ cần gõ duy nhất một lệnh `docker-compose up --build` là toàn bộ Frontend, Backend, Database cùng khởi chạy tự động trơn tru.

### 9. Báo cáo kỹ thuật đầy đủ
- Hành trình phát triển dự án (SDLC) đã được chúng em hệ thống hóa thành các file Markdown chuyên nghiệp và lưu trữ trong mục `docs/`.

### 10. Thuyết trình và demo
- Codebase cực kỳ gọn gàng, sản phẩm hoạt động thực tế 100% không dùng số liệu ảo. Nhóm 02 chúng em hoàn toàn tự tin demo sản phẩm cũng như trình bày trước hội đồng bảo vệ ạ!

*Chúng em xin chân thành cảm ơn Thầy/Cô đã hướng dẫn và chỉ bảo nhóm trong suốt học phần vừa qua!*
