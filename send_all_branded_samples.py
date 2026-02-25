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
CEO_SIG = "\n\n👤 *PrimeSkillDevelopment CEO : MuthuKumar krishnan*"

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

# 1. Diamond Stock Pick
diamond_msg = (
    "💎 *DIAMOND PICK*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `RELIANCE`\n"
    "🎯 *STRIKE*: `3000 CE`\n"
    "💰 *Entry*: `₹65.00`\n"
    "🛑 *Stop Loss*: `₹55.00`\n"
    "🔥 *Confidence*: `94%` (Institutional Breakout)\n"
    "✅ *Target*: `₹85.00`\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    f"🏛️ [Monitor Terminal]({AUTH_URL})"
    f"{CEO_SIG}"
)

# 2. NIFTY 50 Index Power Alert
nifty_msg = (
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
    f"🏛️ [Monitor Terminal]({AUTH_URL})"
    f"{CEO_SIG}"
)

# 3. Rapid Scalp Alert
scalp_msg = (
    "⚡ *RAPID SCALP ALERT (CE)*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `TCS`\n"
    "🎯 *STRIKE*: `4100 CE` (ATM)\n"
    "💰 *Entry*: `₹45.50`\n"
    "🛑 *Stop Loss*: `₹41.00` (Tight)\n"
    "🔥 *Confidence*: `82%` (Vol Spike)\n"
    "✅ *Target*: `₹52.00` (Quick Exit)\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    f"🏛️ [Monitor Terminal]({AUTH_URL})"
    f"{CEO_SIG}"
)

# 4. Institutional Market Pulse
pulse_msg = (
    "📊 *INSTITUTIONAL MARKET PULSE* 🏛️\n"
    "━━━━━━━━━━━━━━\n"
    "🕙 *Time*: `14:26:00` \n"
    "• Sentiment: `BULLISH` \n"
    "━━━━━━━━━━━━━━\n"
    "📈 *NIFTY 50 (PCR: 1.15)* \n"
    "• CE OI: `4.52 Cr` | PE OI: `5.20 Cr` \n"
    "📈 *BANKNIFTY (PCR: 0.92)* \n"
    "• CE OI: `2.10 Cr` | PE OI: `1.93 Cr` \n"
    "🌐 *OVERALL MARKET VIEW* \n"
    "• PCR: `1.04` 🔥 \n"
    "━━━━━━━━━━━━━━\n"
    f"🏛️ [Open Institutional Terminal]({AUTH_URL})"
    f"{CEO_SIG}"
)

print(f"Sending Branded Diamond Alert: {send_telegram(diamond_msg)}")
print(f"Sending Branded Nifty Alert: {send_telegram(nifty_msg)}")
print(f"Sending Branded Scalp Alert: {send_telegram(scalp_msg)}")
print(f"Sending Branded Market Pulse: {send_telegram(pulse_msg)}")
