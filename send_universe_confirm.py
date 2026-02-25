
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

if __name__ == "__main__":
    msg = (
        "🏛️ **DIAMOND UNIVERSE EXPANSION COMPLETED**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📡 **SCAN SCOPE**: All 50 Nifty Constituents ✅\n"
        "🛡️ **PRIORITY STOCK**: `HDFCLIFE` Added 🟩\n"
        "🎭 **LOGIC SYNC**: `Diamond Grade (Accurate Pickup)`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📈 **WHAT'S NEW**: \n"
        "1. Every Nifty 50 stock is now being scanned for **Institutional Rejection** signals.\n"
        "2. All alerts now include **ITM Strike Shift** for Delta advantage.\n"
        "3. **HDFCLIFE** is officially integrated into the high-conviction monitoring engine.\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 **STATUS**: Backend Restarted & Live Synchronization Active.\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(msg)
    print("Universe update alert sent.")
