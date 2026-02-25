
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CEO_NAME = "MuthuKumar Krishnan."
COMPANY_NAME = "Prime Skill Devlopment"
SIGNATURE = f"**{COMPANY_NAME}**\nCEO : {CEO_NAME}"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Mock Alert Sent Successfully to Telegram!")
            return True
        else:
            print(f"❌ Failed to send alert: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def trigger_review_alert():
    # Mock data for review
    signal = {
        'symbol': 'RELIANCE',
        'type': 'CE',
        'strike': 2980,
        'spot': 2965.45,
        'premium': 45.20,
        'delta': 0.68,
        'mtf_signals': {'Scalping': 'BULLISH 🚀', 'Intraday': 'BULLISH 🚀', 'Swing': 'NEUTRAL'},
        'target': 65.50,
        'confidence_score': 8.8,
        'near_expiry': '27-FEB-2026',
        'expiry': '27-FEB-2026',
        'vol': '2.4x',
        'oi': 'HIGH (Long Buildup)',
        'premium_pct': '1.52'
    }

    status_icon = "🧪 TEST"
    mtf = signal['mtf_signals']
    mtf_str = f"Scalp: {mtf.get('Scalping')} | Intra: {mtf.get('Intraday')} | Swing: {mtf.get('Swing')}"
    
    msg = (
        f"📈 **F&O ALERT - RELIANCE CE 2980**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **SPOT**: `₹{signal['spot']:,.2f}`\n"
        f"🎟️ **STRIKE**: `{signal['strike']}`\n"
        f"📅 **CURRENT EXPIRY**: `{signal['near_expiry']}`\n"
        f"📅 **SUGGESTED EXPIRY**: `{signal['expiry']}`\n"
        f"📥 **LTP**: `₹{signal['premium']:.2f}` ({signal['premium_pct']}%)\n"
        f"📊 **OI**: `{signal['oi']}` | **VOL**: `{signal['vol']}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 **CONFIDENCE**: `{signal['confidence_score']}/10` 🔥\n"
        f"🚀 **TARGET**: `₹{signal['target']:.2f} LTP`\n"
        f"🕒 **EST. TIME**: `02:45 PM`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ **SIGNAL**: `BUY {signal['type']} - High Probability`\n"
        f"⚖️ **MTF STATUS**: `{mtf_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [OPEN TERMINAL](http://localhost:8501)\n\n"
        f"{SIGNATURE}"
    )
    
    print("📡 Sending Institutional Mock Alert for Review...")
    send_telegram(msg)

if __name__ == "__main__":
    trigger_review_alert()
