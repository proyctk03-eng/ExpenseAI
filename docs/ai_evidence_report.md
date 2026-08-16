# PHỤ LỤC: TỔNG HỢP NHẬT KÝ VÀ MINH CHỨNG SỬ DỤNG AI
**Dự án: Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI**

> **Ghi chú:** Đây là bảng tổng hợp toàn bộ các prompt và minh chứng tương tác với AI xuyên suốt 3 giai đoạn của dự án, đáp ứng yêu cầu của các bài KT1, KT2 và KT3.

---

## PHẦN 1: GIAI ĐOẠN PHÂN TÍCH & THIẾT KẾ (BÀI KIỂM TRA 1)

| STT | Mục đích | Prompt (Lệnh yêu cầu) | Phản hồi AI tóm tắt | Nhận xét / Chỉnh sửa của tôi |
|:---:|---|---|---|---|
| 1 | **Tạo cấu trúc dự án** | *"Bạn là kỹ sư Python senior. Hãy tạo cấu trúc thư mục chuẩn Python + Docker + PEP8..."* | AI đề xuất cây thư mục rõ ràng, phân tách `src/`, `tests/`, `docs/`, kèm các file `.gitignore`, `requirements.txt`. | **Nhận xét:** Cấu trúc rất chuẩn MVC.<br>**Chỉnh sửa:** Tôi thêm thư mục `templates/` để dùng Jinja2 thay vì tách hẳn client riêng. |
| 2 | **Thiết lập Docker** | *"Tạo Dockerfile và docker-compose.yml cho FastAPI quản lý chi tiêu. Dùng python:3.10-slim..."* | AI viết file Dockerfile dùng multi-stage build, tạo non-root user và ánh xạ volume để hot-reload. | **Nhận xét:** Code Docker an toàn và tối ưu dung lượng.<br>**Chỉnh sửa:** Tôi bổ sung lệnh chạy `init_db.py` vào command của docker-compose. |
| 3 | **Thiết kế Use Case** | *"Xác định actor chính và use case chính cho ứng dụng quản lý chi tiêu. Vẽ sơ đồ Mermaid..."* | AI liệt kê 2 Actor (User, Admin) và 1 Actor phụ (AI), đồng thời sinh code Mermaid cho sơ đồ Use Case. | **Nhận xét:** Phân tích logic.<br>**Chỉnh sửa:** Tôi bỏ bớt phần "Quản lý ngân sách" để tập trung sâu vào "Tư vấn tài chính bằng AI". |
| 4 | **Thiết kế CSDL** | *"Thiết kế cơ sở dữ liệu. Bao gồm users, categories, transactions, ai_predictions. Vẽ ERD..."* | AI thiết kế chuẩn 3NF, thêm bảng `ai_predictions` để lưu lịch sử AI, có ràng buộc khóa ngoại đầy đủ. | **Nhận xét:** Rất chặt chẽ.<br>**Chỉnh sửa:** Đổi kiểu dữ liệu `amount` từ Float sang Numeric(10,2) để không bị sai số tiền tệ. |

---

## PHẦN 2: GIAI ĐOẠN LẬP TRÌNH CƠ BẢN (BÀI KIỂM TRA 2)

