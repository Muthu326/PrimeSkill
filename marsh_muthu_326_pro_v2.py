import os
import sys
import time
import json
import urllib.request
import urllib.parse
from datetime import datetime, time as dt_time
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Force UTF-8 encoding
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from utils.logger import setup_logger
from services.upstox_engine import get_upstox_engine
from config.config import ALL_FO_STOCKS, OPTION_CHAIN_CONFIG, INDEX_WEIGHTS
from services.market_engine import calculate_indicators, flatten_columns
from services.upstox_streamer import get_streamer, get_live_ltp
from config.extended_stocks import EXTENDED_STOCKS_LIST

# Load environment variables
load_dotenv()

# ==========================================
# ⚙️ INSTITUTIONAL CONFIGURATION (v2)
# ==========================================
logger = setup_logger("MarshMuthuProV2")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# AUTH URL for Dashboard
AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={os.getenv('UPSTOX_API_KEY')}&redirect_uri=http://localhost:8501"

# Risk Engine Settings
RISK_PER_TRADE_PCT = 0.02  # 2% Risk 
MAX_DAILY_LOSS_PCT = 0.05  # 5% Daily Stop
TIME_EXIT = dt_time(14, 45) # 2:45 PM Square off
SCORE_THRESHOLD = 70       # Quality Filter (Institutional Rank)

# Performance Tracking
DAILY_RESULTS_FILE = "data/pro_v2_stats.json"
ACTIVE_SIGNALS_FILE = "data/pro_v2_active.json"
MOMENTUM_LIST_FILE = "data/pro_v2_momentum_list.json"
os.makedirs("data", exist_ok=True)

# Lot Sizes (Standard Fallback - Real ones fetched via SDK)
LOT_SIZES = {
    "NIFTY": 75, "BANKNIFTY": 15, "FINNIFTY": 40, "MIDCPNIFTY": 75, "SENSEX": 10
}

# ==========================================
# 🛠️ UTILITY FUNCTIONS
# ==========================================

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False

def get_live_capital():
    """🏛️ Dynamic Capital Engine (Live Based)"""
    engine = get_upstox_engine()
    funds = engine.get_user_funds()
    # Try to get equity margin
    equity = funds.get('equity', {})
    available_margin = float(equity.get('available_margin', 100000)) # Fallback to 1L
    return available_margin

def is_new_5min_candle():
    """📊 Step 3: 5-Min Candle Sync Properly"""
    now = datetime.now()
    return now.minute % 5 == 0 and now.second < 5

def get_expiry_list(engine, key):
    """🗂 Step 1: Fetch Expiry Dates"""
    try:
        expiries = engine.get_expiry_dates_via_sdk(key)
        return sorted(expiries)
    except: return []

def get_nearest_active_expiry(engine, key, symbol_context=""):
    """📊 Step 2: Identify Next Contract & Log Last 5"""
    expiries = get_expiry_list(engine, key)
    if not expiries: return None
    
    today = datetime.now().date()
    future_expiries = []
    for e in expiries:
        try:
            dt = datetime.strptime(e, "%Y-%m-%d").date()
            if dt >= today:
                future_expiries.append(e)
        except: continue
    
    # Context: Show last 5 expiries in logs
    last_5 = expiries[-5:]
    logger.info(f"📅 Expiry Context for {symbol_context}: {last_5} | Next: {future_expiries[0] if future_expiries else 'None'}")
    
    return future_expiries[0] if future_expiries else None

def get_atm_strike(spot, symbol):
    """🎯 Identify ATM Strike based on Index/Stock Price Steps"""
    gaps = OPTION_CHAIN_CONFIG.get("strike_gap", {})
    step = 5
    for idx_name, idx_step in gaps.items():
        if idx_name in symbol.upper():
            step = idx_step
            break
    else:
        if spot > 5000: step = 100
        elif spot > 1000: step = 20
        elif spot > 500: step = 10
        else: step = 5
    return int(round(spot / step) * step)

# ==========================================
# 🧠 INSTITUTIONAL CORE ENGINES
# ==========================================

