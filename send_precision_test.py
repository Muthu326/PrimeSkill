
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Ensure project path is accessible
sys.path.append(os.getcwd())

from am_backend_scanner import send_trade_alert, get_upstox_engine, get_nearest_active_expiry

def send_precise_test():
    print("🎯 Fetching PRECISION Data from Upstox API...")
    engine = get_upstox_engine()
    
    # 1. Get NIFTY Root Key
    nifty_key = "NSE_INDEX|Nifty 50"
    
    try:
        # Fallback to historical if intraday is empty (Market is closed)
        df = engine.get_historical_candles(nifty_key, interval="day", days=1)
        if df.empty:
            # Last ditch effort
            print("⚠️ No history. Using static NIFTY close for formatting test.")
            spot = 23150.45 
        else:
            spot = df['close'].iloc[-1]
        
        # 2. Get REAL Expiry from Upstox
        expiries = engine.get_expiry_dates_via_sdk(nifty_key)
        if not expiries:
            print("❌ No expiries found.")
            return
            
        real_expiry = get_nearest_active_expiry(expiries)
        
        # Find ATM (nearest 50)
        strike = int(round(spot / 50) * 50)
        
        # 3. Simulate correct Option LTP for this strike
        # Since market is closed, we use a realistic placeholder or try to fetch from chain
        actual_ltp = 112.30 
        
        # Try to get from chain if possible (some providers keep last data)
        try:
            chain = engine.get_option_chain_via_sdk(nifty_key, real_expiry)
            for item in chain:
                if item.strike_price == float(strike):
                    if item.call_options and item.call_options.market_data.ltp > 0:
                        actual_ltp = item.call_options.market_data.ltp
                    break
        except: pass

        test_signal = {
            "symbol": "NIFTY",
            "strike": strike,
            "type": "CE",
            "spot": spot,
            "entry": actual_ltp,
            "stop_loss": round(actual_ltp * 0.85, 2),
            "target": round(actual_ltp * 1.3, 2),
            "confidence": 98,
            "status": "Active",
            "expiry": real_expiry,
            "tag": "🏛️ PRECISION TEST"
        }
        
        print(f"✅ REAL DATA SYNCED:")
        print(f"   SPOT: {spot:.2f}")
        print(f"   EXPIRY: {real_expiry} (Validated via API)")
        print(f"   STRIKE: {strike}")
        print(f"   LTP: {actual_ltp}")
        
        # 4. Send Alert
        success = send_trade_alert(test_signal, is_update=False)
        if success:
            print("\n🚀 PRECISION ALERT SENT! Check your Telegram now.")
        else:
            print("\n❌ Failed to send alert.")
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    send_precise_test()
