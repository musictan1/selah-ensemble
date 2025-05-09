@echo off
echo 셀라앙상블 찬양단 웹사이트 필수 패키지 설치를 시작합니다...
echo.

python -m pip install --upgrade pip
pip install flask flask-cors flask-session werkzeug

echo.
echo 패키지 설치가 완료되었습니다.
echo 이제 start_server.bat 파일을 실행하여 서버를 시작할 수 있습니다.
echo.
pause 