import os
import sys
import time
import json
import urllib.request
import urllib.parse
from datetime import time as dt_time
import pandas as pd
import numpy as np
import threading
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
import schedule
from scanner_config import *

# Force UTF-8 encoding
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from utils.logger import setup_logger
from services.upstox_engine import get_upstox_engine
from config.config import OPTION_CHAIN_CONFIG, INDEX_WEIGHTS, NIFTY_50, BANKNIFTY, SENSEX, FINNIFTY
from services.market_engine import get_expiry_details, get_mtf_confluence, calculate_indicators
from services.upstox_streamer import get_streamer, get_live_ltp, update_live_ltp
from config.extended_stocks import EXTENDED_STOCKS_LIST
from utils.cache_manager import ScanCacheManager

# Load environment variables
load_dotenv()

# ==========================================
# ⚙️ CONFIGURATION & SETTINGS
# ==========================================
logger = setup_logger("MasterScanner")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# HOT URL for Authentication (as requested by user)
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={os.getenv('UPSTOX_API_KEY')}&redirect_uri=http://localhost:8501"

STOCKS = list(set(NIFTY_50_STOCKS + 
              [s.replace(".NS","") for s in BANKNIFTY] + 
              [s.replace(".NS","") for s in SENSEX] + 
              [s.replace(".NS","") for s in FINNIFTY]))
INDICES = SCAN_INDICES

# CACHING (Optimization for Institutional Build)
MTF_CACHE = {}
MTF_CACHE_TTL = 300 
OPTION_LTP_CACHE = {} 
OPTION_LTP_TTL = 180 
CANDLE_CACHE = {} 
CANDLE_TTL = CANDLE_CYCLE
MOVERS_CACHE = {"bulls": [], "bears": [], "ts": 0}
MOVERS_TTL = 300 

# OPTION CHAIN & PCR CACHE (Professional Flow)
OPTION_CHAIN_MEM = {} 
CHAINS_TTL = 60

# PERSISTENCE
ALERTS_SENT_FILE = ".inst_alerts_sent.json"
INST_RESULTS_FILE = "data/inst_scanner_results.json"
ACTIVE_SIGNALS_FILE = "data/active_signals.json"
DAILY_STATS_FILE = ".daily_stats.json"
PRE_POST_ANALYSIS_FILE = "data/pre_post_analysis.json"
os.makedirs("data", exist_ok=True)

DAILY_LIMITS = {
    "DIAMOND": 5,
    "TOP": 8,
    "BEST": 10,
    "GOOD": 15,
    "INDEX_BIAS": 10,
    "MEGA": 3 # Rare, high-conviction trades
}

# MEGA MOVE MEMORY (Tiered Architecture)
SECTOR_ROTATION = {}
FII_BIAS_VALUE = "NEUTRAL"
VIX_EXPANDING = False
VIX_VALUE = 15
VIX_REGIME = "NORMAL_VOL"
VIX_CHANGE_PCT = 0
OI_STRUCTURE_MAP = {}
PREV_OI_MAP = {} # To track OI changes
LAST_SECTOR_SYNC = 0
LAST_FII_SYNC = 0
LAST_OI_SYNC = 0

def run_premarket_scan():
    """🏛 PRE-MARKET: Gauge Global Sentiment & Positioning (9:00 AM - 9:15 AM)"""
    logger.info("📡 Running Institutional Pre-Market Analysis...")
    global_pulse = get_global_market_pulse()
    
    # Analyze Gift Nifty (Proxy via SGX or YFinance fallback)
    try:
        nifty_fut = yf.download("^NSEI", period="1d", interval="1m", prepost=True)
        gift_status = "Syncing..." 
        if not nifty_fut.empty:
            last_close = nifty_fut['Close'].iloc[-1]
            prev_close = nifty_fut['Close'].iloc[0]
            chg = ((last_close - prev_close)/prev_close)*100
            gift_status = f"{chg:+.2f}% ({'Gap Up' if chg > 0 else 'Gap Down'})"
    except: gift_status = "N/A"

    msg = (
        "🏛️ **INSTITUTIONAL PRE-MARKET OUTLOOK**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕙 **TIME**: `{datetime.now().strftime('%H:%M:%S')}`\n"
        f"🌍 **GLOBAL BIAS**: `{gift_status}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌎 **GLOBAL INDICES**\n"
    )
    for name, data in global_pulse.items():
        icon = "📈" if data['chg'] > 0 else "📉"
        msg += f"∟ {name}: `{data['chg']:.2f}%` {icon}\n"
    
    msg += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ **STRATEGY**: `Gauging Opening Volatility`\n"
        "📍 **ACTION**: Wait for 9:20 AM Candle Confirmation.\n"
        f"{SIGNATURE}"
    )
    send_telegram(msg)
    return True

def run_postmarket_scan(symbols, engine):
    """🏛 POST-MARKET: Identify Supply/Demand Zones (3:45 PM)"""
    logger.info("📊 Running EOD Post-Market Review...")
    report = "🏛️ **INSTITUTIONAL POST-MARKET REVIEW**\n━━━━━━━━━━━━━━━━━━━━\n"
    
    for sym in ["NIFTY", "BANKNIFTY", "RELIANCE", "HDFCBANK"]:
        try:
            key = engine.get_instrument_key(sym)
            df = engine.get_historical_candles(key, interval="day", days=5)
            if df.empty: continue
            
            # Normalize columns
            df.columns = [c.lower() for c in df.columns]
            
            # Normalize columns to lowercase or use a consistent case
            df.columns = [c.lower() for c in df.columns]
            
            # Simple Supply/Demand logic (Top 3 highs, Bottom 3 lows)
            supply = df['high'].nlargest(3).mean()
            demand = df['low'].nsmallest(3).mean()
            close = df['close'].iloc[-1]
            chg = ((close - df['close'].iloc[-2])/df['close'].iloc[-2])*100
            
            report += (
                f"📍 **{sym}**: `{close:,.2f}` ({chg:+.2f}%)\n"
                f"∟ Supply Zone: `{supply:,.2f}`\n"
                f"∟ Demand Zone: `{demand:,.2f}`\n"
                f"∟ Bias: `{'BULLISH' if close > demand * 1.02 else 'BEARISH'}`\n\n"
            )
        except: continue
        
    report += f"━━━━━━━━━━━━━━━━━━━━\n🚀 **EOD STRATEGY**: Review Order Blocks for Tomorrow.\n{SIGNATURE}"
    send_telegram(report)
    return True

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def load_alerts_sent():
    if os.path.exists(ALERTS_SENT_FILE):
        with open(ALERTS_SENT_FILE, 'r') as f:
            try: 
                data = json.load(f)
                # Convert legacy float/int values to dict format
                for k, v in data.items():
                    if isinstance(v, (int, float)):
                        data[k] = {"ts": v, "status": "Active"}
                return data
            except: return {}
    return {}

def save_alerts_sent(data):
    now = time.time()
    # Keep alerts for 2 hours to prevent spam, checking the 'ts' field in the dict
    cleaned_data = {}
    for k, v in data.items():
        ts = v.get('ts', 0) if isinstance(v, dict) else v
        if now - ts < 7200:
            cleaned_data[k] = v
    with open(ALERTS_SENT_FILE, 'w') as f:
        json.dump(cleaned_data, f)

def load_daily_stats():
    today = datetime.now().strftime('%Y-%m-%d')
    if os.path.exists(DAILY_STATS_FILE):
        with open(DAILY_STATS_FILE, 'r') as f:
            try:
                stats = json.load(f)
                if stats.get('date') == today:
                    return stats
            except: pass
    return {'date': today, 'counts': {k: 0 for k in DAILY_LIMITS}}

def save_daily_stats(stats):
    with open(DAILY_STATS_FILE, 'w') as f:
        json.dump(stats, f)

