
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

def send_live_call_suite_v2():
    print("🚀 Triggering Corrected Live Call Suite (Spot/Strike/Premium Fixed)...")
    
    # Updated Alert Template
    def get_alert_msg(tag, asset, spot, strike, otype, premium, target, sl, confidence, status):
        icon = "🟩" if otype == "CE" else "🟥"
        return (
            f"🔥 *🟢 NEW {tag}*\n"
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

    # 1. DIAMOND CE
    msg1 = get_alert_msg("DIAMOND💎", "RELIANCE", 2985.40, 3000, "CE", 42.15, 65.00, 32.00, 95, "Active")
    send_telegram(msg1)
    time.sleep(1)

    # 2. MEGA CONVICTION PE
    msg2 = get_alert_msg("🔥 MEGA CONVICTION 🔥", "NIFTY 50", 25342.10, 25350, "PE", 128.50, 190.00, 105.00, 98, "Institutional Entry")
    send_telegram(msg2)
    time.sleep(1)

    # 3. STOCK BREAKOUT
    msg3 = get_alert_msg("STOCK MOVE🚀", "INFY", 1920.00, 1940, "CE", 22.10, 35.00, 16.00, 88, "Volume Spike")
    send_telegram(msg3)
    
    print("✅ Corrected Suite Triggered.")

if __name__ == "__main__":
    send_live_call_suite_v2()
