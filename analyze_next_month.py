import os
import sys
from datetime import datetime, timedelta
from services.upstox_engine import get_upstox_engine
import pandas as pd

def analyze_next_month():
    print("🏛️ INSTITUTIONAL NEXT-MONTH ANALYSIS ENGINE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    engine = get_upstox_engine()
    
    indices = {
        "NIFTY 50": "NSE_INDEX|Nifty 50",
        "BANK NIFTY": "NSE_INDEX|Nifty Bank"
    }
    
    for name, key in indices.items():
        print(f"\n🔍 Analyzing {name}...")
        
        # 1. Get Spot Price
        quote = engine.get_market_quote([key])
        if not quote:
            print(f"❌ Could not fetch quote for {name}")
            continue
            
        spot = quote[key]['last_price']
        print(f"📍 Current Spot: ₹{spot:,.2f}")
        
        # 2. Get Expiries
        expiries = engine.get_expiry_dates_via_sdk(key)
        if not expiries:
            print(f"❌ Could not fetch expiries for {name}")
            continue
            
        # Identify next month's monthly expiry (usually the one closest to end of next month)
        # For simplicity, we'll look at March 2026 expiries since current is Feb.
        next_month_expiries = [e for e in expiries if "-03-" in e]
        
        if not next_month_expiries:
            print(f"❌ No March expiries found for {name}")
            continue
            
        # Monthly is usually the last one of the month
        monthly_expiry = next_month_expiries[-1]
        print(f"📅 Next Monthly Expiry: {monthly_expiry}")
        
        # 3. Fetch Option Chain
        print(f"📡 Downloading {monthly_expiry} Option Chain for Institutional Analysis...")
        chain = engine.get_option_chain_via_sdk(key, monthly_expiry)
        
        if not chain:
            print(f"⚠️ Empty option chain for {monthly_expiry}")
            continue
            
        # 4. Process Data
        data = []
        for strike in chain:
            call_oi = strike.call_options.market_data.oi if strike.call_options else 0
            put_oi = strike.put_options.market_data.oi if strike.put_options else 0
            
            data.append({
                "strike": strike.strike_price,
                "call_oi": call_oi,
                "put_oi": put_oi
            })
            
        df = pd.DataFrame(data)
        
        # 5. Find Max Pain & Resistance/Support
        max_call_oi_strike = df.loc[df['call_oi'].idxmax()]
        max_put_oi_strike = df.loc[df['put_oi'].idxmax()]
        
        total_call_oi = df['call_oi'].sum()
        total_put_oi = df['put_oi'].sum()
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        print(f"💹 Next-Month PCR: {pcr:.2f}")
        
        # Biased Logic
        bias = "BULLISH 🚀" if pcr > 1.2 else "BEARISH 📉" if pcr < 0.8 else "NEUTRAL ⛓️"
        print(f"⚖️ Institutional Bias: {bias}")
        
        print(f"🏠 Major Support (Highest Put OI): {max_put_oi_strike['strike']} (OI: {max_put_oi_strike['put_oi']})")
        print(f"🚧 Major Resistance (Highest Call OI): {max_call_oi_strike['strike']} (OI: {max_call_oi_strike['call_oi']})")
        
        # Opportunity Identification
        if bias == "BULLISH 🚀":
            print(f"💡 OPPORTUNITY: Accumulate {monthly_expiry} CE if {name} stays above {max_put_oi_strike['strike']}")
        elif bias == "BEARISH 📉":
            print(f"💡 OPPORTUNITY: Accumulate {monthly_expiry} PE if {name} stays below {max_call_oi_strike['strike']}")
        else:
            print(f"💡 OPPORTUNITY: Iron Condor or Straddle suggested around {round(spot/100)*100}")

if __name__ == "__main__":
    analyze_next_month()
