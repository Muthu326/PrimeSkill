
# -----------------------------------------------
# F&O Professional Test Alert Dashboard
# Streamlit + Upstox API + Telegram
# -----------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import requests
import sys
import os
from dotenv import load_dotenv

# Ensure the root directory is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from services.upstox_engine import get_upstox_engine
from services.upstox_streamer import get_streamer, get_live_ltp
from services.market_engine import calculate_indicators, get_expiry_details, get_mtf_confluence
from config.config import NIFTY_50, BANKNIFTY, SENSEX, FINNIFTY

# Load environment variables
load_dotenv()

# -------------------------------
# 1️⃣ Configuration
# -------------------------------
API_KEY = os.getenv("UPSTOX_API_KEY")
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TEST_MODE = True  # Alerts heading = TEST ALERT
COOLDOWN_SEC = 300  # 5 min cooldown for duplicate alerts

# Initialize Upstox Engine
engine = get_upstox_engine()
streamer = get_streamer()

# -------------------------------
# 2️⃣ Symbols
# -------------------------------
SCAN_INDICES = ["NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY"]
NIFTY_50_STOCKS = [s.replace(".NS", "") for s in NIFTY_50]
all_symbols = SCAN_INDICES + NIFTY_50_STOCKS

# -------------------------------
# 3️⃣ Persistence & Cooldown
# -------------------------------
alert_cooldown = {}

# -------------------------------
# 4️⃣ Helper Functions
# -------------------------------
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        st.error(f"Telegram Alert Failed: {e}")

def get_atm_strike(spot, symbol):
    # Strike gaps for common instruments
    gaps = {
        "NIFTY": 50, "BANKNIFTY": 100, "FINNIFTY": 50, "SENSEX": 100, "MIDCAPNIFTY": 25,
        "RELIANCE": 20, "TCS": 20, "HDFCBANK": 10, "INFY": 10, "ICICIBANK": 5
    }
    gap = gaps.get(symbol, 10)
    if "NIFTY" in symbol and "BANK" not in symbol: gap = 50
    return round(spot / gap) * gap

def fetch_best_itm(symbol, spot, direction="BULLISH"):
    try:
        key = engine.get_instrument_key(symbol)
        if not key: return None
        
        # Get expiry dates
        expiries = engine.get_expiry_dates_via_sdk(key)
        if not expiries: return None
        
        # Sort and take nearest active
        now_str = datetime.now().strftime("%Y-%m-%d")
        valid_expiries = [e for e in expiries if e >= now_str]
        if not valid_expiries: return None
        
        target_expiry = valid_expiries[0]
        
        # Get option chain
        chain = engine.get_option_chain_via_sdk(key, target_expiry)
        if not chain: return None
        
        # Determine Option Type and Strike logic
        opt_type = "CE" if direction == "BULLISH" else "PE"
        
        # Filter for ITM options
        itm_candidates = []
        for contract in chain:
            strike = contract.strike_price
            if opt_type == "CE" and strike <= spot:
                itm_candidates.append(contract)
            elif opt_type == "PE" and strike >= spot:
                itm_candidates.append(contract)
        
        if not itm_candidates: return None
        
        # Pick the one closest to spot (Delta ~ 0.5-0.6)
        itm_candidates.sort(key=lambda x: abs(x.strike_price - spot))
        best = itm_candidates[0]
        
        option_contract = best.call_options if opt_type == "CE" else best.put_options
        if not option_contract or not option_contract.market_data: return None
        
        return {
            'symbol': symbol,
            'strike': best.strike_price,
            'type': opt_type,
            'ltp': option_contract.market_data.ltp,
            'oi': option_contract.market_data.oi,
            'delta': 0.6 if opt_type == "CE" else -0.6, # Simplified for test
            'expiry': target_expiry,
            'valid_expiries': valid_expiries
        }
    except Exception as e:
        print(f"Error fetching ITM for {symbol}: {e}")
        return None

def compute_confidence_score(symbol, option, mtf_status, vol_ratio):
    score = 0.0
    
    # 1. MTF Alignment (3.0 pts)
    bias = "Bull" if option['type'] == "CE" else "Bear"
    if mtf_status.get("Intraday") == f"{bias}ish": score += 1.5
    if mtf_status.get("Scalp") == f"{bias}ish": score += 1.5
    
    # 2. Volume Factor (2.0 pts)
    if vol_ratio > 1.5: score += 2.0
    elif vol_ratio > 1.2: score += 1.0
    
    # 3. Delta/Moneyness (2.0 pts)
    # Since we picked ITM, we give partial points
    score += 2.0 
    
    # 4. Momentum (3.0 pts)
    # Placeholder for simulated momentum score
    score += 2.0
    
    return round(score, 1)

def estimate_target(premium, delta=0.6):
    # Target = Entry + (Delta * 10% move in spot)
    # Simple heuristic: 20% gain for ITM
    return round(premium * 1.2, 2)