def save_inst_results(data, elite_top_5=None, index_picks=None):
    try:
        # Legacy save
        with open(INST_RESULTS_FILE, 'w') as f:
            json.dump(data, f, default=str)
        
        # New Quick Scan Viewer Cache Sync
        cache_manager = ScanCacheManager()
        
        formatted_diamond = []
        if elite_top_5:
            for d in elite_top_5:
                formatted_diamond.append({
                    "Stock": d.get('display_name', d['symbol']),
                    "Price": d['spot'],
                    "Entry": d['premium'],
                    "SL": d['premium'] * 0.9,
                    "Target": d['premium'] * 1.3,
                    "Conf": d['score'],
                    "Strike": d['strike'],
                    "Type": d['type'],
                    "Signal": f"BUY {d['type']}",
                    "Tag": d.get('tag', '')
                })
        
        formatted_index = []
        if index_picks:
            for idx in index_picks:
                formatted_index.append({
                    "Stock": get_friendly_name(idx['index']),
                    "Price": idx.get('spot', 0),
                    "Entry": idx.get('premium', 0),
                    "SL": idx.get('stop_loss', 0),
                    "Target": idx.get('target', 0),
                    "Conf": idx.get('bias_pct', 70),
                    "Strike": idx.get('strike', 'ATM'),
                    "Type": idx.get('type', 'CE'),
                    "Signal": f"BUY {idx.get('type', 'CE')}"
                })
        
        # Extract the results list if data is the summary dict, otherwise use data as is
        scan_list = data.get("all", data) if isinstance(data, dict) else data
        
        cache_manager.save_scan_results(
            scan_data=scan_list,
            index_picks=formatted_index,
            diamond_picks=formatted_diamond
        )
        logger.info("✅ Quick Scan Viewer Cache Synchronized.")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")

def load_active_signals():
    if os.path.exists(ACTIVE_SIGNALS_FILE):
        with open(ACTIVE_SIGNALS_FILE, 'r') as f:
            try: return json.load(f)
            except: return []
    return []

def save_active_signals(signals):
    with open(ACTIVE_SIGNALS_FILE, 'w') as f:
        json.dump(signals, f, default=str)

def is_new_5min_candle():
    """📊 Step 3: 5-Min Candle Sync Properly"""
    now = datetime.now()
    return now.minute % 5 == 0

def get_friendly_name(symbol):
    """💎 Convert ticker symbols to human-readable names (e.g., RELIANCE -> Reliance)"""
    if not symbol: return "N/A"
    symbol = str(symbol).strip().upper()
    overrides = {
        "HDFCBANK": "HDFC Bank", "RELIANCE": "Reliance", "SBIN": "SBI", "AXISBANK": "Axis Bank",
        "ICICIBANK": "ICICI Bank", "SUNPHARMA": "Sun Pharma", "TATASTEEL": "Tata Steel",
        "BHARTIARTL": "Airtel", "KOTAKBANK": "Kotak Bank", "M&M": "Mahindra & Mahindra",
        "BAJFINANCE": "Bajaj Finance", "BAJAJFINSV": "Bajaj Finserv", "MARUTI": "Maruti Suzuki",
        "ADANIENT": "Adani Ent", "ADANIPORTS": "Adani Ports", "TITAN": "Titan", "HAL": "HAL",
        "ASIANPAINT": "Asian Paints", "ULTRACEMCO": "UltraTech Cement", "RECLTD": "REC Ltd",
        "PFC": "PFC Ltd", 
        "NIFTY": "Nifty 50", "BANKNIFTY": "Bank Nifty", "SENSEX": "Sensex",
        "FINNIFTY": "Fin Nifty", "MIDCAPNIFTY": "Midcap Nifty",
        "NIFTY_FIN_SERVICE": "Fin Nifty", "NIFTY_MID_SELECT": "Midcap Nifty",
        "^NSEI": "Nifty 50", "^NSEBANK": "Bank Nifty", "^BSESN": "Sensex",
        "NSE_INDEX|NIFTY 50": "Nifty 50", "NSE_INDEX|NIFTY BANK": "Bank Nifty",
        "NSE_INDEX|INDIA VIX": "India VIX", "NSE_INDEX|NIFTY FIN SERVICE": "Fin Nifty"
    }
    if symbol in overrides: return overrides[symbol]
    # Handle Upstox keys
    if "NIFTY" in symbol and "BANK" in symbol: return "Bank Nifty"
    if "NIFTY" in symbol and "FIN" in symbol: return "Fin Nifty"
    if "NIFTY" in symbol and "MID" in symbol: return "Midcap Nifty"
    if "NIFTY 50" in symbol: return "Nifty 50"
    
    # Default: Title Case + Space out common patterns
    name = symbol.replace("_", " ").title()
    return name

def can_take_trade(symbol, active_signals):
    """DUPLICATE + CE/PE CONFLICT CONTROL"""
    for s in active_signals:
        if s['symbol'] == symbol:
            return False # Block any new trade for same symbol if one exists (CE or PE)
    return True

def classify_vix(vix_value):
    """🎯 STEP 2 — Classify VIX Regime"""
    if vix_value < 12: return "LOW_VOL"
    elif 12 <= vix_value <= 18: return "NORMAL_VOL"
    else: return "HIGH_VOL"

def vix_trending_up(vix_df):
    """🔴 B) 3PM Overnight Filter VIX Trend"""
    if len(vix_df) < 3: return False
    v_close = vix_df['Close'] if 'Close' in vix_df.columns else vix_df['close']
    return v_close.iloc[-1] > v_close.iloc[-3]

def market_regime(index_trend, vix_value):
    """🏛 Professional Market Regime Engine"""
    if index_trend == "Bullish" and vix_value > 15: return "STRONG_BULLISH 🔥"
    if index_trend == "Bearish" and vix_value > 15: return "STRONG_BEARISH 🌋"
    if vix_value < 12: return "RANGE_DAY ⚖️"
    return "NORMAL_DAY 🟢"

def market_sentiment(index_df, pcr_value, vix_df):
    """🏛 15-MIN MARKET SENTIMENT ENGINE"""
    if index_df.empty: return "NEUTRAL"
    
    # Normalize columns for robustness
    index_df.columns = [c.capitalize() for c in index_df.columns]
    vix_df.columns = [c.lower() for c in vix_df.columns]
    
    trend = index_df['Trend'].iloc[-1] if 'Trend' in index_df.columns else "NEUTRAL"
    vix_val = vix_df['close'].iloc[-1] if not vix_df.empty and 'close' in vix_df.columns else 15
    regime = market_regime(trend, vix_val)
    
    # Standard Sentiment logic enhanced by regime
    if "STRONG_BULLISH" in regime and pcr_value > 1.0: return f"BULLISH {regime}"
    if "STRONG_BEARISH" in regime and pcr_value < 0.8: return f"BEARISH {regime}"
    return f"NEUTRAL ({regime})"

def instant_opportunity(premium, prev_premium, vol_ratio):
    """🏛 IMMEDIATE OPPORTUNITY TRIGGER"""
    if prev_premium == 0: return False
    return premium > prev_premium * 1.03 and vol_ratio > 1.8

def is_power_window():
    """3PM Special Window"""
    now = datetime.now()
    return now.hour == 15 and 0 <= now.minute <= 5

def choose_power_strike(spot, symbol, direction):
    """ITM Strike for Overnight Hold"""
    atm = get_atm_strike(spot, symbol)
    if spot > 5000: step = 100
    elif spot > 1000: step = 20
    elif spot > 500: step = 10
    else: step = 5
    return atm - step if direction == "CE" else atm + step

