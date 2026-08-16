# TÀI LIỆU PHÂN TÍCH HỎI ĐÁP (REQUIREMENTS QA)
**Tên ứng dụng:** Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI
**Nhóm:** 02 (Trưởng nhóm: Nguyễn Tuấn Đạt, Phó nhóm: Phàn Ngọc Anh)
**Giai đoạn:** Tuần 1-3 (Lấy yêu cầu)

---

### Bối cảnh Phỏng vấn
- **Khách hàng giả định:** Một nhân viên văn phòng bận rộn, không có thời gian phân loại thủ công từng giao dịch mỗi ngày.
- **Mục tiêu:** Khai thác các tính năng cốt lõi cần có cho ứng dụng.

### Danh sách Câu hỏi (Q) và Trả lời (A)

**Q1: Hiện tại anh/chị đang quản lý chi tiêu như thế nào và gặp khó khăn gì?**
- **A1:** Mình hay dùng sổ hoặc note trên điện thoại. Khó khăn lớn nhất là cuối tháng không biết tiền đi đâu, lười cộng dồn, và việc chia khoản chi (ăn uống, mua sắm) bằng tay rất mất thời gian.

**Q2: Vậy anh/chị mong muốn phần mềm tự động hóa bước nào nhất?**
- **A2:** Tự động phân loại. Ví dụ mình chỉ cần gõ "Đổ xăng 50k", phần mềm tự hiểu đó là khoản chi "Đi lại" và lưu vào ngày hôm nay với số tiền là 50,000 VNĐ.

**Q3: Về mặt báo cáo, anh/chị cần xem những biểu đồ nào?**
- **A3:** Mình muốn thấy tổng số tiền đã tiêu, số dư hiện tại, và một biểu đồ tròn xem mình tiêu nhiều nhất vào khoản nào trong tháng.

**Q4: Có cần tính năng đưa ra lời khuyên tài chính không?**
- **A4:** Có thì tuyệt vời. Ví dụ nếu tháng này mình tiêu quá nhiều cho ăn uống, app có thể cảnh báo hoặc đưa ra lời khuyên cắt giảm hợp lý.

**Q5: Anh/chị có yêu cầu gì về quyền riêng tư không?**
- **A5:** Dữ liệu chi tiêu rất nhạy cảm. Mình không muốn app tự động chia sẻ chi tiết mình mua gì cho bất kỳ ai hoặc hệ thống máy chủ thứ ba đọc được.

### Tổng hợp Yêu cầu rút ra (Quyết định đã xác nhận)
1. **Quản lý cốt lõi:** Cần chức năng Thêm giao dịch nhanh, Thống kê biểu đồ trực quan (Biểu đồ tròn).
2. **AI phân loại:** Xây dựng tính năng "Invisible AI", tự động bắt keyword trong chuỗi nhập để gán danh mục mà không cần user chọn dropdown.
3. **AI tư vấn:** Hệ thống tư vấn dựa trên số liệu tổng gộp (Aggregate data), không gửi lịch sử chi tiết.
4. **Bảo mật:** Ứng dụng phải có cơ chế Đăng nhập mã hóa để bảo vệ tính riêng tư cho từng user.
