@echo off
REM ATM Options Scanner - Top 5 CE/PE Finder
cd /d "%~dp0"

echo.
echo ========================================
echo   ATM OPTIONS SCANNER
echo   Scanning 180+ F&O Stocks
echo ========================================
echo.

python services\atm_option_scanner.py

echo.
pause
