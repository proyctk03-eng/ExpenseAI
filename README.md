# Expense Manager AI (ExpenseAI)

Hệ thống quản lý chi tiêu cá nhân tích hợp AI hỗ trợ tự động bóc tách và phân loại giao dịch từ văn bản tự do, cung cấp Dashboard biểu đồ và Cố vấn tài chính cá nhân hóa.

## Cấu trúc thư mục (Cập nhật)
```text
.
├── alembic/          # Cấu hình Database Migration bằng Alembic
├── docs/             # Chứa toàn bộ các báo cáo đồ án, thiết kế hệ thống
├── src/
│   ├── api/          # Các Router API (auth, transactions, categories, reports, advice)
│   ├── middleware/   # Middleware (VD: Ghi log request/response)
│   ├── models/       # Định nghĩa Schema Database (SQLAlchemy)
│   ├── schemas/      # Định nghĩa Validate Dữ liệu (Pydantic)
│   ├── services/     # Tích hợp AI (OpenAI API)
│   ├── static/       # CSS, ảnh tĩnh
│   ├── templates/    # Giao diện HTML Render bằng Jinja2
│   └── utils/        # Dependencies, bảo mật JWT (HttpOnly), Rate Limiting
├── tests/            # Tự động hóa kiểm thử bằng Pytest
├── .env.example      # File mẫu cấu hình môi trường
├── docker-compose.yml# File triển khai Docker
├── Dockerfile        # File đóng gói môi trường Python
└── requirements.txt  # Danh sách thư viện Python
```

## Hướng dẫn cài đặt và chạy (Docker - Khuyến nghị)

Đây là cách dễ nhất để chạy dự án mà không cần cài đặt Python hay PostgreSQL rườm rà.

1. **Chuẩn bị môi trường:** Cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. **Cấu hình biến môi trường:** Sao chép file `.env.example` thành `.env` và điền key OpenAI của bạn vào `OPENAI_API_KEY`.
3. **Khởi chạy hệ thống:**
   Mở terminal tại thư mục gốc của dự án và chạy:
   ```bash
   docker-compose up --build -d
   ```
4. **Cập nhật Database:** (Bắt buộc chạy lần đầu)
   ```bash
   docker-compose exec web alembic upgrade head
   ```
5. **Truy cập ứng dụng:** Mở trình duyệt tại địa chỉ `http://localhost:8000`.

## Lưu ý về bảo mật (Cập nhật)
- Hệ thống sử dụng **HttpOnly Cookies** để lưu trữ Token thay vì LocalStorage.
- Có tích hợp **Rate Limiter (SlowAPI)** giới hạn 10 requests/phút cho các API xác thực để chống brute-force.
- Mọi dữ liệu nhạy cảm được bọc qua **EscapeHTML** ở frontend.

## API Documentation
Sau khi chạy ứng dụng, bạn có thể xem tài liệu API tự động sinh bởi FastAPI (Swagger UI) tại:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
## Kiểm thử (Testing)
Hệ thống sử dụng Pytest. Lưu ý các cấu hình rate limiter có thể làm fail test nếu chạy quá nhanh, do đó cần cấu hình lại hàm tạo mock user trong file test.
Lệnh: `docker-compose exec web pytest tests/`
