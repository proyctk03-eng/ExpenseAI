# ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)
**Tên ứng dụng:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Nhóm:** 02 (Trưởng nhóm: Nguyễn Tuấn Đạt, Phó nhóm: Phàn Ngọc Anh)
**Giai đoạn:** Tuần 4-5 (Bài KT 1)

---

## 1. DANH SÁCH TÁC NHÂN (ACTOR)
| Mã | Tác nhân | Mô tả |
|:---|:---|:---|
| ACT-001 | User | Người dùng cá nhân có tài khoản, thực hiện thêm/sửa/xóa giao dịch. |
| ACT-002 | AI Engine | Hệ thống AI ẩn, nhận dữ liệu và trả về dự đoán phân loại / lời khuyên. |

## 2. DANH SÁCH USE CASE
| ID | Tên Use Case | Mô tả ngắn gọn | ACTOR |
|:---|:---|:---|:---|
| UC-001 | Đăng nhập/Đăng ký | Xác thực danh tính qua Token JWT. | User |
| UC-002 | Quản lý Giao dịch | Tạo, đọc, cập nhật, xóa các khoản thu/chi. | User |
| UC-003 | Tìm kiếm và Lọc | Lọc theo thời gian, tìm kiếm mô tả. | User |
| UC-004 | Tự động phân loại (AI) | Khi tạo giao dịch, tự động gửi text cho AI phân loại. | User, AI Engine |
| UC-005 | Xem báo cáo tài chính | Xem biểu đồ tròn, tổng thu/chi. | User |
| UC-006 | Xin lời khuyên tài chính (AI) | Đọc dữ liệu tổng hợp để đưa ra lời khuyên. | User, AI Engine |

## 3. YÊU CẦU CHỨC NĂNG (FUNCTIONAL REQUIREMENTS)
- **REQ-F-001:** Hệ thống cho phép User đăng ký tài khoản với username/password.
- **REQ-F-002:** User có thể tạo Giao dịch mới gồm: Số tiền, Mô tả (chuỗi). Hệ thống tự lấy ngày giờ hiện tại.
- **REQ-F-003:** Khi User tạo giao dịch, hệ thống tự động gán Category_ID bằng cách gọi AI. Nếu AI lỗi, hệ thống phải gán vào danh mục mặc định (Fallback).
- **REQ-F-004:** User có thể tìm kiếm giao dịch qua chuỗi nhập, và lọc theo `start_date`, `end_date`.

## 4. YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS)
- **REQ-NF-001 (Bảo mật):** Passwords phải băm bằng Bcrypt trước khi lưu.
- **REQ-NF-002 (Bảo mật - Isolate):** Người dùng A không thể truy cập giao dịch của Người dùng B (Lọc theo `user_id` ở mức Database).
- **REQ-NF-003 (Hiệu năng):** Thao tác tính toán báo cáo phải sử dụng hàm Aggregation của SQL (`func.sum()`), tránh tải toàn bộ dữ liệu vào RAM Python.

## 5. YÊU CẦU AI & BẢO MẬT (AI REQUIREMENTS & GUARDRAILS)
- **REQ-AI-001:** Input vào AI phân loại: Giới hạn độ dài chuỗi nhập để tránh tốn token (VD: max 255 chars).
- **REQ-AI-002:** Output từ AI: Bắt buộc ở định dạng JSON cố định `{"category": "...", "confidence": 0.xx}`.
- **REQ-AI-003 (Đạo đức dữ liệu):** Đối với tính năng tư vấn, nghiêm cấm truyền dữ liệu giao dịch chi tiết cho máy chủ AI bên thứ 3. Chỉ truyền dữ liệu tổng gộp: (Ví dụ: Ăn uống: 5 triệu, Xăng xe: 1 triệu).
