
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
    try:
        expiries = engine.get_expiry_dates_via_sdk(inst_key)
        if not expiries:
            print(f"❌ No expiries found for {symbol}. This stock might not be in F&O segment.")
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
        
        # Sort chain by strike
        sorted_chain = sorted(chain, key=lambda x: x.strike_price)
        
        # Show middle 10 strikes (ATM region)
        mid = len(sorted_chain) // 2
        display_subset = sorted_chain[max(0, mid-5):min(len(sorted_chain), mid+5)]
        
        for item in display_subset:
            ce_ltp = item.call_options.market_data.ltp if item.call_options else "N/A"
            pe_ltp = item.put_options.market_data.ltp if item.put_options else "N/A"
            print(f"{item.strike_price:<10} | {ce_ltp:<10} | {pe_ltp:<10}")

        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ Options Availability Confirmed for {symbol}")
    except Exception as e:
        print(f"❌ Error checking options: {e}")

if __name__ == "__main__":
    check_stock_options("RELIANCE")
    print("\n")
    check_stock_options("HDFCBANK")
    print("\n")
    check_stock_options("SBIN")
