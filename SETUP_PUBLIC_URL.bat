@echo off
title Setup Public URL (ngrok)
cd /d "%~dp0"

echo ==========================================
echo 🌐 PUBLIC URL SETUP GUIDE
echo ==========================================
echo.
echo This guide will help you create a PUBLIC internet URL
echo that can be accessed from ANYWHERE (not just your network)
echo.
echo ==========================================
echo OPTION 1: NGROK (Recommended - Easy Setup)
echo ==========================================
echo.
echo 1. Download ngrok: https://ngrok.com/download
echo 2. Extract ngrok.exe to this folder
echo 3. Create free account at ngrok.com and get auth token
echo 4. Run: ngrok config add-authtoken YOUR_TOKEN
echo.
echo Then run:
echo    ngrok http 8080
echo.
echo You'll get a public URL like:
echo    https://abc123.ngrok-free.app
echo.
echo ==========================================
echo OPTION 2: CLOUDFLARED (Free, No Account)
echo ==========================================
echo.
echo 1. Download cloudflared: https://github.com/cloudflare/cloudflared/releases
echo 2. Extract cloudflared.exe to this folder
echo.
echo Then run:
echo    cloudflared tunnel --url http://localhost:8080
echo.
echo You'll get a public URL like:
echo    https://xyz.trycloudflare.com
echo.
echo ==========================================
echo OPTION 3: STREAMLIT CLOUD (For Full App)
echo ==========================================
echo.
echo Deploy the full Streamlit app to cloud:
echo 1. Push code to GitHub
echo 2. Go to share.streamlit.io
echo 3. Deploy from your repository
echo.
echo See: DEPLOYMENT_GUIDE_STREAMLIT.md for details
echo.
echo ==========================================
echo QUICK START (Recommended):
echo ==========================================
echo.
echo Step 1: Start the viewer server
echo    Double-click: START_VIEWER_SERVER.bat
echo.
echo Step 2: Create public tunnel
echo    Download ngrok, then run:
echo    ngrok http 8080
echo.
echo Step 3: Share the URL!
echo    Copy the https://xxxx.ngrok-free.app URL
echo    Share with anyone - they can view your scans!
echo.
echo ==========================================

pause
