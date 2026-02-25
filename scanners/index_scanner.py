import logging
import time
import pandas as pd
from datetime import datetime
from engine.indicators import calculate_indicators
from engine.regime_detector import detect_market_regime
from utils.logger import setup_logger
from utils.telegram_alert import send_trade_alert
from engine.option_selector import pick_best_strike, estimate_target_sl, pick_professional_expiry, get_option_ltp
from pro_config import SCAN_INDICES

logger = setup_logger("IndexScanner")

# Prevent spamming the same index signal
INDEX_ALERT_COOLDOWN = {}

def get_index_bias(engine, instrument_map):
    """
    🏛 TIER 1: INDEX & MACRO ANALYZER
    Returns a safe snapshot of market conditions.
    """
    try:
        nifty_key = instrument_map.get("NIFTY", "NSE_INDEX|Nifty 50")
        vix_key = "NSE_INDEX|India VIX"
        
        n_df = engine.get_intraday_candles(nifty_key, interval="5minute")
        v_df = engine.get_intraday_candles(vix_key, interval="5minute")
        
        vix_value = 15
        if not v_df.empty:
            v_df = calculate_indicators(v_df)
            vix_value = v_df['close'].iloc[-1]
            
        trend = "NEUTRAL"
        adx = 0
        regime = "NORMAL"
        
        if not n_df.empty:
            n_df = calculate_indicators(n_df)
            n_close = n_df['close'].iloc[-1]
            n_ema = n_df['ema20'].iloc[-1]
            trend = "BULLISH" if n_close > n_ema else "BEARISH"
            adx = n_df['adx'].iloc[-1]
            regime, _ = detect_market_regime(n_df, vix_value)

        return {
            "trend": trend,
            "adx": adx,
            "vix": vix_value,
            "regime": regime,
            "nifty_df": n_df
        }

    except Exception as e:
        logger.error(f"❌ Error getting index bias: {e}")
        return {
            "trend": "NEUTRAL", "adx": 0, "vix": 15, 
            "regime": "NORMAL", "nifty_df": pd.DataFrame()
        }

