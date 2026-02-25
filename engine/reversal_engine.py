import time
import logging
import threading
from datetime import datetime
from utils.telegram_alert import send_telegram
from pro_config import SIGNATURE

logger = logging.getLogger("ReversalEngine")

class ReversalEngine:
    def __init__(self):
        # symbol -> {direction, entry_time, reversal_watch, reversal_start, strength}
        self.market_state = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.REVERSAL_CONFIRM_TIME = 180   # 3 minutes
        self.BLOCK_WINDOW = 300            # 5 min no flip zone
        self.STRENGTH_THRESHOLD = 65
        
    def multi_tf_confirmation(self, data_1m, data_5m):
        """
        🏗️ 1️⃣ MULTI-TIMEFRAME CONFIRMATION
        1 Minute -> Fast momentum
        5 Minute -> Stability confirmation
        """
        if not data_1m or not data_5m:
            return False
            
        # Check alignment
        signals_match = data_1m.get("signal") == data_5m.get("signal")
        
        # 🕒 Relax ADX for 3 PM Session (12 is sufficient for early breakouts)
        now_hour = datetime.now().hour
        adx_threshold = 12 if now_hour == 15 else 20
        adx_stable = data_5m.get("adx", 0) >= adx_threshold
        
        # Volume check: Just ensure some activity
        volume_spike = data_1m.get("volume", 0) > (data_1m.get("avg_volume", 0) * 0.8)
        
        return signals_match and adx_stable and volume_spike

    def reversal_strength(self, rsi, adx, volume_ratio, price_vs_vwap):
        """
        🏋️ 2️⃣ REVERSAL STRENGTH SCORE (0-100)
        """
        score = 0
        if rsi < 40 or rsi > 60: score += 25
        if adx > 25: score += 25
        if volume_ratio > 1.5: score += 25
        if price_vs_vwap: score += 25
        return score

    def select_expiry(self, current_time=None):
        """
        📅 4️⃣ EXPIRY SHIFT LOGIC
        Before 1 PM -> Current Weekly
        After 1 PM -> Next Weekly
        """
        if current_time is None:
            current_time = datetime.now()
            
        if current_time.hour >= 13:
            return "NEXT_WEEK"
        return "CURRENT"

    def check_reversal(self, symbol, new_signal):
        """
        🧠 MASTER REVERSAL LOGIC
        """
        if not new_signal:
            return False

        now = time.time()
        with self.lock:
            state = self.market_state.get(symbol)

            if not state:
                # First signal for this symbol
                self.market_state[symbol] = {
                    "direction": new_signal,
                    "entry_time": now,
                    "reversal_watch": False,
                    "reversal_start": None
                }
                return True

            current_direction = state["direction"]

            # 🛑 Block rapid flip (5 min block window)
            if new_signal != current_direction and (now - state["entry_time"]) < self.BLOCK_WINDOW:
                logger.info(f"🛡️ {symbol} Reversal Blocked: Inside {self.BLOCK_WINDOW}s window.")
                return False

            # If opposite signal detected
            if new_signal != current_direction:
                # Start reversal watch if not already watching
                if not state["reversal_watch"]:
                    state["reversal_watch"] = True
                    state["reversal_start"] = now
                    logger.info(f"⏳ {symbol} Reversal Watch Started: {current_direction} -> {new_signal}")
                    return False

                # Check if reversal has been stable for 3 minutes
                elapsed = now - state["reversal_start"]
                if elapsed >= self.REVERSAL_CONFIRM_TIME:
                    logger.info(f"✅ {symbol} Reversal Confirmed: {current_direction} -> {new_signal}")
                    
                    # 🚀 TRIGGER REVERSAL CHANNEL ALERT
                    from utils.telegram_alert import send_reversal_alert
                    send_reversal_alert(symbol, current_direction, new_signal, 80) # Default strength for confirmation alert
                    
                    state["direction"] = new_signal
                    state["entry_time"] = now
                    state["reversal_watch"] = False
                    state["reversal_start"] = None
                    return True
                else:
                    remaining = int(self.REVERSAL_CONFIRM_TIME - elapsed)
                    logger.debug(f"⏳ {symbol} Countdown: {remaining}s remaining for reversal confirmation.")
                    return False

            # If signal matches current direction, reset reversal watch
            if new_signal == current_direction:
                if state["reversal_watch"]:
                    logger.info(f"🔄 {symbol} Reversal Aborted: Signal reverted to {current_direction}")
                state["reversal_watch"] = False
                state["reversal_start"] = None
                return True # Not a reversal, just a continuation

            return False

    def send_reversal_alert(self, symbol, new_signal, prev_signal, strength, expiry_type):
        """
        📢 PROFESSIONAL REVERSAL ALERT FORMAT
        """
        strength_label = "STRONG" if strength >= 75 else "MODERATE"
        
        msg = (
            f"🔄 **REVERSAL CONFIRMED**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 Symbol: **{symbol}**\n"
            f"⬅️ Previous: `{prev_signal}`\n"
            f"➡️ New: `{new_signal}`\n\n"
            f"📊 Strength: `{strength}/100` ({strength_label})\n"
            f"⏱ Confirmed After: `3 mins stability`\n"
            f"📅 Expiry: `{expiry_type}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{SIGNATURE}"
        )
        send_telegram(msg)

# Singleton
_reversal_engine = ReversalEngine()

def get_reversal_engine():
    return _reversal_engine
