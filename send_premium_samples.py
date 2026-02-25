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

# 1. Premium Diamond/Top Pick Stock Alert
premium_stock_msg = (
    "🔥 *NEW DIAMOND PICK*\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📍 **ASSET**: `RELIANCE`\n"
    "🎟️ **OPTION**: `3000 CE` 🟩\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "💰 **ENTRY**: `₹65.00`\n"
    "🛡️ **STOPLOSS**: `₹58.50`\n"
    "🎯 **TARGET**: `₹84.50`\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📊 **CONFIDENCE**: `94%`\n"
    "⏳ **STATUS**: `Active`\n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
    "👤 *PrimeSkillDevelopment CEO*\n"
    "∟ *MuthuKumar krishnan*"
)

# 2. Premium Index Pulse Alert
premium_pulse_msg = (
    "🏛️ *MARKET SENTIMENT PULSE*\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "🕙 **TIME**: `14:27:00` \n"
    "🎭 **BIAS**: `BULLISH` \n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📈 **NIFTY 50**\n"
    "∟ PCR: `1.15` \n"
    "∟ CE: `4.52Cr` | PE: `5.20Cr` \n\n"
    "📉 **BANKNIFTY**\n"
    "∟ PCR: `0.92` \n"
    "∟ CE: `2.10Cr` | PE: `1.93Cr` \n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📊 **TOTAL PCR**: `1.04` \n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"🏛️ [OPEN TERMINAL]({AUTH_URL})\n\n"
    "👤 *PrimeSkillDevelopment CEO*\n"
    "∟ *MuthuKumar krishnan*"
)

# 3. Premium Rapid Scalp Alert
premium_scalp_msg = (
    "⚡ *NEW RAPID SCALP*\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📍 **ASSET**: `TCS`\n"
    "🎟️ **OPTION**: `4100 CE` 🟩\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "💰 **ENTRY**: `₹45.50`\n"
    "🛡️ **STOPLOSS**: `₹41.00`\n"
    "🎯 **TARGET**: `₹52.00`\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📊 **CONFIDENCE**: `82%`\n"
    "⏳ **STATUS**: `Active`\n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
    "👤 *PrimeSkillDevelopment CEO*\n"
    "∟ *MuthuKumar krishnan*"
)

print(f"Sending Premium Stock Alert: {send_telegram(premium_stock_msg)}")
print(f"Sending Premium Pulse Alert: {send_telegram(premium_pulse_msg)}")
print(f"Sending Premium Scalp Alert: {send_telegram(premium_scalp_msg)}")