def send_trade_alert(signal, is_update=False):
    """💎 Premium Institutional Trade Alert Design - Expiry & Score Aware"""
    is_test = os.getenv("TEST_MODE", "false").lower() == "true"
    status_icon = "🧪 TEST" if is_test else "🟢 LIVE"
    
    if is_update:
        title = f"🔔 *{status_icon} | SIGNAL UPDATE: {signal['status']}*"
    else:
        # 🛡️ SPAM CONTROL / COOLDOWN
        current_ts = time.time()
        alert_key = f"{signal['symbol']}_{signal['type']}"
        if alert_key in ALERTS_COOLDOWN:
            last_sent = ALERTS_COOLDOWN[alert_key]
            if current_ts - last_sent < 1800: # 30 min cooldown
                return False
        
        ALERTS_COOLDOWN[alert_key] = current_ts
        title = f"🔥 *{status_icon} | NEW {signal['type']} TRADE ALERT*"
    
    # 🎨 Data Formatting
    raw_sym = signal['symbol']
    fname = get_friendly_name(raw_sym)
    spot_px = signal.get('spot', 0)
    prem = signal.get('premium', 0)
    delta = signal.get('delta', 0.6)
    mtf = signal.get('mtf_signals', {})
    mtf_str = (
        f"5m: `{mtf.get('5m',{}).get('score',0)} ({mtf.get('5m',{}).get('trend','-')})` | "
        f"15m: `{mtf.get('15m',{}).get('score',0)} ({mtf.get('15m',{}).get('trend','-')})` | "
        f"1h: `{mtf.get('1h',{}).get('score',0)} ({mtf.get('1h',{}).get('trend','-')})`"
    )
    
    # 🎯 Target Estimation
    target_px = signal.get('target')
    if not target_px:
        target_px = estimate_target_premium(prem, delta)
    
    adx_val = signal.get('adx', 25)
    est_time = estimate_target_time(adx_val=adx_val, is_scalp="SCALP" in signal.get('tag', ''))
    score = signal.get('confidence_score', signal.get('score', 8.5))
    
    msg = (
        f"📈 **F&O ALERT - {fname} {signal['type']} {signal['strike']}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **SPOT**: `₹{spot_px:,.2f}`\n"
        f"🎟️ **STRIKE**: `{signal['strike']}`\n"
        f"📅 **CURRENT EXPIRY**: `{signal.get('near_expiry','-') or '-'}`\n"
        f"📅 **SUGGESTED EXPIRY**: `{signal.get('expiry','N/A')}`\n"
        f"📥 **LTP**: `₹{prem:.2f}` ({signal.get('premium_pct','0.5')}%)\n"
        f"📊 **OI**: `{signal.get('oi','LOW')}` | **VOL**: `{signal.get('vol','N/A')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 **CONFIDENCE**: `{score}/10` 🔥\n"
        f"🚀 **TARGET**: `₹{target_px:.2f} LTP`\n"
        f"🕒 **EST. TIME**: `{est_time}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ **SIGNAL**: `BUY {signal['type']} - High Probability`\n"
        f"⚖️ **MTF STATUS**: `{mtf_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [OPEN TERMINAL]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    return send_telegram(msg)

# ==========================================
# 🧠 CORE INTELLIGENCE LOGIC
# ==========================================

def get_atm_strike(spot, symbol):
    """🎯 Smart ATM Strike Locator using Configured Gaps"""
    if not spot or spot <= 0: return 0
    symbol = str(symbol).upper()
    
    gaps = OPTION_CHAIN_CONFIG.get("strike_gap", {})
    step = 0
    if "SENSEX" in symbol: step = gaps.get("SENSEX", 100)
    elif "BANK" in symbol: step = gaps.get("BANKNIFTY", 100)
    elif "FIN" in symbol: step = gaps.get("FINNIFTY", 50)
    elif "MID" in symbol: step = gaps.get("MIDCAPNIFTY", 25)
    elif "NIFTY" in symbol: step = gaps.get("NIFTY", 50)
    
    if step == 0:
        if spot > 10000: step = 100
        elif spot > 5000: step = 50
        elif spot > 1000: step = 20
        else: step = 5
        
    return round(spot / step) * step

def pick_professional_expiry(future_expiries, symbol="NIFTY", is_3pm=False):
    """🏛 EXPIRY PICKUP LOGIC (Professional Style)
    Returns: (target_expiry, current_near_expiry_if_skipped)
    """
    if not future_expiries: return None, None
    now = datetime.now()
    today_dt = now.date()
    
    valid_exp_dts = []
    for e in future_expiries:
        try:
            dt = datetime.strptime(e, "%Y-%m-%d").date()
            if dt >= today_dt: valid_exp_dts.append(dt)
        except: continue
        
    valid_exp_dts.sort()
    if not valid_exp_dts: return None, None
    
    nearest = valid_exp_dts[0].strftime("%Y-%m-%d")
    days_to_nearest = (valid_exp_dts[0] - today_dt).days
    
    if days_to_nearest <= 3 and len(valid_exp_dts) > 1:
        # Suggesting Next Expiry
        return valid_exp_dts[1].strftime("%Y-%m-%d"), nearest
            
    return nearest, None

def get_nearest_active_expiry(expiries):
    """Backward Compatibility for existing logic"""
    today = datetime.now().date()
    future = []
    for e in expiries:
        try:
            dt = datetime.strptime(e, "%Y-%m-%d").date()
            if dt >= today: future.append(e)
        except: continue
    return sorted(future)[0] if future else None

def calculate_tf_score(df):
    """🏛 Dynamic Scoring following User's scoring Matrix (RSI, ADX, VOL)"""
    if df.empty or len(df) < 5:
        return {"score": 0, "trend": "NEUTRAL", "rsi": 50, "adx": 0, "vol": 1.0}
        
    last = df.iloc[-1]
    rsi = float(last.get('RSI', 50.0))
    adx = float(last.get('ADX', 0.0))
    vol_ratio = float(last.get('VolRatio', 1.0))
    
    # 🕵️ SCORE FACTOR (USER LOGIC)
    score = 0
    # RSI contribution
    if rsi < 30: score += 2
    elif rsi > 70: score -= 2
    elif rsi > 55: score += 1
    elif rsi < 45: score += 1

    # ADX contribution
    if adx > 25: score += 2
    elif adx > 15: score += 1

    # Volume contribution
    if vol_ratio > 2: score += 3
    elif vol_ratio > 1.5: score += 2
    elif vol_ratio > 1: score += 1

    # 🕵️ TREND CLASSIFICATION (USER LOGIC)
    if rsi > 60 and adx > 20: trend = "UP"
    elif rsi < 40 and adx > 20: trend = "DOWN"
    else: trend = "NEUTRAL"
    
    return {"score": score, "trend": trend, "rsi": rsi, "adx": adx, "vol": vol_ratio}

def get_mtf_signals(engine, symbol, key):
    """🎯 Multi-Timeframe Institutional Scoring Architecture"""
    from services.market_engine import calculate_indicators
    current_time = time.time()
    
    if symbol in MTF_CACHE:
        cache_data, cache_time = MTF_CACHE[symbol]
        if current_time - cache_time < MTF_CACHE_TTL:
            return cache_data

    try:
        # 1. Fetch TFs with Historical Fallback (Essential for Off-Market testing)
        intervals = {"5m": "5minute", "15m": "15minute", "60m": "60minute"}
        dfs = {}
        
        for label, interval in intervals.items():
            df = engine.get_intraday_candles(key, interval=interval)
            # If intraday is empty or insufficient for indicators (need ~50)
            if df.empty or len(df) < 50:
                res_days = 20 if interval == "60minute" else 10
                df = engine.get_historical_candles(key, interval=interval, days=res_days)
            
            # --- 🚀 TIER 2 FALLBACK: yfinance ---
            if df.empty or len(df) < 20:
                import yfinance as yf
                yf_interval = "5m" if label == "5m" else "15m" if label == "15m" else "60m"
                yf_ticker = f"{symbol}.NS"
                logger.debug(f"🔄 Upstox candle weak for {symbol}. Trying yf fallback for {label}...")
                df = yf.download(yf_ticker, period="5d", interval=yf_interval, progress=False, threads=False)
                if not df.empty:
                    from services.market_engine import flatten_columns
                    df = flatten_columns(df)
                    df.columns = [c.lower() for c in df.columns]
            
            dfs[label] = df
            
        # Verify all TFs have data
        missing = [lbl for lbl, df in dfs.items() if df.empty or len(df) < 5]
        if missing:
            logger.warning(f"⚠️ MTF Data Gap for {symbol}: {missing}")
            return None

        # 2. Score All TFs
        # Ensure indicators are calculated - calculate_indicators renames to Title Case
        indicators_5m = calculate_indicators(dfs["5m"])
        indicators_15m = calculate_indicators(dfs["15m"])
        indicators_60m = calculate_indicators(dfs["60m"])
        
        # calculate_indicators returns input df if too short, so we check for indicator column
        if 'RSI' not in indicators_5m.columns:
            logger.warning(f"⚠️ Indicators (RSI) missing for {symbol}")
            # return None # Don't block, just use defaults in score

        mtf_data = {
            "5m": calculate_tf_score(indicators_5m),
            "15m": calculate_tf_score(indicators_15m),
            "1h": calculate_tf_score(indicators_60m)
        }

        MTF_CACHE[symbol] = (mtf_data, current_time)
        return mtf_data
    except Exception as e:
        logger.error(f"❌ MTF Scoring Error for {symbol}: {e}")
        return None

def get_option_chain_analysis(engine, symbol, is_3pm=False):
    """🏛 STEP 3 to 6 — Professional Option Chain Flow"""
    global OPTION_CHAIN_MEM
    now_ts = time.time()
    
    cache_key = f"{symbol}_{'3PM' if is_3pm else 'REG'}"
    if cache_key in OPTION_CHAIN_MEM:
        data, ts = OPTION_CHAIN_MEM[cache_key]
        if now_ts - ts < CHAINS_TTL: return data

    try:
        inst_key = engine.get_instrument_key(symbol)
        if not inst_key: return None
        
        # 1. Get Expiries
        expiries = engine.get_expiry_dates_via_sdk(inst_key)
        target_expiry, near_expiry = pick_professional_expiry(expiries, is_3pm=is_3pm)
        if not target_expiry: return None
        
        # 2. Fetch Chain
        chain = engine.get_option_chain_via_sdk(inst_key, target_expiry)
        
        # 3. Process OI & LTP
        rows = []
        for strike in chain:
            rows.append({
                "strike": strike.strike_price,
                "call_oi": strike.call_options.market_data.oi if strike.call_options else 0,
                "put_oi": strike.put_options.market_data.oi if strike.put_options else 0,
                "call_ltp": strike.call_options.market_data.ltp if strike.call_options else 0,
                "put_ltp": strike.put_options.market_data.ltp if strike.put_options else 0,
                "raw": strike
            })
        
        df = pd.DataFrame(rows)
        if df.empty: return None
        
        # 4. PCR & S/R
        total_call_oi = df['call_oi'].sum()
        total_put_oi = df['put_oi'].sum()
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        max_call_row = df.loc[df['call_oi'].idxmax()]
        max_put_row = df.loc[df['put_oi'].idxmax()]
        
        analysis = {
            "pcr": round(pcr, 2),
            "resistance": max_call_row['strike'],
            "support": max_put_row['strike'],
            "expiry": target_expiry,
            "near_expiry": near_expiry,
            "df": df,
            "chain": chain
        }
        
        OPTION_CHAIN_MEM[cache_key] = (analysis, now_ts)
        return analysis
    except Exception as e:
        logger.error(f"Option Chain Error for {symbol}: {e}")
        return None

# -----------------------------------------------
# 🏛️ GREEKS & PRICING ENGINE (Simplified Black-Scholes)
# -----------------------------------------------

def calculate_greeks(spot, strike, dte, volatility=0.20, r=0.07):
    """🧠 Calculate Option Greeks (Simplified for Python)"""
    from math import log, sqrt, exp, pi
    from scipy.stats import norm
    
    if dte <= 0: return {"delta_ce": 0.5, "delta_pe": -0.5}
    
    T = dte / 365.0
    S = float(spot)
    K = float(strike)
    
    try:
        d1 = (log(S / K) + (r + volatility**2 / 2) * T) / (volatility * sqrt(T))
        delta_ce = norm.cdf(d1)
        delta_pe = delta_ce - 1.0
        return {"delta_ce": round(delta_ce, 2), "delta_pe": round(delta_pe, 2)}
    except:
        return {"delta_ce": 0.5, "delta_pe": -0.5}

def choose_smart_itm_strike(analysis, spot, option_type="CE", target_delta=0.65):
    """🎯 Selects the best ITM strike based on Delta proximity"""
    if not analysis or 'df' not in analysis: return None
    
    df = analysis['df'].copy()
    dte = (datetime.strptime(analysis['expiry'], "%Y-%m-%d") - datetime.now()).days
    if dte < 0: dte = 0
    
    df['delta'] = df['strike'].apply(lambda k: calculate_greeks(spot, k, dte)['delta_ce' if option_type == "CE" else 'delta_pe'])
    
    if option_type == "CE":
        # CE: ITM means strike < spot, positive delta
        itm = df[(df['strike'] < spot) & (df['delta'] >= 0.5)].copy()
        itm['diff'] = abs(itm['delta'] - target_delta)
        best = itm.sort_values(['diff', 'call_oi'], ascending=[True, False])
    else:
        # PE: ITM means strike > spot, negative delta
        itm = df[(df['strike'] > spot) & (df['delta'] <= -0.5)].copy()
        itm['diff'] = abs(abs(itm['delta']) - target_delta)
        best = itm.sort_values(['diff', 'put_oi'], ascending=[True, False])
        
    return best.iloc[0].to_dict() if not best.empty else None



def compute_winning_confidence_score(symbol, mtf_status, vol_ratio, delta, adx=25, oi_chg=0):
    """🏆 Multi-Factor Institutional Winning Confidence Score (0-10)"""
    score = 0.0
    
    # 1. MTF Trend Alignment (30%) -> 3.0 pts
    # User Rule: Align with 5m, 15m, and 1h
    alignment_count = 0
    target_trend = "UP" if delta > 0 else "DOWN"
    
    if mtf_status.get("5m", {}).get("trend") == target_trend: alignment_count += 1
    if mtf_status.get("15m", {}).get("trend") == target_trend: alignment_count += 1
    if mtf_status.get("1h", {}).get("trend") == target_trend: alignment_count += 1
    
    score += alignment_count * 1.0 # 1 pt per aligned timeframe
    
    # 2. Volume / OI Surge (25%) -> 2.5 pts
    if vol_ratio > 2.5: score += 1.5
    elif vol_ratio > 1.5: score += 1.0
    elif vol_ratio > 1.2: score += 0.5
    
    if oi_chg > 0.05: score += 1.0 # 5% OI buildup
    elif oi_chg > 0.02: score += 0.5
    
    # 3. Greeks & Price Action (25%) -> 2.5 pts
    # High Delta ITM is safer for institutional trades
    if abs(delta) >= 0.70: score += 1.5
    elif abs(delta) >= 0.60: score += 1.0
    
    if adx > 25: score += 1.0 # Strong Trend
    elif adx > 18: score += 0.5
    
    # 4. Supply/Demand Alignment (20%) -> 2.0 pts
    # Heuristic: FII bias or Sector Rotation
    if SECTOR_ROTATION.get(symbol) == ("BULLISH 🚀" if delta > 0 else "BEARISH 🩸"): 
        score += 2.0
    
    return min(10.0, round(score, 2))

def entry_engine(engine, symbol, spot, index_df, vix_df, pcr_value=1.0, threshold=3):
    """
    🚀 Ultimate Entry Engine:
    Combines MTF scoring + Index bias + Option chain + Confidence score
    """
    # 1. Multi-Timeframe Scoring
    inst_key = engine.get_instrument_key(symbol)
    mtf_data = get_mtf_signals(engine, symbol, inst_key)
    if not mtf_data:
        return {"PASS": False, "reason": "MTF data missing", "confidence": 0, "type": "WAIT", "mtf": {}}

    short = mtf_data.get("5m", {})
    medium = mtf_data.get("15m", {})
    long = mtf_data.get("1h", {})

    # 2. Index Bias (from PCR + VIX + Trend)
    index_bias = market_sentiment(index_df, pcr_value, vix_df)

    # 3. Option Chain Analysis
    chain_analysis = get_option_chain_analysis(engine, symbol)
    if not chain_analysis:
        return {"PASS": False, "reason": "Option chain missing", "confidence": 0, "type": "WAIT", "mtf": mtf_data}

    support = chain_analysis['support']
    resistance = chain_analysis['resistance']
    pcr = chain_analysis['pcr']

    # 4. Direction Decision
    final_type = None
    # BULLISH CASE
    if short['trend'] == "UP" and medium['trend'] == "UP" and "BULLISH" in index_bias and spot > support:
        final_type = "CE"
    # BEARISH CASE
    elif short['trend'] == "DOWN" and medium['trend'] == "DOWN" and "BEARISH" in index_bias and spot < resistance:
        final_type = "PE"

    if not final_type:
        return {"PASS": False, "reason": "No directional bias or trend mismatch", "confidence": 0, "type": "WAIT", "mtf": mtf_data}

    # 5. Best ITM Strike Selection
    best_itm = choose_smart_itm_strike(chain_analysis, spot, final_type, target_delta=0.65)
    if not best_itm:
        return {"PASS": False, "reason": "No ITM strike found", "confidence": 0, "type": final_type, "mtf": mtf_data}

    strike = best_itm['strike']
    delta = best_itm.get('delta', 0.6)

    # 6. Confidence Score
    # Use short-term volatility and ADX for precision
    conf_score = compute_winning_confidence_score(
        symbol, mtf_data, short.get('vol', 1.0), delta,
        adx=short.get('adx', 20), oi_chg=0.05
    )

    # 7. Final PASS Decision
    pass_flag = conf_score >= threshold

    return {
        "symbol": symbol,
        "spot": spot,
        "strike": strike,
        "type": final_type,
        "mtf": mtf_data,
        "index_bias": index_bias,
        "pcr": pcr,
        "confidence": conf_score,
        "PASS": pass_flag,
        "expiry": chain_analysis['expiry'],
        "near_expiry": chain_analysis['near_expiry'],
        "analysis": chain_analysis
    }

def estimate_target_premium(current_ltp, delta, volatility_factor=0.1):
    """🎯 Target LTP = Current LTP ± (Delta * Volatility Factor * Current LTP)"""
    expected_move = current_ltp * volatility_factor
    target = current_ltp + (abs(delta) * expected_move)
    return round(target, 2)

def estimate_target_time(adx_val=25, is_scalp=False):
    """🕒 Dynamic Target Time Estimation based on Volatility/ADX"""
    if is_scalp:
        offset = 30 if adx_val > 25 else 60
    else:
        offset = 120 if adx_val > 25 else 240
        
    target_time = datetime.now() + timedelta(minutes=offset)
    return target_time.strftime("%I:%M %p") # e.g. 02:30 PM

ALERTS_COOLDOWN = {} # key -> timestamp

def choose_strike_professional(spot, symbol, index_trend, ranking_score=0, is_3pm=False):
    """�️ ULTIMATE PROFESSIONAL STRATEGY ENGINE
    Integrates MTF + Scoring + Greeks + Order Blocks
    """
    engine = get_upstox_engine()
    analysis = get_option_chain_analysis(engine, symbol, is_3pm=is_3pm)
    if not analysis: return None, None, None, "SCANNING"
    
    # 1. MTF Bias Alignment
    inst_key = engine.get_instrument_key(symbol)
    mtf = get_mtf_signals(engine, symbol, inst_key)
    bias = mtf.get("Intraday", "Neutral")
    
    # 2. Refined Selection using Score
    # Score = Trend + PCR + Spot vs S/R
    raw_pcr = analysis['pcr']
    
    final_type = None
    if "Bull" in bias or (raw_pcr > 1.1 and spot > analysis['support']):
        final_type = "CE"
    elif "Bear" in bias or (raw_pcr < 0.9 and spot < analysis['resistance']):
        final_type = "PE"
        
    if not final_type and is_3pm:
        final_type = "CE" if index_trend == "BULLISH" else "PE"

    if not final_type: return None, None, None, "WAITING"

    # 3. Best ITM Pick
    best_itm = choose_smart_itm_strike(analysis, spot, final_type, target_delta=0.70)
    if not best_itm: return None, None, None, "NO LIQUIDITY"
    
    strike = best_itm['strike']
    tag = "PRO BOT ✅" if abs(best_itm.get('delta', 0)) >= 0.65 else "AUTO 🤖"
    if is_3pm: tag = "🏛️ 3PM POWER"
    
    return strike, final_type, analysis['expiry'], tag

    if not option_type: return None, None, None, "WAIT"
    
    return selected_strike, option_type, premium, tag

def premium_quality_filter(premium, decay, vol_ratio):
    """🎯 STEP 3 — PREMIUM STRUCTURE FILTER (Professional Rules)"""
    if premium < 50 or premium > 180:
        return False
    if decay > 65:
        return False
    if vol_ratio < 1.5:
        return False
    return True

def get_option_ltp(engine, symbol, strike, option_type, target_expiry=None):
    """Fetch actual Option Price from Upstox with high precision matching and Multi-Source Fallback"""
    if not strike or strike <= 0: return 0
    cache_key = f"{symbol}_{strike}_{option_type}_{target_expiry}"
    now = time.time()
    
    if cache_key in OPTION_LTP_CACHE:
        val, ts = OPTION_LTP_CACHE[cache_key]
        if now - ts < OPTION_LTP_TTL:
            return val

    try:
        idx_key = engine.get_instrument_key(symbol)
        if not idx_key: return 0
        
        if not target_expiry:
            expiries = engine.get_expiry_dates_via_sdk(idx_key)
            target_expiry, _ = pick_professional_expiry(expiries, symbol=symbol)
        
        if not target_expiry: return 0
        
        # 🟢 Try 1: SDK Option Chain
        opt_key = None
        chain = engine.get_option_chain_via_sdk(idx_key, target_expiry)
        if chain:
            for item in chain:
                if abs(item.strike_price - float(strike)) < 0.1:
                    side_data = item.call_options if option_type == "CE" else item.put_options
                    if side_data:
                        opt_key = side_data.instrument_key
                        break
        
        # 🟢 Try 2: HTTP Option Chain (If SDK failed or returned empty)
        if not opt_key:
            http_chain = engine.get_option_chain(idx_key, target_expiry)
            for item in http_chain:
                if abs(item.get('strike_price', 0) - float(strike)) < 0.1:
                    side_key = 'call_options' if option_type == "CE" else 'put_options'
                    if side_key in item and item[side_key]:
                        opt_key = item[side_key].get('instrument_key')
                        break
                        
        if opt_key:
            # Try 1: Streamer (Real-time)
            result = get_live_ltp(opt_key) or 0
            
            # Try 2: Quotes (Exchange Snapshot)
            if result <= 0:
                quotes = engine.get_market_quote([opt_key], mode="ltp")
                if opt_key in quotes:
                    result = float(quotes[opt_key].get('last_price', 0))
                    if result <= 0: result = float(quotes[opt_key].get('cp', 0))
            
            # Try 3: Historical Full Quote (Deep Fallback)
            if result <= 0:
                quotes = engine.get_market_quote([opt_key], mode="full")
                if opt_key in quotes:
                    result = float(quotes[opt_key].get('last_price', 0))
                    if result <= 0: result = float(quotes[opt_key].get('cp', 0))

            if result > 0:
                logger.debug(f"💎 Found Premium for {symbol} {strike} {option_type}: ₹{result}")
                OPTION_LTP_CACHE[cache_key] = (result, now)
                return result
    except Exception as e:
        logger.error(f"Precision LTP Error: {e}")
    return 0

def calculate_adx(df, window=14):
    """🏛 📊 ADX Calculation (True Institutional Momentum)"""
    if len(df) < window * 2: return 0
    df = df.copy()
    # Handle both close/Close casing
    c_col = 'Close' if 'Close' in df.columns else 'close'
    df['tr'] = np.maximum(df['high'] - df['low'], 
                         np.maximum(abs(df['high'] - df[c_col].shift(1)), 
                                  abs(df['low'] - df[c_col].shift(1))))
    df['plus_dm'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']), 
                            np.maximum(df['high'] - df['high'].shift(1), 0), 0)
    df['minus_dm'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)), 
                             np.maximum(df['low'].shift(1) - df['low'], 0), 0)
    
    df['atr'] = df['tr'].rolling(window=window).mean()
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=window).mean() / df['atr'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=window).mean() / df['atr'])
    
    df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']).replace(0, 0.001)
    adx = df['dx'].rolling(window=window).mean().iloc[-1]
    return adx

