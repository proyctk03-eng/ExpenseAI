# ExpenseAI — Smart Personal Finance Management Platform

[![Continuous Integration](https://github.com/proyctk03-eng/ExpenseAI/actions/workflows/ci.yml/badge.svg)](https://github.com/proyctk03-eng/ExpenseAI/actions/workflows/ci.yml)
[![Tests Passing](https://img.shields.io/badge/Tests-87%2F87%20Passed%20(100%25)-brightgreen.svg?logo=pytest&logoColor=white)](https://github.com/proyctk03-eng/ExpenseAI/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Multi--Key%20Failover-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Security: OWASP Hardened](https://img.shields.io/badge/Security-OWASP%20Top%2010%20Hardened-success.svg?logo=shield)](https://owasp.org)
[![Docker Ready](https://img.shields.io/badge/Docker-Production%20Ready-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **ExpenseAI** là nền tảng quản lý tài chính cá nhân thông minh ứng dụng Trí tuệ Nhân tạo thế hệ mới (Google Gemini, OpenAI, Heuristics Engine), tích hợp hệ thống bảo mật cấp doanh nghiệp theo chuẩn **OWASP Top 10**, hệ thống **Quản lý Ngân sách** toàn diện và cơ chế **Failover Đa khóa (Multi-Key Failover)** tự động chuyển đổi khóa khi hết hạn ngạch.

---

## Mục Lục

1. [Tính Năng Nổi Bật](#tính-năng-nổi-bật)
2. [Kiến Trúc Đột Phá](#kiến-trúc-đột-phá)
   - [Bộ Điều Phối AI Multi-Key Failover](#1-bộ-điều-phối-ai-multi-key-failover)
   - [Hệ Thống Quản Lý Ngân Sách Thông Minh](#2-hệ-thống-quản-lý-ngân-sách-thông-minh)
   - [Bảo Mật Chuẩn OWASP Top 10 & Zero-Backdoor](#3-bảo-mật-chuẩn-owasp-top-10--zero-backdoor)
3. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
4. [Hướng Dẫn Cài Đặt & Khởi Chạy](#hướng-dẫn-cài-đặt--khởi-chạy)
   - [Cách 1: Chạy Cục Bộ (Local Development — Khuyên Dùng)](#cách-1-chạy-cục-bộ-local-development--khuyên-dùng)
   - [Cách 2: Chạy Bằng Docker Compose (Production Ready)](#cách-2-chạy-bằng-docker-compose-production-ready)
5. [Cấu Hình Biến Môi Trường (.env)](#cấu-hình-biến-môi-trường-env)
6. [Chạy Kiểm Thử Tự Động (Automated Testing - 87/87 Tests)](#chạy-kiểm-thử-tự-động-automated-testing)
7. [Tài Liệu API (Swagger / OpenAPI)](#tài-liệu-api-swagger--openapi)
8. [Cam Kết An Toàn & Bảo Mật (Secret Safety)](#cam-kết-an-toàn--bảo-mật-secret-safety)
9. [Tác Giả & Bản Quyền](#tác-giả--bản-quyền)

---

## Tính Năng Nổi Bật

### Trí Tuệ Nhân Tạo & Phân Tích Thông Minh
- **Tự động phân loại chi tiêu (AI Auto-Classification):** Nhận diện danh mục chi tiêu tự động với bộ từ điển quy chuẩn tiếng Việt mở rộng kết hợp mô hình LLM.
- **Tư vấn tài chính cá nhân hóa (AI Financial Advice):** Phân tích dữ liệu thu chi thực tế theo nguyên tắc quản lý tài chính chuẩn quốc tế **50/30/20** và dòng tiền 3 tháng gần nhất.
- **Trò chuyện ngữ cảnh thông minh (Contextual AI Chat):** Trực tiếp trò chuyện với trợ lý AI dựa trên lịch sử giao dịch cá nhân, có thẻ phân định XML bảo vệ chống Prompt Injection.
- **Quét hóa đơn bằng hình ảnh (Receipt Vision OCR):** Trích xuất tự động số tiền, danh mục, ngày giao dịch và tên người bán từ ảnh hóa đơn/biên lai.
- **Phân tích hành vi & Cảnh báo thói quen (Behavioral Analytics):** Nhận diện các xu hướng chi tiêu bất thường và đưa ra cảnh báo sớm trước khi thâm hụt ngân sách.

### Quản Lý Ngân Sách & Cảnh Báo Hạn Mức
- **Thiết lập ngân sách linh hoạt:** Tạo và quản lý hạn mức chi tiêu theo từng danh mục riêng biệt (Ăn uống, Di chuyển, Mua sắm, Hóa đơn, v.v.) theo tháng.
- **Theo dõi tiến độ chi tiêu thời gian thực:** Hiển thị trực quan tỷ lệ phần trăm đã chi tiêu so với hạn mức đã định.
- **Cảnh báo vượt ngưỡng tự động:** Cảnh báo khi chi tiêu chạm ngưỡng 80% và cảnh báo đỏ khi vượt mức 100% ngân sách.

### Bảo Mật Cấp Doanh Nghiệp (OWASP Top 10 Hardened)
- **HttpOnly & Secure JWT Cookie:** Loại bỏ triệt để nguy cơ đánh cắp phiên đăng nhập qua lỗi XSS (không lưu trữ JWT trong `localStorage`).
- **Phòng chống CSRF toàn diện:** Cơ chế bảo vệ *Double Submit Cookie* tự động xác thực cho toàn bộ các yêu cầu `POST`, `PUT`, `DELETE`.
- **Phân quyền người dùng (RBAC):** Kiểm soát truy cập nghiêm ngặt dựa trên vai trò (Admin, User) phía máy chủ.
- **Chính sách mật khẩu nghiêm ngặt:** Bắt buộc mật khẩu tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt được kiểm tra chặt chẽ phía server.
- **Kiểm soát lưu lượng (Rate Limiting):** Giới hạn tần suất gọi API qua SlowAPI để chống tấn công Denial of Wallet và Brute Force.
- **Kiểm tra upload ảnh an toàn:** Kiểm tra nghiêm ngặt phần mở rộng, MIME Type và Magic Bytes của tệp ảnh trước khi xử lý.
- **Chống XSS & SQL Injection:** 100% truy vấn sử dụng SQLAlchemy ORM / Parameterized Queries và lọc HTML nguy hiểm trước khi render.

---

## Kiến Trúc Đột Phá

### 1. Bộ Điều Phối AI Multi-Key Failover

Hệ thống được trang bị kiến trúc tự động xoay vòng và dự phòng khóa thông minh qua module tập trung `GeminiKeyManager`:

```mermaid
flowchart TD
    Req["Yêu cầu AI: Advice / Classifier / Vision / Behavior"] --> TryPrimary["1. Gọi Google Gemini với Key Chính"]
    TryPrimary -->|Thành công| Success["Trả kết quả cho người dùng"]
    TryPrimary -->|429 RateLimit / Hết Quota| TriggerFailover["2. GeminiKeyManager kích hoạt Failover"]
    TriggerFailover --> SwitchBackup["3. Tự động xoay sang Gemini Key Dự Phòng"]
    SwitchBackup --> Retry["4. Thực hiện Retry ngay lập tức"]
    Retry -->|Thành công| Success
    SwitchBackup -->|Nếu hết cả 2 Key Gemini| FallbackOpenAI["5. Fallback sang OpenAI API"]
    FallbackOpenAI -->|Thành công| Success
    FallbackOpenAI -->|Không có OpenAI / Mạng lỗi| HeuristicFallback["6. Chuyên gia Quy tắc Tiếng Việt 50/30/20 Ngoại tuyến"]
    HeuristicFallback --> Success
```

- **Phản hồi tức thì (< 5ms):** Tầng Heuristics xử lý nhanh hơn 85% các giao dịch thường nhật bằng từ điển quy chuẩn mà không tiêu hao hạn ngạch LLM.
- **Redis Cache thông minh (TTL 24h):** Lưu đệm kết quả phân tích theo mã băm MD5 duy nhất, tránh các lệnh gọi API trùng lặp.

### 2. Hệ Thống Quản Lý Ngân Sách Thông Minh

Module Budget cho phép người dùng thiết lập kế hoạch tài chính chủ động:
- Giao diện Web chuyên nghiệp với thanh tiến độ trực quan.
- Tính toán thời gian thực tổng số tiền đã chi tiêu trong tháng tương ứng cho từng danh mục.
- Tích hợp API RESTful đầy đủ: tạo mới, cập nhật, xóa và xem tổng quan ngân sách.

### 3. Bảo Mật Chuẩn OWASP Top 10 & Zero-Backdoor

Mọi yêu cầu đều được kiểm tra xuyên suốt qua pipeline bảo mật:
1. Nginx Reverse Proxy với các Header bảo mật (X-Frame-Options, Content-Security-Policy, X-Content-Type-Options).
2. CSRF Middleware kiểm tra Double Submit Cookie.
3. SlowAPI Rate Limiter chống tấn công vét cạn.
4. Pydantic Schemas kiểm tra tính hợp lệ của dữ liệu đầu vào.
5. SQLAlchemy ORM Parameterization ngăn chặn SQL Injection.

---

## Cấu Trúc Dự Án

```text
ExpenseAI/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Pipeline CI/CD GitHub Actions (Python 3.10, 3.11, 3.12 + Trivy)
├── backend/                       # Máy chủ Backend (FastAPI)
│   ├── alembic/                   # Quản lý Database Migrations
│   ├── src/                       # Mã nguồn chính
│   │   ├── api/                   # Router Endpoints (auth, advice, budgets, feedback, reports, transactions, web)
│   │   ├── middleware/            # CSRF Protection, Rate Limiting Middleware
│   │   ├── models/                # Thực thể SQLAlchemy ORM
│   │   ├── schemas/               # Lược đồ Pydantic Input/Output Validation
│   │   ├── services/              # Nghiệp vụ AI (Advice, Classifier, Vision, Behavior, Budget)
│   │   ├── utils/                 # GeminiKeyManager, Security Helpers, Dependencies
│   │   ├── config.py              # Nạp biến môi trường toàn cục (.env)
│   │   └── main.py                # Điểm khởi động ứng dụng FastAPI
│   ├── tests/                     # Bộ kiểm thử tự động Pytest (87/87 tests)
│   │   ├── conftest.py            # Global Pytest Fixtures & CI Mock Environment
│   │   ├── test_agent_memory.py
│   │   ├── test_ai_and_deduplication.py
│   │   ├── test_api.py
│   │   ├── test_budgets.py
│   │   ├── test_export.py
│   │   ├── test_feedback.py
│   │   ├── test_gemini_failover.py
│   │   ├── test_pentest_hardening.py
│   │   ├── test_qa_qc_verification.py
│   │   └── test_security_fixes.py
│   ├── .env.example               # Mẫu cấu hình biến môi trường
│   ├── Dockerfile                 # Dockerfile đa tầng cho Backend
│   └── requirements.txt           # Danh mục thư viện Python
├── frontend/                      # Giao diện người dùng
│   ├── static/                    # Tệp tĩnh (CSS hiện đại, JavaScript, Biểu đồ Chart.js)
│   └── templates/                 # Giao diện Jinja2 (Dashboard, Budgets, Stats, Feedback, v.v.)
├── nginx/
│   └── nginx.conf                 # Cấu hình Nginx Reverse Proxy & Secure Headers
├── docker-compose.yml             # Cấu hình triển khai hệ thống (Nginx + App + Postgres + Redis)
├── pyproject.toml                 # Cấu hình Linting & Code Style
├── requirements.txt               # Thư viện gốc thuận tiện cài đặt
└── README.md                      # Tài liệu hướng dẫn sử dụng
```

---

## Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Chạy Cục Bộ (Local Development — Khuyên Dùng)

#### Yêu cầu tiên quyết:
- **Python 3.10+** (Khuyến nghị Python 3.11 hoặc 3.12).
- **Git** đã cài đặt trên máy.

#### Bước 1: Sao chép mã nguồn
```bash
git clone https://github.com/proyctk03-eng/ExpenseAI.git
cd ExpenseAI
```

#### Bước 2: Tạo và kích hoạt môi trường ảo (Virtual Environment)
- **Trên Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Trên Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```
- **Trên macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### Bước 3: Cài đặt các thư viện cần thiết
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Bước 4: Thiết lập file môi trường `.env`
Sao chép file mẫu vào thư mục `backend/`:
- **Trên Windows (PowerShell):**
  ```powershell
  Copy-Item backend\.env.example backend\.env
  ```
- **Trên Linux / macOS:**
  ```bash
  cp backend/.env.example backend/.env
  ```

Mở file `backend/.env` bằng trình soạn thảo và điền các khóa API của bạn.

#### Bước 5: Khởi chạy máy chủ phát triển
Chuyển vào thư mục `backend` và khởi chạy Uvicorn:
```bash
cd backend
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

#### Bước 6: Truy cập ứng dụng
- **Giao diện Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Tài liệu API tương tác (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Tài liệu API thay thế (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### Cách 2: Chạy Bằng Docker Compose (Production Ready)

Nếu máy tính của bạn đã cài đặt **Docker** và **Docker Desktop**:

```bash
# 1. Sao chép file cấu hình môi trường
cp backend/.env.example backend/.env

# 2. Khởi chạy toàn bộ hệ thống bằng Docker Compose
docker-compose up --build -d

# 3. Theo dõi logs ứng dụng
docker-compose logs -f backend
```

Hệ thống sẽ tự động khởi tạo:
- **Nginx Reverse Proxy** tại cổng `80`
- **FastAPI Backend Service** tại cổng `8000`
- **PostgreSQL 15 Database** tại cổng `5432`
- **Redis 7 Cache Server** tại cổng `6379`

Để dừng ứng dụng:
```bash
docker-compose down
```

---

## Cấu Hình Biến Môi Trường (.env)

Nội dung chuẩn của tệp `backend/.env`:

```ini
# --- Cấu hình Nhà cung cấp AI ---
# Khóa chính Google Gemini (Được ưu tiên cao nhất)
GEMINI_API_KEY=your_primary_gemini_api_key_here

# Khóa dự phòng Google Gemini (Tự động kích hoạt khi khóa chính hết quota/token)
GEMINI_API_KEY_BACKUP=your_backup_gemini_api_key_here

# Khóa OpenAI dự phòng (Tùy chọn fallback)
OPENAI_API_KEY=

# --- Cấu hình Cơ sở dữ liệu ---
# Mặc định sử dụng SQLite cục bộ (Zero-config)
DATABASE_URL=sqlite:///./expense_db.sqlite

# Nếu sử dụng PostgreSQL:
# DATABASE_URL=postgresql://expense_admin:expense_pass@localhost:5432/expenseai

# --- Khóa bảo mật & Phiên làm việc (JWT) ---
SECRET_KEY=generate_a_strong_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# --- Cấu hình Bộ nhớ đệm (Redis) ---
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=false

# --- Môi trường thực thi ---
ENVIRONMENT=development
```

> **LƯU Ý BẢO MẬT QUAN TRỌNG:**
> File `backend/.env` chứa các API Key riêng tư của bạn và đã được cấu hình trong `.gitignore`. **TUYỆT ĐỐI KHÔNG** chia sẻ hoặc commit file `.env` lên GitHub hay bất kỳ kho mã nguồn công khai nào.

---

## Chạy Kiểm Thử Tự Động (Automated Testing)

Toàn bộ hệ thống kiểm thử tự động được thiết kế độc lập, tự động giả lập mock keys trong môi trường CI mà không tốn chi phí gọi API ngoài:

```bash
# Chuyển vào thư mục backend và chạy Pytest
cd backend
python -m pytest -q
```

### Kết quả kiểm thử toàn diện (87/87 tests passed):

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: ExpenseAI
collected 87 items

backend/tests/test_agent_memory.py .                                    [  1%]
backend/tests/test_ai_and_deduplication.py ......                       [  8%]
backend/tests/test_api.py ....................................          [ 49%]
backend/tests/test_budgets.py .....                                     [ 55%]
backend/tests/test_export.py .                                          [ 56%]
backend/tests/test_feedback.py .......                                  [ 64%]
backend/tests/test_gemini_failover.py .....                             [ 70%]
backend/tests/test_pentest_hardening.py ..........                      [ 81%]
backend/tests/test_qa_qc_verification.py ...........                    [ 94%]
backend/tests/test_security_fixes.py .....                              [100%]

============================== 87 passed in 19.64s ==============================
```

- **100% Passed (87/87 bài test):** Kiểm định toàn diện logic nghiệp vụ, quản lý ngân sách, chống trùng lặp dữ liệu, xác thực phân quyền RBAC, phòng thủ tấn công xâm nhập (Pentest Hardening), kiểm tra tiêu chuẩn QA/QC giao diện và cơ chế xoay vòng đa khóa Multi-Key Failover.

---

## Tài Liệu API (Swagger / OpenAPI)

Sau khi khởi chạy ứng dụng, bạn có thể kiểm thử toàn bộ API trực tiếp tại:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

| Nhóm Chức Năng | Giao Thức | Endpoint | Mô Tả Nghiệp Vụ |
|:---|:---:|:---|:---|
| **Xác thực** | `POST` | `/api/auth/register` | Đăng ký tài khoản với mật khẩu chuẩn OWASP |
| | `POST` | `/api/auth/login` | Đăng nhập an toàn, thiết lập HttpOnly JWT Cookie |
| | `POST` | `/api/auth/logout` | Đăng xuất và xóa bỏ Cookie phiên làm việc |
| **Giao dịch** | `GET` | `/api/transactions/` | Lấy danh sách giao dịch (hỗ trợ tìm kiếm, lọc) |
| | `POST` | `/api/transactions/` | Thêm giao dịch (Tự động kích hoạt AI phân loại) |
| | `POST` | `/api/transactions/upload-receipt` | Tải ảnh hóa đơn để quét OCR và trích xuất dữ liệu |
| **Ngân sách** | `GET` | `/api/budgets/` | Lấy danh sách ngân sách và tiến độ chi tiêu theo danh mục |
| | `POST` | `/api/budgets/` | Thiết lập hoặc cập nhật hạn mức ngân sách theo tháng |
| | `DELETE`| `/api/budgets/{id}` | Xóa bỏ hạn mức ngân sách |
| **AI Thông Minh**| `POST` | `/api/advice/` | Nhận lời khuyên tài chính theo quy tắc 50/30/20 |
| | `POST` | `/api/advice/chat` | Trò chuyện trực tiếp với AI trợ lý tài chính |
| | `POST` | `/api/behavior/` | Phân tích thói quen và xu hướng chi tiêu bất thường |
| **Phản hồi** | `GET` | `/api/feedback/` | Lấy phản hồi người dùng (Role-based Authorization) |
| | `POST` | `/api/feedback/` | Gửi phản hồi kèm bảo vệ chống tấn công CSRF |

---

## Cam Kết An Toàn & Bảo Mật (Secret Safety)

Dự án ExpenseAI áp dụng các nguyên tắc phòng vệ nghiêm ngặt:
1. **Secret Scanning:** Tự động loại trừ `.env`, file database SQLite và các tệp tạm thời khỏi Git tracking.
2. **Key Masking:** Không hiển thị đầy đủ chuỗi ký tự API Key trong logs hệ thống (chỉ hiển thị dưới dạng rút gọn ví dụ `AIzaSy...4xyz`).
3. **Double Fallback:** Trong trường hợp toàn bộ API bên ngoài bị gián đoạn, hệ thống vẫn duy trì hoạt động 100% nhờ bộ động cơ quy tắc tài chính nội bộ.
4. **Automated CI Security Gate:** Pipeline tích hợp kiểm tra an ninh Trivy tự động trên mỗi lần push mã nguồn lên GitHub.

---

## Tác Giả & Bản Quyền

- **Nhóm Phát Triển:** Nhóm 02 — ExpenseAI Core Engineering Team
- **Giấy Phép:** Phân phối theo giấy phép [MIT License](LICENSE).
