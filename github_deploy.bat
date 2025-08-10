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
echo 3. Creating commit with timestamp...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"
git commit -m "Auto update: %datestamp%"

echo.
echo 4. Pushing to GitHub...
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
echo Press any key to exit...
pause >nul 