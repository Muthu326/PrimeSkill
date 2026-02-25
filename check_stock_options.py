
import os
import json
import pandas as pd
from dotenv import load_dotenv
from services.upstox_engine import get_upstox_engine

load_dotenv()

def check_stock_options(symbol="RELIANCE"):
    print(f"🔍 Checking Option Availability for: {symbol}")
    engine = get_upstox_engine()
    
    # 1. Get Instrument Key
    inst_key = engine.get_instrument_key(symbol)
    if not inst_key:
        print(f"❌ Could not find instrument key for {symbol}")
        return

    # 2. Get Expiries
    expiries = engine.get_expiry_dates_via_sdk(inst_key)
    if not expiries:
        print(f"❌ No expiries found for {symbol}")
        return
    
    expiries.sort()
    nearest_expiry = expiries[0]
    print(f"📅 Nearest Expiry: {nearest_expiry}")

    # 3. Get Option Chain
    print(f"📡 Fetching Option Chain for {symbol}...")
    chain = engine.get_option_chain_via_sdk(inst_key, nearest_expiry)
    
    if not chain:
        print(f"❌ Could not fetch option chain.")
        return

    # 4. Filter and Display a few strikes
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{'STRIKE':<10} | {'CE LTP':<10} | {'PE LTP':<10}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Show only 10 strikes around the spot
    # We need spot to center it
    quote = engine.get_market_quote([inst_key])
    spot = quote[inst_key]['last_price']
    print(f"📍 Spot Price: {spot}")
    
    # Sort chain by strike
    sorted_chain = sorted(chain, key=lambda x: x.strike_price)
    
    # Find strikes near spot
    count = 0
    for item in sorted_chain:
        if abs(item.strike_price - spot) < 100: # Showing strikes within 100 points
            ce_ltp = item.call_options.market_data.ltp if item.call_options else "N/A"
            pe_ltp = item.put_options.market_data.ltp if item.put_options else "N/A"
            print(f"{item.strike_price:<10} | {ce_ltp:<10} | {pe_ltp:<10}")
            count += 1
        if count >= 10: break

    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Options Availability Confirmed for {symbol}")

if __name__ == "__main__":
    check_stock_options("RELIANCE")
    print("\n")
    check_stock_options("HDFCBANK")
