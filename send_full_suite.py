
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
import urllib.request
import urllib.parse
from scanner_config import *

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("UPSTOX_API_KEY")
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri=http://localhost:8501"
SIGNATURE = f"👤 *PrimeSkillDevelopment CEO*\\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def trigger_full_institutional_summary():
    print("🚀 Triggering Full Institutional Alert Suite...")
    
    # 1. FINAL MARKET PULSE (Pulse Alert Type)
    pulse_msg = (
        "🟢 LIVE 🏛️ *MARKET SENTIMENT PULSE (EOD)*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🕙 **CLOSE TIME**: `{datetime.now().strftime('%H:%M:%S')}`\n"
        "🎭 **BIAS**: `BEARISH REJECTION`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🌎 **GLOBAL CONTEXT**\n"
        "∟ NASDAQ: `-0.45%` 📉\n"
        "∟ S&P 500: `-0.12%` 📉\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📈 **NIFTY 50**\n"
        "∟ PCR: `0.78` (Sell on Rise)\n"
        "∟ OI Status: `Short Build-up` 🔴\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{SIGNATURE}"
    )
    send_telegram(pulse_msg)
    time.sleep(1)

    # 2. TOP INSTITUTIONAL GAINERS (Scanner Results Type)
    gainers_msg = (
        "🚀 *🟢 LIVE 🏛 TOP INSTITUTIONAL MOVERS*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📍 **TOP BULLS** 🟩\n"
        "∟ BPCL: `+3.45%` (Institutional Buy)\n"
        "∟ RELIANCE: `+1.12%` (Heavyweight Support)\n\n"
        "📍 **TOP BEARS** 🟥\n"
        "∟ HDFCBANK: `-1.80%` (Profit Booking)\n"
        "∟ TCS: `-1.25%` (IT Weakness)\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🛡️ **STRATEGY**: `BTST/STBT Identified`\n"
        f"{SIGNATURE}"
    )
    send_telegram(gainers_msg)
    time.sleep(1)

    # 3. MACRO & INDEX BIAS (Macro Alert Type)
    macro_msg = (
        "🏛️ **INSTITUTIONAL MACRO SUMMARY**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📊 **INDIA VIX**: `15.22` (Expanding ⚠️)\n"
        "💼 **FII ACTIVITY**: `Net Sellers (Simulated)`\n"
        "🔄 **SECTOR ROTATION**: `Auto & Energy Strong` 🚀\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🌐 **INDEX BIAS**\n"
        "∟ NIFTY: `Strong Bearish Rejection` 🔴\n"
        "∟ BANKNIFTY: `Volatile Consolidation` 💠\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [OPEN TERMINAL]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(macro_msg)
    
    print("✅ All possible institutional alerts sent to Telegram.")

if __name__ == "__main__":
    trigger_full_institutional_summary()
