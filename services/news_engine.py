import time
import logging
from datetime import datetime
from services.upstox_engine import get_upstox_engine
from utils.telegram_alert import send_news_alert

logger = logging.getLogger("NewsEngine")

class NewsEngine:
    def __init__(self):
        self.news_state = {
            "impact_score": 0,
            "last_news_time": 0,
            "active_event": None
        }
        self.NEWS_BLOCK_TIME = 900  # 15 mins
        self.engine = get_upstox_engine()
        self.vix_key = "NSE_INDEX|India VIX"
        self.last_vix = None
        self.last_price = {}
        
        # News Keywords
        self.HIGH_IMPACT = ["RBI", "Budget", "Fed", "Election", "War", "Rate Decision", "FOMC"]
        self.MEDIUM_IMPACT = ["Earnings", "Inflation", "GDP", "CPI", "Quarterly", "Result"]

    def process_headline(self, headline):
        """Classifies news headline and updates market mode"""
        impact = 0
        event_name = headline[:50]
        
        for word in self.HIGH_IMPACT:
            if word.lower() in headline.lower():
                impact = 90
                break
        
        if impact == 0:
            for word in self.MEDIUM_IMPACT:
                if word.lower() in headline.lower():
                    impact = 60
                    break
                    
        if impact > 0:
            self.update_manual_news(event_name, impact)
            return True
        return False

    def update_manual_news(self, event_title, impact_score):
        """Allows manual injection of news via admin dashboard"""
        self.news_state["impact_score"] = impact_score
        self.news_state["last_news_time"] = time.time()
        self.news_state["active_event"] = event_title
        
        mode = "BLOCKED" if impact_score >= 80 else "VOLATILE"
        send_news_alert(event_title, impact_score, mode, 15)
        logger.info(f"News Injection: {event_title} (Impact: {impact_score})")

    def detect_volatility_spike(self, symbol, current_ltp):
        """Auto-detects shock moves even without news APIs"""
        if symbol not in self.last_price:
            self.last_price[symbol] = current_ltp
            return False, 0
            
        prev_ltp = self.last_price[symbol]
        move_pct = abs((current_ltp - prev_ltp) / prev_ltp) * 100
        self.last_price[symbol] = current_ltp
        
        # ⚡ 0.5% move in 1 minute on NIFTY is a volatility shock
        if move_pct > 0.4:
            logger.warning(f"⚡ {symbol} Volatility Spike: {move_pct:.2f}% detected.")
            return True, move_pct
        return False, move_pct

    def check_vix_spike(self):
        """Monitors sudden VIX expansion"""
        try:
            quotes = self.engine.get_market_quote([self.vix_key], mode="ltp")
            if self.vix_key in quotes:
                curr_vix = float(quotes[self.vix_key].get('last_price', 15))
                if self.last_vix and (curr_vix - self.last_vix) > 0.8: # > 5% spike in VIX
                    logger.warning(f"🔥 VIX Spike detected: {curr_vix - self.last_vix:.2f} points increase.")
                    return True, curr_vix
                self.last_vix = curr_vix
            return False, 15
        except: return False, 15

    def get_market_mode(self, symbol_ltp_map=None):
        """Returns NORMAL, VOLATILE, or BLOCKED status"""
        now = time.time()
        
        # 1. Manual News Impact (highest priority)
        if self.news_state["impact_score"] >= 80:
            if now - self.news_state["last_news_time"] < self.NEWS_BLOCK_TIME:
                return "BLOCKED", f"News: {self.news_state['active_event']}"

        # 2. VIX Spike Check
        vix_spike, curr_vix = self.check_vix_spike()
        if vix_spike or curr_vix > 22:
            return "VOLATILE", f"VIX Spike ({curr_vix:.1f})"

        # 3. Price Move Check (if Nifty data available)
        if symbol_ltp_map and "NIFTY" in symbol_ltp_map:
            price_spike, pct = self.detect_volatility_spike("NIFTY", symbol_ltp_map["NIFTY"])
            if price_spike:
                return "VOLATILE", f"Volatility Spike ({pct:.2f}%)"

        return "NORMAL", "Steady Market"

    def is_trade_allowed(self, mode):
        """Final permission check for Trade Engine"""
        if mode == "BLOCKED":
            return False
        return True

# Singleton
_news_engine = NewsEngine()

def get_news_engine():
    return _news_engine
