@echo off
echo ========================================
echo 셀라앙상블 찬양단 서버 배포 스크립트
echo ========================================
echo.

echo 1. 현재 서버 프로세스 종료 중...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo 2. 배포할 파일 목록:
echo    - app.py
echo    - music.html
echo    - admin.html
echo    - data/ 폴더
echo    - uploads/ 폴더 (필요시)
echo.

echo 3. 서버 재시작 중...
start python app.py

echo.
echo ========================================
echo 배포 완료!
echo 웹사이트: http://localhost:5000
echo ========================================
echo.
echo 다음 단계:
echo 1. 웹사이트 접속 확인
echo 2. 로그인 기능 테스트
echo 3. 음악 업로드 기능 테스트 (관리자 계정)
echo.
pause 