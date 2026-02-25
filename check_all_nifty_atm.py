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

def check_all_nifty_50_stocks():
    load_dotenv()
    engine = get_upstox_engine()
    
    print(f"🏛️ FULL NIFTY 50 + INDICES SPOT/ATM DASHBOARD")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Process Indices + ALL Nifty 50 stocks
    universe = SCAN_INDICES + NIFTY_50_STOCKS
    
    results = []
    
    print(f"📡 Mapping {len(universe)} instruments...")
    key_map = {}
    for sym in universe:
        k = engine.get_instrument_key(sym)
        if k: 
            key_map[sym] = k
    
    # Fetch quotes in chunks to avoid URL length issues (Upstox limit is often ~50-100 symbols)
    all_keys = list(key_map.values())
    quotes = {}
    chunk_size = 30
    
    print(f"📊 Fetching quotes in chunks...")
    for i in range(0, len(all_keys), chunk_size):
        chunk = all_keys[i:i + chunk_size]
        q = engine.get_market_quote(chunk, mode="full")
        quotes.update(q)
        time.sleep(0.5) # Avoid rate limiting
    
    print(f"📈 Processing specific ATM data for each stock...")
    
    for sym, key in key_map.items():
        try:
            # Get Spot
            quote_data = quotes.get(key, {})
            spot = float(quote_data.get('last_price', 0))
            if spot <= 0: spot = float(quote_data.get('close', 0))
            
            if spot <= 0:
                # If still 0, try a quick LTP direct fetch
                l_quote = engine.get_market_quote([key], mode="ltp")
                spot = float(l_quote.get(key, {}).get('last_price', 0))
                
            if spot <= 0: continue
            
            atm_strike = get_atm_strike(spot, sym)
            
            # Use chain analysis (this includes its own caching)
            analysis = get_option_chain_analysis(engine, sym)
            
            ce_prem = 0.0
            pe_prem = 0.0
            expiry = "N/A"
            
            if analysis and 'df' in analysis:
                expiry = analysis['expiry']
                df = analysis['df']
                # Search for closest strike to ATM
                df['diff'] = abs(df['strike'] - atm_strike)
                atm_row = df.sort_values('diff').iloc[0]
                
                if atm_row['diff'] < (atm_strike * 0.05): # Safety check
                    ce_prem = float(atm_row['call_ltp'])
                    pe_prem = float(atm_row['put_ltp'])
            
            results.append({
                "Symbol": sym,
                "Spot": spot,
                "ATM Strike": atm_strike,
                "CE Premium": ce_prem,
                "PE Premium": pe_prem,
                "Expiry": expiry
            })
            
            # Console progress for feedback
            indicator = "✅" if ce_prem > 0 else "🟠"
            # print(f"{indicator} {sym:12} | Spot: {spot:,.2f} | ATM: {atm_strike}")
            
        except Exception as e:
            # print(f"❌ Error for {sym}: {e}")
            pass

    if results:
        df = pd.DataFrame(results)
        
        # Format for display
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1000)
        
        print("\n" + "="*95)
        print(f"{'INSTITUTIONAL SNAPSHOT: ALL NIFTY 50 + INDICES':^95}")
        print("="*95)
        print(df.to_string(index=False))
        print("="*95)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/full_nifty50_atm_{timestamp}.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"\n📂 Full report saved to: {filename}")
    else:
        print("❌ No data could be retrieved.")

if __name__ == "__main__":
    check_all_nifty_50_stocks()