def scalper_indicator_check(df, engine=None, symbol=None, threshold=3):
    """🏆 Multi-Timeframe Scoring Integration (User's Final Decision Logic)"""
    from services.market_engine import calculate_indicators
    
    if df.empty or len(df) < 5:
        return False, False, 50.0, 1.0, 0, 0.0, "NEUTRAL"
    
    # 1. Short-Term Indicators
    df = calculate_indicators(df)
    st = calculate_tf_score(df)
    
    short_score = st['score']
    short_trend = st['trend']
    rsi, adx, vol = st['rsi'], st['adx'], st['vol']
    
    # Defaults
    medium_score = 0; medium_trend = "NEUTRAL"
    long_score = 0; long_trend = "NEUTRAL"
    pass_flag = False
    
    # 2. MTF Scoring Decision Flow (USER LOGIC)
    if engine and symbol:
        inst_key = engine.get_instrument_key(symbol)
        mtf_data = get_mtf_signals(engine, symbol, inst_key)
        
        if mtf_data:
            medium_score = mtf_data['15m']['score']
            medium_trend = mtf_data['15m']['trend']
            long_score = mtf_data['1h']['score']
            long_trend = mtf_data['1h']['trend']
            
            # 🚀 USER RULE: Final Decision Logic
            pass_flag = (
                short_score >= threshold and
                medium_score >= threshold and
                short_trend == medium_trend and
                long_trend in [short_trend, "NEUTRAL"]
            )
    else:
        # Emergency Fallback
        if short_score >= threshold: pass_flag = True
    
    is_bullish = pass_flag and (short_trend == "UP")
    is_bearish = pass_flag and (short_trend == "DOWN")
    
    return is_bullish, is_bearish, rsi, vol, short_score, adx, short_trend

