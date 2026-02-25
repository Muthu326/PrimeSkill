
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

def send_3pm_accuracy_analysis():
    print("🚀 Triggering Universal 3PM Accurate Pickup Analysis...")
    
    # 🏛 Template for the new Accurate Pickup
    def get_accuracy_msg(tag, asset, spot, strike, otype, premium, logic_reason):
        icon = "🟩" if otype == "CE" else "🟥"
        return (
            f"🏛️ *🟢 LIVE ACCURATE PICKUP ({tag})*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 **ASSET**: `{asset}`\n"
            f"🎯 **SPOT PRICE**: `₹{spot:,.2f}`\n"
            f"🎟️ **ENTRY STRIKE**: `{strike} {otype}` {icon}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **OPTION PREMIUM**: `₹{premium:.2f}`\n"
            f"🛡️ **STRATEGY**: `3PM Institutional Accurate Pickup`\n"
            f"🔬 **LOGIC**: `{logic_reason}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ **DELTA GAIN**: `+0.65` (High Conviction ITM)\n"
            f"🚀 **CONVICTION**: `Institutional Grade` 💎\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"{SIGNATURE}"
        )

    # 1. NIFTY Analysis (Applying 3PM Accuracy to Nifty)
    msg1 = get_accuracy_msg("NIFTY 50", "NIFTY 50", 25345.00, 25400, "PE", 132.40, "PCR < 1.1 + Strong Bearish Rejection at Resistance")
    send_telegram(msg1)
    time.sleep(1.5)

    # 2. HDFCBANK Analysis (Applying 3PM Accuracy to Stock)
    msg2 = get_accuracy_msg("STOCK ALPHA", "HDFCBANK", 1720.50, 1740, "PE", 24.15, "Institutional Sell-side Pressure + Vol Spike")
    send_telegram(msg2)
    time.sleep(1.5)

    # 3. RELIANCE Analysis (Applying 3PM Accuracy to Heavyweight)
    msg3 = get_accuracy_msg("MEGA MOVE", "RELIANCE", 2988.00, 2960, "CE", 48.90, "Bullish Accumulation + ITM Gap Pickup")
    send_telegram(msg3)
    
    print("✅ All-Asset Analysis Sent.")

if __name__ == "__main__":
    send_3pm_accuracy_analysis()