def calculate_pro_score(df, rs_value=0):
    """
    💎 Institutional Scoring Model (120 Point Scale with RS)
    Factor            Points
    Breakout          +30
    Volume Spike      +20
    EMA Trend         +20
    ATR Expansion     +15
    VWAP Alignment    +15
    Relative Strength +20 (NEW)
    """
    if df.empty or len(df) < 50: return 0, "Wait"
    
    score = 0
    # Indicators should already be present in df
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 1. Breakout (+30)
    if last['Close'] > prev['High']: score += 30
    elif last['Close'] < prev['Low']: score -= 30 
    
    # 2. Volume Spike (+20)
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    if last['Volume'] > avg_vol * 1.5: score += 20 if score >= 0 else -20
    
    # 3. EMA Trend (+20)
    if last['EMA20'] > last['EMA50']: score += 20
    elif last['EMA20'] < last['EMA50']: score -= 20
    
    # 4. ATR Expansion (+15)
    if last['ATR'] > prev['ATR']: score += 15 if score >= 0 else -15
    
    # 5. VWAP Alignment (+15)
    if last['Close'] > last['VWAP']: score += 15
    elif last['Close'] < last['VWAP']: score -= 15
    
    # 6. Relative Strength (+20)
    if rs_value > 0.01: score += 20
    elif rs_value < -0.01: score -= 20
    
    # Determine Bias
    bias = "BULLISH" if score > 0 else "BEARISH" if score < 0 else "NEUTRAL"
    return abs(score), bias

def calculate_position_sizing(capital, entry_px, sl_px, symbol):
    """🏛️ Risk-Based Position Sizing (2% Rule)"""
    risk_amount = capital * RISK_PER_TRADE_PCT
    
    # Get Lot Size
    lot_size = LOT_SIZES.get(symbol, 1)
    if lot_size == 1:
        # Try to infer for stocks (usually 250-1000)
        lot_size = 1 # We'll fetch real one in main loop or use 1 for cash
        
    risk_per_point = abs(entry_px - sl_px)
    if risk_per_point == 0: return 0
    
    # Quantity = Risk Capital / (SL Points * Lot Size)
    # Here we return number of LOTS
    risk_per_lot = risk_per_point * lot_size
    lots = int(risk_amount / risk_per_lot) if risk_per_lot > 0 else 0
    
    return max(lots, 1) # Min 1 lot for alert suggestion

def get_atr_sl_target(df, entry, bias):
    """🎨 Smart SL & Target (ATR Based)"""
    atr = df['ATR'].iloc[-1]
    if bias == "BULLISH":
        sl = entry - (atr * 1.5)
        target = entry + (atr * 3.0)
    else:
        sl = entry + (atr * 1.5)
        target = entry - (atr * 3.0)
    return round(sl, 2), round(target, 2)

def classify_trend(df, mtf_df=None):
    """
    🏛️ PROFESSIONAL TREND CLASSIFICATION MODEL
    Classifies based on EMA structure, ADX (strength), and RSI (momentum).
    """
    if df.empty or len(df) < 50: return "NEUTRAL"
    
    # Ensure indicators are present
    if 'EMA200' not in df.columns:
        df = calculate_indicators(df)
        
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    close = last['Close']
    ema20 = last['EMA20']
    ema50 = last['EMA50']
    ema200 = last['EMA200']
    adx = last['ADX']
    rsi = last['RSI']
    vwap = last['VWAP']
    atr_expanding = last['ATR'] > prev['ATR']
    
    # --- 1. STRONG BULLISH ---
    if (close > ema20 > ema50 > ema200 and 
        adx > 25 and rsi > 60 and 
        close > vwap and atr_expanding):
        if mtf_df is not None and not mtf_df.empty:
            mtf_last = mtf_df.iloc[-1]
            if not (mtf_last['Close'] > mtf_last['EMA20'] > mtf_last['EMA50']):
                return "BULLISH"
        return "STRONG BULLISH"

    # --- 2. BULLISH ---
    elif (close > ema20 > ema50 and adx > 18 and rsi > 55):
        return "BULLISH"

    # --- 3. STRONG BEARISH ---
    elif (close < ema20 < ema50 < ema200 and 
          adx > 25 and rsi < 40 and 
          close < vwap and atr_expanding):
        if mtf_df is not None and not mtf_df.empty:
            mtf_last = mtf_df.iloc[-1]
            if not (mtf_last['Close'] < mtf_last['EMA20'] < mtf_last['EMA50']):
                return "BEARISH"
        return "STRONG BEARISH"

    # --- 4. BEARISH ---
    elif (close < ema20 < ema50 and adx > 18 and rsi < 45):
        return "BEARISH"

    return "NEUTRAL"

