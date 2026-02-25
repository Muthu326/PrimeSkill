import pandas as pd
import numpy as np

def calculate_indicators(df):
    """Calculates RSI, ADX, VWAP, EMA for the scanner"""
    if df.empty: return df
    
    # Normalize columns
    df.columns = [c.lower() for c in df.columns]
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # EMA
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    # ATR (for ADX)
    df['tr'] = np.maximum(df['high'] - df['low'], 
                         np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                  abs(df['low'] - df['close'].shift(1))))
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    # ADX (Directional Movement)
    df['up_move'] = df['high'] - df['high'].shift(1)
    df['down_move'] = df['low'].shift(1) - df['low']
    
    df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
    
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=14).mean() / df['atr'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=14).mean() / df['atr'])
    
    # DX and ADX
    df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
    df['adx'] = df['dx'].rolling(window=14).mean()
    
    # VWAP
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['cum_tp_vol'] = (df['typical_price'] * df['volume']).cumsum()
    df['cum_vol'] = df['volume'].cumsum()
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
    
    return df
