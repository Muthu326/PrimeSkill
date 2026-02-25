@echo off
REM ============================================
REM Streamlit Cloud Deployment Helper
REM Prime Skill Development - Marsh Muthu 326
REM ============================================

cd /d "%~dp0"

echo.
echo ========================================
echo   STREAMLIT CLOUD DEPLOYMENT HELPER
echo ========================================
echo.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed!
    echo.
    echo Please download Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)

echo [Step 1/5] Checking Git repository...
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo Git repository created!
) else (
    echo Git repository already exists.
)

echo.
echo [Step 2/5] Preparing files for deployment...
git add .
git status

echo.
echo [Step 3/5] Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update for Streamlit Cloud deployment

git commit -m "%commit_msg%"

echo.
echo [Step 4/5] GitHub Repository Setup
echo.
echo IMPORTANT: You need a GitHub repository to deploy to Streamlit Cloud.
echo.
echo If you DON'T have a GitHub repo yet:
echo   1. Go to https://github.com/new
echo   2. Create a new repository (name it: PrimeSkill)
echo   3. Copy the repository URL
echo.
echo Example URL: https://github.com/YOUR_USERNAME/PrimeSkill.git
echo.

set /p github_url="Paste your GitHub repository URL (or press Enter to skip): "

if not "%github_url%"=="" (
    echo.
    echo Setting up remote repository...
    git remote remove origin 2>nul
    git remote add origin %github_url%
    git branch -M main
    
    echo.
    echo Pushing code to GitHub...
    git push -u origin main
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo   SUCCESS! Code pushed to GitHub!
        echo ========================================
        echo.
    ) else (
        echo.
        echo [WARNING] Push failed. You may need to authenticate with GitHub.
        echo Try running: git push -u origin main
        echo.
    )
) else (
    echo Skipping GitHub push.
)

echo.
echo [Step 5/5] Final Steps - Deploy to Streamlit Cloud
echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Go to: https://share.streamlit.io
echo 2. Sign in with your GitHub account
echo 3. Click "New app"
echo 4. Select your repository: PrimeSkill
echo 5. Branch: main
echo 6. Main file: marsh_muthu_326_pro_terminal.py
echo.
echo 7. Click "Advanced settings"
echo 8. Add your secrets in "Secrets" section:
echo.
echo    TELEGRAM_TOKEN = "your_bot_token_here"
echo    TELEGRAM_CHAT_ID = "your_chat_id_here"
echo.
echo 9. Click "Deploy!"
echo.
echo Your app will be live at:
echo https://YOUR_APP_NAME.streamlit.app
echo.
echo ========================================
echo.

pause
