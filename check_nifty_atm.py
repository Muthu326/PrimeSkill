import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

import sys
sys.path.append(os.getcwd())

from services.upstox_engine import get_upstox_engine
from am_backend_scanner import get_atm_strike, get_option_chain_analysis
from scanner_config import SCAN_INDICES, NIFTY_50_STOCKS

def check_nifty_50_spot_and_atm():
    load_dotenv()
    engine = get_upstox_engine()
    
    print(f"🏛️ Nifty 50 & Indices Spot/ATM Dashboard")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Process Indices + First 5 Nifty 50 stocks
    universe = SCAN_INDICES + NIFTY_50_STOCKS[:5]
    
    results = []
    
    print(f"📡 Mapping instruments...")
    key_map = {}
    for sym in universe:
        k = engine.get_instrument_key(sym)
        if k: 
            key_map[sym] = k
        else:
            print(f"⚠️ Could not map instrument for: {sym}")
    
    all_keys = list(key_map.values())
    quotes = engine.get_market_quote(all_keys, mode="full")
    
    for sym, key in key_map.items():
        try:
            spot = float(quotes.get(key, {}).get('last_price', 0))
            if spot <= 0: spot = float(quotes.get(key, {}).get('close', 0))
            
            if spot <= 0:
                print(f"⚠️ {sym}: No spot price found in quotes.")
                continue
            
            atm_strike = get_atm_strike(spot, sym)
            analysis = get_option_chain_analysis(engine, sym)
            
            ce_prem = 0.0
            pe_prem = 0.0
            expiry = "N/A"
            
            if analysis and 'df' in analysis:
                expiry = analysis['expiry']
                df = analysis['df']
                atm_row = df[abs(df['strike'] - atm_strike) < 0.1]
                if not atm_row.empty:
                    ce_prem = float(atm_row.iloc[0]['call_ltp'])
                    pe_prem = float(atm_row.iloc[0]['put_ltp'])
            
            results.append({
                "Symbol": sym,
                "Spot": spot,
                "ATM": atm_strike,
                "CE Prem": ce_prem,
                "PE Prem": pe_prem,
                "Expiry": expiry
            })
            print(f"✅ {sym:12} | Spot: {spot:,.2f} | ATM: {atm_strike:7} | Exp: {expiry} | CE: {ce_prem:6.2f} | PE: {pe_prem:6.2f}")
            
        except Exception as e:
            print(f"❌ Error for {sym}: {e}")

    if results:
        df = pd.DataFrame(results)
        print("\n" + "="*85)
        print(f"{'NIFTY 50 & INDICES ATM PREVIEW':^85}")
        print("="*85)
        print(df.to_string(index=False))
        print("="*85)

if __name__ == "__main__":
    check_nifty_50_spot_and_atm()
