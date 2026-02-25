@echo off
title Quick Scan Viewer Server
cd /d "%~dp0"

echo ==========================================
echo 🚀 Starting Quick Scan Viewer Server
echo ==========================================
echo.
echo This will start a web server that allows you to:
echo - Access the viewer from any device on your network
echo - Share the URL with others
echo - Use with ngrok for internet access
echo.

python serve_viewer.py

pause
