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

# Sample 1: Stock Alert
stock_msg = (
    "💎 *DIAMOND PICK*\n"
    "━━━━━━━━━━━━━━\n"
    "📍 *SYMBOL*: `Reliance`\n"
    "🎯 *STRIKE*: `2900 CE`\n"
    "💰 *Entry*: `₹85.40`\n"
    "🛑 *Stop Loss*: `₹76.86`\n"
    "🔥 *Confidence*: `88%`\n"
    "✅ *Target*: `₹102.48`\n"
    "⏳ *Status*: `Active`\n"
    "━━━━━━━━━━━━━━\n"
    "🏛️ [Monitor Terminal](https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=1b6cc4f3-19d7-4434-a066-c977121227fa&redirect_uri=http://localhost:8501)"
)

# Sample 2: Index Bias
index_msg = (
    "🌐 *INDEX BIAS: BANKNIFTY (PE)*\n"
    "Power: `72.4%` \n"
    "Strategy: `Focus on ITM Put Options` \n"
    "Detail: `🔴 HDFCBANK(30%), 🔴 ICICIBANK(18%), 🔴 SBIN(10%)`"
)

# Sample 3: Market Pulse
pulse_msg = (
    "📊 *INSTITUTIONAL MARKET PULSE* 🏛️\n"
    "━━━━━━━━━━━━━━\n"
    "🕙 *Time*: `14:20:05` \n"
    "• Sentiment: `BULLISH` \n"
    "━━━━━━━━━━━━━━\n"
    "📈 *NIFTY 50 (PCR: 1.15)* \n"
    "• CE OI: `4.52 Cr` | PE OI: `5.20 Cr` \n"
    "📈 *BANKNIFTY (PCR: 0.92)* \n"
    "• CE OI: `2.10 Cr` | PE OI: `1.93 Cr` \n"
    "🌐 *OVERALL MARKET VIEW* \n"
    "• PCR: `1.04` 🔥 \n"
    "━━━━━━━━━━━━━━\n"
    "🏛️ [Open Institutional Terminal](https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=1b6cc4f3-19d7-4434-a066-c977121227fa&redirect_uri=http://localhost:8501)"
)

print(f"Sending Stock Alert: {send_telegram(stock_msg)}")
print(f"Sending Index Bias: {send_telegram(index_msg)}")
print(f"Sending Market Pulse: {send_telegram(pulse_msg)}")
