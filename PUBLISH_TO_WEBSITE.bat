@echo off
title 🚀 PUBLISH TO STREAMLIT CLOUD
cd /d "%~dp0"

echo ==========================================
echo 🚀 SYNCING LATEST CHANGES TO WEBSITE
echo ==========================================
echo.

:: 1. Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed! 
    echo Please install Git to use automated updates.
    pause
    exit /b
)

:: 2. Automated Git Push
echo 📝 Staging all changes...
git add .

echo 💾 Committing updates...
set "commit_msg="
set /p "commit_msg=Enter update message (or press enter for 'Auto Update'): "
if "%commit_msg%"=="" (
    git commit -m "Auto Update: %date% %time%"
) else (
    git commit -m "%commit_msg%"
)

echo 🛰️ Sending to GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ PUSH FAILED! 
    echo Make sure you have connected your GitHub repository.
    pause
    exit /b
)

echo.
echo ==========================================
echo ✅ SUCCESS! Website is now updating.
echo 🌐 Check: https://share.streamlit.io
echo ==========================================
echo.
timeout /t 5
