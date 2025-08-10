@echo off
chcp 65001 >nul
echo ========================================
echo Selah Ensemble - GitHub Deploy Script
echo ========================================
echo.

echo 1. Checking current changes...
git status

echo.
echo 2. Staging changes...
git add .

echo.
echo 3. Enter commit message:
set /p commit_msg="Enter commit message (default: update): "
if "%commit_msg%"=="" set commit_msg=update

echo.
echo 4. Creating commit...
git commit -m "%commit_msg%"

echo.
echo 5. Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo GitHub deployment completed!
echo ========================================
echo.
echo Next steps:
echo 1. Check GitHub repository: https://github.com/musictan1/selah-ensemble
echo 2. Verify auto-deploy on Netlify/Vercel/Railway
echo 3. Test website access
echo.
pause 