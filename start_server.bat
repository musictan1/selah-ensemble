@echo off
cd /d %~dp0
echo 셀라앙상블 찬양단 서버를 시작합니다...
echo 서버가 시작되면 자동으로 브라우저가 열립니다.
echo 서버를 종료하려면 이 창을 닫으세요.
echo.

REM 파이썬이 설치되어 있는지 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다. Python을 설치하고 다시 실행해주세요.
    echo Python 다운로드: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 필요한 패키지 설치 확인
echo 필요한 패키지 설치 확인 중...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask 설치가 필요합니다. install_requirements.bat 파일을 실행해주세요.
    pause
    exit /b 1
)

REM 필요한 디렉토리 생성
echo 필요한 디렉토리 생성 중...
mkdir uploads\music\ai 2>nul
mkdir uploads\music\mr 2>nul
mkdir uploads\music\live 2>nul
mkdir uploads\scores 2>nul
mkdir uploads\videos 2>nul
mkdir uploads\posts 2>nul
mkdir data 2>nul
mkdir flask_session 2>nul
mkdir IMAGES 2>nul
mkdir css 2>nul
mkdir js 2>nul

REM 데이터 파일 초기화
echo 기본 데이터 파일 확인 중...
if not exist data\users.json (
    echo [] > data\users.json
    echo 사용자 파일 생성 완료: data\users.json
)
if not exist data\posts.json (
    echo [] > data\posts.json
    echo 게시글 파일 생성 완료: data\posts.json
)
if not exist data\data.json (
    echo {"music": {"ai": [], "mr": [], "live": []}, "scores": [], "videos": []} > data\data.json
    echo 데이터 파일 생성 완료: data\data.json
)

echo 모든 준비가 완료되었습니다. 서버를 시작합니다...
echo.

start http://localhost:5000
python app.py
pause 