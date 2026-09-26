@echo off
chcp 65001 >nul
echo ========================================================
echo        CÀI ĐẶT MÔI TRƯỜNG EXPENSE AI
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Đang kiểm tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LỖI] Không tìm thấy Python. Vui lòng cài đặt Python và thêm vào PATH!
    pause
    exit /b 1
)

echo [2/3] Đang tạo môi trường ảo (venv)...
if not exist venv (
    python -m venv venv
    echo Đã tạo thư mục venv.
) else (
    echo Thư mục venv đã tồn tại, bỏ qua bước tạo.
)

echo [3/3] Đang cài đặt các thư viện từ backend\requirements.txt...
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt

echo.
echo [OK] Cài đặt hoàn tất! Bạn có thể chạy run_web.bat để khởi động server.
pause
