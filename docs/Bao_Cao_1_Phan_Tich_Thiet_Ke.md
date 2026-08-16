# BÁO CÁO BÀI KIỂM TRA SỐ 1: PHÂN TÍCH VÀ THIẾT KẾ
**Kính gửi:** Giảng viên hướng dẫn môn học
**Dự án:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Thành viên:** Nguyễn Tuấn Đạt (Trưởng nhóm), Phàn Ngọc Anh (Phó nhóm) - Nhóm 02

*Kính thưa Thầy/Cô, nhóm chúng em xin phép trình bày báo cáo tiến độ Bài kiểm tra số 1 như sau:*

---

### 1. Phân tích đúng bài toán quản lý
- **Bối cảnh:** Qua quá trình tìm hiểu thực tế, chúng em nhận thấy việc quản lý chi tiêu cá nhân bằng sổ sách hoặc ứng dụng truyền thống thường khiến người dùng mệt mỏi vì phải tự gõ và phân loại từng khoản chi.
- **Người dùng:** Cá nhân, nhân viên văn phòng, sinh viên và hộ gia đình.
- **Dữ liệu & Quy trình:** Nhập khoản chi -> Ghi nhận thời gian, số tiền -> Phân loại -> Tính số dư -> Lập báo cáo.
- **Vấn đề giải quyết:** Ứng dụng AI giúp tự động phân loại ngay khi người dùng gõ mô tả ngắn gọn (VD: "Ăn bún chả 30k" -> tự phân vào "Ăn uống"), giúp tiết kiệm thời gian đáng kể.

### 2. Xác định đầy đủ yêu cầu chức năng
Chúng em đã thiết kế các chức năng cốt lõi cho ứng dụng gồm:
- **Quản lý Auth:** Đăng ký, đăng nhập bảo mật bằng JWT.
- **Quản lý Giao dịch:** Cho phép tạo, sửa, xóa (CRUD), tìm kiếm từ khóa, lọc theo khoảng thời gian và danh mục.
- **Thống kê:** Tính tổng thu/chi, số dư hiện tại và vẽ biểu đồ chi tiêu.
- **AI Phân loại:** Tự động dự đoán và gán nhãn danh mục cho giao dịch mới.
- **AI Tư vấn:** Đưa ra báo cáo tài chính và lời khuyên dựa trên dữ liệu 3 tháng gần nhất.

### 3. Xác định yêu cầu phi chức năng
- **Bảo mật:** Mật khẩu được mã hóa an toàn bằng `bcrypt`, API được bảo vệ qua `JWT`, khóa bí mật (Secret Key) được chúng em bảo mật hoàn toàn ở file `.env`.
- **Hiệu năng:** Xử lý AI không đồng bộ; sử dụng hàm tính toán nội bộ của Database để giảm thiểu chi phí bộ nhớ cho server.
- **Trải nghiệm:** Giao diện Web thiết kế dưới dạng SPA lai, mọi thao tác lọc đều mượt mà.

### 4. Thiết kế actor và use case
- **Actor:** `User` (Thêm giao dịch, xem báo cáo, xin tư vấn), `System AI` (Gán nhãn tự động, Phân tích).
- **Use Case chính:** User Đăng nhập -> Truy cập Dashboard (Nhận lời khuyên AI) -> Mở Form giao dịch (Hệ thống AI phân loại) -> Lưu vào Cơ sở dữ liệu.

### 5. Thiết kế cơ sở dữ liệu
Hệ thống được nhóm em thiết kế 4 bảng chính đạt chuẩn 3NF:
- `users`: id, username, password_hash, role
- `categories`: id, name, type, user_id
- `transactions`: id, amount, description, date, category_id (Khóa ngoại), user_id (Khóa ngoại)
- `ai_predictions`: id, tx_id (Khóa ngoại), predicted_category, confidence.

### 6. Thiết kế kiến trúc hệ thống
- **Frontend:** Jinja2 Template + Bootstrap 5.
- **Backend:** FastAPI (Python) - kiến trúc RESTful.
- **Database:** PostgreSQL/SQLite kết hợp với SQLAlchemy ORM.
- **AI Service:** Tích hợp OpenAI API (GPT-3.5) trực tiếp vào luồng logic Backend.

### 7. Xác định vị trí ứng dụng AI
Chúng em quyết định áp dụng AI ở 2 vị trí thiết thực nhất:
- **Vị trí 1 (Data Entry):** Tự động phân loại danh mục ngay lúc tạo giao dịch. 
- **Vị trí 2 (Advisory):** Tại trang chủ (Dashboard), AI sẽ đọc tóm tắt dữ liệu tháng để sinh ra lời khuyên cá nhân hóa.

### 8. Thiết kế prompt và luồng gọi AI sơ bộ
- **System Prompt:** Nhóm em đã cấu hình nghiêm ngặt: "Bạn là AI phân loại chi tiêu. Chỉ trả về JSON dạng `{"category": "Tên", "confidence": 0.9}`."
- **User Prompt mẫu:** "Mua ly cafe 35k".

### 9. Minh chứng sử dụng AI trong phân tích thiết kế
- Mọi lịch sử tìm kiếm, prompt thiết kế cấu trúc và chỉnh sửa CSDL cùng AI đều được chúng em đóng gói và lưu tại file `docs/ai_evidence_report.md` ạ.

### 10. Tài liệu phân tích thiết kế
- Báo cáo này cùng các tài liệu thiết kế khác đã được chúng em lập cấu trúc thư mục rõ ràng, làm tiền đề chuẩn bị bước sang Giai đoạn Lập trình (Bài kiểm tra 2).

*Nhóm 02 trân trọng cảm ơn Thầy/Cô đã theo dõi!*
