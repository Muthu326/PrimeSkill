import threading
import time
import logging
import sys
import pandas as pd
from datetime import datetime
from services.upstox_engine import get_upstox_engine
from services.upstox_streamer import get_streamer, get_live_ltp
from scanners.index_scanner import get_index_bias, run_index_scan
from scanners.stock_scanner import run_parallel_stock_scan
from utils.logger import setup_logger
from pro_config import SCAN_INDICES, NIFTY_50_STOCKS

# --- STARTUP VALIDATION ---
logger = setup_logger("MainController")
logger.info("🛠 Validating System Modules...")

required_modules = [
    "scanners.index_scanner",
    "scanners.stock_scanner",
    "engine.scoring_engine",
    "engine.risk_manager",
    "utils.helpers"
]

for module in required_modules:
    try:
        __import__(module)
    except ImportError as e:
        logger.error(f"❌ Missing or Corrupt Module: {module} | Error: {e}")
        sys.exit(1)

logger.info("✅ Startup Validation Successful.")

def main():
    logger.info("🔥 PRO-VERSION BULLETPROOF ENGINE STARTING...")
    
    # 1. Initialize API Engine
    engine = get_upstox_engine()
    
    # 2. Map Instruments for WebSocket
    fo_symbols = [s.replace(".NS", "") for s in NIFTY_50_STOCKS]
    all_symbols = SCAN_INDICES + fo_symbols
    
    logger.info(f"📡 Mapping {len(all_symbols)} instruments...")
    instrument_map = {}
    for sym in all_symbols:
        k = engine.get_instrument_key(sym)
        if k:
            instrument_map[sym] = k
        else:
            if sym == "NIFTY": instrument_map[sym] = "NSE_INDEX|Nifty 50"
            elif sym == "BANKNIFTY": instrument_map[sym] = "NSE_INDEX|Nifty Bank"
            elif sym == "SENSEX": instrument_map[sym] = "BSE_INDEX|SENSEX"

    # 3. Start High-Speed WebSocket Streamer
    streamer = get_streamer()
    streamer.start(initial_keys=list(instrument_map.values()))
    
    # 4. Initialize Institutional Engines
    from services.news_engine import get_news_engine
    from services.sentiment_engine import get_sentiment_engine
    news_engine = get_news_engine()
    
    logger.info("🏛 Initializing Institutional Control Architecture...")

    last_scan_time = 0
    SCAN_INTERVAL = 300 # 5 Minutes Default
    POWER_WINDOW_SENT = False
    bias = {}

    while True:
        try:
            now = datetime.now()
            current_ts = time.time()
            
            # --- 🛡️ MARKET TIME CONTROL ---
            if now.hour == 15 and now.minute >= 25:
                logger.info("🕒 Market Close (3:25 PM). Dispatching Daily Summary...")
                from services.trade_monitor import get_trade_monitor
                get_trade_monitor().send_daily_summary()
                break

            # --- 📡 INSTITUTIONAL MODE CHECK ---
            nifty_key = instrument_map.get("NIFTY")
            nifty_ltp = (get_live_ltp(nifty_key) or 0) if nifty_key else 0
            if nifty_ltp == 0 and 'bias' in locals() and isinstance(bias, dict) and not bias.get('nifty_df', pd.DataFrame()).empty:
                nifty_ltp = bias['nifty_df']['close'].iloc[-1]
                
            mode, reason = news_engine.get_market_mode(symbol_ltp_map={"NIFTY": nifty_ltp} if nifty_ltp > 0 else None)
            
            # --- ⏰ INSTITUTIONAL SCHEDULER HEARTBEAT ---
            from services.scheduler import get_scheduler
            get_scheduler().check_schedule()

            if mode == "BLOCKED":
                logger.warning(f"🛑 TRADING BLOCKED: {reason}. Waiting for stabilization...")
                time.sleep(30)
                continue

            # --- ⚡ 3 PM POWER WINDOW OVERRIDE ---
            is_power_window = (now.hour == 15 and 0 <= now.minute < 20)
            if is_power_window:
                SCAN_INTERVAL = 60 
                if not POWER_WINDOW_SENT:
                    logger.info("🔥 3 PM POWER WINDOW ACTIVE - High Frequency (Every 60s)...")
                    POWER_WINDOW_SENT = True
            else:
                SCAN_INTERVAL = 300 # Reset to 5 mins

            # TIER 1: Get Index Bias & Sentiment
            logger.info(f"📡 Index Scan Started [Mode: {mode}]...")
            bias = get_index_bias(engine, instrument_map)
            
            # Run Index Scan with Sentiment Integration
            run_index_scan(engine, instrument_map, bias)
            
            # TIER 2: Run Stock Scanner if Interval Reached
            if current_ts - last_scan_time >= SCAN_INTERVAL:
                tag_suffix = " 🏛️ 3PM POWER" if is_power_window else ""
                if mode == "VOLATILE": tag_suffix += " ⚠️ VOLATILE"
                
                logger.info(f"🚀 Stock Scan Started{tag_suffix} (ADX: {bias.get('adx', 0):.1f})...")
                run_parallel_stock_scan(engine, instrument_map, bias)
                last_scan_time = current_ts
                logger.info("✅ Parallel Scan Cycle Complete.")

            time.sleep(5) 

        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested...")
            break
        except Exception as e:
            logger.error(f"❌ Critical Engine Failure: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