def calculate_strength_score(rsi, vol_ratio):
    """Elite Strength Filter: Returns SIGNED score (Fix 1: Score Is Signed)"""
    direction = 1 if rsi > 50 else -1
    rsi_score = abs(rsi - 50) * 1.5
    vol_score = min(30, vol_ratio * 5)
    return (rsi_score + vol_score) * direction

def get_premium_breakdown(spot, strike, option_type, premium):
    """Premium Intelligence: Intrinsic vs Time Value split"""
    if option_type == "CE":
        intrinsic = max(0, spot - strike)
    else:
        intrinsic = max(0, strike - spot)
    
    time_value = max(0, premium - intrinsic)
    decay_risk = (time_value / premium * 100) if premium > 0 else 100
    return intrinsic, time_value, decay_risk

def calculate_index_bias(candidates_map):
    """🔥 Heavyweight Bias Logic: Calculates Index momentum based on actual component weightage."""
    index_alerts = []
    for idx_name, components in INDEX_WEIGHTS.items():
        bull_weight = 0
        bear_weight = 0
        total_tracked_weight = sum(components.values())
        details = []
        for stock_ns, weight in components.items():
            stock = stock_ns.replace(".NS", "")
            if stock in candidates_map:
                c = candidates_map[stock]
                if c['is_bull']:
                    bull_weight += weight
                    details.append(f"🟢 {stock}({weight}%)")
                else:
                    bear_weight += weight
                    details.append(f"🔴 {stock}({weight}%)")
        
        bull_pct = (bull_weight / total_tracked_weight) * 100
        bear_pct = (bear_weight / total_tracked_weight) * 100
        
        if bull_pct >= 60:
            index_alerts.append({"index": idx_name, "type": "CE", "bias_pct": bull_pct, "components": details})
        elif bear_pct >= 60:
            index_alerts.append({"index": idx_name, "type": "PE", "bias_pct": bear_pct, "components": details})
    return index_alerts

