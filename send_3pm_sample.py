
import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={os.getenv('UPSTOX_API_KEY')}&redirect_uri=http://localhost:8501"
SIGNATURE = "👤 *PrimeSkillDevelopment CEO*\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def send_3pm_sample():
    # Simulated 3PM High Conviction Setup
    # Typically 3PM trades use the next expiry for overnight safety
    symbol = "NIFTY 50"
    strike = "22200"
    opt_type = "CE"
    premium = 145.80
    confidence = 96
    target = 210.00
    sl = 110.00
    
    msg = (
        f"🔥 *🟢 LIVE 🏛 3PM POWER CLOSE*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 **ASSET**: `{symbol}`\n"
        f"🎟️ **OPTION**: `{strike} {opt_type}` 🟩\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 **ENTRY**: `₹{premium:.2f}`\n"
        f"🛡️ **STOPLOSS**: `₹{sl:.2f}`\n"
        f"🎯 **TARGET**: `₹{target:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **CONFIDENCE**: `{confidence}%`\n"
        f"⏳ **STATUS**: `Institutional Buy-Side Accumulation`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🚀 *Strategy*: `BTST Opportunity (Next Expiry)`\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    
    print("🚀 Sending 3PM Power Close Sample...")
    success = send_telegram(msg)
    print(f"Result: {success}")

if __name__ == "__main__":
    send_3pm_sample()
