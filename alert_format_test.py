import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

# Import functions from backend scanner
from am_backend_scanner import send_trade_alert, send_15min_summary, send_telegram

def run_test():
    print("🚀 Starting Professional Alert Format Test...")
    
    # Enable TEST MODE flag for the header
    os.environ["TEST_MODE"] = "true"
    
    # 1. Test Trade Alert (NIFTY 50)
    print("📡 Sending Nifty 50 Trade Alert...")
    nifty_signal = {
        "symbol": "^NSEI",
        "type": "CE",
        "strike": 22200,
        "spot": 22198.50,
        "entry": 145.20,
        "stop_loss": 130.00,
        "target": 190.00,
        "confidence": 92,
        "status": "Active Opportunity",
        "expiry": "27-FEB-2024",
        "tag": "🌐 INDEX BIAS"
    }
    send_trade_alert(nifty_signal)
    
    # 2. Test Trade Alert (BANK NIFTY)
    print("📡 Sending Bank Nifty Trade Alert...")
    bn_signal = {
        "symbol": "^NSEBANK",
        "type": "PE",
        "strike": 46500,
        "spot": 46480.20,
        "entry": 320.50,
        "stop_loss": 280.00,
        "target": 420.00,
        "confidence": 88,
        "status": "Active Opportunity",
        "expiry": "27-FEB-2024",
        "tag": "💎 DIAMOND"
    }
    send_trade_alert(bn_signal)
    
    # 3. Test Trade Alert (Stock - RELIANCE)
    print("📡 Sending Stock Trade Alert (RELIANCE)...")
    stock_signal = {
        "symbol": "RELIANCE",
        "type": "CE",
        "strike": 2980,
        "spot": 2975.00,
        "entry": 42.00,
        "stop_loss": 35.00,
        "target": 65.00,
        "confidence": 78,
        "status": "Active Opportunity",
        "expiry": "27-FEB-2024",
        "tag": "🚀 TOP PICK🏆"
    }
    send_trade_alert(stock_signal)

    # 4. Test Sector Leadership Alert
    print("📡 Sending Sector Leadership Alert...")
    sector_msg = (
        "🧪 TEST 🏛 *SECTOR LEADERSHIP: BANKING*\n"
        "━━━━━━━━━━━━━━\n"
        "📍 **STATUS**: `STRONG_BULLISH` 🚀\n"
        "🎯 **STRATEGY**: `Focus on BANKING Call Options`\n"
        "━━━━━━━━━━━━━━\n"
        "👤 *PrimeSkillDevelopment CEO : MuthuKumar krishnan*"
    )
    send_telegram(sector_msg)

    # 5. Test 15-Min Summary Pulse
    print("📡 Sending 15-Min Market Pulse...")
    pcr_data = {
        "overall": {"pcr": 1.05, "bias": "NEUTRAL"},
        "NIFTY": {"pcr": 0.98, "ce_oi": 85000000, "pe_oi": 83300000},
        "BANKNIFTY": {"pcr": 1.12, "ce_oi": 42000000, "pe_oi": 47040000}
    }
    send_15min_summary(pcr_data)

    print("\n✅ All test formats sent to Telegram!")

if __name__ == "__main__":
    run_test()
