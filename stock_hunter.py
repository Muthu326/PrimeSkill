
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
import urllib.request
import urllib.parse
from scanner_config import *

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SIGNATURE = f"👤 *PrimeSkillDevelopment CEO*\\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def stock_hunter():
    print("🏹 [STOCK HUNTER] Active...")
    # Checking Top 5 NIFTY Heavyweights
    heavy = ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS"]
    data = yf.download(heavy, period="1d", interval="5m", progress=False)
    
    for s in heavy:
        c = data['Close'][s].iloc[-1]
        p = data['Close'][s].iloc[-5]
        m = (c-p)/p * 100
        
        if abs(m) > 0.4: # Significant 3PM move
            typ = "CE" if m > 0 else "PE"
            icon = "🟩" if m > 0 else "🟥"
            name = s.replace(".NS", "")
            
            msg = (
                f"🚀 *🟢 LIVE 🏛 TOP STOCK MOVE*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📍 **STOCK**: `{name}`\n"
                f"🎟️ **PREMIUM PICK**: `{typ}` {icon}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📈 **INSTITUTIONAL MOVE**: `{m:.2f}%` (Last 25m)\n"
                f"🛡️ **STRATEGY**: `Momentum BTST`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{SIGNATURE}"
            )
            send_telegram(msg)
            print(f"Sent alert for {name}")

if __name__ == "__main__":
    stock_hunter()
