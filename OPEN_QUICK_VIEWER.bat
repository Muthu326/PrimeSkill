@echo off
title Quick Scan Viewer
cd /d "%~dp0"

echo ==========================================
echo 🚀 Opening Quick Scan Viewer...
echo ==========================================
echo.
echo This is a FAST viewer that loads scan results
echo instantly from cached JSON data!
echo.
echo Viewer URL: file:///%~dp0static\scan_viewer.html
echo.

start "" "%~dp0static\scan_viewer.html"

echo.
echo ✅ Quick Viewer opened in your browser!
echo.
timeout /t 3
