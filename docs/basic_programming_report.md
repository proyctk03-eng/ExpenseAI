# BÁO CÁO LẬP TRÌNH: HỆ THỐNG QUẢN LÝ CHI TIÊU CÁ NHÂN

> **Lưu ý dành cho sinh viên:** Dưới đây là dàn ý chuẩn và các đoạn văn mẫu để bạn có thể tham khảo, chỉnh sửa hoặc đưa trực tiếp vào file Word báo cáo nộp cho giảng viên (phục vụ Bài KT2 và Báo cáo cuối kỳ).

---

## 1. Cấu trúc Dự án (Project Structure)
Dự án được tổ chức theo kiến trúc module hóa nhằm tách biệt rõ ràng giữa cấu hình, kết nối CSDL, xử lý logic (Services), định tuyến (Routers) và giao diện (Templates).

*Mẫu viết:*
> Hệ thống được triển khai bằng framework FastAPI (Python) với cấu trúc thư mục chuẩn:
> - **`src/models/`**: Chứa định nghĩa các bảng CSDL bằng SQLAlchemy (User, Category, Transaction).
> - **`src/schemas/`**: Chứa các Pydantic models dùng để kiểm tra tính hợp lệ của dữ liệu đầu vào/đầu ra (Data Validation).
> - **`src/api/`**: Nơi đặt các Router xử lý Request/Response (auth.py, transactions.py, reports.py...).
> - **`src/templates/` & `src/static/`**: Quản lý giao diện Web hiển thị bằng Jinja2 và Bootstrap.
> - **`src/database.py` & `config.py`**: Quản lý kết nối DB và tải biến môi trường.
> Cách tổ chức này giúp code dễ bảo trì, dễ mở rộng tính năng và tránh xung đột khi làm việc nhóm.

---

## 2. Kết nối Cơ sở Dữ liệu
*Mẫu viết:*
> Ứng dụng sử dụng **SQLAlchemy 2.0** làm ORM (Object-Relational Mapping) để giao tiếp với CSDL (PostgreSQL/SQLite). Thông tin cấu hình chuỗi kết nối (`DATABASE_URL`) được giấu an toàn trong file `.env`. 
> 
> Để tối ưu hóa hiệu năng và ngăn chặn lỗi sập kết nối, hệ thống đã bật tính năng `pool_pre_ping=True`. Việc quản lý phiên làm việc với CSDL (Session) được đưa vào Dependency Injection `get_db()` của FastAPI, đảm bảo Session luôn được tự động đóng (`db.close()`) sau khi hoàn thành một request dù có xảy ra lỗi hay không.

---

## 3. Chức năng Đăng nhập và Phân quyền (Auth)
*Mẫu viết:*
> Hệ thống ứng dụng chuẩn bảo mật **OAuth2 với JWT (JSON Web Token)**.
> - **Bảo mật mật khẩu:** Mật khẩu của người dùng không bao giờ lưu dạng plain-text mà được băm (hash) bằng thuật toán **Bcrypt** (thư viện `passlib`).
> - **Đăng nhập:** Khi người dùng cung cấp đúng Username và Password, hệ thống cấp một mã JWT có thời hạn 30 phút. 
> - **Phân quyền & Cách ly dữ liệu:** FastAPI Dependency `get_current_user` được gọi ở mọi endpoint để giải mã JWT, xác định người dùng đang thực hiện request là ai. Bất kỳ câu truy vấn nào (`SELECT`, `UPDATE`, `DELETE`) cũng đi kèm điều kiện `user_id == current_user.id`, đảm bảo tuyệt đối người dùng A không thể nhìn thấy hay sửa xóa dữ liệu của người dùng B.

---

## 4. Xây dựng CRUD Nghiệp vụ Chính
*Mẫu viết:*
> Các chức năng Thêm (Create), Đọc (Read), Sửa (Update), Xóa (Delete) được hoàn thiện đầy đủ cho bảng **Danh mục (Category)** và **Giao dịch (Transaction)**.
> - Khi Thêm mới giao dịch: Pydantic Schema kiểm tra dữ liệu đầu vào (Ví dụ: số tiền `amount > 0`).
> - Khi Xóa danh mục: Hệ thống có cơ chế kiểm tra ràng buộc (Constraint Check). Nếu danh mục đang chứa giao dịch, hệ thống sẽ chặn hành động xóa và trả về lỗi 400 Bad Request để bảo toàn tính nguyên vẹn của dữ liệu báo cáo.

