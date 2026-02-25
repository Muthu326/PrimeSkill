
import requests
import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Ensure the root directory is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from services.upstox_engine import get_upstox_engine

load_dotenv()

def get_hdfclife_details():
    engine = get_upstox_engine()
    symbol = "HDFCLIFE"
    
    # 1. Diagnostic: Find actual key
    matches = engine.find_all_instruments(symbol)
    
    # Most likely: NSE_EQ|INE795G01014 or HDFCLIFE
    key = None
    for k in matches:
        if "NSE_EQ" in matches[k] and k == "HDFCLIFE":
            key = matches[k]
            symbol_matched = k
            break
            
    if not key:
        # Fallback to any NSE_EQ match
        for k in matches:
            if "NSE_EQ" in matches[k]:
                key = matches[k]
                symbol_matched = k
                break

    if not key:
        print(f"❌ Could not find reliable instrument key for {symbol}")
        return

    print(f"✅ Using Key: {key} (Symbol: {symbol_matched})")

    # 2. Get Live Spot Price
    try:
        url_intra = f"https://api.upstox.com/v2/historical-candle/intraday/{key}/1minute"
        headers = {"Authorization": f"Bearer {os.getenv('UPSTOX_ACCESS_TOKEN')}", "Accept": "application/json"}
        print(f"📡 Testing Intraday URL: {url_intra}")
        resp = requests.get(url_intra, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        spot = 0
        if resp.status_code == 200:
            candles = resp.json().get("data", {}).get("candles", [])
            print(f"✅ Received {len(candles)} intraday candles.")
            if candles:
                spot = float(candles[0][4]) # Latest close
                print(f"Latest candle time: {candles[0][0]}, Close: {spot}")
            else:
                print("⚠️ No candles returned for intraday.")
        else:
            print(f"❌ Intraday Error: {resp.text}")

        if spot <= 0:
            # Try historical as ultimate fallback - LOOK BACK 2 DAYS
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - pd.Timedelta(days=2)).strftime("%Y-%m-%d")
            url_hist = f"https://api.upstox.com/v2/historical-candle/{key}/day/{to_date}/{from_date}"
            print(f"📡 Testing Historical Day URL: {url_hist}")
            resp_h = requests.get(url_hist, headers=headers, timeout=10)
            if resp_h.status_code == 200:
                h_candles = resp_h.json().get("data", {}).get("candles", [])
                if h_candles:
                    # Candles are sorted newest first, so [0] is the most recent close
                    spot = float(h_candles[0][4])
                    print(f"✅ Historical Close (Date: {h_candles[0][0]}): ₹{spot}")
    except Exception as e:
        print(f"Error fetching spot: {e}")
        spot = 0
    
    if spot <= 0:
        print(f"❌ Could not fetch live spot price for {symbol}")
        return
        
    print(f"📍 {symbol} Spot Price: ₹{spot:.2f}")
    
    if spot <= 0:
        print(f"❌ Could not fetch live spot price for {symbol}")
        return
        
    print(f"📍 {symbol} Spot Price: ₹{spot:.2f}")

    # 3. Calculate ATM Strike
    gap = 10 # HDFCLIFE strike gap is usually 10
    atm_strike = round(spot / gap) * gap
    print(f"🎯 ATM Strike: {atm_strike}")

    # 4. Get Nearest Active Expiry
    expiries = engine.get_expiry_dates_via_sdk(key)
    if not expiries:
        print("❌ No expiry dates found")
        return
        
    now_str = datetime.now().strftime("%Y-%m-%d")
    valid_expiries = [e for e in expiries if e >= now_str]
    if not valid_expiries:
        print("❌ No upcoming expiries found")
        return
        
    expiry = valid_expiries[0]
    print(f"📅 Nearest Expiry: {expiry}")

    # 5. Fetch Option LTPs
    # We need to find the specific instrument keys for CE and PE at this strike/expiry
    chain = engine.get_option_chain_via_sdk(key, expiry)
    if not chain:
        print("❌ Could not fetch option chain")
        return

    ce_ltp = 0
    pe_ltp = 0
    
    for contract in chain:
        if abs(contract.strike_price - atm_strike) < 0.1:
            if contract.call_options and contract.call_options.market_data:
                ce_ltp = contract.call_options.market_data.ltp
            if contract.put_options and contract.put_options.market_data:
                pe_ltp = contract.put_options.market_data.ltp
            break

    print(f"🟢 {atm_strike} CE LTP: ₹{ce_ltp:.2f}")
    print(f"🔴 {atm_strike} PE LTP: ₹{pe_ltp:.2f}")

if __name__ == "__main__":
    get_hdfclife_details()
