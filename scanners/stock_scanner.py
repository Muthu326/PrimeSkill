import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pro_config import NIFTY_50_STOCKS
from engine.indicators import calculate_indicators
from engine.scoring_engine import calculate_professional_score
from engine.risk_manager import risk_check
from engine.option_selector import pick_best_strike, estimate_target_sl, pick_professional_expiry, get_option_ltp
from utils.logger import setup_logger
from utils.telegram_alert import send_trade_alert
from utils.helpers import load_active_signals, load_alerts_sent, load_daily_stats, save_active_signals, save_daily_stats, save_inst_results
from services.upstox_streamer import get_live_ltp

logger = setup_logger("StockScanner")
tag = "🚀 Prime Skill"

def scan_single_stock(engine, sym, key, bias, active_signals, daily_stats):
    """
    Independent worker function for a single stock using Reversal Engine MTF logic.
    """
    from engine.reversal_engine import get_reversal_engine
    rev_engine = get_reversal_engine()
    
    try:
        spot = get_live_ltp(key)
        if not spot: return None
        
        # 1. Fetch MTF stock data
        df_5m = engine.get_intraday_candles(key, interval="5minute")
        df_1m = engine.get_intraday_candles(key, interval="1minute")
        
        if df_5m.empty or len(df_5m) < 20 or df_1m.empty: return None
        
        df_5m = calculate_indicators(df_5m)
        df_1m = calculate_indicators(df_1m)
        
        lat_5m = df_5m.iloc[-1]
        lat_1m = df_1m.iloc[-1]
        
        # 2. MTF Signal Confirmation Layer
        def get_stock_sig(latest):
            price = latest['close']
            ema = latest.get('ema20', price)
            rsi = latest.get('rsi', 50)
            if price > ema and rsi > 55: return "CE"
            if price < ema and rsi < 45: return "PE"
            return None

        sig_5m = get_stock_sig(lat_5m)
        sig_1m = get_stock_sig(lat_1m)

        if not sig_5m or not sig_1m:
            return None

        data_1m = {
            "signal": sig_1m,
            "volume": lat_1m.get('volume', 0),
            "avg_volume": df_1m['volume'].tail(20).mean(),
            "rsi": lat_1m.get('rsi', 50),
            "volume_ratio": lat_1m.get('volume', 1) / (df_1m['volume'].tail(20).mean() or 1),
            "price_vs_vwap": lat_1m['close'] > lat_1m['vwap'] if sig_1m == "CE" else lat_1m['close'] < lat_1m['vwap']
        }
        
        data_5m = {
            "signal": sig_5m,
            "adx": lat_5m.get('adx', 0)
        }

        if not rev_engine.multi_tf_confirmation(data_1m, data_5m):
            return None

        # 3. Decision Logic & Strength Score
        strength = rev_engine.reversal_strength(
            data_1m["rsi"], 
            data_5m["adx"], 
            data_1m["volume_ratio"], 
            data_1m["price_vs_vwap"]
        )
        
        if strength < rev_engine.STRENGTH_THRESHOLD:
            return None

        # Check for reversal stability
        if not rev_engine.check_reversal(sym, sig_5m):
            return None

        # Risk Check
        passed, reason = risk_check(sym, daily_stats, active_signals, bias['vix'], bias['adx'])
        
        # 🧠 BROAD MARKET SENTIMENT FILTER
        from services.sentiment_engine import get_sentiment_engine
        from services.news_engine import get_news_engine
        nifty_sentiment = get_sentiment_engine("NIFTY").analyze()
        market_mode, _ = get_news_engine().get_market_mode()
        
        if passed and nifty_sentiment:
            # Block CE signals if market broad sentiment is Bearish
            if sig_5m == "CE" and "BEARISH" in nifty_sentiment['sentiment']:
                logger.info(f"🚫 {sym} CE Blocked: Nifty Sentiment is {nifty_sentiment['sentiment']}")
                passed = False
            # Block PE signals if market broad sentiment is Bullish
            if sig_5m == "PE" and "BULLISH" in nifty_sentiment['sentiment']:
                logger.info(f"🚫 {sym} PE Blocked: Nifty Sentiment is {nifty_sentiment['sentiment']}")
                passed = False

        if passed:
            # Adjust strength threshold for Volatile markets
            effective_threshold = rev_engine.STRENGTH_THRESHOLD + 10 if market_mode == "VOLATILE" else rev_engine.STRENGTH_THRESHOLD
            if strength < effective_threshold:
                return None

            side = sig_5m
            strike = pick_best_strike(spot, side, sym)
            
            # --- 🎯 REAL PRICE FETCHING ---
            idx_key = engine.get_instrument_key(sym)
            expiries = engine.get_expiry_dates_via_sdk(idx_key) if idx_key else []
            
            # Expiry Shift Logic
            expiry_pref = rev_engine.select_expiry()
            now_hour = datetime.now().hour
            is_3pm = (now_hour == 15)
            force_next = (expiry_pref == "NEXT_WEEK" or is_3pm)
            
            target_expiry = pick_professional_expiry(expiries, symbol=sym, force_next=force_next)
            
            premium, opt_key = get_option_ltp(engine, sym, strike, side, target_expiry=target_expiry)
            
            if not premium or premium <= 0:
                return None
                
            target, sl = estimate_target_sl(premium, side)
            
            state = rev_engine.market_state.get(sym, {})
            is_reversal = state.get('reversal_watch') == False and state.get('direction') == side
            
            if is_3pm:
                tag_text = "🏛️ 3PM Power Close"
            elif is_reversal:
                tag_text = "🔄 Stock Reversal Confirmed"
            else:
                tag_text = "🚀 Prime Skill Development"
            
            from datetime import datetime
            now = datetime.now()
            return {
                "symbol": sym, "type": side, "strike": strike, 
                "spot": spot, "premium": premium, "target": target, 
                "stop_loss": sl, "score": strength, "tag": tag_text,
                "expiry": target_expiry or "Current",
                "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "target_window": "Intraday (By 3:15 PM)",
                "option_key": opt_key
            }
        return None
    except Exception as e:
        logger.debug(f"Error scanning {sym}: {e}")
        return None

