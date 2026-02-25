@echo off
title MARSH MUTHU 326 ENGINE
cd /d "%~dp0"

echo ==========================================
echo 🎯 PRIME SKILL | ULTIMATE ENGINE START
echo ==========================================
echo.
echo [1] Starting AM BACKEND SCANNER (5-Min Loop)...
start "AM SCANNER" cmd /k "python am_backend_scanner.py"

echo.
echo [2] Starting DASHBOARD (Visual Interface)...
timeout /t 3 >nul
streamlit run marsh_muthu_326_pro_terminal.py

pause
