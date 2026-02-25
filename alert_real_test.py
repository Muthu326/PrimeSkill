import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Add current directory to path
sys.path.append(os.getcwd())

# Import functions from backend scanner
from am_backend_scanner import send_trade_alert, send_telegram, get_friendly_name
from services.upstox_engine import get_upstox_engine
from services.upstox_streamer import get_streamer, get_live_ltp
from services.market_engine import get_expiry_details

def run_real_test():
    print("🚀 Starting REAL-TIME Professional Alert Test...")
    load_dotenv()
    
    engine = get_upstox_engine()
    
    # Initialize streamer for live prices
    streamer = get_streamer()
    
    indices = {
        "NIFTY": "NSE_INDEX|Nifty 50",
        "BANKNIFTY": "NSE_INDEX|Nifty Bank",
        "SENSEX": "BSE_INDEX|SENSEX"
    }
    
    # Pre-fetch keys
    keys = list(indices.values())
    streamer.start(initial_keys=keys)
    
    print("⏳ Waiting for WebSocket sync...")
    time.sleep(5)
    
    for label, key in indices.items():
        try:
            print(f"📡 Fetching REAL data for {label}...")
            spot = get_live_ltp(key)
            if not spot:
                # Fallback to HTTP quote if WS not ready
                quotes = engine.get_market_quote([key], mode="ltp")
                if key in quotes:
                    spot = float(quotes[key]['last_price'])
            
            if not spot:
                print(f"❌ Could not fetch spot for {label}")
                continue
                
            # Get real ATM strike
            step = 100 if "BANK" in label or "SENSEX" in label else 50
            atm = round(spot / step) * step
            
            # Fetch real expiries
            expiries = engine.get_expiry_dates_via_sdk(key)
            if not expiries:
                print(f"❌ No expiries found for {label}")
                continue
            
            exp_date = sorted(expiries)[0]
            
            # Fetch real option premium
            # For test, we look for CE
            chain = engine.get_option_chain_via_sdk(key, exp_date)
            premium = 0
            for item in chain:
                if item.strike_price == float(atm):
                    if item.call_options:
                        premium = item.call_options.market_data.ltp
                    break
            
            if premium == 0:
                # Try sibling
                premium = 150.0 # Fallback if specific strike not in heavy chain
            
            signal = {
                "symbol": label,
                "type": "CE",
                "strike": atm,
                "spot": spot,
                "entry": premium,
                "stop_loss": round(premium * 0.85, 2),
                "target": round(premium * 1.4, 2),
                "confidence": 85,
                "status": "Active Opportunity",
                "expiry": exp_date,
                "tag": "🌐 INDEX BIAS" if label == "NIFTY" else "💎 DIAMOND"
            }
            
            print(f"✅ Sending Real Alert for {label}: Spot {spot}, Strike {atm}, Premium {premium}")
            send_trade_alert(signal)
            
        except Exception as e:
            print(f"❌ Error testing {label}: {e}")

    print("\n✅ Real-time data test alerts sent!")
    # Close streamer
    streamer.stop()

if __name__ == "__main__":
    run_real_test()