# ==========================================
# 🏛️ ENTRY LOGIC STRUCTURE (Professional)
# ==========================================

def index_allows_trade(index_trend, direction):
    """🔵 STEP 1 — INDEX FILTER"""
    if direction == "LONG":
        return index_trend in ["BULLISH", "STRONG BULLISH"]
    if direction == "SHORT":
        return index_trend in ["BEARISH", "STRONG BEARISH"]
    return False

def breakout_entry(df, direction):
    """🟢 BREAKOUT ENTRY (Momentum Style)"""
    close = df['Close'].iloc[-1]
    prev_high = df['High'].iloc[-2]
    prev_low = df['Low'].iloc[-2]
    volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume'].rolling(10).mean().iloc[-1]
    
    if direction == "LONG":
        if close > prev_high and volume > (avg_volume * 1.5):
            return "Breakout"
    if direction == "SHORT":
        if close < prev_low and volume > (avg_volume * 1.5):
            return "Breakout"
    return None

def pullback_entry(df, direction):
    """🟢 PULLBACK ENTRY (Safer Entry)"""
    close = df['Close'].iloc[-1]
    ema20 = df['EMA20'].iloc[-1]
    ema50 = df['EMA50'].iloc[-1]
    
    if direction == "LONG":
        # Pullback near EMA20 but stays above EMA50
        if close > ema50 and close <= (ema20 * 1.005):
            return "Pullback"
    if direction == "SHORT":
        if close < ema50 and close >= (ema20 * 0.995):
            return "Pullback"
    return None

def calculate_sl_target(df, entry_price, direction):
    """🔵 STEP 4 — STOP LOSS & TARGET (ATR-based)"""
    atr = df['ATR'].iloc[-1]
    if "BUY" in direction or "LONG" in direction:
        sl = entry_price - (atr * 1.5)
        target = entry_price + (atr * 3.0)
    else:
        sl = entry_price + (atr * 1.5)
        target = entry_price - (atr * 3.0)
    return round(sl, 2), round(target, 2)

# ==========================================
# 🧠 FINAL INTELLIGENCE ENGINES
# ==========================================

def calculate_relative_strength(stock_df, index_df):
    """🅰 RELATIVE STRENGTH ENGINE"""
    if stock_df.empty or index_df.empty or len(stock_df) < 10 or len(index_df) < 10:
        return 0
    stock_return = (stock_df['Close'].iloc[-1] - stock_df['Close'].iloc[-10]) / stock_df['Close'].iloc[-10]
    index_return = (index_df['Close'].iloc[-1] - index_df['Close'].iloc[-10]) / index_df['Close'].iloc[-10]
    return stock_return - index_return

def detect_trend_day(index_df):
    """🅱 TREND-DAY DETECTION ENGINE"""
    if index_df.empty or len(index_df) < 20: return "NORMAL"
    close = index_df['Close'].iloc[-1]
    prev_high = index_df['High'].iloc[-2]
    prev_low = index_df['Low'].iloc[-2]
    adx = index_df['ADX'].iloc[-1]
    atr_now = index_df['ATR'].iloc[-1]
    atr_prev = index_df['ATR'].iloc[-2]
    
    if close > prev_high and adx > 25 and atr_now > atr_prev:
        return "BULL_TREND_DAY"
    if close < prev_low and adx > 25 and atr_now > atr_prev:
        return "BEAR_TREND_DAY"
    return "NORMAL"

def mtf_alignment(trend_5m, trend_15m, trend_daily):
    """🅲 MULTI-TIMEFRAME ALIGNMENT"""
    if (trend_5m in ["BULLISH", "STRONG BULLISH"] and
        trend_15m in ["BULLISH", "STRONG BULLISH"] and
        trend_daily in ["BULLISH", "STRONG BULLISH"]):
        return "STRONG_LONG"
    if (trend_5m in ["BEARISH", "STRONG BEARISH"] and
        trend_15m in ["BEARISH", "STRONG BEARISH"] and
        trend_daily in ["BEARISH", "STRONG BEARISH"]):
        return "STRONG_SHORT"
    return "WEAK"

# ==========================================
# 🚀 MAIN SCANNER EXECUTION
# ==========================================

