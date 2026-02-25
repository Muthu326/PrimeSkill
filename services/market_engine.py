
import yfinance as yf
import pandas as pd
import numpy as np
import math
import re
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.upstox_engine import get_upstox_engine
import streamlit as st
import functools

# 🏛️ SILENT CACHE UTILITY
# Prevents Streamlit "No runtime found" warnings in backend logs
def safe_cache(ttl=300, show_spinner=False):
    def decorator(func):
        try:
            # Check if streamlit is actually running (in a script runner context)
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            if get_script_run_ctx() is not None:
                return st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
        except:
            pass
        # Fallback for backend: No caching or simple memory cache
        return func
    return decorator

def flatten_columns(df):
    if df.empty: return df
    if isinstance(df.columns, pd.MultiIndex):
        levels = [df.columns.get_level_values(i) for i in range(df.columns.nlevels)]
        best_level = 0
        for i, level in enumerate(levels):
            if any(c in level for c in ['Close', 'Open', 'High', 'Low']):
                best_level = i
                break
        df.columns = levels[best_level]
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def option_premium_estimate(spot, strike, iv, days, option_type):
    """
    🎯 Smart Premium Estimator (Institutional Quality)
    Formula: Premium = Intrinsic + (TimeValue * 0.6)
    TimeValue = Spot * (IV/100) * sqrt(Days/365)
    """
    days = max(1, days)
    time_value = spot * (iv/100) * math.sqrt(days/365)
    
    if option_type == "CE":
        intrinsic = max(0, spot - strike)
    else:
        intrinsic = max(0, strike - spot)
        
    premium = intrinsic + (time_value * 0.6)
    return round(premium, 2)

@safe_cache(ttl=120, show_spinner=False)
def get_real_option_price(stock_name, strike, option_type, spot_price, iv, days_to_expiry):
    """
    🎯 Fetch REAL option price from market (NSE Option Chain)
    Works for ALL stocks and indices - Falls back to theoretical estimate if API fails
    
    Args:
        stock_name: Stock symbol (e.g., "HAL", "NIFTY", "BANKNIFTY", "TCS", "RELIANCE")
        strike: Strike price
        option_type: "CE" or "PE"
        spot_price: Current spot price (for fallback)
        iv: Implied volatility (for fallback)
        days_to_expiry: Days to expiry (for fallback)
    
    Returns:
        Real market price or estimated price
    """
    try:
        # Comprehensive index mapping (handles all NSE indices)
        nse_indices = {
            "NIFTY": "NIFTY",
            "NIFTY50": "NIFTY",
            "NIFTY_50": "NIFTY",
            "BANKNIFTY": "BANKNIFTY",
            "BANK_NIFTY": "BANKNIFTY",
            "FINNIFTY": "FINNIFTY",
            "FIN_NIFTY": "FINNIFTY",
            "MIDCPNIFTY": "MIDCPNIFTY",
            "MIDCAP_NIFTY": "MIDCPNIFTY",
            "NIFTY_IT": "NIFTYIT",
            "NIFTYIT": "NIFTYIT",
            "SENSEX": "SENSEX"
        }
        
        # Clean stock name (remove .NS, .BO suffixes and whitespace)
        clean_name = stock_name.replace(".NS", "").replace(".BO", "").strip().upper()
        
        # Check if it's an index or a stock
        nse_symbol = nse_indices.get(clean_name, clean_name)
        is_index = clean_name in nse_indices
        
        # NSE headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Choose API endpoint based on instrument type
        if is_index:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={nse_symbol}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={nse_symbol}"
        
        # Fetch option chain data
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode())
        
        # Parse option chain records
        records = data.get('records', {}).get('data', [])
        
        # Search for matching strike price
        for record in records:
            strike_price = record.get('strikePrice', 0)
            
            # Match strike price (allow ±1 tolerance for rounding)
            if abs(strike_price - strike) < 1:
                if option_type == "CE":
                    option_data = record.get('CE', {})
                else:
                    option_data = record.get('PE', {})
                
                # Get Last Traded Price (LTP) - REAL market price
                ltp = option_data.get('lastPrice', 0)
                
                # Return real price if available
                if ltp > 0:
                    return round(ltp, 2)
        
        # If no matching strike found, fallback to estimate
        return option_premium_estimate(spot_price, strike, iv, days_to_expiry, option_type)
        
    except Exception as e:
        # Fallback to theoretical estimate on any error (API down, symbol not found, etc.)
        return option_premium_estimate(spot_price, strike, iv, days_to_expiry, option_type)

