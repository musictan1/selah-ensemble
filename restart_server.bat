@echo off
echo Stopping Python server processes...
taskkill /F /IM python.exe /T
timeout /t 2 /nobreak >nul
echo Starting server...
start python app.py
echo Server restarted successfully! 