| STT | Chức năng | Prompt đã sử dụng | Code AI trả về (Tóm tắt) | Phần tôi đã chỉnh sửa / Kết quả |
|:---:|---|---|---|---|
| 5 | **Đăng nhập & JWT** | *"Viết chức năng đăng nhập, sử dụng JWT. Mã hóa bcrypt. Viết bằng FastAPI."* | AI viết các router `/register`, `/login`, hàm `create_access_token` và `get_password_hash`. | **Chỉnh sửa:** Chuyển `SECRET_KEY` từ hardcode sang đọc từ file `.env` để bảo mật. **Kết quả:** Chạy tốt, chặn được user không hợp lệ. |
| 6 | **CRUD Giao dịch** | *"Viết API CRUD cho transactions. Hỗ trợ lọc theo ngày, tự động tính số dư."* | AI dùng SQLAlchemy truy vấn, viết các phương thức GET, POST, PUT, DELETE cho `Transaction`. | **Chỉnh sửa:** Bổ sung `db.rollback()` vào khối `except` để tránh treo DB nếu lỗi xảy ra. |
| 7 | **Báo cáo thống kê** | *"Xây dựng API thống kê GET /reports/summary và by_category dùng func.sum và GROUP BY."* | AI dùng `func.sum()` của SQLAlchemy kết hợp `join(Category)` để tính tổng thu/chi. | **Chỉnh sửa:** Thêm `extract('month', ...)` để chỉ tính trong tháng hiện tại. **Kết quả:** Trả về JSON chuẩn cho Chart.js. |
| 8 | **Seed Data** | *"Viết script tạo dữ liệu mẫu: 2 users, 10 danh mục, 50 giao dịch trong 3 tháng."* | AI viết vòng lặp dùng thư viện `random` và `timedelta` để tạo 50 giao dịch. | **Chỉnh sửa:** Sửa logic để tỉ lệ Thu/Chi là 20/80 cho chân thực hơn. **Kết quả:** Load dashboard có sẵn số liệu đẹp. |

---

## PHẦN 3: GIAI ĐOẠN TÍCH HỢP AI & HOÀN THIỆN (BÀI KIỂM TRA 3)

| STT | Vấn đề / Yêu cầu | Prompt | Phản hồi AI | Nhận xét / Chỉnh sửa / Kết quả |
|:---:|---|---|---|---|
| 9 | **Gọi API OpenAI** | *"Viết module gọi OpenAI API để phân loại giao dịch. Đọc key từ biến môi trường, xử lý timeout."* | AI tạo class `AIClassifier` dùng thư viện `openai`, thiết lập `httpx.Client(timeout=15.0)`. | **Nhận xét:** Đã xử lý tốt timeout.<br>**Chỉnh sửa:** Thêm khối `try-except`, nếu lỗi trả về fallback `{"category": "Khác"}`. |
| 10 | **Tối ưu Prompt** | *"Thiết kế prompt phân loại. Yêu cầu chỉ trả về JSON có category và confidence."* | AI dùng cấu trúc System Prompt, bổ sung tham số `response_format={"type": "json_object"}`. | **Chỉnh sửa:** Viết rõ danh sách các Category cho AI trong system prompt để tránh AI tự bịa danh mục mới. |
| 11 | **Bảo vệ quyền riêng tư**| *"Tạo chức năng AI tư vấn tài chính từ dữ liệu 3 tháng. Đảm bảo không lộ thông tin nhạy cảm."* | AI hướng dẫn gom nhóm tổng số tiền theo danh mục rồi biến thành chuỗi JSON ngắn gửi lên AI. | **Nhận xét:** Giải pháp an toàn.<br>**Kết quả:** Lời khuyên trả về rất thực tế dựa trên đúng số tiền tổng hợp. |
| 12 | **Review Code** | *"Hãy review toàn bộ file `transactions.py` và tìm lỗi tiềm ẩn, bảo mật."* | AI phát hiện việc tạo Category mới và Transaction không nằm trong cùng 1 khối transaction (Atomicity). | **Chỉnh sửa:** Dùng `db.flush()` thay vì `db.commit()` liên tục, chỉ `commit()` một lần cuối cùng. |

---
**TỔNG KẾT:** AI đã đóng vai trò như một "Senior Mentor" giúp định hướng cấu trúc, giải quyết các bug phức tạp (như xử lý JSON của OpenAI) và tối ưu hóa câu truy vấn CSDL. Tuy nhiên, toàn bộ logic nghiệp vụ, bảo mật (chuyển API Key sang .env) và quản lý lỗi (rollback) đều được tôi trực tiếp kiểm duyệt và chỉnh sửa để hệ thống chạy ổn định và thực tế nhất.
