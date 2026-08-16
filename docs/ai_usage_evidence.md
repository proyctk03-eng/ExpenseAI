# MINH CHỨNG SỬ DỤNG AI TRONG DỰ ÁN EXPENSE AI

Tài liệu này tổng hợp các bằng chứng về việc ứng dụng Trí tuệ Nhân tạo (AI Code Assistant) trong toàn bộ Vòng đời phát triển phần mềm (SDLC) của dự án ExpenseAI, từ khâu phân tích thiết kế đến khi hoàn thiện mã nguồn và kiểm thử.

---

## 1. Giai đoạn Phân tích và Thiết kế Hệ thống
**Mục tiêu:** Sử dụng AI để hỗ trợ phân tích yêu cầu, thiết kế cơ sở dữ liệu và xây dựng các tài liệu kỹ thuật.

### Prompt của sinh viên:
> *"Tôi đang làm bài tập lớn môn Công nghệ phần mềm. Hệ thống Quản lý chi tiêu cá nhân (ExpenseAI). Yêu cầu: Backend FastAPI, Database PostgreSQL, Frontend HTML/CSS/JS. Hãy đóng vai một chuyên gia phân tích hệ thống, giúp tôi tạo ra các tài liệu chuẩn SDLC bao gồm: Yêu cầu chức năng, Phi chức năng, Thiết kế Database (ERD), và Kiến trúc hệ thống."*

### Phản hồi & Kết quả từ AI:
- AI đã phân tích và sinh ra cấu trúc 4 bảng CSDL cốt lõi: `Users`, `Categories`, `Transactions`, và `AIPredictions`.
- AI tự động sinh ra các tài liệu markdown chuyên nghiệp (`system_design_document.md`, `ai_integration_report.md`, v.v.).
- **Sự can thiệp của sinh viên:** Sinh viên đã kiểm tra lại kiến trúc, yêu cầu AI không sử dụng dữ liệu ảo trong các biểu đồ và bắt buộc tích hợp AI vào việc phân loại thay vì chỉ CRUD thông thường.

---

## 2. Giai đoạn Phát triển Giao diện (UI/UX)
**Mục tiêu:** Yêu cầu AI thiết kế lại giao diện dựa trên Mockup thô sơ thành một giao diện hiện đại.

### Prompt của sinh viên:
> *"Yêu cầu tái thiết kế giao diện ExpenseAI. Bạn là một chuyên gia UI/UX và frontend. Hãy thiết kế lại toàn bộ giao diện dựa trên mockup hiện tại. Phong cách: Minimalism + Glassmorphism (Ưu tiên Glassmorphism). Màu chủ đạo: Xanh dương đậm. Bố cục 2 cột (Sidebar bên trái, Nội dung bên phải)."*

### Phản hồi & Kết quả từ AI:
- AI đã viết lại file `base.html` và `style.css`, áp dụng các thuộc tính CSS như `backdrop-filter: blur()`, CSS Variables cho Light Theme.
- AI đã tự động tạo layout Sidebar Responsive (có nút hamburger trên mobile).
- **Sự can thiệp của sinh viên:** Khi giao diện đăng nhập bị lỗi hiển thị (bị dính footer và margin của sidebar), sinh viên đã gửi prompt yêu cầu AI sửa lỗi: *"giao diện đăng nhập bị lỗi..."*. AI đã fix bằng JavaScript logic để ẩn sidebar ở các route auth.

---

## 3. Giai đoạn Phát triển Chức năng (Backend & Logic)
**Mục tiêu:** Xây dựng logic xử lý thống kê, cài đặt và kết nối các chức năng bị thiếu.

### Prompt của sinh viên:
> *"Tôi đang phát triển ứng dụng ExpenseAI. Giao diện hiện tại đã có các mục menu: Dashboard, Giao dịch, Thống kê, Cài đặt, Hỗ trợ. Tuy nhiên, khi nhấp vào Thống kê, Cài đặt trang không chuyển đổi. Hãy kiểm tra và sửa lỗi điều hướng, đồng thời xây dựng trang Thống kê (có biểu đồ tròn, biểu đồ cột 6 tháng) và trang Cài đặt (cập nhật thông tin, đổi mật khẩu)."*

### Phản hồi & Kết quả từ AI:
- AI đã phân tích mã nguồn `main.py` và `web.py`, phát hiện thiếu API Routes.
- AI viết thêm endpoint `GET /api/reports/monthly_trend` bằng Python/SQLAlchemy để lấy dữ liệu 6 tháng.
- Xây dựng 3 trang HTML mới tích hợp `Chart.js` để vẽ biểu đồ và `Fetch API` để giao tiếp với backend.
- **Sự can thiệp của sinh viên:** Sinh viên đã duyệt bản kế hoạch triển khai (Implementation Plan) của AI trước khi cho phép AI can thiệp vào mã nguồn thật.

---

## 4. Giai đoạn Tích hợp AI (Nghiệp vụ Core)
**Mục tiêu:** Tích hợp OpenAI vào FastAPI để xử lý ngôn ngữ tự nhiên.

### Trích xuất Code do AI hỗ trợ tạo ra:
```python
# Trích xuất từ src/api/transactions.py
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Bạn là trợ lý AI. Hãy phân loại giao dịch sau vào 1 trong các category ID đã cho. Chỉ trả về số ID hợp lệ."},
        {"role": "user", "content": f"Giao dịch: {transaction_in.description}. Danh sách Category: {cat_mapping}"}
    ],
    temperature=0
)
```
- **Sự can thiệp của sinh viên:** Sinh viên yêu cầu AI phải xử lý lỗi (Exception) trong trường hợp OpenAI bị timeout, đảm bảo hệ thống không bị crash mà tự động gán vào danh mục "Khác".

---

## 5. Giai đoạn Kiểm thử & Triển khai
**Mục tiêu:** Tạo dữ liệu mẫu và viết Test Cases.

### Prompt của sinh viên:
> *"hãy thêm dữ liệu của sinh viên vào"* và *"tạo thêm testcase quan trọng"*

### Phản hồi & Kết quả từ AI:
- AI đã tạo script `seed_data.py` tự động insert 54 giao dịch chi tiêu thực tế của sinh viên (tiền trọ, ăn uống, trà sữa, đổ xăng) trong 30 ngày.
- AI sử dụng `pytest` và `TestClient` của FastAPI để viết tự động **35 Test Cases**, bao phủ toàn bộ API (từ Auth, CRUD đến phân quyền và Security).
- **Sự can thiệp của sinh viên:** Sinh viên kiểm thử lại bằng cách chạy lệnh `docker exec expense_app python -m pytest` và xác nhận 35/35 Test cases PASSED.

---

## TỔNG KẾT VAI TRÒ CỦA AI TRONG SDLC:
1. **Coding Assistant:** Thay vì gõ tay từng dòng HTML/CSS, sinh viên dùng AI như một công cụ sinh boilerplate code nhanh chóng, sau đó tự tinh chỉnh.
2. **Reviewer & Debugger:** Khi có lỗi UI hoặc lỗi logic, sinh viên cung cấp ngữ cảnh để AI phân tích logs và tìm ra nguyên nhân (VD: Lỗi thiếu file tĩnh trong Docker container).
3. **Tester:** Tận dụng AI để sinh ra các kịch bản kiểm thử (Test cases) bao phủ các trường hợp biên (nhập số âm, string quá dài) mà lập trình viên dễ bỏ sót.
4. **Quyền quyết định:** AI chỉ đưa ra giải pháp, sinh viên là người kiểm duyệt (Review) thông qua `implementation_plan` và chạy thực tế trên Docker để xác nhận độ chính xác.