def calculate_pcr_data(engine, look_at_next_month=False):
    """📊 Market-Wide PCR Logic (SDK based) - Ultimate Reliability"""
    pcr_stats = {
        "overall": {"ce_cnt": 0, "pe_cnt": 0, "ce_oi": 0, "pe_oi": 0},
        "NIFTY": {"ce_cnt": 0, "pe_cnt": 0, "ce_oi": 0, "pe_oi": 0},
        "BANKNIFTY": {"ce_cnt": 0, "pe_cnt": 0, "ce_oi": 0, "pe_oi": 0}
    }
    
    targets = {
        "NIFTY": "NSE_INDEX|Nifty 50",
        "BANKNIFTY": "NSE_INDEX|Nifty Bank"
    }
    
    for label, target_key in targets.items():
        expiries = engine.get_expiry_dates_via_sdk(target_key)
        if not expiries: continue
        
        expiries.sort()
        if look_at_next_month and len(expiries) > 1:
            expiry_date = expiries[1] 
        else:
            expiry_date = get_nearest_active_expiry(expiries)
            
        if not expiry_date: continue
        chain_data = engine.get_option_chain_via_sdk(target_key, expiry_date)
        
        for contract in chain_data:
            ce = contract.call_options
            pe = contract.put_options
            if ce and ce.market_data:
                pcr_stats[label]["ce_cnt"] += 1
                pcr_stats[label]["ce_oi"] += ce.market_data.oi
                pcr_stats["overall"]["ce_cnt"] += 1
                pcr_stats["overall"]["ce_oi"] += ce.market_data.oi
            if pe and pe.market_data:
                pcr_stats[label]["pe_cnt"] += 1
                pcr_stats[label]["pe_oi"] += pe.market_data.oi
                pcr_stats["overall"]["pe_cnt"] += 1
                pcr_stats["overall"]["pe_oi"] += pe.market_data.oi
                
    for k in pcr_stats:
        coi = pcr_stats[k]["ce_oi"]
        poi = pcr_stats[k]["pe_oi"]
        pcr_stats[k]["pcr"] = round(poi / coi, 2) if coi > 0 else 0
        pcr_stats[k]["bias"] = "BULLISH" if pcr_stats[k]["pcr"] > 1.2 else "BEARISH" if pcr_stats[k]["pcr"] < 0.8 else "NEUTRAL"
        
    return pcr_stats
def analyze_sector_rotation(engine, nifty_df):
    """Idea: Compare sector index strength vs NIFTY (Step A)"""
    sectors = {
        "BANK": "NSE_INDEX|Nifty Bank", "IT": "NSE_INDEX|Nifty IT", 
        "PHARMA": "NSE_INDEX|Nifty Pharma", "FMCG": "NSE_INDEX|Nifty FMCG",
        "AUTO": "NSE_INDEX|Nifty Auto", "METAL": "NSE_INDEX|Nifty Metal"
    }
    rotation_map = {}
    try:
        # Helper for case-insensitive return calculation
        def get_ret(df_in):
            col = 'Close' if 'Close' in df_in.columns else 'close'
            return (df_in[col].iloc[-1] - df_in[col].iloc[-5]) / df_in[col].iloc[-5] if len(df_in) >= 5 else 0

        n_ret = get_ret(nifty_df)
        for name, key in sectors.items():
            sdf = engine.get_intraday_candles(key, interval="5minute")
            if sdf.empty: continue
            s_ret = get_ret(sdf)
            if s_ret > n_ret * 1.5:
                rotation_map[name] = "STRONG_ROTATION"
            else:
                rotation_map[name] = "NORMAL"
    except: pass
    return rotation_map

def check_volatility_expansion(engine):
    """🅓 VOLATILITY EXPANSION (VIX FILTER)"""
    try:
        vix_key = "NSE_INDEX|India VIX"
        vix_df = engine.get_intraday_candles(vix_key, interval="5minute")
        if vix_df.empty or len(vix_df) < 10: return False
        
        v_close_col = 'Close' if 'Close' in vix_df.columns else 'close'
        recent_high = vix_df[v_close_col].rolling(10).max().iloc[-2]
        return vix_df[v_close_col].iloc[-1] > recent_high
    except: return False

def get_fii_bias_macro():
    """🅑 FII / DII FLOW BIAS (Daily net data simulation/placeholder)"""
    # Note: Real-time FII data usually arrives EOD. We use VIX stability as proxy during day.
    return "BULLISH" # Simplified for architecture

def get_oi_structure(symbol, current_oi, prev_oi, price_change):
    """🅒 OI + PRICE COMBO (Very Powerful)"""
    if current_oi == 0: return "NEUTRAL"
    oi_change = current_oi - prev_oi
    if price_change > 0 and oi_change > 0: return "LONG_BUILDUP"
    if price_change < 0 and oi_change > 0: return "SHORT_BUILDUP"
    if price_change > 0 and oi_change < 0: return "SHORT_COVERING"
    return "NEUTRAL"

def get_global_market_pulse():
    """🌎 Institutional Global Sentiment (Robust Fetch)"""
    results = {}
    try:
        symbols = list(GLOBAL_SENTIMENT_SYMBOLS.values())
        data = yf.download(symbols, period="2d", interval="5m", progress=False)
        if data.empty: return results
        
        close_data = data['Close']
        for name, sym in GLOBAL_SENTIMENT_SYMBOLS.items():
            if sym in close_data.columns:
                series = close_data[sym].dropna()
                if len(series) >= 2:
                    last_px = series.iloc[-1]
                    prev_px = series.iloc[-2]
                    chg = ((last_px - prev_px) / prev_px) * 100
                    results[name] = {"px": round(last_px, 2), "chg": round(chg, 2)}
    except: pass
    return results

def send_15min_summary(pcr_data, is_next_month=False):
    """📩 Premium 15-Minute Market Pulse Alert with Global Context"""
    status_icon = "🟢 LIVE"
    o = pcr_data["overall"]
    n = pcr_data["NIFTY"]
    b = pcr_data["BANKNIFTY"]
    global_pulse = get_global_market_pulse()
    
    title = f"{status_icon} 🏛️ *INSTITUTIONAL PULSE (MARCH)*" if is_next_month else f"{status_icon} 🏛️ *MARKET SENTIMENT PULSE*"
    
    def fmt_oi(val):
        if val >= 10000000: return f"{val/10000000:.2f}Cr"
        if val >= 100000: return f"{val/100000:.2f}L"
        return str(val)

    global_str = ""
    for name, data in global_pulse.items():
        icon = "📈" if data['chg'] > 0 else "📉"
        global_str += f"∟ {name}: `{data['chg']:.2f}%` {icon}\n"

    msg = (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"� **TIME**: `{datetime.now().strftime('%H:%M:%S')}`\n"
        f"🎭 **BIAS**: `{o['bias']}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌎 **GLOBAL CONTEXT**\n"
        f"{global_str if global_str else '∟ Syncing Global Data...'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 **NIFTY 50**\n"
        f"∟ PCR: `{n['pcr']}`\n"
        f"∟ CE: `{fmt_oi(n['ce_oi'])}` | PE: `{fmt_oi(n['pe_oi'])}`\n\n"
        f"📉 **BANKNIFTY**\n"
        f"∟ PCR: `{b['pcr']}`\n"
        f"∟ CE: `{fmt_oi(b['ce_oi'])}` | PE: `{fmt_oi(b['pe_oi'])}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **TOTAL PCR**: `{o['pcr']}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏛️ [OPEN TERMINAL]({AUTH_URL})\n\n"
        f"{SIGNATURE}"
    )
    send_telegram(msg)

