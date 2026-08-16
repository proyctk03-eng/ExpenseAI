# BÁO CÁO BÀI KIỂM TRA SỐ 3: TÍCH HỢP AI VÀ HOÀN THIỆN
**Kính gửi:** Giảng viên hướng dẫn môn học
**Dự án:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Thành viên:** Nguyễn Tuấn Đạt (Trưởng nhóm), Phàn Ngọc Anh (Phó nhóm) - Nhóm 02

*Kính thưa Thầy/Cô, nhóm chúng em xin trình bày cách thức chúng em đã đưa Trí tuệ Nhân tạo vào hệ thống:*

---

### 1. Tích hợp được chức năng AI vào hệ thống
- Khác với việc tạo một chatbot riêng biệt, chúng em ứng dụng mô hình **Invisible AI** (AI vô hình). AI phục vụ luồng tạo Giao dịch (Tự phân loại danh mục ngay khi người dùng điền mô tả). Điều này mang lại giá trị thực tiễn rất cao.

### 2. Kết nối API/model AI đúng cách
- Nhóm đã kết nối thành công mô hình **OpenAI GPT-3.5-Turbo**.
- Khóa API Key được nhóm đọc tuyệt đối bảo mật từ `os.getenv("OPENAI_API_KEY")` lấy từ file `.env` (Đã cấu hình chặn trong .gitignore để không bao giờ lộ lên mạng).

### 3. Thiết kế prompt có hệ thống
- Chúng em tách biệt hoàn toàn System Prompt (Định hình quy tắc: "Bạn là trợ lý tài chính...") và User Prompt (Nơi truyền dữ liệu động của từng giao dịch).
- Có ràng buộc định dạng gắt gao bằng `response_format={"type": "json_object"}` để code xử lý an toàn.

### 4. Tối ưu prompt qua thử nghiệm
- Chúng em đã trải qua 3 vòng thử nghiệm (từ Prompt thô sơ trả về text tự do -> Prompt JSON -> Prompt JSON kèm danh sách các Category hệ thống sẵn có để tránh AI bịa tên linh tinh). Kết quả nhận diện mô tả Tiếng Việt đạt độ chuẩn xác rất cao.

### 5. Sử dụng dữ liệu hệ thống trong chức năng AI
- Tính năng AI Advice (Tư vấn): Để bảo mật quyền riêng tư của khách hàng, Backend của nhóm tự động chạy script tổng hợp ra 1 biến JSON chứa thông tin khái quát: `{"Thu nhập": 20M, "Ăn uống": 8M, "Khác": 1M}`. Sau đó mới dùng chuỗi này gửi cho AI, tuyệt đối không gửi lịch sử mua hàng chi tiết của người dùng.

### 6. Hiển thị kết quả AI rõ ràng
- Khi tạo giao dịch, kết quả tự động phân loại lập tức nằm trong bảng hiển thị.
- Khung "Lời khuyên AI" trên màn hình Dashboard được thiết kế gọn gàng, mang tính hành động cao và rất dễ đọc.

### 7. Xử lý lỗi và giới hạn AI
- Nhận thức được AI gọi qua mạng có thể bị trễ, chúng em đã thiết lập thêm biến `timeout=15.0`.
- Luôn có khối `try..except` bọc API AI. Nếu bị rate limit hoặc mất mạng, Backend tự động kích hoạt luồng Fallback, gán giao dịch vào danh mục mặc định `Khác` để trải nghiệm người dùng không bị gián đoạn.

### 8. Kiểm thử chức năng quản lý và chức năng AI
- Trong file `tests/test_api.py`, chúng em đã sử dụng `TestClient` và `pytest` chạy một luồng Integration Test e2e thực tế, giả lập từ tạo tài khoản, lấy Token đến gọi AI phân loại và xác minh CSDL.

### 9. Review code và cải thiện chất lượng bằng AI
- Nhờ quá trình dùng AI để Review Code, nhóm đã phát hiện và xử lý được vấn đề liên quan đến "Tính nguyên tử" (Atomicity) của CSDL. Cụ thể, chúng em chuyển sang sử dụng `db.flush()` để lấy ID trung gian và chỉ `db.commit()` một lần duy nhất vào cuối luồng nhằm tránh sai sót.

### 10. Tích hợp chức năng AI với trải nghiệm người dùng
- Luồng sử dụng của dự án cực kỳ tự nhiên. Thay vì phải làm 2 bước tốn thời gian, người dùng chỉ cần gõ "Mua sách 200k" và bấm Lưu. AI làm phần còn lại một cách hoàn hảo.

*Nhóm 02 trân trọng cảm ơn Thầy/Cô!*
