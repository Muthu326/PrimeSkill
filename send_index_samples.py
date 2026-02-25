import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except Exception as e:
        print(f"Error: {e}")
        return False

# Sample: NIFTY 50 CE Trade Alert
nifty_ce_msg = (
    "🚀 *INDEX POWER TRADE (CE)*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `NIFTY 50`\n"
    "🎯 *STRIKE*: `22200 CE`\n"
    "💰 *Entry*: `₹145.00`\n"
    "🛑 *Stop Loss*: `₹128.00`\n"
    "🔥 *Confidence*: `92%` (Strong Bias)\n"
    "✅ *Target*: `₹185.00`\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    "🏛️ [Monitor Terminal](https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=1b6cc4f3-19d7-4434-a066-c977121227fa&redirect_uri=http://localhost:8501)"
)

# Sample: NIFTY 50 PE Trade Alert
nifty_pe_msg = (
    "🌋 *INDEX POWER TRADE (PE)*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `NIFTY 50`\n"
    "🎯 *STRIKE*: `22100 PE`\n"
    "💰 *Entry*: `₹125.00`\n"
    "🛑 *Stop Loss*: `₹110.00`\n"
    "🔥 *Confidence*: `85%` (Sector Drag)\n"
    "✅ *Target*: `₹160.00`\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    "🏛️ [Monitor Terminal](https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=1b6cc4f3-19d7-4434-a066-c977121227fa&redirect_uri=http://localhost:8501)"
)

print(f"Sending NIFTY CE Alert: {send_telegram(nifty_ce_msg)}")
print(f"Sending NIFTY PE Alert: {send_telegram(nifty_pe_msg)}")
