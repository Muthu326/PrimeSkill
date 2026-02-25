
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
CEO_SIG = "\n\n👤 *PrimeSkillDevelopment CEO*\n∟ *MuthuKumar krishnan*"
LIVE_TAG = "🟢 LIVE"

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

def get_premium_msg(symbol, strike, opt_type, entry, sl, target, conf, tag="DIAMOND PICK"):
    icon = "🟩" if opt_type == "CE" else "🟥"
    return (
        f"🔥 *{LIVE_TAG} NEW {tag}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 **ASSET**: `{symbol}`\n"
        f"🎟️ **OPTION**: `{strike} {opt_type}` {icon}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 **ENTRY**: `₹{entry:.2f}`\n"
        f"🛡️ **STOPLOSS**: `₹{sl:.2f}`\n"
        f"🎯 **TARGET**: `₹{target:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **CONFIDENCE**: `{conf}%`\n"
        f"⏳ **STATUS**: `Active`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})"
        f"{CEO_SIG}"
    )

# 1. Simulate 5 Random NIFTY 50 Stock Alerts
stocks_to_send = [
    {"sym": "RELIANCE", "strike": "3000", "type": "CE", "entry": 65.40, "sl": 58.85, "tg": 82.50, "conf": 92},
    {"sym": "HDFCBANK", "strike": "1720", "type": "PE", "entry": 28.50, "sl": 25.65, "tg": 36.00, "conf": 81},
    {"sym": "INFY", "strike": "1650", "type": "CE", "entry": 34.20, "sl": 30.75, "tg": 43.50, "conf": 76},
    {"sym": "TCS", "strike": "4200", "type": "CE", "entry": 88.00, "sl": 79.20, "tg": 110.00, "conf": 88},
    {"sym": "ICICIBANK", "strike": "1100", "type": "PE", "entry": 19.40, "sl": 17.45, "tg": 24.50, "conf": 84},
]

# 2. Simulate 1 Index Power Alert
index_alert = {"sym": "NIFTY 50", "strike": "22200", "type": "CE", "entry": 142.00, "sl": 127.80, "tg": 185.00, "conf": 94}

print("🚀 Starting Final Institutional Alert Simulation...")

for s in stocks_to_send:
    msg = get_premium_msg(s['sym'], s['strike'], s['type'], s['entry'], s['sl'], s['tg'], s['conf'])
    success = send_telegram(msg)
    print(f"[{s['sym']}] Alert Sent: {success}")

idx_msg = get_premium_msg(index_alert['sym'], index_alert['strike'], index_alert['type'], index_alert['entry'], index_alert['sl'], index_alert['tg'], index_alert['conf'], tag="INDEX POWER TRADE")
success = send_telegram(idx_msg)
print(f"[NIFTY 50] Index Alert Sent: {success}")

# 3. Final Market Pulse
pulse_msg = (
    f"🟢 LIVE 🏛️ *MARKET SENTIMENT PULSE*\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "🕙 **TIME**: `14:33:00` \n"
    "🎭 **BIAS**: `BULLISH` \n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📈 **NIFTY 50**\n"
    "∟ PCR: `1.18` \n\n"
    "📉 **BANKNIFTY**\n"
    "∟ PCR: `0.94` \n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"🏛️ [OPEN TERMINAL]({AUTH_URL})"
    f"{CEO_SIG}"
)
success = send_telegram(pulse_msg)
print(f"[MARKET PULSE] Sent: {success}")
