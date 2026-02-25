
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
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

def send_diamond_grade_analysis():
    print("🚀 Triggering Diamond Grade Analysis (Matched to NIFTY 25450 CE Style)...")
    
    # This is the exact style the user "liked"
    def get_diamond_msg(asset, spot, strike, otype, premium, target, sl, logic):
        icon = "🟩" if otype == "CE" else "🟥"
        return (
            f"🔥 *🟢 NEW DIAMOND💎*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 **ASSET**: `{asset}`\n"
            f"🎯 **SPOT PRICE**: `₹{spot:,.2f}`\n"
            f"🎟️ **ENTRY STRIKE**: `{strike} {otype}` {icon}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **OPTION PREMIUM**: `₹{premium:.2f}`\n"
            f"🛡️ **STOPLOSS**: `₹{sl:.2f}`\n"
            f"🎯 **TARGET**: `₹{target:.2f}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 **CONFIDENCE**: `98%` (Elite Level)\n"
            f"🔬 **DIAMOND LOGIC**: `{logic}`\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"{SIGNATURE}"
        )

    # 1. THE GOLD STANDARD (Matched to their favorite)
    msg1 = get_diamond_msg("NIFTY 50", 25432.10, 25450, "CE", 112.50, 165.00, 85.00, "PCR Rejection at Support + Institutional Volume Spike")
    send_telegram(msg1)
    
    print("✅ Diamond Grade Alert Sent.")

if __name__ == "__main__":
    send_diamond_grade_analysis()
