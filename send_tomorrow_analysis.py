
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

def analyze_tomorrow():
    print("🏹 [TOMORROW ANALYSIS] Generating Institutional Outlook...")
    
    # Symbols for analysis
    assets = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "RELIANCE": "RELIANCE.NS", "HDFCBANK": "HDFCBANK.NS"}
    
    analysis_results = {}
    
    try:
        for name, sym in assets.items():
            df = yf.download(sym, period="5d", interval="1d", progress=False)
            if df.empty: continue
            
            # Flatten columns if MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            last_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            high = float(df['High'].iloc[-1])
            low = float(df['Low'].iloc[-1])
            
            support = round(low, 2)
            resistance = round(high, 2)
            bias = "BULLISH" if last_close > (high + low)/2 else "BEARISH"
            
            analysis_results[name] = {
                "close": round(last_close, 2),
                "sup": support,
                "res": resistance,
                "bias": bias,
                "chg": round(((last_close - prev_close)/prev_close)*100, 2)
            }
            
        # Formulate Strategy
        nifty = analysis_results.get("NIFTY", {})
        bank = analysis_results.get("BANKNIFTY", {})
        rel = analysis_results.get("RELIANCE", {})
        
        msg = (
            "🏛️ **INSTITUTIONAL TOMORROW ANALYSIS**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 **DATE**: `February 25, 2026`\n"
            "🔭 **MARKET OUTLOOK**: `Gap Down Recovery Possible` 🧩\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📈 **NIFTY 50 (PRECISE LEVELS)**\n"
            f"∟ **CLOSE**: `{nifty.get('close')}`\n"
            f"∟ **SUPPORT**: `{nifty.get('sup')}`\n"
            f"∟ **RESISTANCE**: `{nifty.get('res')}`\n"
            f"∟ **BIAS**: `{'🟢' if nifty.get('bias') == 'BULLISH' else '🔴'} {nifty.get('bias')}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📉 **BANKNIFTY (PRECISE LEVELS)**\n"
            f"∟ **CLOSE**: `{bank.get('close')}`\n"
            f"∟ **SUPPORT**: `{bank.get('sup')}`\n"
            f"∟ **RESISTANCE**: `{bank.get('res')}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 **POSSIBLE TRADES FOR TOMORROW**\n"
            f"1️⃣ **BTST HOLD**: `NIFTY 25450 PE` (from 3PM Pulse)\n"
            f"2️⃣ **RELIANCE**: Buy above `{rel.get('res')}` for Target `{rel.get('res', 0)*1.02:.2f}`\n"
            f"3️⃣ **PE SCALP**: If NIFTY breaks `{nifty.get('sup')}` on Open.\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **STRATEGY**: `Wait for 9:20 AM Candle Confirmation`\n"
            f"{SIGNATURE}"
        )
        
        success = send_telegram(msg)
        print(f"Analysis sent: {success}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_tomorrow()
