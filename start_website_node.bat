@echo off
echo Starting Sela Ensemble Website...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Starting Node.js web server...
    start /B npx http-server
    timeout /t 2 >nul
    start http://localhost:8080
) else (
    echo Node.js is not installed. Please install Node.js and try again.
    pause
    exit
)

echo.
echo Website is running at http://localhost:8080
echo Press Ctrl+C in this window to stop the server
echo.
pause 