def run_parallel_stock_scan(engine, instrument_map, bias):
    """
    Orchestrates the parallel scan using ThreadPoolExecutor.
    Safe, Lock-Free, and Independent.
    """
    symbols = [s.replace(".NS", "") for s in NIFTY_50_STOCKS]
    active_signals = load_active_signals()
    daily_stats = load_daily_stats()
    
    results = []
    
    # 🏃 Parallel Execution
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scan_single_stock, engine, sym, instrument_map.get(sym), bias, active_signals, daily_stats): sym for sym in symbols if instrument_map.get(sym)}
        
        for future in as_completed(futures):
            try:
                alert = future.result(timeout=10) # 10s Timeout Protection
                if alert:
                    # Only the main coordinator thread handles alerts/saves to avoid race conditions
                    try:
                        if send_trade_alert(alert):
                            # 🚀 REGISTER FOR MONITORING
                            from services.trade_monitor import get_trade_monitor
                            get_trade_monitor().register_trade(alert)
                            
                            active_signals.append(alert)
                            daily_stats['counts']["TOP"] += 1
                            save_active_signals(active_signals)
                            save_daily_stats(daily_stats)
                            # Safe access to tag if it exists in data
                            tag_text = alert.get('tag', 'Signal')
                            logger.info(f"🏆 {tag_text} Dispatched: {alert['symbol']}")
                    except NameError as ne:
                        logger.error(f"DEBUG: NameError in alert loop: {ne}")
                        logger.error(f"DEBUG: Alert content: {alert}")
                        raise ne
            except Exception as e:
                logger.error(f"Worker Error: {e}")

    # 📊 Dashboard Sync
    save_inst_results({
        "all": sorted(active_signals, key=lambda x: x.get('score', 0), reverse=True)[:10],
        "active_trades": active_signals,
        "last_update": datetime.now().isoformat()
    })
