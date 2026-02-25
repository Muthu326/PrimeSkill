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

# Sample: FAST CE SCALP
scalp_ce_msg = (
    "⚡ *RAPID SCALP ALERT (CE)*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `RELIANCE`\n"
    "🎯 *STRIKE*: `3120 CE` (ATM)\n"
    "💰 *Entry*: `₹42.50`\n"
    "🛑 *Stop Loss*: `₹38.25` (Tight)\n"
    "🔥 *Confidence*: `78%` (Vol Spike)\n"
    "✅ *Target*: `₹46.75` (Quick Exit)\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    "🏛️ [Monitor Terminal](https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=1b6cc4f3-19d7-4434-a066-c977121227fa&redirect_uri=http://localhost:8501)"
)

# Sample: FAST PE SCALP
scalp_pe_msg = (
    "📉 *RAPID SCALP ALERT (PE)*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `HDFCBANK`\n"
    "🎯 *STRIKE*: `1780 PE` (ATM)\n"
    "💰 *Entry*: `₹24.80`\n"
    "🛑 *Stop Loss*: `₹22.30` (Tight)\n"
    "🔥 *Confidence*: `82%` (Breakdown)\n"
    "✅ *Target*: `₹27.30` (Quick Exit)\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    "🏛️ [Monitor Terminal](https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=1b6cc4f3-19d7-4434-a066-c977121227fa&redirect_uri=http://localhost:8501)"
)

print(f"Sending Scalp CE Alert: {send_telegram(scalp_ce_msg)}")
print(f"Sending Scalp PE Alert: {send_telegram(scalp_pe_msg)}")
