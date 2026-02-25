
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

def send_exact_verify_alert():
    print("🚀 Triggering Exact Data Verification Alert...")
    
    title = "🔥 *🟢 NEW DIAMOND💎*"
    asset = "NIFTY 50"
    spot = 25345.10
    strike = "25400"
    otype = "PE"
    premium = 132.45
    sl = 105.00
    target = 195.00
    confidence = 95
    status = "Active"
    icon = "🟥"

    msg = (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 **ASSET**: `{asset}`\n"
        f"🎯 **SPOT PRICE**: `₹{spot:,.2f}`\n"
        f"🎟️ **ENTRY STRIKE**: `{strike} {otype}` {icon}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 **OPTION PREMIUM**: `₹{premium:.2f}`\n"
        f"🛡️ **STOPLOSS**: `₹{sl:.2f}`\n"
        f"🎯 **TARGET**: `₹{target:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **CONFIDENCE**: `{confidence}%`\n"
        f"⏳ **STATUS**: `{status}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )

    send_telegram(msg)
    print("✅ Exact alert sent.")

if __name__ == "__main__":
    send_exact_verify_alert()
