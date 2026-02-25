import os
import sys
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.getcwd())

from utils.telegram_alert import send_trade_alert, send_telegram
from services.sentiment_engine import get_sentiment_engine
from services.news_engine import get_news_engine

def send_sample_alerts():
    print("🚀 Sending Sample Institutional Alerts...")
    
    # 1. Sample Entry Alert (Index)
    sample_entry = {
        "symbol": "NIFTY",
        "type": "CE",
        "strike": 22200,
        "premium": 145.80,
        "target": 180.00,
        "stop_loss": 130.00,
        "score": 85,  # STRONG (🔴)
        "tag": "🏛 PRIMARY SKILL",
        "expiry": "2026-02-27",
        "option_key": "NSE_FO|54321",
        "price_ts": datetime.now().timestamp(),
        "generated_at": datetime.now().strftime("%H:%M:%S"),
        "target_window": "Intraday (High Momentum)",
        "sentiment": "STRONG BULLISH",
        "pcr": 0.72,
        "max_pain": 22100
    }
    
    # Send Entry Alert
    send_trade_alert(sample_entry)
    print("✅ Sample Entry Alert Sent.")

    # 2. High Conviction Sample (💎)
    high_conv_entry = {
        "symbol": "BANKNIFTY",
        "type": "PE",
        "strike": 48000,
        "premium": 210.50,
        "target": 350.00,
        "stop_loss": 180.00,
        "score": 92,  # DIAMOND (💎)
        "option_key": "NSE_FO|67890",
        "price_ts": datetime.now().timestamp(),
        "sentiment": "STRONG BEARISH",
        "pcr": 1.45,
        "max_pain": 48500
    }
    send_trade_alert(high_conv_entry)
    print("✅ High Conviction Sample Sent.")

if __name__ == "__main__":
    send_sample_alerts()
