"""
Low Premium Scanner - Find Hidden Gem Options
Scans for options at ₹3-10 that could 5-10x
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import yfinance as yf

from services.options_pricer import get_options_pricer
from services.market_engine import calculate_indicators, get_days_to_expiry
from models.trade_models import OptionType
from config.config import SYMBOLS, ALL_FO_STOCKS

class LowPremiumScanner:
    """
    Finds undervalued options with high potential
    - Low premium (₹3-10)
    - Strong technical setup
    - High probability of 5-10x gains
    """
    
    def __init__(self):
        self.pricer = get_options_pricer()
        self.min_premium = 3.0
        self.max_premium = 15.0
        self.target_multiplier = 5.0  # Looking for 5x minimum
    
    def get_otm_options(self, symbol: str, spot: float, days_to_expiry: int) -> List[Dict]:
        """Get OTM options with low premiums"""
        iv = self.pricer.estimate_iv_from_history(symbol)
        
        # Generate strike ladder
        strikes = self.pricer.get_strike_ladder(spot, symbol)
        
        low_premium_options = []
        
        for strike in strikes:
            # Skip ITM and ATM for calls (we want cheap OTM)
            if strike <= spot + 100:  # Only OTM+ for calls
                continue
            
            if strike >= spot - 100:  # Only OTM+ for puts
                continue
            
            # Calculate Call premium
            call_premium = self.pricer.bs_calculator.call_price(
                spot, strike, days_to_expiry/365, 0.06, iv/100
            )
            
            # Calculate Put premium  
            put_premium = self.pricer.bs_calculator.put_price(
                spot, strike, days_to_expiry/365, 0.06, iv/100
            )
            
            # Check if CALL is in range
            if self.min_premium <= call_premium <= self.max_premium:
                # Calculate potential
                distance_pct = abs(strike - spot) / spot * 100
                
                # Potential multiplier if spot moves to strike
                intrinsic_at_strike = max(0, strike - spot) if strike > spot else 0
                potential_value = intrinsic_at_strike + (call_premium * 0.3)  # Conservative
                potential_multiplier = potential_value / call_premium if call_premium > 0 else 0
                
                if potential_multiplier >= 3.0:  # 3x+ potential
                    low_premium_options.append({
                        'symbol': symbol,
                        'type': 'CE',
                        'strike': strike,
                        'spot': spot,
                        'premium': round(call_premium, 2),
                        'distance_pct': round(distance_pct, 2),
                        'potential_multiplier': round(potential_multiplier, 1),
                        'potential_value': round(potential_value, 2),
                        'iv': round(iv, 2),
                        'days': days_to_expiry
                    })
            
            # Check if PUT is in range
            if self.min_premium <= put_premium <= self.max_premium:
                distance_pct = abs(spot - strike) / spot * 100
                
                intrinsic_at_strike = max(0, spot - strike) if strike < spot else 0
                potential_value = intrinsic_at_strike + (put_premium * 0.3)
                potential_multiplier = potential_value / put_premium if put_premium > 0 else 0
                
                if potential_multiplier >= 3.0:
                    low_premium_options.append({
                        'symbol': symbol,
                        'type': 'PE',
                        'strike': strike,
                        'spot': spot,
                        'premium': round(put_premium, 2),
                        'distance_pct': round(distance_pct, 2),
                        'potential_multiplier': round(potential_multiplier, 1),
                        'potential_value': round(potential_value, 2),
                        'iv': round(iv, 2),
                        'days': days_to_expiry
                    })
        
        return low_premium_options
    
    def score_opportunity(self, option: Dict, market_data: pd.DataFrame) -> float:
        """
        Score the opportunity based on multiple factors
        Returns score 0-100
        """
        score = 0
        
        # Factor 1: Low premium (lower is better for multibagger potential)
        if option['premium'] < 5:
            score += 30
        elif option['premium'] < 10:
            score += 20
        else:
            score += 10
        
        # Factor 2: Potential multiplier
        if option['potential_multiplier'] >= 8:
            score += 30
        elif option['potential_multiplier'] >= 5:
            score += 20
        else:
            score += 10
        
        # Factor 3: Reasonable distance (not too far OTM)
        if option['distance_pct'] < 3:
            score += 20
        elif option['distance_pct'] < 5:
            score += 15
        else:
            score += 5
        
        # Factor 4: Enough time (min 5 days)
        if option['days'] >= 7:
            score += 10
        elif option['days'] >= 5:
            score += 5
        
        # Factor 5: Market momentum (from technical data)
        if not market_data.empty and len(market_data) > 5:
            latest = market_data.iloc[-1]
            
            if option['type'] == 'CE':
                # For calls, we want bullish setup
                if latest.get('RSI', 50) > 55 and latest['Close'] > latest.get('EMA20', latest['Close']):
                    score += 10
            else:
                # For puts, we want bearish setup
                if latest.get('RSI', 50) < 45 and latest['Close'] < latest.get('EMA20', latest['Close']):
                    score += 10
        
        return min(100, score)
    
    def scan_for_opportunities(self, symbols: List[str] = None) -> List[Dict]:
        """Scan all symbols for low premium opportunities"""
        
        if symbols is None:
            symbols = ["NIFTY", "BANKNIFTY", "FINNIFTY"] + [s.replace(".NS", "") for s in ALL_FO_STOCKS[:10]]
        
        all_opportunities = []
        
        print("🔍 Scanning for Low Premium Opportunities...")
        
        for symbol_name in symbols:
            try:
                # Get market data
                ticker_symbol = SYMBOLS.get(symbol_name, f"{symbol_name}.NS")
                
                ticker = yf.Ticker(ticker_symbol)
                df = ticker.history(period="10d")
                
                if df.empty:
                    continue
                
                # Use unified indicators
                df = calculate_indicators(df)
                
                spot = df['Close'].iloc[-1]
                days_to_expiry = get_days_to_expiry()
                
                # Get low premium options
                options = self.get_otm_options(symbol_name, spot, days_to_expiry)
                
                # Score each
                for opt in options:
                    opt['score'] = self.score_opportunity(opt, df)
                    
                    # Only include good scores (60+)
                    if opt['score'] >= 60:
                        all_opportunities.append(opt)
                        print(f"✅ {symbol_name} {opt['type']} {opt['strike']}: ₹{opt['premium']} → ₹{opt['potential_value']} ({opt['potential_multiplier']}x) [Score: {opt['score']}]")
            
            except Exception as e:
                print(f"❌ Error scanning {symbol_name}: {e}")
        
        # Sort by score
        all_opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return all_opportunities
    
    def _get_days_to_expiry(self) -> int:
        return get_days_to_expiry()
    
    def generate_alert_message(self, opportunities: List[Dict]) -> str:
        """Generate alert message for top opportunities"""
        if not opportunities:
            return "No low premium opportunities found today."
        
        msg = "💎 *LOW PREMIUM OPPORTUNITIES* (₹3-15)\n\n"
        msg += "These options have 5-10x potential:\n\n"
        
        for idx, opp in enumerate(opportunities[:5], 1):  # Top 5
            msg += f"{idx}. *{opp['symbol']} {opp['type']} {opp['strike']}*\n"
            msg += f"   Premium: ₹{opp['premium']:.2f}\n"
            msg += f"   Target: ₹{opp['potential_value']:.2f} ({opp['potential_multiplier']:.1f}x)\n"
            msg += f"   Distance: {opp['distance_pct']:.1f}% OTM\n"
            msg += f"   Score: {opp['score']}/100\n"
            msg += f"   Days: {opp['days']}\n\n"
        
        msg += "⚠️ *Risk Warning:*\n"
        msg += "Deep OTM options are high risk. Only use 1-2% capital per trade.\n"
        msg += "These can expire worthless if market doesn't move.\n\n"
        
        msg += "💡 *Strategy:*\n"
        msg += "• Buy only with strong technical confirmation\n"
        msg += "• Book partial profits at 3x\n"
        msg += "• Let runners go for 5-10x\n"
        msg += "• Cut loss if premium drops 50%"
        
        return msg

# Singleton
_premium_scanner = None

def get_premium_scanner() -> LowPremiumScanner:
    """Get singleton premium scanner"""
    global _premium_scanner
    if _premium_scanner is None:
        _premium_scanner = LowPremiumScanner()
    return _premium_scanner

# Test
if __name__ == "__main__":
    scanner = get_premium_scanner()
    opps = scanner.scan_for_opportunities()
    
    print(f"\n📊 Found {len(opps)} opportunities")
    
    if opps:
        msg = scanner.generate_alert_message(opps)
        print("\n" + msg)
