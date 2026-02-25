import pandas as pd
import numpy as np

def detect_market_regime(nifty_df, vix_value):
    """
    Detects market state: Trending, Sideways, Volatile, or Momentum Day.
    """
    if nifty_df.empty:
        return "NEUTRAL", 0
    
    # 1. Trend Strength (ADX)
    adx = nifty_df['adx'].iloc[-1] if 'adx' in nifty_df.columns else 20
    
    # 2. Volatility (VIX)
    is_volatile = vix_value > 20
    
    # 3. Momentum (Gap Detection)
    # Simple gap detection based on first 5-min candle vs prev close would be better
    # for now we use a placeholder or simpler logic
    
    if is_volatile:
        return "HIGH_VOLATILITY", adx
    if adx > 25:
        return "TRENDING", adx
    if adx < 18:
        return "SIDEWAYS", adx
        
    return "NORMAL", adx

def get_strategy_for_regime(regime, is_expiry_day=False):
    """
    Determines which strategy to prioritize based on market regime and date.
    """
    if is_expiry_day:
        return "EXPIRY_SPECIAL"
        
    if regime == "TRENDING":
        return "INTRADAY_BREAKOUT"
    elif regime == "SIDEWAYS":
        return "SCALPING_ONLY"
    elif regime == "HIGH_VOLATILITY":
        return "REDUCED_EXPOSURE"
    else:
        return "STANDARD"
