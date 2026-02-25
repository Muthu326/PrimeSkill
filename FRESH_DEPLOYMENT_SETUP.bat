@echo off
title 🚀 FRESH GITHUB DEPLOYMENT
cd /d "%~dp0"

echo ==========================================
echo 🧼 CLEANING & RESETTING GIT HISTORY
echo ==========================================
echo.

:: 1. Remove old Git if exists
if exist .git (
    echo 🗑️ Removing existing Git history...
    rd /s /q .git
)

:: 2. Initialize Fresh Git
echo 🆕 Initializing fresh repository...
git init

:: 3. Add Files
echo 📝 Adding cleaned files...
git add .

:: 4. Commit
echo 💾 Creating fresh commit...
git commit -m "🚀 Fresh Deployment v3.0 - Clean Stable Build"

echo.
echo ==========================================
echo 🛰️ CONNECT TO YOUR GITHUB
echo ==========================================
echo.
set /p "repo_url=Paste your GitHub Repository URL (e.g., https://github.com/user/PrimeSkill.git): "

if "%repo_url%"=="" (
    echo ❌ No URL entered. Skipping remote setup.
) else (
    git remote add origin %repo_url%
    echo ⬆️ Pushing to GitHub (Force Overwrite)...
    git branch -M main
    git push -u origin main --force
    echo.
    echo ✅ SUCCESS! Your GitHub is now "Fresh" and matches your PC.
)

echo.
echo ==========================================
echo 🌐 NEXT STEPS:
echo 1. Go to share.streamlit.io
2. Delete your old app if it exists.
3. Click "Create app" and select this fresh repository.
echo ==========================================
pause
