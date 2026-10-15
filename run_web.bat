@echo off
chcp 65001 >nul
title EXPENSE AI - KHỞI ĐỘNG HỆ THỐNG
cd /d "%~dp0"

echo ========================================================
echo        KHỞI ĐỘNG HỆ THỐNG EXPENSE AI WEB APP
echo ========================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Môi trường ảo chưa được cài đặt. Đang tự động gọi install.bat...
    call install.bat
    if not exist "venv\Scripts\python.exe" (
        echo [LỖI] Cài đặt thất bại. Vui lòng kiểm tra lại.
        pause
        exit /b 1
    )
)

:: Kiểm tra tính toàn vẹn của các thư viện phụ thuộc
echo [INFO] Đang kiểm tra các thư viện phụ thuộc...
venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, pydantic, jinja2, jose, slowapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [CẢNH BÁO] Phát hiện thiếu một số thư viện Python cần thiết.
    echo [INFO] Đang tự động tiến hành cài đặt từ backend\requirements.txt...
    venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo [LỖI] Quá trình cài đặt thư viện không thành công. Vui lòng kiểm tra kết nối mạng.
        pause
        exit /b 1
    )
    echo [OK] Đã cài đặt hoàn tất các thư viện cần thiết!
) else (
    echo [OK] Toàn bộ thư viện phụ thuộc đã sẵn sàng.
)
echo.

:: Kiểm tra xem cổng 8000 đã có tiến trình nào đang lắng nghe chưa
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [THÔNG BÁO] Hệ thống ExpenseAI hiện ĐANG CHẠY trên cổng 8000!
    echo [INFO] Đang mở trình duyệt web: http://127.0.0.1:8000
    start http://127.0.0.1:8000
    echo.
    echo Để tắt hoặc khởi động lại hệ thống, bạn hãy chạy file "stop_web.bat".
    echo ========================================================
    pause
    exit /b 0
)

echo [OK] Đang khởi chạy máy chủ Uvicorn trên cổng 8000...
echo [INFO] Địa chỉ Web: http://127.0.0.1:8000
echo [INFO] Tài liệu API: http://127.0.0.1:8000/docs
echo [INFO] Nhấn Ctrl+C trong cửa sổ này để dừng server.
echo.

ping 127.0.0.1 -n 2 >nul
start http://127.0.0.1:8000
cd backend
..\venv\Scripts\python.exe -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
pause
