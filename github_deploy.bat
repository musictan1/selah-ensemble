@echo off
echo ========================================
echo 셀라앙상블 찬양단 - GitHub 배포 스크립트
echo ========================================
echo.

echo 1. 현재 변경사항 확인...
git status

echo.
echo 2. 변경사항 스테이징...
git add .

echo.
echo 3. 커밋 메시지 입력:
set /p commit_msg="커밋 메시지를 입력하세요 (기본값: 업데이트): "
if "%commit_msg%"=="" set commit_msg=업데이트

echo.
echo 4. 커밋 생성...
git commit -m "%commit_msg%"

echo.
echo 5. GitHub에 푸시...
git push origin master

echo.
echo ========================================
echo GitHub 배포 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. GitHub 저장소 확인: https://github.com/musictan1/selah-ensemble
echo 2. Netlify/Vercel/Railway에서 자동 배포 확인
echo 3. 웹사이트 접속 테스트
echo.
pause 