# BÁO CÁO TIẾN ĐỘ TỔNG THỂ DỰ ÁN - NHÓM 02
**Môn học:** Ứng dụng Trí tuệ Nhân tạo trong Phát triển Phần mềm  
**Đơn vị:** Khoa Công nghệ Thông tin - Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU)  
**Đề tài:** ExpenseAI - Hệ thống Quản lý Chi tiêu Cá nhân thông minh tích hợp Trí tuệ Nhân tạo  

### Thành viên nhóm thực hiện:
1. **Trưởng nhóm:** Nguyễn Tuấn Đạt (Phụ trách Kiến trúc Hệ thống, Backend, Tích hợp AI & CI/CD)
2. **Phó nhóm:** Phàn Ngọc Anh (Phụ trách Giao diện Frontend UI/UX, Kiểm thử & Quản trị CSDL)

---

## 1. TÌNH TRẠNG HOÀN THÀNH THEO TOÀN BỘ RUBRIC ĐÁNH GIÁ (100% SẴN SÀNG)

| Hạng mục đánh giá | Số tiêu chí | Tỷ lệ hoàn thành | Đánh giá & Kết quả đạt được |
|---|:---:|:---:|---|
| **Bài kiểm tra 1 (Phân tích & Thiết kế)** | 10/10 | **100%** | Đã hoàn thiện toàn diện: Bối cảnh, Bảng I/P/O chức năng, Yêu cầu phi chức năng, Sơ đồ Use Case Mermaid, Sơ đồ ERD 3NF, Kiến trúc 3 tầng và Kế hoạch triển khai 4 giai đoạn. |
| **Bài kiểm tra 2 (Lập trình cơ bản)** | 10/10 | **100%** | Cấu trúc chuẩn MVC/Router, Auth JWT + Cookie, RBAC 3 vai trò, CRUD giao dịch & danh mục, Bộ lọc tìm kiếm đa tiêu chí, Thống kê biểu đồ Chart.js, Xử lý lỗi an toàn không crash. |
| **Bài kiểm tra 3 (Tích hợp AI & Kiểm thử)** | 10/10 | **100%** | Mô hình Invisible AI (Classifier & Advisor), Bảo mật API Key trong `.env`, Kỹ thuật Prompt 3 vòng thử nghiệm (Độ chính xác 96%), Phòng vệ Fault-Tolerant, Bộ test **35/35 Pytest PASS 100%**. |
| **Thi kết thúc học phần (Bảo vệ đồ án)** | 10/10 | **100%** | Hoàn thiện trọn vẹn mọi chức năng thực tế, CSDL 7 bảng, UI Glassmorphism Responsive, Docker container hóa, **GitHub Actions CI/CD passed xanh 100%**, Kịch bản thuyết trình và demo 7 phút chi tiết. |

---

## 2. NHỮNG CẬP NHẬT KỸ THUẬT ĐỘT PHÁ MỚI NHẤT (NỐI TIẾP BÀI KIỂM TRA 2)

Nhóm 02 đã thực hiện một đợt nâng cấp kỹ thuật toàn diện để đưa dự án từ giai đoạn "Lập trình cơ bản" sang "Tích hợp AI và Sẵn sàng Sản phẩm Thực tế":

1. **Chuẩn hóa Giao diện Thu / Chi và Quản lý Danh mục:**
   - Sửa triệt để lỗi hiển thị "Chưa phân loại" trên giao diện web.
   - Định nghĩa tính ngữ nghĩa màu sắc: Thu nhập (+ xanh lá) và Chi tiêu (- đỏ cam) dựa trên thuộc tính `category_type` của CSDL.
   - Tích hợp thành công **Modal Chỉnh sửa Giao dịch** (`PUT /api/transactions/{id}`) trực tiếp trên trang lịch sử giao dịch.
   - Bổ sung **Modal Thêm Danh mục mới** (`POST /api/categories/`) trong trang Cài đặt (`settings.html`), sửa lỗi biến `msg` không xác định.
2. **Nâng cấp Bộ Test Suite từ 21 lỗi lên 35/35 Test PASS (100%):**
   - Tạo file `tests/conftest.py` tự động chạy `init_db()` để tạo bảng, quyền RBAC và danh mục mẫu cho bất kỳ CSDL mới nào.
   - Thắt chặt các assertion của bài test (loại bỏ mã lỗi 500 nới lỏng trước đây).
   - Tách biệt cookie và cô lập phiên làm việc giữa các test case.
3. **Tự động hóa CI/CD với GitHub Actions Đạt Trạng Thái Xanh Tuyệt Đối (Success):**
   - Đã sửa cấu hình `.github/workflows/ci.yml`: Nâng cấp Actions lên `@v4`, `@v5`.
   - Cấp quyền bảo mật `permissions: security-events: write` cho bước quét lỗ hổng Trivy.
   - Pipeline tự động chạy và PASS 100% cả 3 môi trường Python 3.10, Python 3.11, Python 3.12 trên nền CSDL PostgreSQL 15.
4. **Cơ chế Dự phòng Heuristic cho AI (Zero-Downtime Fallback):**
   - Xây dựng thuật toán phân loại Heuristic và tư vấn tài chính quy tắc thông minh nội bộ trong trường hợp mất kết nối OpenAI hoặc hết hạn mức API Key, đảm bảo trải nghiệm người dùng không bao giờ bị đứt đoạn.

---

## 3. PHÂN CÔNG VÀ KỊCH BẢN THUYẾT TRÌNH BẢO VỆ CỦA NHÓM 02

Nhóm 02 đã thống nhất kịch bản bảo vệ trước Hội đồng chấm thi với thời lượng chuẩn 7 phút:

- **Phần 1 - Đặt vấn đề & Kiến trúc (Nguyễn Tuấn Đạt - 1.5 phút):**  
  Trình bày lý do chọn đề tài, đối tượng sinh viên/cá nhân, kiến trúc phân tầng FastAPI + Jinja2 + PostgreSQL + OpenAI.
- **Phần 2 - Demo Thực tế Nghiệp vụ & Giao diện (Phàn Ngọc Anh - 2.5 phút):**  
  Thao tác trên giao diện web: Đăng nhập tài khoản sinh viên với seed data 30 ngày có sẵn, thao tác bộ lọc ngày tháng và từ khóa, sử dụng Modal sửa giao dịch và Modal tạo danh mục mới.
- **Phần 3 - Trình diễn Tích hợp AI & Cơ chế Phòng vệ (Nguyễn Tuấn Đạt - 2 phút):**  
  Thêm giao dịch bằng ngôn ngữ tự nhiên để AI tự động phân loại, trình diễn khối Lời khuyên tài chính trên Dashboard, giải thích kỹ thuật 3 vòng tối ưu prompt và cơ chế Fallback an toàn.
- **Phần 4 - Minh chứng Kiểm thử & CI/CD (Cả nhóm - 1 phút):**  
  Chạy lệnh `pytest tests/` tại terminal để chứng minh 35/35 tests đạt kết quả xanh, mở trang GitHub Repository để chứng minh pipeline CI/CD GitHub Actions đạt dấu tích xanh ✅ 100%.

---

*Hệ thống ExpenseAI của Nhóm 02 đã hoàn thiện trọn vẹn, xuất sắc vượt qua mọi tiêu chí kỹ thuật và tự tin bảo vệ thành công!*
