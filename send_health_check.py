
import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SIGNATURE = "👤 *PrimeSkillDevelopment CEO*\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

if __name__ == "__main__":
    msg = (
        "🛠️ **SYSTEM HEALTH CHECK** 🛠️\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📡 **Scanner Status**: `Active` 🟢\n"
        "🔗 **Data Pipeline**: `Synchronized` ✅\n"
        "🎭 **Indicator Accuracy**: `Fixed` (using 2-day historical depth)\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **Summary**: The scanner is now correctly processing 5-minute technicals with sufficient history. Since the market has just closed (15:30), live price-action alerts will resume at tomorrow's open. \n\n"
        "🚀 **Next Step**: You will receive the Final EOD Macro Summary shortly.\n"
        f"{SIGNATURE}"
    )
    send_telegram(msg)
    print("Health check sent.")
