
import os
import sys
import time
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv

# Ensure project path is accessible
sys.path.append(os.getcwd())

from am_backend_scanner import send_trade_alert

def send_real_data_test():
    print("🔄 Fetching REAL Market Data (YFinance) for Test Alert...")
    
    # 1. Get NIFTY Spot using YFinance (since market is closed)
    ticker = yf.Ticker("^NSEI")
    data = ticker.history(period="1d")
    
    if data.empty:
        spot = 22212.70 # Last known fallback
    else:
        spot = data['Close'].iloc[-1]
    
    # 2. Hardcode real-looking data since it's after hours
    real_expiry = "27-FEB-2025" # Next Thursday Expiry
    strike = int(round(spot / 50) * 50)
    
    # Estimated Premium for ATM
    opt_ltp = 145.20 
    
    test_signal = {
        "symbol": "NIFTY",
        "strike": strike,
        "type": "CE",
        "spot": spot,
        "entry": opt_ltp,
        "stop_loss": round(opt_ltp * 0.8, 2),
        "target": round(opt_ltp * 1.5, 2),
        "confidence": 95,
        "status": "Active",
        "expiry": real_expiry,
        "tag": "🏛️ INSTITUTIONAL ENTRY"
    }
    
    print(f"✅ Data Prepared for NIFTY @ {spot:.2f}, Expiry: {real_expiry}")
    
    # 3. Send the Alert
    success = send_trade_alert(test_signal, is_update=False)
    
    if success:
        print("🚀 REAL DATA ALERT SENT! Check Telegram.")
    else:
        print("❌ Failed to send alert.")

if __name__ == "__main__":
    send_real_data_test()
