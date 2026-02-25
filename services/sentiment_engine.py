import time
import logging
from datetime import datetime
from services.upstox_engine import get_upstox_engine
from utils.telegram_alert import send_telegram
from pro_config import SIGNATURE

logger = logging.getLogger("SentimentEngine")

class OptionSentimentEngine:
    def __init__(self, symbol):
        self.symbol = symbol
        self.last_pcr = None
        self.last_sentiment = None
        self.last_max_pain = None
        self.last_alert_time = 0
        self.last_fetch_time = 0
        self.cache = None
        self.engine = get_upstox_engine()
        
        # Mapping for VIX lookup
        self.vix_key = "NSE_INDEX|India VIX"

    def fetch_option_chain_data(self):
        """Fetches and normalizes option chain data from Upstox"""
        try:
            # 1. Get underlying instrument key
            idx_key = self.engine.get_instrument_key(self.symbol)
            if not idx_key: return []
            
            # 2. Get nearest expiry
            expiries = self.engine.get_expiry_dates_via_sdk(idx_key)
            if not expiries: return []
            target_expiry = expiries[0] # Always analyze the nearest (most active)
            
            # 3. Fetch full chain via SDK
            chain = self.engine.get_option_chain_via_sdk(idx_key, target_expiry)
            if not chain: return []
            
            def safe_get(obj, attr):
                try:
                    return getattr(obj, attr, 0)
                except:
                    return 0

            normalized_chain = []
            for item in chain:
                strike = item.strike_price
                ce_data = item.call_options.market_data if item.call_options else None
                pe_data = item.put_options.market_data if item.put_options else None
                
                normalized_chain.append({
                    "strike": strike,
                    "CE": {
                        "oi": float(safe_get(ce_data, 'oi')),
                        "oi_change": float(safe_get(ce_data, 'oi_day_change') or safe_get(ce_data, 'oi_change') or 0),
                        "ltp": float(safe_get(ce_data, 'ltp'))
                    },
                    "PE": {
                        "oi": float(safe_get(pe_data, 'oi')),
                        "oi_change": float(safe_get(pe_data, 'oi_day_change') or safe_get(pe_data, 'oi_change') or 0),
                        "ltp": float(safe_get(pe_data, 'ltp'))
                    }
                })
            return normalized_chain
        except Exception as e:
            logger.error(f"Error fetching sentiment data for {self.symbol}: {e}")
            return []

    def calculate_pcr(self, chain):
        total_ce_oi = sum(s["CE"]["oi"] for s in chain)
        total_pe_oi = sum(s["PE"]["oi"] for s in chain)
        if total_ce_oi == 0: return 1.0
        return round(total_pe_oi / total_ce_oi, 2)

    def calculate_oi_buildup(self, chain):
        from engine.option_oi_engine import get_oi_engine
        oi_engine = get_oi_engine()
        
        total_ce_change = sum(s["CE"]["oi_change"] for s in chain)
        total_pe_change = sum(s["PE"]["oi_change"] for s in chain)
        
        # Analyze top strikes buildup
        buildups = oi_engine.process_chain(chain[:10]) # Look at top 10 strikes
        
        return total_ce_change, total_pe_change, buildups

    def calculate_max_pain(self, chain):
        """Max Pain: Strike where option buyers lose the most (and sellers gain the most)"""
        try:
            strikes = [s["strike"] for s in chain]
            total_pain_list = []
            
            for test_strike in strikes:
                pain = 0
                for s in chain:
                    # Call Pain: If test_strike > strike, CE is ITM
                    if test_strike > s["strike"]:
                        pain += (test_strike - s["strike"]) * s["CE"]["oi"]
                    # Put Pain: If test_strike < strike, PE is ITM
                    if test_strike < s["strike"]:
                        pain += (s["strike"] - test_strike) * s["PE"]["oi"]
                total_pain_list.append(pain)
                
            min_pain_idx = total_pain_list.index(min(total_pain_list))
            return strikes[min_pain_idx]
        except:
            return 0

    def get_vix(self):
        try:
            quotes = self.engine.get_market_quote([self.vix_key], mode="ltp")
            if self.vix_key in quotes:
                return float(quotes[self.vix_key].get('last_price', 15))
            return 15
        except: return 15

    def analyze(self):
        now = time.time()
        # 🛡️ 60s Cache to prevent API overload
        if self.cache and (now - self.last_fetch_time < 60):
            return self.cache

        chain = self.fetch_option_chain_data()
        if not chain: return self.cache # Return old cache instead of None if API fails
        
        pcr = self.calculate_pcr(chain)
        ce_change, pe_change, buildups = self.calculate_oi_buildup(chain)
        max_pain = self.calculate_max_pain(chain)
        vix = self.get_vix()
        
        # 🧪 Sentiment Logic
        sentiment = "SIDEWAYS"
        if pcr < 0.7 and pe_change > ce_change:
            sentiment = "STRONG BULLISH"
        elif pcr > 1.3 and ce_change > pe_change:
            sentiment = "STRONG BEARISH"
        elif 0.7 <= pcr <= 1.0:
            sentiment = "MILD BULLISH"
        elif 1.0 < pcr <= 1.3:
            sentiment = "MILD BEARISH"
            
        # 🛡️ VIX Filter (Override)
        if vix > 22:
            sentiment = f"⚠️ VOLATILE ({sentiment})"
            
        result = {
            "symbol": self.symbol,
            "pcr": pcr,
            "sentiment": sentiment,
            "max_pain": max_pain,
            "ce_change": ce_change,
            "pe_change": pe_change,
            "buildups": buildups,
            "vix": vix,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        self.cache = result
        self.last_fetch_time = now
        return result

    def check_and_alert(self, analysis):
        if not analysis: return
        
        now = time.time()
        # rules: PCR shift > 0.1 OR Sentiment Flip OR Max Pain Shift
        pcr_shift = abs((analysis['pcr'] or 0) - (self.last_pcr or 0)) > 0.1 if self.last_pcr else True
        sentiment_flip = analysis['sentiment'] != self.last_sentiment
        pain_shift = analysis['max_pain'] != self.last_max_pain
        
        cooldown_passed = (now - self.last_alert_time) > 600 # 10 min cooldown for sentiment updates
        
        if (pcr_shift or sentiment_flip or pain_shift) and (cooldown_passed or self.last_alert_time == 0):
            self.send_sentiment_alert(analysis)
            self.last_pcr = analysis['pcr']
            self.last_sentiment = analysis['sentiment']
            self.last_max_pain = analysis['max_pain']
            self.last_alert_time = now

    def send_sentiment_alert(self, data):
        emoji = "📊"
        if "STRONG BULLISH" in data['sentiment']: emoji = "🚀"
        elif "STRONG BEARISH" in data['sentiment']: emoji = "🩸"
        
        msg = (
            f"{emoji} *MARKET SENTIMENT UPDATE*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 **INDEX**: `{data['symbol']}`\n"
            f"⚖️ **PCR**: `{data['pcr']}`\n"
            f"🧠 **SENTIMENT**: `{data['sentiment']}`\n"
            f"📉 **VIX**: `{data['vix']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **OI BUILDUP**:\n"
            f"∟ Call: `{data['ce_change']:,.0f}`\n"
            f"∟ Put:  `{data['pe_change']:,.0f}`\n"
            f"🎯 **MAX PAIN**: `{data['max_pain']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **TIME**: `{data['timestamp']}`\n"
            f"{SIGNATURE}"
        )
        send_telegram(msg)
        logger.info(f"Sentiment Alert Dispatched for {data['symbol']}")

# Global engines
_engines = {
    "NIFTY": OptionSentimentEngine("NIFTY"),
    "BANKNIFTY": OptionSentimentEngine("BANKNIFTY")
}

def get_sentiment_engine(symbol):
    return _engines.get(symbol)
