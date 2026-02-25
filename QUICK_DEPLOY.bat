@echo off
REM ============================================
REM Quick Deploy - Update GitHub & Streamlit
REM Prime Skill Development - Marsh Muthu 326
REM ============================================

cd /d "%~dp0"

echo.
echo ========================================
echo   QUICK UPDATE - Push Changes to GitHub
echo ========================================
echo.

REM Check if Git repo exists
if not exist ".git" (
    echo [ERROR] No Git repository found!
    echo.
    echo Please run DEPLOY_TO_STREAMLIT.bat first to set up deployment.
    pause
    exit /b 1
)

echo [1/3] Adding all changed files...
git add .

echo.
echo [2/3] Creating commit...
set /p commit_msg="Enter commit message: "
if "%commit_msg%"=="" set commit_msg=Update code

git commit -m "%commit_msg%"

echo.
echo [3/3] Pushing to GitHub...
git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Changes pushed to GitHub
    echo ========================================
    echo.
    echo Streamlit Cloud will automatically redeploy your app
    echo in 1-2 minutes.
    echo.
    echo Check your app at: https://YOUR_APP_NAME.streamlit.app
    echo.
) else (
    echo.
    echo [ERROR] Push failed!
    echo Try running: git push
    echo.
)

pause
