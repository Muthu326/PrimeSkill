import logging
import time
from datetime import datetime
from services.upstox_engine import get_upstox_engine
from services.sentiment_engine import get_sentiment_engine
from engine.option_oi_engine import get_oi_engine

logger = logging.getLogger("IntelligenceEngine")

class IntelligenceEngine:
    def __init__(self):
        self.engine = get_upstox_engine()
        self.news_risk_level = "LOW"
        self.last_blueprint = None

    def calculate_tomorrow_bias(self, symbol):
        """🧠 Logic to calculate tomorrow's CE/PE Probability"""
        try:
            sentiment_engine = get_sentiment_engine(symbol)
            sentiment_data = sentiment_engine.analyze()
            if not sentiment_data: return None

            pcr = sentiment_data['pcr']
            vix = sentiment_data['vix']
            
            # Simple scoring model (0-100)
            score = 50 # Base neutral
            
            # PCR Impact
            if pcr < 0.7: score += 20 # Strong Bullish
            elif pcr < 0.9: score += 10 # Bullish
            elif pcr > 1.3: score -= 20 # Strong Bearish
            elif pcr > 1.1: score -= 10 # Bearish
            
            # OI Buildup (Mocked from sentiment data)
            if "STRONG BULLISH" in sentiment_data['sentiment']: score += 15
            elif "STRONG BEARISH" in sentiment_data['sentiment']: score -= 15
            
            # VIX Impact
            if vix > 20: score -= 5 # Higher risk/cap
            
            probability = min(90, max(50, score if score > 50 else (100 - score)))
            bias = "BULLISH" if score > 50 else "BEARISH" if score < 50 else "SIDEWAYS"
            
            # Levels (Mock logic: Support/Resistance based on round numbers/ATR)
            # This would ideally use actual pivot point calculations
            close = 22345 # Prototype
            ce_level = round(close * 1.005 / 50) * 50
            pe_level = round(close * 0.995 / 50) * 50

            return {
                "close": close,
                "pcr": pcr,
                "max_pain": sentiment_data['max_pain'],
                "oi_build": sentiment_data['sentiment'],
                "bias": bias,
                "prob": probability,
                "ce_level": ce_level,
                "pe_level": pe_level
            }
        except Exception as e:
            logger.error(f"Intelligence Error for {symbol}: {e}")
            return None

    def get_global_data(self):
        """🌍 Fetches mock global market data for 8:30 AM report"""
        # In a real setup, this would fetch from Investing.com or Bloomberg API
        return {
            "us": "+0.62% (Bullish)",
            "asia": "Mixed (Cautious)",
            "crude": "Rising ($78.4)",
            "dxy": "104.1 (Stable)",
            "vix": "14.2 (Low Fear)",
            "gap": "Mild Gap Up (50-70 Points)",
            "mode": "NORMAL"
        }

    def get_tactical_range(self, symbol):
        """⚡ Calculates 9:10 AM tactical levels"""
        return {
            "nifty_range": "22,360 - 22,420",
            "bank_range": "48,100 - 48,250",
            "stocks": "RELIANCE, HDFCBANK"
        }

# Singleton
_intel_engine = IntelligenceEngine()

def get_intel_engine():
    return _intel_engine