def get_nifty_movers(engine, symbols, instrument_map):
    """🏛 STEP 1: Rank Top Momentum (Relative Strength) - Optimized Fetching (Fix B)"""
    global MOVERS_CACHE
    now = time.time()
    
    if now - MOVERS_CACHE["ts"] < MOVERS_TTL and MOVERS_CACHE["bulls"]:
        return MOVERS_CACHE["bulls"], MOVERS_CACHE["bears"]

    movers = []
    logger.info(f"📡 Updating NIFTY 50 Relative Strength (Every {MOVERS_TTL/60} mins)...")
    
    # Pre-fetch ALL live prices in BULK (Crucial for off-market or cold cache)
    all_keys = [instrument_map.get(s) for s in symbols if instrument_map.get(s)]
    quotes = engine.get_market_quote(all_keys, mode="ltp")
    for k, q in quotes.items():
        update_live_ltp(k, q.get('last_price', 0))

    for sym in symbols:
        try:
            key = instrument_map.get(sym)
            if not key: continue
            
            # Use live LTP (now populated by bulk fetch)
            ltp = get_live_ltp(key)
            if not ltp or ltp <= 0: continue
            
            # Fetch Daily candles once per cycle
            df = engine.get_historical_candles(key, interval="day", days=2)
            if df.empty: continue
            
            # Normalize columns
            df.columns = [c.lower() for c in df.columns]
            if 'close' not in df.columns: continue
            
            prev_close = df['close'].iloc[-1]
            pct_chg = ((ltp - prev_close) / prev_close) * 100
            movers.append({"symbol": sym, "pct": pct_chg, "ltp": ltp, "key": key})
        except: continue
    
    if not movers: return [], []
    
    # Sort: Top 10 Bulls & Top 10 Bears
    movers.sort(key=lambda x: x['pct'], reverse=True)
    top_bulls = movers[:10]
    top_bears = movers[-10:]
    
    MOVERS_CACHE = {"bulls": top_bulls, "bears": top_bears, "ts": now}
    return top_bulls, top_bears

def get_sector_bias_v2(cand_map):
    """🎯 STEP 2: Sector Rotation Detection"""
    sectors = {
        "BANKING": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
        "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
        "AUTO": ["TATAMOTORS", "MARUTI", "M&M", "EICHERMOT", "BAJAJ-AUTO"],
        "METAL": ["TATASTEEL", "JSWSTEEL", "HINDALCO"]
    }
    
    sector_sentiment = {}
    for sec, stocks in sectors.items():
        bulls = 0; bears = 0
        for s in stocks:
            if s in cand_map:
                if cand_map[s]['is_bull']: bulls += 1
                else: bears += 1
        
        if bulls >= 3: sector_sentiment[sec] = "BULLISH 🚀"
        elif bears >= 3: sector_sentiment[sec] = "BEARISH 🩸"
        else: sector_sentiment[sec] = "NEUTRAL"
    return sector_sentiment

# ==========================================
# 🏛️ SCHEDULER JOBS (Best Flow Implementation)
# ==========================================

def premarket_job():
    """PRE-MARKET SNAPSHOT (8:45 AM)"""
    logger.info("⏰ Scheduler: Running Pre-Market Job...")
    run_premarket_scan()

def live_sentiment_job():
    """LIVE SENTIMENT PULSE (15m)"""
    logger.info("⏰ Scheduler: Triggering Live Sentiment Analysis...")
    # This is also called in the main loop, but here for redundancy/scheduling
    engine = get_upstox_engine()
    nifty_key = INDICES.get("NIFTY") if "INDICES" in globals() else "NSE_INDEX|Nifty 50"
    idx_df = engine.get_intraday_candles(nifty_key, interval="15minute")
    vix_df = engine.get_intraday_candles("NSE_INDEX|India VIX", interval="5minute")
    sentiment = market_sentiment(idx_df, 1.0, vix_df)
    send_telegram(f"🟢 LIVE 🏛️ *Market Sentiment Pulse*: `{sentiment}`\n\n� *PrimeSkillDevelopment CEO : MuthuKumar krishnan*")

def midday_job():
    """MIDDAY REVIEW (12:00 PM)"""
    logger.info("⏰ Scheduler: Running Midday Review...")
    engine = get_upstox_engine()
    nifty_analysis = get_option_chain_analysis(engine, "NIFTY", is_3pm=False)
    pcr = nifty_analysis.get('pcr', 1.0)
    bias = "BULLISH �🚀" if pcr > 1.1 else "BEARISH 🩸" if pcr < 0.9 else "NEUTRAL"
    send_telegram(f"🏛️ **MIDDAY MARKET REVIEW**\n━━━━━━━━━━━━━━━━━━━━━\n📍 **NIFTY PCR**: `{pcr:.2f}`\n📊 **BIAS**: `{bias}`\n📡 **STATUS**: `Monitoring Volume Spikes`\n━━━━━━━━━━━━━━━━━━━━━\n👤 *MuthuKumar krishnan*")

def postmarket_job():
    """POST-MARKET REVIEW (6:00 PM)"""
    logger.info("⏰ Scheduler: Running Post-Market Summary...")
    engine = get_upstox_engine()
    run_postmarket_scan(NIFTY_50_STOCKS, engine)

def setup_scheduler():
    schedule.every().day.at("08:45").do(premarket_job)
    schedule.every(15).minutes.do(live_sentiment_job)
    # Opportunity scans (5m, 1m) are integrated into the high-precision loop below
    schedule.every().day.at("12:00").do(midday_job)
    schedule.every().day.at("18:00").do(postmarket_job)
    logger.info("📅 Schedule setup complete.")

def generate_elite_index_alerts(engine, index_alerts_list, alerts_sent, current_ts):
    """👑 Generate High-Conviction Best ITM Alerts for Indices using Multi-Factor Score"""
    for alert in index_alerts_list:
        sym = alert['index']
        status = "BULLISH" if alert['type'] == "CE" else "BEARISH"
        
        alert_key = f"ELITE_{sym}_{status}"
        if current_ts - alerts_sent.get(alert_key, {}).get('ts', 0) > 1800: # 30 min cooldown
            spot = engine.get_spot_via_sdk(engine.get_instrument_key(sym))
            if not spot: continue
            
            # Use Professional Engine to pick the BEST ITM call
            strike, opt_type, exp, tag = choose_strike_professional(spot, sym, status, ranking_score=90)
            
            if strike and opt_type:
                prem = get_option_ltp(engine, sym, strike, opt_type, exp)
                if prem > 0:
                    # Calculate Greeks for Delta
                    dte = (datetime.strptime(exp, "%Y-%m-%d").date() - datetime.now().date()).days
                    greeks = calculate_greeks(spot, strike, dte)
                    delta = greeks['delta_ce' if opt_type == "CE" else 'delta_pe']
                    
                    # Compute Score
                    # --- 🌍 MULTI-TIMEFRAME ALIGNMENT & SCORING ---
                    mtf_data = get_mtf_signals(engine, sym, engine.get_instrument_key(sym))
                    _, mtf_status_summary = get_mtf_confluence(sym, mtf_data=mtf_data)
                    
                    conf_score = compute_winning_confidence_score(sym, mtf_data or {}, 2.0, delta)
                    
                    if conf_score >= 4.0: # Trigger alert only if score is high enough
                        signal = {
                            "symbol": sym, "type": opt_type, "strike": strike, "spot": spot,
                            "premium": prem, "expiry": exp, "tag": f"💎 ELITE {status}",
                            "confidence_score": conf_score, "delta": delta,
                            "premium_pct": round((prem / spot) * 100, 2) if spot > 0 else 0,
                            "stop_loss": prem * 0.85, "target": estimate_target_premium(prem, delta),
                            "mtf_signals": mtf_data or {}
                        }
                        if send_trade_alert(signal):
                            alerts_sent[alert_key] = {"ts": current_ts, "status": "Active"}
                            save_alerts_sent(alerts_sent)
                            logger.info(f"🏆 Elite Index Alert Sent: {sym} {opt_type} {strike} Score: {conf_score}")

