# ==========================================
# STAGE 1: BUILDER (Tải và cài đặt thư viện)
# ==========================================
FROM python:3.10-slim as builder

WORKDIR /app

# Khởi tạo môi trường ảo (Virtual Environment)
RUN python -m venv /opt/venv
# Kích hoạt venv
ENV PATH="/opt/venv/bin:$PATH"

# Cài đặt thư viện
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 2: FINAL (Đóng gói Image cuối cùng)
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# Copy toàn bộ venv từ stage builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# TẠO USER NON-ROOT
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Copy mã nguồn dự án
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini .


# HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

EXPOSE 8000

# Lệnh khởi động
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
