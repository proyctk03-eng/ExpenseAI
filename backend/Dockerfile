# Sử dụng Python 3.11 slim theo yêu cầu
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Khắc phục lỗi timezone & cài đặt các thư viện hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Tạo non-root user (appuser)
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy toàn bộ mã nguồn vào container và gán quyền
COPY --chown=appuser:appgroup . .

# Chuyển sang user non-root
USER appuser

# Chuyển WORKDIR vào backend để chạy app
WORKDIR /app/backend

# Expose port 8000
EXPOSE 8000

# Khởi chạy ứng dụng qua Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
