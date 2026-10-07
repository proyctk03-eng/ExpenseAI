@echo off
chcp 65001 >nul
title EXPENSE AI - DỪNG HỆ THỐNG
cd /d "%~dp0"

echo ========================================================
echo          DỪNG HỆ THỐNG EXPENSE AI WEB APP
echo ========================================================
echo.

set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /R /C:":8000 .*LISTENING"') do (
    echo [INFO] Đang đóng tiến trình PID %%a đang chiếm cổng 8000...
    taskkill /F /PID %%a >nul 2>&1
    set FOUND=1
)

if "%FOUND%"=="1" (
    echo [OK] Đã giải phóng cổng 8000 thành công!
) else (
    echo [INFO] Không tìm thấy tiến trình nào đang chạy trên cổng 8000.
)

echo [OK] Hệ thống ExpenseAI đã dừng hoàn toàn.
echo ========================================================
ping 127.0.0.1 -n 3 >nul
