@echo off
cd /d "%~dp0"
echo 🔄 Starting Upstox Token Refresh Service...
python refresh_upstox_token.py
echo 🏁 Refresh process complete.
pause
