@echo off
title PRIME SKILL - Dashboard
cd /d "%~dp0"

echo ==========================================
echo 🎯 PRIME SKILL DASHBOARD STARTING...
echo ==========================================
echo.
echo Dashboard URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

streamlit run marsh_muthu_326_pro_terminal.py

pause
