# KẾ HOẠCH THỰC HIỆN DỰ ÁN
**Tên ứng dụng:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Nhóm:** 02 (Trưởng nhóm: Nguyễn Tuấn Đạt, Phó nhóm: Phàn Ngọc Anh)
**Thời gian thực hiện:** 9 Tuần

---

## 1. Mục tiêu dự án (OBJ)
- **OBJ-001:** Xây dựng hệ thống quản lý chi tiêu (CRUD giao dịch, danh mục).
- **OBJ-002:** Tích hợp AI để tự động phân loại giao dịch (Data Entry) và tư vấn tài chính (Advisory).
- **OBJ-003:** Đảm bảo bảo mật với hệ thống Auth JWT, mã hóa bcrypt.

## 2. Phạm vi (Scope)
- **Trong phạm vi:** Quản trị tài khoản, quản lý chi tiêu, bộ lọc giao dịch, Dashboard biểu đồ, AI nhận diện phân loại giao dịch tự động.
- **Ngoài phạm vi:** Kết nối trực tiếp tài khoản ngân hàng thực tế, thanh toán online.

## 3. Vai trò các bên (STK)
- **STK-001 - Người dùng:** Nhập giao dịch, xem báo cáo thống kê.
- **STK-002 - Quản trị viên (Admin):** Cấu hình hệ thống (nếu có).
- **STK-003 - Giảng viên:** Đánh giá tiến độ và kết quả dự án.

## 4. Kế hoạch chi tiết theo tuần
| Tuần | Giai đoạn SDLC | Công việc (Deliverables) | Thành viên thực hiện | Ghi chú / Milestone |
|:---:|:---|:---|:---|:---|
| **Tuần 1-3** | Khởi tạo & Lấy yêu cầu | - Khảo sát bài toán, xác định yêu cầu.<br>- Viết Project Plan và Requirements QA. | Đạt, Ngọc Anh | Hoàn thành bộ tài liệu Tuần 1-3. |
| **Tuần 4** | Phân tích | - Phân tích Đặc tả yêu cầu phần mềm (SRS). | Nguyễn Tuấn Đạt | Chốt Use Case, Yêu cầu phi chức năng. |
| **Tuần 5** | Thiết kế (Bài KT 1) | - Thiết kế hướng đối tượng (OOD).<br>- Thiết kế Cơ sở dữ liệu (Database Design). | Phàn Ngọc Anh | Hoàn thành Bài KT 1. Bàn giao ERD. |
| **Tuần 6** | Lập trình cốt lõi | - Setup Docker, cấu trúc `src/`.<br>- Code Auth JWT, API CRUD chi tiêu. | Nguyễn Tuấn Đạt | Chạy test API bằng Postman. |
| **Tuần 7** | Lập trình Frontend (Bài KT 2) | - Xây dựng giao diện Bootstrap, Filter.<br>- Hoàn thiện tài liệu User Guide. | Phàn Ngọc Anh | Hoàn thành Bài KT 2. App có giao diện. |
| **Tuần 8** | Tích hợp AI & Kiểm thử (Bài KT 3) | - Tích hợp OpenAI GPT-3.5 API.<br>- Viết Test case (Functional Testing). | Cả nhóm | Hoàn thành Bài KT 3. AI chạy ổn định. |
| **Tuần 9** | Báo cáo & Bàn giao | - Đóng gói dự án (Docker compose).<br>- Hoàn thiện Báo cáo Cuối kỳ. | Cả nhóm | Thi kết thúc học phần. |

## 5. Rủi ro & Biện pháp (RISK)
- **RISK-001:** Mất mạng/API AI phản hồi chậm. -> *Biện pháp:* Dùng Timeout và cơ chế Fallback gán danh mục mặc định "Khác".
- **RISK-002:** Lộ khóa API Key OpenAI. -> *Biện pháp:* Thiết lập file `.env` và đưa vào `.gitignore`.

*Tài liệu này được sinh tự động từ mã nguồn thực tế của dự án.*