def expiry_aware(option):
    exp_date = datetime.strptime(option['expiry'], "%Y-%m-%d").date()
    days_left = (exp_date - datetime.now().date()).days
    
    if days_left <= 2 and len(option['valid_expiries']) > 1:
        option['next_expiry'] = option['valid_expiries'][1]
    else:
        option['next_expiry'] = "-"
    return option

def send_test_alert(option, score, mtf_status, spot):
    alert_key = f"TEST_{option['symbol']}_{option['type']}_{option['strike']}"
    now = time.time()
    
    if alert_key in alert_cooldown and now - alert_cooldown[alert_key] < COOLDOWN_SEC:
        return False

    heading = "🚀 *TEST ALERT (PROFESSIONAL)*" if TEST_MODE else "🔥 *LIVE TRADE ALERT*"
    target = estimate_target(option['ltp'])
    
    message = (
        f"{heading}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 **SYMBOL**: `{option['symbol']} {option['strike']} {option['type']}`\n"
        f"💰 **SPOT**: `{spot:.2f}` | **ENTRY**: `₹{option['ltp']}`\n"
        f"🏆 **CONFIDENCE**: `{score}/10`\n"
        f"🎯 **TARGET**: `₹{target}` | **SL**: `₹{round(option['ltp']*0.85, 2)}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **MTF CONFLUENCE**\n"
        f"∟ Scalp: `{mtf_status.get('Scalp', 'N/A')}`\n"
        f"∟ Intraday: `{mtf_status.get('Intraday', 'N/A')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📅 **EXPIRY**: `{option['expiry']}`\n"
        f"⏭️ **NEXT SUGGESTION**: `{option.get('next_expiry', '-')}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏰ **TIME**: `{datetime.now().strftime('%H:%M:%S')}`\n"
        f"👤 *PrimeSkill - Test Mode*"
    )
    
    send_telegram_alert(message)
    alert_cooldown[alert_key] = now
    return True

# -------------------------------
# 5️⃣ Streamlit Dashboard Setup
# -------------------------------
st.set_page_config(page_title="📊 F&O Professional Test Dashboard", layout="wide")
st.title("📈 F&O Professional Live Test Alert Dashboard")

# Initialize Session State
if 'running' not in st.session_state:
    st.session_state.running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🚀 Start Test Scanner"):
        st.session_state.running = True
    if st.button("🛑 Stop Scanner"):
        st.session_state.running = False
    
    st.markdown("---")
    st.info(f"Scanning Universe: {len(all_symbols)} Instruments")
    st.warning("⚠️ Mode: TEST ALERT (No real trades)")

table_placeholder = col2.empty()
log_placeholder = st.expander("📝 Scanner Live Logs", expanded=True)

# -------------------------------
# 6️⃣ Main Execution Loop
# -------------------------------
if st.session_state.running:
    # Pre-warm instrument keys
    instrument_map = {}
    for sym in all_symbols:
        k = engine.get_instrument_key(sym)
        if k: instrument_map[sym] = k
    
    streamer.start(initial_keys=list(instrument_map.values()))
    
    while st.session_state.running:
        results = []
        for sym in all_symbols[:20]: # Focus on top 20 for speed in test
            try:
                spot = get_live_ltp(instrument_map.get(sym))
                if not spot: continue
                
                # Fetch 5-min data for indicators
                df = engine.get_historical_candles(instrument_map[sym], interval="5minute", days=2)
                if df.empty: continue
                
                df = calculate_indicators(df)
                last = df.iloc[-1]
                
                # MTF Check
                _, mtf_summary = get_mtf_confluence(sym)
                mtf_dict = {"Intraday": mtf_summary, "Scalp": "Bullish" if last['RSI'] > 50 else "Bearish"}
                
                # Biased Direction
                bias = "BULLISH" if last['RSI'] > 55 else "BEARISH" if last['RSI'] < 45 else None
                
                if bias:
                    option = fetch_best_itm(sym, spot, bias)
                    if option and option['ltp'] > 0:
                        score = compute_confidence_score(sym, option, mtf_dict, last['VolRatio'])
                        option = expiry_aware(option)
                        
                        # Trigger Alert if high score
                        if score >= 5.0:
                            if send_test_alert(option, score, mtf_dict, spot):
                                st.session_state.logs.append(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Alert Sent: {sym} {option['type']} {option['strike']} (Score: {score})")
                        
                        results.append({
                            "Symbol": sym,
                            "Spot": round(spot, 2),
                            "Bias": bias,
                            "Option": f"{option['strike']} {option['type']}",
                            "LTP": option['ltp'],
                            "Score": score,
                            "RSI": round(last['RSI'], 1),
                            "Vol": round(last['VolRatio'], 1),
                            "MTF": mtf_summary
                        })
            except Exception as e:
                print(f"Error in scan cycle for {sym}: {e}")
                continue
        
        # Update Table
        if results:
            df_results = pd.DataFrame(results)
            table_placeholder.table(df_results)
            
        # Update Logs
        with log_placeholder:
            for log in st.session_state.logs[-10:]:
                st.write(log)
                
        time.sleep(10) # Wait between cycles
else:
    table_placeholder.info("Click 'Start Test Scanner' to begin live monitoring.")
