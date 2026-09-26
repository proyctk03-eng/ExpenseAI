@echo off
chcp 65001 >nul
echo ========================================================
echo        KHỞI ĐỘNG HỆ THỐNG EXPENSE AI WEB APP
echo ========================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Môi trường ảo chưa được cài đặt. Đang tự động gọi install.bat...
    call install.bat
    if not exist "venv\Scripts\python.exe" (
        echo [LỖI] Cài đặt thất bại. Vui lòng kiểm tra lại.
        pause
        exit /b 1
    )
)

echo [OK] Đang khởi chạy máy chủ Uvicorn...
echo [INFO] Địa chỉ Web: http://127.0.0.1:8000
echo [INFO] Tài liệu API: http://127.0.0.1:8000/docs
echo [INFO] Nhấn Ctrl+C trong cửa sổ này để tắt server.
echo.

timeout /t 2 >nul
start http://127.0.0.1:8000
cd backend
..\venv\Scripts\python.exe -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
pause
