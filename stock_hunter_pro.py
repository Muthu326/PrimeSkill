
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
API_KEY = os.getenv("UPSTOX_API_KEY")
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri=http://localhost:8501"
SIGNATURE = f"👤 *PrimeSkillDevelopment CEO*\\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def stock_hunter_pro():
    print("🏹 [STOCK HUNTER PRO] Scanning Full NIFTY 50 Universe...")
    
    # 1. Prepare symbols (filter out known issues if any, but TATAMOTORS.NS is usually standard)
    symbols = [f"{s}.NS" for s in NIFTY_50_STOCKS]
    
    # 2. Fetch Daily and Intraday data
    try:
        # Get last 30 mins move
        data = yf.download(symbols, period="1d", interval="5m", progress=False)
        if data.empty:
            print("No data found.")
            return

        close_data = data['Close']
        moves = []
        
        for s in symbols:
            try:
                if s not in close_data.columns: continue
                s_data = close_data[s].dropna()
                if len(s_data) < 6: continue
                
                curr = float(s_data.iloc[-1])
                prev = float(s_data.iloc[-6]) # ~30 mins ago
                m_pct = (curr - prev) / prev * 100
                
                moves.append({
                    "symbol": s.replace(".NS", ""),
                    "price": curr,
                    "move": m_pct
                })
            except: continue
            
        # 3. Sort by absolute move to find top volatility
        moves.sort(key=lambda x: abs(x['move']), reverse=True)
        top_movers = moves[:5] # Top 5 movers
        
        print(f"Found {len(top_movers)} significant institutional moves.")
        
        for item in top_movers:
            name = item['symbol']
            m = item['move']
            typ = "CE" if m > 0 else "PE"
            icon = "🟩" if m > 0 else "🟥"
            status = "BULLISH ACCUMULATION" if m > 0 else "BEARISH DISTRIBUTION"
            
            # Formatting the message specifically for 3PM closing window
            msg = (
                f"🔥 *🟢 LIVE 🏛 INSTITUTIONAL BTST*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📍 **STOCK**: `{name}`\n"
                f"🎟️ **PREMIUM PICK**: `{typ}` {icon}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📈 **3PM MOMENTUM**: `{m:.2f}%` (30m Pulse)\n"
                f"💰 **CMP**: `₹{item['price']:.2f}`\n"
                f"🛡️ **STRATEGY**: `{status}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏛️ [OPEN TERMINAL]({AUTH_URL})\n\n"
                f"{SIGNATURE}"
            )
            success = send_telegram(msg)
            print(f"Alert Sent for {name}: {success}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    stock_hunter_pro()