# ==========================================
# 🚀 MASTER SCANNER ENGINE
# ==========================================

# ==========================================
# 🏛 PARALLEL SCANNER STATE (Shared Context)
# ==========================================

# ==========================================
# 🏛 PARALLEL SCANNER ARCHITECTURE
# ==========================================

class ScannerContext:
    def __init__(self, engine, instrument_map):
        self.engine = engine
        self.map = instrument_map
        self.nifty_df = pd.DataFrame()
        self.vix_df = pd.DataFrame()
        self.idx_trend = "NEUTRAL"
        self.pcr_value = 1.0
        self.active_signals = load_active_signals()
        self.alerts_sent = load_alerts_sent()
        self.daily_stats = load_daily_stats()
        self.now = datetime.now()
        self.is_new_cycle = False
        self.power_mode = False
        self.lock = threading.Lock()

def index_scanner_loop(context):
    """🏛 TIER 1: INDEX, MACRO & LIFECYCLE MANAGER (Ultra Responsive)"""
    logger.info("📡 Index Scanner Loop Active — Handling Macros & Trades")
    engine = context.engine
    instrument_map = context.map
    
    last_summary_time = time.time()
    last_sentiment_time = time.time()
    sent_premarket = False
    sent_postmarket = False
    
    while True:
        try:
            current_ts = time.time()
            now = datetime.now()
            context.now = now
            context.power_mode = is_power_window()
            
            # 1. TIMED SYSTEM TRIGGERS
            if now.hour == 9 and 0 <= now.minute < 15 and not sent_premarket:
                run_premarket_scan(); sent_premarket = True
            if now.hour == 15 and 45 <= now.minute < 55 and not sent_postmarket:
                run_postmarket_scan(["NIFTY", "BANKNIFTY", "RELIANCE"], engine); sent_postmarket = True
            if now.hour == 0 and now.minute == 0:
                sent_premarket = sent_postmarket = False
                
            # 2. NEXT DAY EXIT ENGINE
            if now.hour == 9 and 20 <= now.minute < 22:
                for sig in context.active_signals:
                    if sig.get('tag') == "🏛 3PM POWER CLOSE":
                        sig['status'] = "Hold Exit"; send_trade_alert(sig, is_update=True)
                with context.lock:
                    context.active_signals = [s for s in context.active_signals if s.get('tag') != "🏛 3PM POWER CLOSE"]
                save_active_signals(context.active_signals)

            # 3. LIFECYCLE MONITORING (Target/SL Hits)
            still_active = []
            for sig in context.active_signals:
                ltp = get_option_ltp(engine, sig['symbol'], sig['strike'], sig['type'])
                if not ltp: still_active.append(sig); continue
                if ltp >= sig['target']:
                    sig['status'] = "Target Achieved ✅"; send_trade_alert(sig, is_update=True)
                elif ltp <= sig['stop_loss']:
                    sig['status'] = "Stopped Out ❌"; send_trade_alert(sig, is_update=True)
                else: still_active.append(sig)
            with context.lock: context.active_signals = still_active
            save_active_signals(context.active_signals)

            # 4. GLOBAL MACRO SYNC
            nifty_key = instrument_map.get("NIFTY", "NSE_INDEX|Nifty 50")
            vix_key = "NSE_INDEX|India VIX"
            
            nifty_df = engine.get_intraday_candles(nifty_key, interval="5minute")
            vix_df = engine.get_intraday_candles(vix_key, interval="5minute")
            
            with context.lock:
                if not nifty_df.empty: 
                    context.nifty_df = calculate_indicators(nifty_df)
                    n_col = 'Close' if 'Close' in context.nifty_df.columns else 'close'
                    n_ema = context.nifty_df[n_col].ewm(span=20, adjust=False).mean()
                    context.idx_trend = "BULLISH" if context.nifty_df[n_col].iloc[-1] > n_ema.iloc[-1] else "BEARISH"
                if not vix_df.empty: context.vix_df = calculate_indicators(vix_df)
                
                nifty_analysis = get_option_chain_analysis(engine, "NIFTY", is_3pm=context.power_mode)
                context.pcr_value = nifty_analysis['pcr'] if nifty_analysis else 1.0
                
                # --- 🚀 ELITE INDEX ALERTS ---
                index_alerts = calculate_index_bias({"NIFTY": context.nifty_df})
                generate_elite_index_alerts(engine, index_alerts, context.alerts_sent, current_ts)

            # 5. PERIODIC SUMMARY
            if current_ts - last_summary_time >= SUMMARY_INTERVAL:
                send_15min_summary({"NIFTY": {"pcr": context.pcr_value}}, False)
                last_summary_time = current_ts
            
            schedule.run_pending()
            time.sleep(15) 
            
        except Exception as e:
            logger.error(f"❌ Index Loop Error: {e}"); time.sleep(10)

def stock_scanner_loop(context):
    """🏛 TIER 2: STOCK SCANNER (High-Speed Batch Scanning)"""
    logger.info("📡 Stock Scanner Loop Active — Processing Global Stocks")
    engine = context.engine
    instrument_map = context.map
    fo_symbols = [s.replace(".NS", "") for s in STOCKS]
    prev_prices = {}
    last_cycle_min = -1
    
    while True:
        try:
            now = datetime.now()
            current_ts = time.time()
            context.is_new_cycle = is_new_5min_candle() and now.minute != last_cycle_min
            if context.is_new_cycle: last_cycle_min = now.minute
            
            if context.is_new_cycle or not MOVERS_CACHE["bulls"]:
                get_nifty_movers(engine, STOCKS, instrument_map)

            deep_scan_list = [s for s in fo_symbols if s in instrument_map]
            
            batch_size = 5
            for i in range(0, len(deep_scan_list), batch_size):
                batch = deep_scan_list[i : i + batch_size]
                for sym in batch:
                    key = instrument_map.get(sym)
                    spot = get_live_ltp(key)
                    if not spot: continue
                    
                    price_jump = abs(spot - prev_prices.get(key, spot)) / spot * 100
                    prev_prices[key] = spot
                    
                    if context.is_new_cycle or price_jump > 0.3 or context.power_mode:
                        with context.lock:
                            n_df, v_df, pcr = context.nifty_df, context.vix_df, context.pcr_value
                        
                        decision = entry_engine(engine, sym, spot, n_df, v_df, pcr_value=pcr)
                        
                        if context.is_new_cycle or price_jump > 0.5:
                            print(f"🔍 DEBUG [{sym}] | LTP: {spot:.2f} | Score: {decision['confidence']} | PASS: {decision['PASS']}")

                        if decision["PASS"]:
                            with context.lock:
                                if can_take_trade(sym, context.active_signals):
                                    prem = get_option_ltp(engine, sym, decision['strike'], decision['type'], target_expiry=decision.get("expiry"))
                                    if prem > 0:
                                        entry = {
                                            "symbol": sym, "type": decision['type'], "strike": decision['strike'], 
                                            "spot": spot, "premium": prem, "score": decision['confidence'], 
                                            "expiry": decision['expiry'], "target": estimate_target_premium(prem, 0.65), 
                                            "stop_loss": round(prem * 0.85, 2), "time": now.strftime("%H:%M:%S"), "tag": "🏛 UNIFIED"
                                        }
                                        if send_trade_alert(entry):
                                            context.active_signals.append(entry)
                                            save_active_signals(context.active_signals)
                                            logger.info(f"🏆 Unified signal: {sym}")
                
                time.sleep(0.5) 
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Stock Loop Error: {e}"); time.sleep(10)

def run_master_scanner():
    engine = get_upstox_engine()
    logger.info("🔥 PARALLEL ENGINE INITIALIZING...")
    
    setup_scheduler()
    fo_symbols = [s.replace(".NS", "") for s in STOCKS]
    all_symbols = INDICES + fo_symbols
    
    instrument_map = {}
    for sym in all_symbols:
        k = engine.get_instrument_key(sym)
        if k: instrument_map[sym] = k
    
    get_streamer().start(initial_keys=list(instrument_map.values()))
    
    # Shared State Context
    context = ScannerContext(engine, instrument_map)
    
    # Spawn Index Thread
    threading.Thread(target=index_scanner_loop, args=(context,), daemon=True).start()
    
    # Run Stock Scanner in Main Thread
    stock_scanner_loop(context)

if __name__ == "__main__":
    run_master_scanner()
