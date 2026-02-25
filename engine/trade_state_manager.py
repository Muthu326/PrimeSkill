import logging
import time
from datetime import datetime

logger = logging.getLogger("TradeState")

class TradeStateManager:
    def __init__(self):
        self.active_signals = {} # Symbol -> {direction, entry_time, entry_price, status}
        self.reversal_wait = {}   # Symbol -> {new_direction, start_time}
        self.BLOCK_WINDOW = 300   # 5 mins block after entry

    def is_signal_allowed(self, symbol, new_direction):
        """
        Main logic to prevent 'Confusion' (rapid flips)
        """
        now = time.time()
        state = self.active_signals.get(symbol)

        if not state:
            return True # First signal always allowed

        current_direction = state["direction"]

        # 1. If same signal, it's just a continuation
        if current_direction == new_direction:
            return False # Avoid duplicate alerts for the same direction

        # 2. If opposite signal (Potential Reversal)
        # Check against entry block window
        elapsed_since_entry = now - state["entry_time"]
        if elapsed_since_entry < self.BLOCK_WINDOW:
            logger.info(f"🛡️ {symbol} Reversal blocked: Inside {self.BLOCK_WINDOW}s window.")
            return False

        # 3. Handle Reversal Confirmation
        wait_state = self.reversal_wait.get(symbol)
        if not wait_state or wait_state["new_direction"] != new_direction:
            # Start the reversal watch
            self.reversal_wait[symbol] = {
                "new_direction": new_direction,
                "start_time": now
            }
            logger.info(f"⏳ {symbol} Reversal watch started: {current_direction} -> {new_direction}")
            return False

        # Check if reversal has been stable for N seconds (e.g. 180s = 3 mins)
        if now - wait_state["start_time"] >= 180:
            logger.info(f"✅ {symbol} Reversal confirmed after stability window.")
            # Clear wait state, new signal is allowed
            self.reversal_wait.pop(symbol)
            return True
            
        return False

    def update_trade_state(self, symbol, direction, price):
        """Register the final confirmed signal"""
        self.active_signals[symbol] = {
            "direction": direction,
            "entry_time": time.time(),
            "entry_price": price,
            "status": "ACTIVE"
        }
        logger.info(f"🏛️ TradeState updated for {symbol}: {direction} @ {price}")

    def get_active_direction(self, symbol):
        state = self.active_signals.get(symbol)
        return state["direction"] if state else None

# Singleton
_ts_manager = TradeStateManager()

def get_trade_state_manager():
    return _ts_manager
