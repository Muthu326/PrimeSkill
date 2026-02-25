
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
import urllib.request
import urllib.parse

from services.upstox_engine import get_upstox_engine
from services.upstox_streamer import get_streamer, get_live_ltp
from scanner_config import *

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={os.getenv('UPSTOX_API_KEY')}&redirect_uri=http://localhost:8501"
SIGNATURE = f"👤 *PrimeSkillDevelopment CEO*\\n∟ *MuthuKumar krishnan*"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def get_atm_strike(spot, step=50):
    return int(round(spot / step) * step)

def run_hunter():
    print("🏹 [3PM HUNTER] Starting Live Search...")
    engine = get_upstox_engine()
    
    # 1. Get Nifty Spot
    nifty_key = "NSE_INDEX|Nifty 50"
    quote = engine.get_market_quote([nifty_key])
    spot = quote[nifty_key]['last_price']
    print(f"∟ NIFTY SPOT: {spot}")
    
    # 2. Get Expiries & Pick Next (for BTST)
    expiries = engine.get_expiry_dates_via_sdk(nifty_key)
    expiries.sort()
    # Use next week for safer 3PM BTST
    target_expiry = expiries[1] if len(expiries) > 1 else expiries[0]
    print(f"∟ TARGET EXPIRY: {target_expiry}")
    
    # 3. Get Option Chain & Analysis
    chain = engine.get_option_chain_via_sdk(nifty_key, target_expiry)
    rows = []
    for strike in chain:
        rows.append({
            "strike": strike.strike_price,
            "call_oi": strike.call_options.market_data.oi if strike.call_options else 0,
            "put_oi": strike.put_options.market_data.oi if strike.put_options else 0,
            "call_ltp": strike.call_options.market_data.ltp if strike.call_options else 0,
            "put_ltp": strike.put_options.market_data.ltp if strike.put_options else 0
        })
    df = pd.DataFrame(rows)
    pcr = df['put_oi'].sum() / df['call_oi'].sum() if df['call_oi'].sum() > 0 else 0
    sup = df.loc[df['put_oi'].idxmax()]['strike']
    res = df.loc[df['call_oi'].idxmax()]['strike']
    
    print(f"∟ PCR: {pcr:.2f} | SUP: {sup} | RES: {res}")
    
    # 4. Selection Logic
    atm = get_atm_strike(spot)
    print(f"∟ ATM: {atm}")
    
    # We find the top 5 movers of Nifty 50 to confirm bias
    yf_symbols = [f"{s}.NS" for s in NIFTY_50_STOCKS[:10]] # Quick check top 10
    data = yf.download(yf_symbols, period="1d", interval="5m", progress=False)
    latest_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-5] # 25 mins ago
    movers = (latest_close - prev_close) / prev_close * 100
    avg_m = movers.mean()
    
    bias = "BULLISH" if avg_m > 0 else "BEARISH"
    opt_type = "CE" if bias == "BULLISH" else "PE"
    icon = "🟩" if opt_type == "CE" else "🟥"
    
    premium = 0
    for strike in chain:
        if strike.strike_price == float(atm):
            premium = strike.call_options.market_data.ltp if opt_type == "CE" else strike.put_options.market_data.ltp
            break
            
    if premium == 0: premium = 150 # Fallback for sim if needed
    
    msg = (
        f"🔥 *🟢 LIVE ALERT: 3PM BTST POWER*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 **ASSET**: `NIFTY 50`\n"
        f"🎟️ **OPTION**: `{atm} {opt_type}` {icon}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 **ENTRY**: `₹{premium:.2f}`\n"
        f"🛡️ **STOPLOSS**: `₹{premium*0.8:.2f}`\n"
        f"🎯 **TARGET**: `₹{premium*1.4:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **PCR**: `{pcr:.2f}` | **BIAS**: `{bias}`\n"
        f"⏳ **EXPIRY**: `{target_expiry}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\n\n"
        f"👤 *PrimeSkillDevelopment CEO*\\n∟ *MuthuKumar krishnan*"
    )
    
    print("🚀 Sending REAL-TIME Hunter Alert...")
    success = send_telegram(msg)
    print(f"Result: {success}")

if __name__ == "__main__":
    run_hunter()
