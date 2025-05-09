@echo off
echo Starting Sela Ensemble Website...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Starting Python web server...
    start /B python -m http.server 8000
    timeout /t 2 >nul
    start http://localhost:8000
) else (
    echo Python is not installed. Please install Python and try again.
    pause
    exit
)

echo.
echo Website is running at http://localhost:8000
echo Press Ctrl+C in this window to stop the server
echo.
pause 