@safe_cache(ttl=60, show_spinner=False)
def fetch_realtime_price(symbol, is_index=True):
    try:
        # 🏢 Institutional Feed Priority: Upstox
        engine = get_upstox_engine()
        key = engine.get_instrument_key(symbol)
        if key:
            quotes = engine.get_market_quote([key], mode="ltp")
            if key in quotes:
                v = quotes[key]
                return {
                    'lastprice': float(v['last_price']), 
                    'prevclose': float(v.get('cp', 0)),
                    'source': 'Upstox'
                }
                
        # 🌐 Fallback 1: Google Finance (Existing Logic)
        g_map = {
            "NIFTY_MID_SELECT": "NIFTY_MID_SELECT", 
            "NIFTY_FIN_SERVICE": "NIFTY_FIN_SERVICE", 
            "NIFTY_50": "NIFTY_50", 
            "NIFTY_BANK": "NIFTY_BANK", 
            "SENSEX": "SENSEX"
        }
        symbol = g_map.get(symbol, symbol)
        suffix = ":INDEXNSE" if is_index else ":NSE"
        if "SENSEX" in symbol: suffix = ":INDEXBOM"
        url = f"https://www.google.com/finance/quote/{symbol}{suffix}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as res:
            html = res.read().decode('utf-8')
            p_match = re.search(r'data-last-price="([\d,.]+)"', html)
            prev_match = re.search(r'data-previous-close="([\d,.]+)"', html)
            if p_match:
                last = float(p_match.group(1).replace(',', ''))
                prev = float(prev_match.group(1).replace(',', '')) if prev_match else None
                return {'lastprice': last, 'prevclose': prev, 'source': 'Google'}
    except: pass
    return None

def get_expiry_details(symbol="NIFTY"):
    """
    📅 Calculates expiry details based on index type with SMART SAFETY.
    Logic: If current expiry is <= 1 day away, suggest NEXT for safer buying.
    """
    now = datetime.now()
    
    expiry_map = {
        "MIDCAPNIFTY": 0, "FINNIFTY": 1, "BANKNIFTY": 2, "NIFTY": 3, "SENSEX": 4
    }
    
    target_day = 3 # Stocks default
    s_upper = symbol.upper()
    for key, day in expiry_map.items():
        if key in s_upper:
            target_day = day
            break
            
    days_ahead = target_day - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
        
    recommended_week = "CURRENT"
    
    # 🔥 SMART SAFETY: If within 1 day of expiry, current is risky (Gamma/Theta).
    # Switch to NEXT if days_ahead <= 1 (e.g., if today is Tue and expiry is Wed)
    if days_ahead <= 1:
        days_ahead += 7
        recommended_week = "NEXT"
        
    expiry_date = now + timedelta(days=days_ahead)
    expiry_str = expiry_date.strftime('%d-%m-%Y')
    
    return max(0, days_ahead), expiry_str, recommended_week

def get_days_to_expiry():
    """Legacy wrapper for backward compatibility"""
    days, _, _ = get_expiry_details()
    return days

def estimate_target_time(signal_type, adx_val=25):
    """
    ⏰ Estimates how long a target achievement might take based on signal type and momentum.
    """
    if "SCALP" in signal_type:
        return "15 - 45 Mins" if adx_val > 30 else "45 - 90 Mins"
    elif "BREAKOUT" in signal_type or "ANTICIPATION" in signal_type:
        return "2 - 4 Hours" if adx_val > 30 else "4 - 8 Hours"
    elif "DIAMOND" in signal_type or "INDEX" in signal_type:
        return "Interday (1-2 Days)"
    elif "BTST" in signal_type or "FIRE" in signal_type:
        return "Next Morning Opening"
    return "1 - 3 Hours"

