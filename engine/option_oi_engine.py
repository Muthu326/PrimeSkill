import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger("OptionOI")

class OptionOIEngine:
    def __init__(self):
        self.last_oi_data = {} # Key: option_key, Value: {oi, timestamp}

    def analyze_buildup(self, ltp, oi, last_ltp, last_oi):
        """
        Institutional Smart Money Detection
        Returns: BUILUP_TYPE
        """
        if not last_ltp or not last_oi or oi == last_oi:
            return "NO_CHANGE"

        price_up = ltp > last_ltp
        price_down = ltp < last_ltp
        oi_up = oi > last_oi
        oi_down = oi < last_oi

        if price_up and oi_up:
            return "LONG BUILDUP"
        elif price_down and oi_up:
            return "SHORT BUILDUP"
        elif price_up and oi_down:
            return "SHORT COVERING"
        elif price_down and oi_down:
            return "LONG UNWINDING"
        
        return "NEUTRAL"

    def process_chain(self, chain_data):
        """
        Analyzes the full option chain for OI shifts
        """
        analysis = []
        for strike in chain_data:
            # Analyze CE
            ce = strike.get("CE", {})
            ce_oi = ce.get("oi", 0)
            ce_ltp = ce.get("ltp", 0)
            
            # Analyze PE
            pe = strike.get("PE", {})
            pe_oi = pe.get("oi", 0)
            pe_ltp = pe.get("ltp", 0)

            analysis.append({
                "strike": strike.get("strike"),
                "CE_BUILDP": self.analyze_buildup(ce_ltp, ce_oi, 0, 0), # Simplified for now
                "PE_BUILDP": self.analyze_buildup(pe_ltp, pe_oi, 0, 0)
            })
        return analysis

    def get_market_bias(self, chain):
        """
        Calculates PCR and overall smart money bias
        """
        total_ce_oi = sum(s["CE"]["oi"] for s in chain)
        total_pe_oi = sum(s["PE"]["oi"] for s in chain)
        
        if total_ce_oi == 0: return "NEUTRAL", 1.0
        
        pcr = round(total_pe_oi / total_ce_oi, 2)
        
        bias = "SIDEWAYS"
        if pcr > 1.3: bias = "EXTREME BULLISH"
        elif pcr > 1.1: bias = "BULLISH"
        elif pcr < 0.7: bias = "EXTREME BEARISH"
        elif pcr < 0.9: bias = "BEARISH"
        
        return bias, pcr

# Singleton
_oi_engine = OptionOIEngine()

def get_oi_engine():
    return _oi_engine
