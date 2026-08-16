# BÁO CÁO TIẾN ĐỘ DỰ ÁN CUỐI KỲ
**Môn học:** Đồ án phần mềm / Thực hành chuyên môn
**Nhóm thực hiện:** Nhóm 02
**Đề tài:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp Trí tuệ Nhân tạo (AI)

### Thành viên nhóm:
1. **Trưởng nhóm:** Nguyễn Tuấn Đạt
2. **Phó nhóm:** Phàn Ngọc Anh

---

## 1. TÌNH TRẠNG HOÀN THÀNH (DỰA TRÊN RUBRIC KIỂM TRA)

| Hạng mục | Tỷ lệ hoàn thành | Đánh giá |
|---|:---:|---|
| **Bài kiểm tra 1 (Phân tích thiết kế)** | 100% | Đã hoàn thiện toàn bộ Use Case, ERD, Sơ đồ luồng dữ liệu AI và Báo cáo Markdown. |
| **Bài kiểm tra 2 (Lập trình cơ bản)** | 100% | Đã triển khai xong Backend (FastAPI), CRUD, và đặc biệt **đã tích hợp đầy đủ chức năng Lọc & Tìm kiếm Giao dịch** theo mô tả, ngày tháng. |
| **Bài kiểm tra 3 (Tích hợp AI)** | 100% | Hệ thống AI Classifier và AI Advisor hoạt động hoàn hảo, bắt lỗi timeout và fallback chuẩn xác. |
| **Hệ thống minh chứng AI** | 100% | Bảng minh chứng (Prompt, Code, Nhận xét) được ghi chép đầy đủ tại file `ai_evidence_report.md`. |

---

## 2. NHỮNG CẬP NHẬT MỚI NHẤT (CỦA TUẦN NÀY)

Nhằm đảm bảo dự án đáp ứng **100%** tiêu chí của Bài Kiểm Tra 2 (Tiêu chí số 4: Tìm kiếm và lọc dữ liệu), Nhóm 02 đã thực hiện cập nhật toàn diện:

- **Về phía Backend (`transactions.py`):** Cập nhật Endpoint `GET /transactions/` để tiếp nhận các query parameters: `search`, `start_date`, `end_date`, `category_id`. Sử dụng các hàm nội suy của SQLAlchemy (`ilike`, `>=`, `<=`) để lọc giao dịch mạnh mẽ và tối ưu.
- **Về phía Frontend (`transactions.html`):** Bổ sung một thanh công cụ (Filter Bar) hoàn chỉnh ngay phía trên bảng giao dịch. Thanh công cụ bao gồm: Ô tìm kiếm văn bản, Bộ chọn ngày bắt đầu (Từ ngày), Bộ chọn ngày kết thúc (Đến ngày) và nút bấm xử lý logic trực tiếp qua Fetch API mà không cần tải lại trang.

---

## 3. KẾ HOẠCH ĐỀ XUẤT CHO TUẦN TIẾP THEO (BẢO VỆ DỰ ÁN)

- **Nguyễn Tuấn Đạt (Trưởng nhóm):** Chịu trách nhiệm tổng hợp 4 file báo cáo trong thư mục `docs/` thành file Word (.docx) và chuẩn bị slide PowerPoint thuyết trình (tập trung vào cấu trúc Hệ thống và Demo AI).
- **Phàn Ngọc Anh (Phó nhóm):** Chịu trách nhiệm kiểm thử toàn diện lại các luồng (Manual Testing) trên giao diện Web, chuẩn bị sẵn các dữ liệu đẹp để Demo trực tiếp trên lớp.

*Dự án đã sẵn sàng để đóng gói và bảo vệ thành công!*