---

## 5. Chức năng Tìm kiếm, Lọc và Phân trang
*Mẫu viết:*
> Đối với danh sách Giao dịch, để đối phó với trường hợp dữ liệu phình to theo thời gian, hệ thống tích hợp sẵn tham số **Phân trang (Pagination)** thông qua `skip` và `limit` trong câu truy vấn SQLAlchemy. Đồng thời, hàm truy vấn tự động áp dụng hàm `order_by(Transaction.transaction_date.desc())` để luôn hiển thị các khoản chi tiêu/thu nhập mới nhất lên trên cùng.

*(Gợi ý: Nếu bạn có bổ sung thêm lọc theo thời gian cụ thể thì viết thêm vào đây)*

---

## 6. Chức năng Thống kê và Báo cáo
*Mẫu viết:*
> Việc tính toán tổng thu, tổng chi và vẽ biểu đồ không được thực hiện ở Backend bằng vòng lặp Python, mà được tối ưu hóa ở tầng CSDL bằng các hàm tổng hợp SQL (Aggregation functions). 
> 
> Nhờ kết hợp `func.sum(Transaction.amount)` và `group_by(Category.name)`, hệ thống chỉ trả về kết quả đã cộng gộp. Điều này giúp endpoint `/api/reports/by_category` xử lý cực kỳ nhanh chóng và tiết kiệm bộ nhớ cho Server.

---

## 7. Giao diện Người dùng (UI/UX)
*Mẫu viết:*
> Giao diện (Frontend) được thiết kế theo tư tưởng SPA lai (Single Page Application) sử dụng **Jinja2** và **Bootstrap 5**.
> - **Hiển thị trực quan:** Bảng điều khiển (Dashboard) sử dụng thẻ Card để làm nổi bật số dư, tổng thu, tổng chi. Biểu đồ tròn phân bổ chi tiêu được vẽ mượt mà bằng thư viện **Chart.js**.
> - **Trải nghiệm thao tác:** Người dùng thao tác (thêm/xóa giao dịch) thông qua Fetch API bất đồng bộ. Giao diện không cần reload lại toàn bộ trang, tạo cảm giác mượt mà. Hệ thống hiển thị cảnh báo Alert rõ ràng khi thao tác thành công hay thất bại.

---

## 8. Xử lý Lỗi và Giới hạn (Error Handling)
*Mẫu viết:*
> Để ngăn chặn ứng dụng bị crash khi có sự cố, toàn bộ các endpoint giao tiếp với DB đều được đặt trong khối `try...except SQLAlchemyError`. 
> Nếu xảy ra lỗi (như vi phạm khóa ngoại, mất kết nối DB), hệ thống lập tức gọi `db.rollback()` để hoàn tác, sau đó trả về mã lỗi HTTP chuẩn mực như `404 Not Found` (không tìm thấy data), `400 Bad Request` (sai định dạng) hoặc `403 Forbidden` (không đủ quyền hạn) kèm theo câu thông báo JSON rõ ràng.

---

## 9. Minh chứng Sử dụng AI trong Quá trình Lập trình
*(Khu vực này bạn tự điền nội dung từ lịch sử chat hoặc chụp màn hình)*

**Ví dụ:**
- **Vấn đề gặp phải:** Khi code endpoint tạo JWT Token, tôi không nhớ cú pháp tạo thời gian sống (expire time) cho Token bằng thư viện python-jose.
- **Prompt:** *"Tôi đang viết endpoint login cho FastAPI. Hãy viết hàm tạo JWT Token bằng thư viện python-jose có gắn thời hạn hết hạn (expire) là 30 phút."*
- **Kiểm chứng/Sửa đổi:** AI đã sinh ra hàm `create_access_token` sử dụng `datetime.utcnow() + timedelta`. Tôi đã đọc hiểu logic, copy hàm này vào file `security.py` và truyền thêm biến môi trường `SECRET_KEY` thay vì fix cứng key trong code do AI gợi ý ban đầu.

*(Chèn 1-2 hình ảnh chụp màn hình đoạn chat với AI để làm minh chứng sinh động).*
