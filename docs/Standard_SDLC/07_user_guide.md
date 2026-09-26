# HƯỚNG DẪN SỬ DỤNG PHẦN MỀM (USER GUIDE)
**Tên ứng dụng:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Nhóm:** 02 (Trưởng nhóm: Nguyễn Tuấn Đạt, Phó nhóm: Phàn Ngọc Anh)
**Giai đoạn:** Tuần 6-7 (Lập trình xong giao diện)

---

## 1. KHỞI ĐỘNG HỆ THỐNG
Sao chép `.env.example` thành `.env`, điền ít nhất một khóa AI nếu cần AI trực tuyến, rồi chạy:
```bash
docker-compose up --build
```
Chờ khoảng 30 giây để tiến trình cài đặt Python và tải Database hoàn tất.
Mở trình duyệt Web tại địa chỉ: `http://localhost:8000/docs` để kiểm tra API, hoặc `http://localhost:8000` (nếu giao diện độc lập được setup).

## 2. CHỨC NĂNG ĐĂNG NHẬP / ĐĂNG KÝ
- Hệ thống yêu cầu phải có tài khoản cá nhân.
- Truy cập vào trang Auth (Đăng nhập). Điền Username và Password.
- Bấm nút "Đăng nhập". Sau khi thành công, Token bảo mật sẽ được gán tự động vào trình duyệt (LocalStorage hoặc Cookie).

## 3. THÊM GIAO DỊCH BẰNG AI
- Mở trang **Quản lý Giao dịch**.
- Bấm vào nút màu xanh **"Thêm giao dịch mới"**. Một bảng pop-up (Modal) sẽ hiện ra.
- **Bước quan trọng:** Thay vì phải đau đầu tìm xem "Mua bún chả" nằm ở thư mục "Ăn uống" hay "Hẹn hò", người dùng chỉ việc:
  1. Gõ Số tiền: `30000`.
  2. Gõ Mô tả: `Ăn bún chả với đồng nghiệp`.
  3. Bấm **Lưu**.
- Ngay lập tức, AI chạy ngầm và tự động xếp khoản 30,000 này vào cột Danh mục **"Ăn uống"** trên bảng lưới. Rất tiện lợi và tiết kiệm 50% thao tác.

## 4. TÌM KIẾM VÀ LỌC GIAO DỊCH
- Trên màn hình danh sách, phía trên cùng có thanh **Filter Bar**.
- User điền ngày bắt đầu, ngày kết thúc và gõ từ khóa mô tả (Ví dụ: `bún chả`).
- Bấm **"Lọc"**. Bảng lưới bên dưới chỉ hiện các giao dịch khớp điều kiện mà không tải lại toàn bộ trang.

## 5. XEM BÁO CÁO VÀ NHẬN TƯ VẤN (AI ADVISORY)
- Chuyển sang màn hình **Dashboard (Tổng quan)**.
- Dashboard gọi các API `/api/reports/summary`, `/api/reports/by_category`, và `/api/reports/monthly_trend` để hiển thị tổng quan.
- Phía bên phải, khung **"AI Tư vấn"** sẽ tải trong vài giây (gọi API `GET /api/advice/`). Sau khi chạy xong, AI sẽ in ra một đoạn đánh giá ngắn gọn.

## 6. PHÂN TÍCH HÀNH VI VÀ QUYỀN RIÊNG TƯ
- Lời khuyên AI thông thường chỉ dùng tổng số theo danh mục.
- Nếu chọn **Phân tích hành vi**, hệ thống hiển thị hộp xác nhận. Chỉ đồng ý khi bạn chấp nhận gửi chi tiết giao dịch cần thiết tới nhà cung cấp AI.
