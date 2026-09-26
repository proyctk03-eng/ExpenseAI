# ExpenseAI - Tài liệu kỹ thuật chính thức

**Trạng thái:** phiên bản thực tế đã kiểm chứng ngày 17/09/2026.

Tài liệu này là điểm tham chiếu duy nhất cho kiến trúc, phạm vi, dữ liệu và trạng thái kiểm thử của ExpenseAI. Các tệp trong `docs/backup/` và `docs/backup/archive_old/` chỉ phục vụ lưu vết, không dùng để nộp hay trích dẫn như mô tả hiện hành.

## Phạm vi hiện tại

ExpenseAI là ứng dụng web quản lý thu chi cá nhân. Hệ thống cung cấp xác thực JWT, CRUD giao dịch và danh mục, báo cáo, dashboard, lời khuyên tài chính tổng hợp, quét hóa đơn, ticket phản hồi và bộ nhớ danh mục theo từng người dùng. Quản lý ngân sách hoặc cảnh báo ngưỡng 85% chưa được triển khai; đó là hướng phát triển, không phải chức năng hiện tại.

## Kiến trúc đã triển khai

```text
Browser (Jinja2, Bootstrap, Chart.js)
  -> FastAPI routers and Pydantic validation
  -> Services: classifier, advice, behavior, vision
  -> SQLAlchemy ORM -> PostgreSQL hoặc SQLite
  -> Tùy chọn: Redis cache
  -> AI: Gemini 1.5 Flash ưu tiên; OpenAI GPT-3.5 Turbo là fallback
```

Gemini được gọi qua OpenAI-compatible endpoint khi có `GEMINI_API_KEY`; khi không có Gemini, hệ thống dùng `OPENAI_API_KEY`. Nếu không có khóa hoặc dịch vụ lỗi, classifier và advice có fallback nội bộ. Redis chỉ được bật khi `CACHE_ENABLED=true`.

## Dữ liệu và quyền

Schema hiện có 11 bảng: `users`, `categories`, `transactions`, `ai_predictions`, `user_memory_rules`, `roles`, `permissions`, `user_roles`, `role_permissions`, `feedback_tickets`, `ticket_replies`.

`users` có nhiều `roles`; `roles` có nhiều `permissions`. Giao dịch thuộc một user và có thể thuộc một category. `ai_predictions` là audit một-một với giao dịch. Ticket và memory rule đều thuộc user. Các bảng RBAC, prediction, ticket reply và memory rule có foreign key cascade ở nơi được định nghĩa trong model; việc xóa user ở lớp ORM dùng `delete-orphan` cho transactions, categories và tickets.

## Hợp đồng API chính

| Nhóm | Endpoint |
|---|---|
| Auth | `POST /api/auth/register`, `/login`, `/refresh`, `/logout`; `GET/PUT /api/auth/me`; `PUT /api/auth/password` |
| Giao dịch | `GET/POST /api/transactions/`; `PUT/DELETE /api/transactions/{id}`; `POST /api/transactions/scan-receipt` |
| Danh mục | `GET/POST /api/categories/`; `PUT/DELETE /api/categories/{id}` |
| Báo cáo | `GET /api/reports/summary`, `/by_category`, `/monthly_trend`; `GET /api/dashboard/summary`, `/monthly-comparison`, `/category-breakdown` |
| AI | `POST /api/advice/`; `GET /api/advice/behavior?share_transaction_details=true` |
| Feedback | `/api/feedback/`, `/api/feedback/my`, `/api/feedback/stats`, ticket detail/status/reply |

## Quyền riêng tư

`POST /api/advice/` chỉ gửi số liệu tổng hợp theo danh mục. `GET /api/advice/behavior` có thể gửi ngày, danh mục, mô tả và số tiền của tối đa 50 giao dịch chi tới nhà cung cấp AI; endpoint và giao diện đều yêu cầu người dùng xác nhận rõ ràng trước khi gọi. Đây là opt-in, không phải luồng mặc định.

## Trạng thái chất lượng

Không dùng các tuyên bố "100%", "zero downtime", hay chỉ số hiệu năng/độ chính xác khi chưa có artifact tái lập được. Kết quả test được ghi theo lệnh, thời điểm, môi trường và đầu ra thật. CI có tại `.github/workflows/ci.yml`; kết quả CI chỉ được công bố sau khi workflow chạy trên GitHub.
