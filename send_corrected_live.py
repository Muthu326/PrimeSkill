import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

# Import actual production functions
from am_backend_scanner import (
    send_trade_alert, 
    get_friendly_name, 
    pick_professional_expiry, 
    get_option_ltp,
    get_atm_strike
)
from services.upstox_engine import get_upstox_engine
from services.upstox_streamer import get_streamer, get_live_ltp

def send_corrected_live_alert():
    print("🚀 Initializing CORRECTED Live Data Alert...")
    load_dotenv()
    engine = get_upstox_engine()
    
    # 🟢 STEP 1: Sync Streamer
    streamer = get_streamer()
    keys = ["NSE_INDEX|Nifty 50", "NSE_INDEX|Nifty Bank", "BSE_INDEX|SENSEX"]
    streamer.start(initial_keys=keys)
    time.sleep(3) # Wait for cache
    
    indices = ["NIFTY", "BANKNIFTY", "SENSEX"]
    
    for symbol in indices:
        try:
            print(f"📡 Processing {symbol}...")
            # 🟢 STEP 2: Actual Spot
            inst_key = engine.get_instrument_key(symbol)
            spot = get_live_ltp(inst_key)
            if not spot:
                quotes = engine.get_market_quote([inst_key], mode="ltp")
                spot = float(quotes[inst_key]['last_price'])
            
            # 🟢 STEP 3: Actual Professional Expiry (Next Week if close)
            expiries = engine.get_expiry_dates_via_sdk(inst_key)
            target_exp = pick_professional_expiry(expiries, symbol=symbol)
            
            # 🟢 STEP 4: Actual ATM Strike
            strike = get_atm_strike(spot, symbol)
            
            # 🟢 STEP 5: Actual LTP of the OPTION
            premium = get_option_ltp(engine, symbol, strike, "CE", target_expiry=target_exp)
            
            if not premium: premium = 0
            
            signal = {
                "symbol": symbol,
                "type": "CE",
                "strike": strike,
                "spot": spot,
                "entry": premium,
                "stop_loss": round(premium * 0.85, 2),
                "target": round(premium * 1.5, 2),
                "confidence": 95,
                "status": "Active Opportunity",
                "expiry": target_exp,
                "tag": "🌐 INDEX BIAS"
            }
            
            print(f"✅ Corrected Signal for {symbol}: Expiry {target_exp}, Premium {premium}")
            send_trade_alert(signal)
            
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
            
    streamer.stop()

if __name__ == "__main__":
    send_corrected_live_alert()
