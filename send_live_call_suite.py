
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("UPSTOX_API_KEY")
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri=http://localhost:8501"
SIGNATURE = f"👤 *PrimeSkillDevelopment CEO*\\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    import urllib.request
    import urllib.parse
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def send_live_call_suite():
    print("🚀 Triggering Live Call Suite (CE/PE Variations)...")
    
    # 1. DIAMOND CE ALERT
    diamond_ce = (
        "💎 *🟢 LIVE DIAMOND SIGNAL*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📍 **ASSET**: `RELIANCE`\n"
        "🎟️ **OPTION**: `3000 CE` 🟩\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 **ENTRY**: `₹45.50`\n"
        "🛡️ **STOPLOSS**: `₹38.00`\n"
        "🎯 **TARGET**: `₹68.00`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📊 **CONFIDENCE**: `92%` (Supertrend Confirmed)\n"
        "⚡ **MOMENTUM**: `High Velocity` 🚀\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [OPEN TERMINAL]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(diamond_ce)
    time.sleep(1.5)

    # 2. MEGA CONVICTION PE ALERT
    mega_pe = (
        "🔥 *🟢 MEGA CONVICTION 🔥 ALERT*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📍 **ASSET**: `NIFTY 50`\n"
        "🎟️ **OPTION**: `25400 PE` 🟥\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 **ENTRY**: `₹125.00`\n"
        "🛡️ **STOPLOSS**: `₹105.00`\n"
        "🎯 **TARGET**: `₹195.00`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📊 **CONFIDENCE**: `98%` (FII Exit Identified)\n"
        "☢️ **OI STATUS**: `Short Build-up Peak` 🩸\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(mega_pe)
    time.sleep(1.5)

    # 3. ⚡ INSTANT BREAKOUT PE
    instant_pe = (
        "⚡ *🟢 LIVE INSTANT BREAKOUT*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📍 **ASSET**: `HDFCBANK`\n"
        "🎟️ **OPTION**: `1680 PE` 🟥\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 **ENTRY**: `₹22.30`\n"
        "🛡️ **STOPLOSS**: `₹18.00`\n"
        "🎯 **TARGET**: `₹35.00`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📊 **CONFIDENCE**: `88%` (Volume Spike Detected)\n"
        "📍 **ALERT**: `Critical Level Breach` ⚠️\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(instant_pe)
    time.sleep(1.5)

    # 4. TOP PICK CE (Standard)
    top_pick = (
        "🏆 *🟢 LIVE TOP PICK ALERT*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📍 **ASSET**: `SBIN`\n"
        "🎟️ **OPTION**: `900 CE` 🟩\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💰 **ENTRY**: `₹18.90`\n"
        "🛡️ **STOPLOSS**: `₹15.00`\n"
        "🎯 **TARGET**: `₹28.00`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📊 **CONFIDENCE**: `75%` (MACD Crossover)\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(top_pick)
    
    print("✅ Live Call Suite Triggered.")

if __name__ == "__main__":
    send_live_call_suite()
