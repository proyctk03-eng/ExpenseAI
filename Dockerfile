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
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port 8000
EXPOSE 8000

# Khởi chạy ứng dụng qua Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
