import pandas as pd
import numpy as np

def calculate_professional_score(df, symbol, nifty_df):
    """
    Calculates 0-100 score based on:
    RSI (20), ADX (20), Volume (20), Breakout (20), RS (20)
    """
    if df.empty: return 0, {}
    
    score = 0
    breakdown = {}
    
    # 1. RSI (20 Points)
    rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
    rsi_pts = 0
    if rsi > 60: rsi_pts = 20
    elif rsi > 55: rsi_pts = 15
    elif rsi > 50: rsi_pts = 8
    score += rsi_pts
    breakdown['rsi'] = rsi_pts

    # 2. ADX Trend Strength (20 Points)
    adx = df['adx'].iloc[-1] if 'adx' in df.columns else 15
    adx_pts = 0
    if adx > 30: adx_pts = 20
    elif adx > 25: adx_pts = 15
    elif adx > 20: adx_pts = 8
    score += adx_pts
    breakdown['adx'] = adx_pts

    # 3. Volume Spike (20 Points)
    vol = df['volume'].iloc[-1] if 'volume' in df.columns else 0
    avg_vol = df['volume'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else vol
    vol_pts = 0
    if vol > 2 * avg_vol: vol_pts = 20
    elif vol > 1.5 * avg_vol: vol_pts = 15
    elif vol > 1.2 * avg_vol: vol_pts = 8
    score += vol_pts
    breakdown['volume'] = vol_pts

    # 4. Breakout Structure (20 Points)
    day_high = df['high'].max() # This is a simplified day high
    curr_price = df['close'].iloc[-1]
    prev_high = df['high'].iloc[-50:].max() # Last 50 candles
    
    bo_pts = 0
    if curr_price >= day_high * 0.998: bo_pts = 20
    elif curr_price >= prev_high * 0.99: bo_pts = 10
    score += bo_pts
    breakdown['breakout'] = bo_pts

    # 5. Relative Strength vs NIFTY (20 Points)
    rs_pts = 0
    if not nifty_df.empty:
        stock_ret = (df['close'].iloc[-1] / df['close'].iloc[-15]) - 1 if len(df) >= 15 else 0
        nifty_ret = (nifty_df['close'].iloc[-1] / nifty_df['close'].iloc[-15]) - 1 if len(nifty_df) >= 15 else 0
        
        if stock_ret > nifty_ret + 0.01: rs_pts = 20
        elif stock_ret > nifty_ret: rs_pts = 10
    score += rs_pts
    breakdown['rs'] = rs_pts

    return score, breakdown
