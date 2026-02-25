@echo off
REM Test Real Option Pricing & Send Telegram Alert
cd /d "%~dp0"

echo.
echo ========================================
echo   REAL OPTION PRICING TEST
echo ========================================
echo.

python test_real_option_price.py

echo.
pause