@safe_cache(ttl=300, show_spinner=False)
def load_data(ticker, interval="5m", period="5d"):
    try:
        # 🏢 Strategy: Use Upstox for live/intraday, yfinance for historical/bulk
        engine = get_upstox_engine()
        key = engine.get_instrument_key(ticker)
        
        # If intraday data requested and Upstox is ready
        if key and interval in ["1m", "5m", "15m"]:
            upstox_interval = "1minute" if interval == "1m" else "5minute" if interval == "5m" else "15minute"
            df = engine.get_intraday_candles(key, interval=upstox_interval)
            if not df.empty:
                return df
                
        # Fallback to yfinance
        for _ in range(2):
            df = yf.download(ticker, period=period, interval=interval, progress=False, threads=True)
            if not df.empty: break
        
        if df.empty:
            return pd.DataFrame()
            
        df = flatten_columns(df)
        return df
    except Exception as e:
        return pd.DataFrame()

@safe_cache(ttl=300, show_spinner=False)
def calculate_indicators(df):
    if df.empty or len(df) < 20: return df
    
    # Skip if already calculated (Fix A: Indicators recalculated repeatedly)
    if 'EMA200' in df.columns: return df
    
    df = df.copy()
    df.columns = [c.capitalize() for c in df.columns]
    close = df['Close']; high = df['High']; low = df['Low']; open_px = df['Open']; vol = df['Volume']
    
    # 1. EMAs & VWAP
    df['EMA20'] = close.ewm(span=20, adjust=False).mean()
    df['EMA50'] = close.ewm(span=50, adjust=False).mean()
    df['EMA200'] = close.ewm(span=200, adjust=False).mean()
    tp = (high + low + close) / 3
    df['VWAP'] = (tp * vol).cumsum() / vol.cumsum()

    # 2. RSI & ADX (Wilder's Implementation)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + gain / loss.replace(0, 0.001)))
    
    # 🕵️ ROBUST ADX (Wilder's Smoothing)
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    up_move = high.diff(); down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    atr = tr.ewm(alpha=1/14, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/14, adjust=False).mean() / atr.replace(0, 0.001))
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).ewm(alpha=1/14, adjust=False).mean() / atr.replace(0, 0.001))
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, 0.001)
    df['ADX'] = dx.ewm(alpha=1/14, adjust=False).mean()
    df['ATR'] = atr

    # 3. Supertrend Calculation
    multiplier = 3.0
    atr_st = tr.rolling(10).mean() # Standard for Supertrend
    hl2 = (high + low) / 2
    upper = hl2 + (multiplier * atr_st)
    lower = hl2 - (multiplier * atr_st)
    
    v_close = close.values
    v_upper = upper.values
    v_lower = lower.values
    st_vals = np.zeros(len(df))
    st_dir = np.zeros(len(df))
    
    for i in range(1, len(df)):
        if v_close[i] > v_upper[i-1]:
            st_dir[i] = 1
        elif v_close[i] < v_lower[i-1]:
            st_dir[i] = -1
        else:
            st_dir[i] = st_dir[i-1]
            if st_dir[i] == 1 and v_lower[i] < v_lower[i-1]: v_lower[i] = v_lower[i-1]
            if st_dir[i] == -1 and v_upper[i] > v_upper[i-1]: v_upper[i] = v_upper[i-1]
        st_vals[i] = v_lower[i] if st_dir[i] == 1 else v_upper[i]
        
    df['Supertrend'] = st_vals

    # 4. Support & Resistance
    df['Support'] = low.rolling(20).min()
    df['Resistance'] = high.rolling(20).max()

    # 5. Volume Pressure & Strength
    avg_vol = vol.rolling(20).mean()
    df['VolRatio'] = vol / avg_vol
    df['Vol_Pressure'] = np.where(close > open_px, "🟢 BUY PRESSURE", "🔴 SELL PRESSURE")
    df['PressureStatus'] = np.where(close > open_px, "Buy Pressure", "Sell Pressure")

    # 6. SMC / BOS
    df['SMC'] = "Neutral"
    df.iloc[20:, df.columns.get_loc('SMC')] = np.where(close.iloc[20:] > high.shift(1).rolling(20).max().iloc[20:], "BOS Bullish", 
                                               np.where(close.iloc[20:] < low.shift(1).rolling(20).min().iloc[20:], "BOS Bearish", "Neutral"))

    # 7. Heikin Ashi
    ha_close = (open_px + high + low + close) / 4
    v_ha_close = ha_close.values
    v_open = open_px.values
    v_ha_open = np.zeros(len(df))
    v_ha_open[0] = v_open[0]
    for j in range(1, len(df)):
        v_ha_open[j] = (v_ha_open[j-1] + v_ha_close[j-1]) / 2
    df['HA_Status'] = np.where(ha_close > v_ha_open, "Bullish HA", "Bearish HA")
    df['HA_Close'] = ha_close

    # 8. Stochastic RSI
    ha_rsi_delta = df['HA_Close'].diff()
    ha_gain = ha_rsi_delta.where(ha_rsi_delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
    ha_loss = (-ha_rsi_delta.where(ha_rsi_delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    ha_rsi = 100 - (100 / (1 + ha_gain / ha_loss.replace(0, 0.001)))
    stoch_rsi_min = ha_rsi.rolling(14).min()
    stoch_rsi_max = ha_rsi.rolling(14).max()
    df['StochRSI'] = (ha_rsi - stoch_rsi_min) / (stoch_rsi_max - stoch_rsi_min).replace(0, 0.001)

    # 9. TREND CLASSIFICATION (User Suggested Directional Bias)
    rsi_vals = df['RSI']
    adx_vals = df['ADX']
    
    conditions = [
        (rsi_vals > 60) & (adx_vals > 20),
        (rsi_vals < 40) & (adx_vals > 20)
    ]
    choices = ['UP', 'DOWN']
    df['Trend'] = np.select(conditions, choices, default='NEUTRAL')
    
    # 10. Signal Logic
    df['Signal'] = "WAIT"
    # Fix: Pullback Too Loose (Add RSI filter)
    buy_scalp = (df['Trend'] == "Bullish") & (df['StochRSI'] < 0.25) & (df['HA_Status'] == "Bullish HA") & (df['RSI'] > 45) & (df['RSI'] < 65)
    sell_scalp = (df['Trend'] == "Bearish") & (df['StochRSI'] > 0.75) & (df['HA_Status'] == "Bearish HA") & (df['RSI'] > 35) & (df['RSI'] < 55)
    
    recent_high = high.shift(1).rolling(20).max()
    recent_low = low.shift(1).rolling(20).min()
    vol_spike = df['VolRatio'] > 1.2
    
    # Fix: Breakout Too Sensitive (Add 0.2% confirmation buffer)
    buy_breakout = (close > recent_high * 1.002) & vol_spike & (df['RSI'] > 60) & (df['ADX'] > 25)
    sell_breakout = (close < recent_low * 0.998) & vol_spike & (df['RSI'] < 40) & (df['ADX'] > 25)
    
    # 🌟 ANTICIPATION LOGIC (Expectation of Breakout)
    buy_anticipation = (close <= recent_high) & (close > recent_high * 0.992) & (df['Trend'] == "Bullish") & (df['RSI'] > 55)
    sell_anticipation = (close >= recent_low) & (close < recent_low * 1.008) & (df['Trend'] == "Bearish") & (df['RSI'] < 45)

    df.loc[buy_scalp, 'Signal'] = "CE SCALP (ST+STOCH)"
    df.loc[sell_scalp, 'Signal'] = "PE SCALP (ST+STOCH)"
    df.loc[buy_breakout, 'Signal'] = "⚡ CE BREAKOUT"
    df.loc[sell_breakout, 'Signal'] = "⚡ PE BREAKOUT"
    df.loc[buy_anticipation, 'Signal'] = "⏳ CE ANTICIPATION"
    df.loc[sell_anticipation, 'Signal'] = "⏳ PE ANTICIPATION"

    # 11. Momentum Speed Index
    df['MomentumSpeed'] = df['RSI'] * 0.4 + df['ADX'] * 0.4 + np.where(df['PressureStatus'] == "Buy Pressure", 20, -20)
    df['MomentumSpeed'] = df['MomentumSpeed'].clip(1, 100)
    df['SignalValidity'] = np.where((df['Signal'] != "WAIT") & (df['VolRatio'] > 1.2), "Strong Signal", "Neutral")

    # 12. Pattern Detection
    h_slope = high.rolling(20).apply(lambda x: np.polyfit(np.arange(20), x, 1)[0], raw=True)
    l_slope = low.rolling(20).apply(lambda x: np.polyfit(np.arange(20), x, 1)[0], raw=True)
    df['Pattern'] = np.where((h_slope > 0) & (l_slope > h_slope), "Rising Wedge", 
                    np.where((l_slope < 0) & (h_slope < l_slope), "Falling Wedge", "None"))

    df['Pos_In_Range'] = (close - df['Support']) / (df['Resistance'] - df['Support']).replace(0, 0.001)
    df['Day_Chg'] = (close - open_px) / open_px * 100
    
    return df


def calculate_option_greeks(spot, strike, premium, o_type="CE"):
    """
    📊 Calculates Intrinsic Value (IV), Time Value (TV), and Moneyness
    """
    if o_type == "CE":
        intrinsic = max(0, spot - strike)
        if spot > strike + 2: moneyness = "In-the-Money (ITM)"
        elif spot < strike - 2: moneyness = "Out-of-the-Money (OTM)"
        else: moneyness = "At-the-Money (ATM)"
    else:
        intrinsic = max(0, strike - spot)
        if spot < strike - 2: moneyness = "In-the-Money (ITM)"
        elif spot > strike + 2: moneyness = "Out-of-the-Money (OTM)"
        else: moneyness = "At-the-Money (ATM)"
    
    time_value = max(0, premium - intrinsic)
    return round(intrinsic, 2), round(time_value, 2), moneyness

def get_mtf_confluence(ticker, mtf_data=None):
    """
    🔍 Verifies Trend Confluence across 5m, 15m, and 1h
    If mtf_data is provided (from Upstox engine), we use that.
    """
    if mtf_data:
        # Use existing scoring from mtf_data
        t5 = mtf_data.get("5m", {}).get("trend", "NEUTRAL")
        t15 = mtf_data.get("15m", {}).get("trend", "NEUTRAL")
        t1h = mtf_data.get("1h", {}).get("trend", "NEUTRAL")
        
        bull_count = [t5, t15, t1h].count("UP")
        bear_count = [t5, t15, t1h].count("DOWN")
        
        score = bull_count - bear_count
        status = "Strong Bullish" if bull_count == 3 else "Strong Bearish" if bear_count == 3 else \
                 "Bullish Bias" if score > 0 else "Bearish Bias" if score < 0 else "Neutral"
        return score, status

    # Fallback to a simpler calculation if no mtf_data (legacy support)
    return 0, "Neutral"

def get_comprehensive_scan(stock_list_tuple):
    results = []
    stock_list = list(stock_list_tuple)
    if not stock_list: return results
    
    all_prev_px = {}
    try:
        base_all = yf.download(" ".join(stock_list), period="5d", interval="1d", progress=False, threads=True)
        if not base_all.empty:
            close_data = base_all['Close']
            for t in stock_list:
                try:
                    vals = close_data[t].dropna() if len(stock_list) > 1 else close_data.dropna()
                    if len(vals) >= 2: all_prev_px[t] = float(vals.iloc[-2])
                except: continue
    except: pass

    engine = get_upstox_engine()
    def process_chunk(chunk, chunk_idx):
        chunk_results = []
        try:
            # 🏢 Strategy: Try individual Upstox fetch if possible, else batch yfinance
            for i, ticker in enumerate(chunk):
                try:
                    df_s = pd.DataFrame()
                    key = engine.get_instrument_key(ticker)
                    if key:
                        df_s = engine.get_intraday_candles(key, interval="5minute")
                    
                    # Fallback to yfinance if Upstox fails
                    if df_s.empty:
                        df_s = yf.download(ticker, period="1d", interval="5m", progress=False, threads=False)
                    
                    if not df_s.empty:
                        df_s = flatten_columns(df_s)
                    
                    prev_px = all_prev_px.get(ticker)
                    if len(df_s) < 10 or prev_px is None: continue
                    
                    df_s = calculate_indicators(df_s)
                    last = df_s.iloc[-1]
                    price = float(last['Close'])
                    chg = round(price - prev_px, 2)
                    chg_pct = round((chg / prev_px) * 100, 2)
                    sig = str(last['Signal'])
                    
                    # 🔍 MTF Verification for Active Signals
                    mtf_score, mtf_status = 0, "Neutral"
                    if sig != "WAIT":
                        mtf_score, mtf_status = get_mtf_confluence(ticker)
                    
                    chunk_results.append({
                        "Stock": ticker.replace(".NS", ""), "Ticker": ticker, "Price": round(price, 2),
                        "Chg": chg, "Chg%": chg_pct, "Signal": sig, "Scalp": sig, "Intraday": sig,
                        "Swing": str(last.get('Forecast', 'Wait')), "RSI": round(float(last['RSI']), 1),
                        "ADX": round(float(last['ADX']), 1), "Trend": str(last['Trend']),
                        "Momentum": round(float(last.get('MomentumSpeed', 50)), 1),
                        "HA_Status": str(last.get('HA_Status', 'Neutral')), "HA": str(last.get('HA_Status', 'Neutral')),
                        "SMC": str(last.get('SMC', 'Neutral')), 
                        "Vol_Pressure": str(last.get('Vol_Pressure', 'Neutral')),
                        "Vol Pressure": str(last.get('Vol_Pressure', 'Neutral')),
                        "PressureStatus": str(last.get('PressureStatus', 'Neutral')),
                        "SignalValidity": str(last.get('SignalValidity', 'Neutral')), "Forecast": str(last.get('Forecast', 'Wait')),
                        "Support": float(last.get('Support', 0)), "Resistance": float(last.get('Resistance', 0)),
                        "Pattern": str(last.get('Pattern', 'None')), "Pos_In_Range": float(last.get('Pos_In_Range', 0.5)),
                        "Day_Chg": float(last.get('Day_Chg', 0)), "ATR": float(last.get('ATR', 0)),
                        "Supertrend": float(last.get('Supertrend', 0)), "StochRSI": float(last.get('StochRSI', 0)),
                        "MTF_Score": mtf_score, "MTF_Status": mtf_status,
                        "ST_Dir": 1 if last['Trend'] == "Bullish" else -1, "Rank": chunk_idx + i + 1
                    })
                except: continue
        except: pass
        return chunk_results

    chunk_size = 40
    chunks = [stock_list[i : i + chunk_size] for i in range(0, len(stock_list), chunk_size)]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk, i*chunk_size): i for i, chunk in enumerate(chunks)}
        for future in as_completed(future_to_chunk):
            chunk_results = future.result()
            if chunk_results: results.extend(chunk_results)
    
    return results

def get_index_price(name, ticker):
    try:
        df = yf.download(ticker, period='5d', interval='1d', progress=False)
        if df.empty or len(df) < 2:
            return None, None, ticker
        
        lp = float(df['Close'].iloc[-1])
        fp = float(df['Close'].iloc[-2])
        return lp, fp, ticker
    except:
        return None, None, ticker

def send_telegram(token, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': message.replace('%0A', '\n'),
            'parse_mode': 'Markdown'
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except: return False
