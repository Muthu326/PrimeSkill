
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
        "🏛️ **INSTITUTIONAL 3-STAGE WORKFLOW LIVE**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌅 **STAGE 1: PRE-MARKET** (9:00 AM)\n"
        "∟ Gauges Global Sentiment & Gap Probability.\n\n"
        "📊 **STAGE 2: LIVE MARKET** (9:15 AM)\n"
        "∟ Scalping, Breakout & Diamond Grade Entries.\n\n"
        "📉 **STAGE 3: POST-MARKET** (3:45 PM)\n"
        "∟ Supply/Demand Zone Analysis & Order Blocks.\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 **SYNC**: All 51 Nifty Assets + HDFCLIFE Active.\n"
        "🎭 **BIAS**: Dynamic Institution-Grade Engine.\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(msg)
    print("3-Stage Workflow Alert Sent.")