class MarshMuthuProScanner:
    def __init__(self):
        self.engine = get_upstox_engine()
        self.streamer = get_streamer()
        self.capital = 100000
        self.daily_loss = 0
        self.active_signals = []
        self.momentum_list = []
        self.last_candle_time = None
        self.instrument_map = {}
        
    def initialize(self):
        logger.info("Initializing MARSH MUTHU PRO v2 Institutional Engine...")
        self.capital = get_live_capital()
        logger.info(f"Live Capital: ₹{self.capital:,.2f}")
        
        # Load Universe
        all_symbols = ["NIFTY", "BANKNIFTY", "FINNIFTY"] + [s.replace(".NS", "") for s in EXTENDED_STOCKS_LIST]
        logger.info(f"Mapping {len(all_symbols)} instruments...")
        for sym in all_symbols:
            key = self.engine.get_instrument_key(sym)
            if key: self.instrument_map[sym] = key
        
        # Initial 180 Stock Scan to build Momentum List (Simulating 9:45 AM behavior)
        self.refresh_momentum_list()
        
    def refresh_momentum_list(self):
        """🔍 Layer 2: Momentum Expansion Detection (Filter 180 -> Top 20)"""
        logger.info("Refreshing Momentum Shortlist (Deep Scan)...")
        candidates = []
        symbols = list(self.instrument_map.keys())
        
        # We can't scan all 180 perfectly in one go without high API load, so we batch
        for i in range(0, len(symbols), 20):
            chunk = symbols[i:i+20]
            for sym in chunk:
                try:
                    key = self.instrument_map[sym]
                    df = self.engine.get_intraday_candles(key, interval="5minute")
                    if df.empty or len(df) < 50: continue
                    
                    df = calculate_indicators(df)
                    
                    # 🏛️ Apply Trend Classification (Filtering 180 -> Momentum Stocks)
                    trend = classify_trend(df)
                    
                    if trend in ["STRONG BULLISH", "STRONG BEARISH"]:
                        # Calculate Score for ranking
                        vol_spike = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
                        score = vol_spike * 1.5 + df['ADX'].iloc[-1] * 0.5
                        candidates.append({"symbol": sym, "m_score": score, "trend": trend})
                except: continue
            time.sleep(0.5)
            
        # Sort and take top 25
        candidates.sort(key=lambda x: x['m_score'], reverse=True)
        self.momentum_list = [c['symbol'] for c in candidates[:25]]
        # Always include indices
        for idx in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
            if idx not in self.momentum_list: self.momentum_list.append(idx)
            
        with open(MOMENTUM_LIST_FILE, 'w') as f:
            json.dump(self.momentum_list, f)
        logger.info(f"Momentum List Updated: {len(self.momentum_list)} stocks tracked.")

    def run_cycle(self, force=False):
        """Core Execution Loop"""
        # 1. Global Safety Checks
        if self.daily_loss <= -(self.capital * MAX_DAILY_LOSS_PCT):
            logger.warning("🚨 DAILY LOSS LIMIT HIT! Locking system.")
            send_telegram("⚠️ *SYSTEM LOCK*: Daily Loss Limit (5%) reached. Trading stopped for today.")
            return False
            
        now_time = datetime.now().time()
        if now_time >= TIME_EXIT:
            logger.info("🕒 Time Exit Reached. Closing cycles.")
            if self.active_signals:
                send_telegram("🕒 *TIME EXIT*: 2:45 PM Reached. Closing all monitoring.")
                self.active_signals = []
            return True

        # 2. Candle Synchronization
        current_candle = datetime.now().replace(second=0, microsecond=0)
        if not force:
            if not is_new_5min_candle():
                return True
            
            if self.last_candle_time == current_candle:
                return True
            self.last_candle_time = current_candle
        
        logger.info(f"🚀 New 5-Min Candle Scan: {current_candle.strftime('%H:%M')}")
        
        # 2.5 Index Context & Trend Day Detection
        index_regimes = self.detect_index_regime()
        primary_idx_trend = index_regimes[0]['trend_name'] if index_regimes else "NEUTRAL"
        
        # Detect Trend Day on NIFTY
        nifty_key = self.instrument_map.get("NIFTY")
        nifty_df = self.engine.get_intraday_candles(nifty_key, interval="5minute")
        nifty_df = calculate_indicators(nifty_df)
        market_state = detect_trend_day(nifty_df)
        logger.info(f"Market State: {market_state} | Index: {primary_idx_trend}")
        
        # 3. Scan Momentum List
        new_signals = []
        for sym in self.momentum_list:
            try:
                key = self.instrument_map.get(sym)
                if not key: continue
                
                # Fetch Multi-Timeframe Data
                df5m = self.engine.get_intraday_candles(key, interval="5minute")
                df15m = self.engine.get_intraday_candles(key, interval="15minute")
                df_daily = self.engine.get_historical_candles(key, interval="day", days=30)
                
                df5m = calculate_indicators(df5m)
                df15m = calculate_indicators(df15m)
                df_daily = calculate_indicators(df_daily)
                
                # RS Calculation vs Nifty
                rs_val = calculate_relative_strength(df5m, nifty_df)
                
                # MTF Trend Alignment
                trend_5m = classify_trend(df5m)
                trend_15m = classify_trend(df15m)
                trend_daily = classify_trend(df_daily)
                alignment = mtf_alignment(trend_5m, trend_15m, trend_daily)
                
                direction = "LONG" if "BULLISH" in trend_5m else "SHORT" if "BEARISH" in trend_5m else None
                if not direction: continue
                
                # Final Intelligence Filter Layer
                if alignment == "WEAK": continue # Must have MTF confirmation
                if not index_allows_trade(primary_idx_trend, direction): continue
                
                # Entry Trigger
                trigger = breakout_entry(df5m, direction) or pullback_entry(df5m, direction)
                if not trigger: continue
                
                # --- 🎯 EXPIRY ROLLOVER & OPTION ANALYSIS ---
                # Step 3: Fetch Option Chain for Next Expiry
                next_expiry = get_nearest_active_expiry(self.engine, key, sym)
                if not next_expiry: continue
                
                spot_px = float(df5m['Close'].iloc[-1])
                strike = get_atm_strike(spot_px, sym)
                
                # Step 4: Suggest CE/PE Entry with Real Premium
                chain = self.engine.get_option_chain_via_sdk(key, next_expiry)
                if not chain: continue
                
                # Calculate Stock PCR & Bias for real-time edge
                total_ce_oi = sum(c.call_options.market_data.oi for c in chain if c.call_options and c.call_options.market_data)
                total_pe_oi = sum(c.put_options.market_data.oi for c in chain if c.put_options and c.put_options.market_data)
                stock_pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 1.0
                
                # Find Target ATM Contract LTP
                target_contract = next((c for c in chain if c.strike_price == strike), None)
                if not target_contract: continue
                
                option_data = target_contract.call_options if direction == "LONG" else target_contract.put_options
                if not option_data or not option_data.market_data: continue
                
                entry_premium = float(option_data.market_data.ltp)
                if entry_premium < 20: continue # Filter low-value junk options
                
                # Scoring with RS bonus
                score, _ = calculate_pro_score(df5m, rs_val)
                if score < SCORE_THRESHOLD: continue

                if any(s['symbol'] == sym for s in self.active_signals): continue
                
                # SL/Target based on Premium (10% SL, 30% Target protocol)
                sl, target = round(entry_premium * 0.9, 2), round(entry_premium * 1.3, 2)
                lots = calculate_position_sizing(self.capital, spot_px, spot_px * 0.98, sym) # Use 2% spot risk for sizing
                
                # Log to Performance Engine
                self.log_trade(sym, entry_premium, sl, target, "Ready")
                
                sig = {
                    "symbol": sym, "bias": "BULLISH" if direction == "LONG" else "BEARISH",
                    "type": f"{direction} ({trigger})", "entry": entry_premium, 
                    "sl": sl, "target": target, "lots": lots, "score": score,
                    "time": datetime.now().strftime("%H:%M:%S"), "status": "Ready",
                    "mtf": alignment, "rs": round(rs_val, 4), "pcr": stock_pcr,
                    "strike": strike, "expiry": next_expiry
                }
                new_signals.append(sig)
            except Exception as e:
                logger.error(f"Error scanning {sym}: {e}")

        # 4. Rank and Send Alerts
        new_signals.sort(key=lambda x: x['score'], reverse=True)
        top_3 = new_signals[:3]
        
        for sig in top_3:
            self.send_pro_alert(sig)
            self.active_signals.append(sig)
            
        # 5. Index & PCR Update
        pcr_data = self.calculate_market_pcr()
        index_regime = self.detect_index_regime()
        
        # 6. Dashboard Sync (Compatible with Institutional View)
        # Prepare "all" signals for the institutional view table
        all_formatted = []
        for s in new_signals:
            all_formatted.append({
                "symbol": s['symbol'], "type": "CE" if s['bias'] == "BULLISH" else "PE",
                "strike": s['strike'], "premium": s['entry'], "score": s['score'],
                "mtf": "Strong", "rsi": 65, "vol": 2.0, "time": s['time'],
                "mtf_signals": {"Scalping": "BUY", "Intraday": "BUY", "Swing": "WAIT"}
            })
            
        top_formatted = []
        for s in top_3:
            top_formatted.append({
                "symbol": s['symbol'], "type": "CE" if s['bias'] == "BULLISH" else "PE",
                "strike": s['strike'], "premium": s['entry'], "score": s['score'],
                "mtf": "Strong", "rsi": 65, "vol": 2.0, "decay": 15, "expiry": "Weekly"
            })

        self.update_dashboard_data(all_formatted, top_formatted, index_bias=index_regime, pcr_data=pcr_data)
        
        return True

    def calculate_market_pcr(self):
        """📊 Market-Wide PCR Logic"""
        try:
            # Import here to avoid circular dependency
            from am_backend_scanner import calculate_pcr_data
            return calculate_pcr_data(self.engine)
        except:
            return {}

    def detect_index_regime(self):
        """🏛️ Layer 1: Index Regime Detection (Brain)"""
        regimes = []
        for idx in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
            try:
                key = self.instrument_map.get(idx)
                # MTF Check: 5m + 15m
                df5m = self.engine.get_intraday_candles(key, interval="5minute")
                df15m = self.engine.get_intraday_candles(key, interval="15minute")
                
                df5m = calculate_indicators(df5m)
                df15m = calculate_indicators(df15m)
                
                trend = classify_trend(df5m, mtf_df=df15m)
                
                last = df5m.iloc[-1]
                bias_pct = last['RSI'] * 0.5 + (100 if "BULL" in trend else 0 if "BEAR" in trend else 50) * 0.5
                bias_type = "CE" if "BULL" in trend else "PE" if "BEAR" in trend else "Neutral"
                
                regimes.append({
                    "index": idx,
                    "type": bias_type,
                    "trend_name": trend, # Add objective name
                    "bias_pct": bias_pct,
                    "components": ["Institutional Flow Active" if "STRONG" in trend else "Normal Trading"]
                })
            except: continue
        return regimes

    def clean_symbol(self, symbol):
        """🧹 Professional Symbol Formatter (e.g., HDFCBANK -> HDFC BANK)"""
        s = symbol.replace(".NS", "").replace("^NSEI", "NIFTY").replace("^NSEBANK", "BANK NIFTY").replace("^BSESN", "SENSEX")
        replacements = {
            "HDFCBANK": "HDFC BANK", "ICICIBANK": "ICICI BANK", "KOTAKBANK": "KOTAK BANK", 
            "AXISBANK": "AXIS BANK", "INDUSINDBK": "INDUSIND BANK", "BANDHANBNK": "BANDHAN BANK",
            "IDFCFIRSTB": "IDFC FIRST BANK", "BANKBARODA": "BANK OF BARODA", "BANKINDIA": "BANK OF INDIA",
            "PNB": "PNB", "CANBK": "CANARA BANK", "FEDERALBNK": "FEDERAL BANK", "AUBANK": "AU BANK",
            "TITAN": "TITAN", "RELIANCE": "RELIANCE", "ASHOKLEY": "ASHOK LEYLAND", "APOLLOHOSP": "APOLLO HOSP",
            "BAJAJFINSV": "BAJAJ FINSERV", "BAJFINANCE": "BAJAJ FINANCE", "BHARTIARTL": "BHARTI AIRTEL",
            "HEROMOTOCO": "HERO MOTOCORP", "M&M": "M&M", "MARUTI": "MARUTI SUZUKI", "TATASTEEL": "TATA STEEL",
            "ULTRACEMCO": "ULTRATECH CEMENT", "TATACONSUM": "TATA CONSUMER", "JSWSTEEL": "JSW STEEL",
            "HINDUNILVR": "HINDUSTAN UNILEVER", "ADANIENT": "ADANI ENT", "ADANIPORTS": "ADANI PORTS",
            "COALINDIA": "COAL INDIA", "POWERGRID": "POWER GRID", "SUNPHARMA": "SUN PHARMA",
            "HDFCLIFE": "HDFC LIFE", "SBILIFE": "SBI LIFE", "SBIN": "SBI", "NIFTY_FIN_SERVICE": "FIN NIFTY"
        }
        for k, v in replacements.items():
            if s == k: return v
        return s

    def send_pro_alert(self, sig):
        emoji = "🚀" if sig['bias'] == "BULLISH" else "🩸"
        type_str = "🚀 BUY CALL" if sig['bias'] == "BULLISH" else "🩸 BUY PUT"
        clean_name = self.clean_symbol(sig['symbol'])
        
        msg = (
            f"{emoji} *MARSH MUTHU PRO v2 ALERT*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 *Stock Name*: `{clean_name}`\n"
            f"📅 *Expiry*: `{sig['expiry']}`\n"
            f"🎯 *Strike Price*: **`{sig['strike']} {'CALL' if sig['bias'] == 'BULLISH' else 'PUT'}`**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *Action*: **`{type_str}`**\n"
            f"💰 *Premium Entry*: `₹{sig['entry']:.2f}`\n"
            f"🛑 *Stop Loss*: `₹{sig['sl']:.2f}`\n"
            f"🎯 *Target*: `₹{sig['target']:.2f}`\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🏛 *Institutional Rank*: `{sig['score']}/100`\n"
            f"📊 *Stock PCR*: `{sig['pcr']}`\n"
            f"⚖ *Suggested Size*: `{sig['lots']} Lots` (2% Risk)\n"
            f"⏳ *Time*: `{sig['time']}`\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 [Analyze Chart]({AUTH_URL})\n\n"
            f"✨ *PrimeSkillDevelopment*\n"
            f"👑 *CEO : MuthuKumar Krishnan*"
        )
        send_telegram(msg)
        logger.info(f"Alert Sent: {sig['symbol']} {sig['bias']} Score: {sig['score']}")

    def log_trade(self, symbol, entry, sl, target, result, pnl=0):
        """🅳 PERFORMANCE TRACKER"""
        try:
            log_entry = {
                "symbol": symbol, "entry": entry, "sl": sl, "target": target,
                "result": result, "pnl": pnl, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            log_file = "data/pro_v2_performance_log.json"
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f: logs = json.load(f)
            logs.append(log_entry)
            with open(log_file, 'w') as f: json.dump(logs, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to log trade: {e}")

    def update_dashboard_data(self, all_signals, top_signals, index_bias, pcr_data):
        # Format for institutional_view.py
        data = {
            "all": all_signals,
            "top5": top_signals,
            "index_bias": index_bias,
            "pcr": pcr_data,
            "last_update": datetime.now().isoformat()
        }
        
        # 🛡️ SANITIZE DATA: Replace NaN/Inf with None (null in JSON)
        # This prevents the "Unexpected token 'N' (NaN)" error in Streamlit
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize(i) for i in obj]
            elif isinstance(obj, float):
                if np.isnan(obj) or np.isinf(obj):
                    return None
            return obj

        sanitized_data = sanitize(data)
        
        # Save to both for reliability
        with open("data/inst_scanner_results.json", 'w') as f:
            json.dump(sanitized_data, f, indent=4)
        with open("data/pro_v2_dashboard.json", 'w') as f:
            json.dump(sanitized_data, f, indent=4)

    def main_loop(self):
        self.initialize()
        logger.info("Running Institutional Main Loop...")
        
        # ⚡ Force immediate sync on startup to avoid "2 hour old" data
        logger.info("⚡ Executing initial startup scan...")
        self.run_cycle(force=True)
        
        while True:
            try:
                # Refresh capital daily or every hour
                if datetime.now().minute == 0:
                    self.capital = get_live_capital()
                
                success = self.run_cycle()
                if not success: break
                
                # Sleep briefly
                time.sleep(10)
            except KeyboardInterrupt: break
            except Exception as e:
                logger.error(f"Main Loop Error: {e}")
                time.sleep(20)

if __name__ == "__main__":
    scanner = MarshMuthuProScanner()
    scanner.main_loop()