def run_index_scan(engine, instrument_map, bias):
    """
    🏛 TIER 1.5: INDEX SIGNAL GENERATOR
    Scans indices for breakout/trend setups using Master Reversal Engine.
    """
    from engine.reversal_engine import get_reversal_engine
    rev_engine = get_reversal_engine()
    
    current_ts = time.time()
    for idx_sym in SCAN_INDICES:
        try:
            key = instrument_map.get(idx_sym)
            if not key: continue
            
            # Fetch MTF Data
            df_5m = engine.get_intraday_candles(key, interval="5minute")
            df_1m = engine.get_intraday_candles(key, interval="1minute")
            
            if df_5m.empty or len(df_5m) < 20 or df_1m.empty: continue
            
            df_5m = calculate_indicators(df_5m)
            df_1m = calculate_indicators(df_1m)
            
            lat_5m = df_5m.iloc[-1]
            lat_1m = df_1m.iloc[-1]
            
            # Signal Detection (Simple Logic for MTF check)
            def get_sig(latest):
                spot = latest['close']
                ema = latest.get('ema20', spot)
                rsi = latest.get('rsi', 50)
                if spot > ema and rsi > 55: return "CE"
                if spot < ema and rsi < 45: return "PE"
                return None

            sig_5m = get_sig(lat_5m)
            sig_1m = get_sig(lat_1m)

            if not sig_5m or not sig_1m:
                continue

            # 1️⃣ Signal Confirmation Layer
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
                continue

            signal_type = sig_5m

            # 2️⃣ Reversal Engine Layer (Strength & Stability)
            strength = rev_engine.reversal_strength(
                data_1m["rsi"], 
                data_5m["adx"], 
                data_1m["volume_ratio"], 
                data_1m["price_vs_vwap"]
            )
            
            if strength < rev_engine.STRENGTH_THRESHOLD:
                continue

            # 🛠️ 2️⃣ Institutional State Manager Layer (Confusion Control)
            from engine.trade_state_manager import get_trade_state_manager
            ts_manager = get_trade_state_manager()
            
            if not ts_manager.is_signal_allowed(idx_sym, signal_type):
                continue
            
            # 🛡️ Cooldown Check (Internal redundant but safe)
            alert_key = f"{idx_sym}_{signal_type}"
            if current_ts - INDEX_ALERT_COOLDOWN.get(alert_key, 0) < 1800:
                continue

            # 🧠 3️⃣ Sentiment Filter Layer
            from services.sentiment_engine import get_sentiment_engine
            sentiment_engine = get_sentiment_engine(idx_sym)
            sentiment_data = None
            if sentiment_engine:
                sentiment_data = sentiment_engine.analyze()
                if sentiment_data:
                    # Logic: If SIGNAL is CE, sentiment must NOT be STRONG BEARISH
                    # If SIGNAL is PE, sentiment must NOT be STRONG BULLISH
                    if signal_type == "CE" and "BEARISH" in sentiment_data['sentiment']:
                        logger.info(f"🚫 {idx_sym} CE Blocked: Sentiment is {sentiment_data['sentiment']}")
                        continue
                    if signal_type == "PE" and "BULLISH" in sentiment_data['sentiment']:
                        logger.info(f"🚫 {idx_sym} PE Blocked: Sentiment is {sentiment_data['sentiment']}")
                        continue
                    
                    # Also check for periodic alerts
                    sentiment_engine.check_and_alert(sentiment_data)

            # Expiry Shift Logic: If after 1:00 PM or 3:00 PM window, consider it BTST 'force_next'
            expiry_pref = rev_engine.select_expiry()
            now_hour = datetime.now().hour
            is_3pm = (now_hour == 15)
            force_next = (expiry_pref == "NEXT_WEEK" or is_3pm)
            
            expiries = engine.get_expiry_dates_via_sdk(key)
            target_expiry = pick_professional_expiry(expiries, symbol=idx_sym, force_next=force_next)
            # 🏛️ 4️⃣ OPTION PICKER & PRICER
            from engine.option_selector import pick_best_strike, get_option_ltp, estimate_target_sl
            spot = lat_5m['close']
            strike = pick_best_strike(spot, signal_type, idx_sym)
            premium, opt_key, opt_ts = get_option_ltp(engine, idx_sym, strike, signal_type, target_expiry=target_expiry)
            
            if premium > 0:
                target, sl = estimate_target_sl(premium, signal_type)
                
                # If it's a confirmed reversal
                state = rev_engine.market_state.get(idx_sym, {})
                is_reversal = state.get('reversal_watch') == False and state.get('direction') == signal_type
                
                if is_3pm:
                    tag = "🏛️ 3PM Power Close"
                elif is_reversal:
                    tag = "🔄 Index Reversal Confirmed"
                else:
                    tag = "🏛 Index Elite Setup"
                
                alert = {
                    "symbol": idx_sym,
                    "type": signal_type,
                    "strike": strike,
                    "spot": spot,
                    "premium": premium,
                    "target": target,
                    "stop_loss": sl,
                    "score": strength, 
                    "tag": tag,
                    "expiry": target_expiry or "Current",
                    "generated_at": datetime.now().strftime("%H:%M:%S"),
                    "target_window": "Intraday (High Momentum)",
                    "option_key": opt_key,
                    "price_ts": opt_ts, # Verification Time
                    "sentiment": sentiment_data['sentiment'] if sentiment_data else "N/A",
                    "pcr": sentiment_data['pcr'] if sentiment_data else "N/A",
                    "max_pain": sentiment_data['max_pain'] if sentiment_data else "N/A"
                }
                
                if send_trade_alert(alert):
                    from services.trade_monitor import get_trade_monitor
                    get_trade_monitor().register_trade(alert)
                    
                    INDEX_ALERT_COOLDOWN[alert_key] = current_ts
                    ts_manager.update_trade_state(idx_sym, signal_type, premium)
                    logger.info(f"📍 INDEX ALERT SENT: {idx_sym} {strike} {signal_type} @ {premium}")
                    
        except Exception as e:
            logger.error(f"Error scanning index {idx_sym}: {e}")
