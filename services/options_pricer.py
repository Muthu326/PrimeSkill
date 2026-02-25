"""
Options Pricer Service
Enhanced option pricing with NSE option chain generation
"""
import pandas as pd
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf

from models.trade_models import OptionContract, OptionType, Greeks
from utils.greeks_calculator import BlackScholesCalculator, calculate_option_price, calculate_greeks
from config.config import BS_PARAMS, OPTION_CHAIN_CONFIG, SYMBOLS

class OptionsPricer:
    """
    Comprehensive options pricing service
    - Black-Scholes pricing
    - Greeks calculations
    - Option chain generation
    - IV estimation
    """
    
    def __init__(self):
        self.bs_calculator = BlackScholesCalculator()
        self.iv_cache = {}  # Cache IV estimates
    
    def estimate_iv_from_history(self, symbol: str, period: str = "30d") -> float:
        """
        Estimate Implied Volatility from historical price volatility
        
        Args:
            symbol: Trading symbol (NIFTY, BANKNIFTY, etc.)
            period: Historical period for calculation
        
        Returns:
            Estimated IV as percentage
        """
        # Check cache
        cache_key = f"{symbol}_{period}"
        if cache_key in self.iv_cache:
            cache_time, iv = self.iv_cache[cache_key]
            if (datetime.now() - cache_time).seconds < 3600:  # 1 hour cache
                return iv
        
        try:
            # Get historical data
            ticker_symbol = SYMBOLS.get(symbol, symbol)
            if not ticker_symbol.startswith("^"):
                ticker_symbol = f"{ticker_symbol}.NS"
            
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return 20.0  # Default fallback
            
            # Calculate historical volatility (annualized)
            returns = hist['Close'].pct_change().dropna()
            hist_vol = returns.std() * math.sqrt(252) * 100  # Annualized %
            
            # IV is typically higher than historical volatility
            # Add a markup (10-30%) based on market conditions
            iv_estimate = hist_vol * 1.15  # 15% markup
            iv_estimate = max(10.0, min(60.0, iv_estimate))  # Clamp between 10-60%
            
            # Cache the result
            self.iv_cache[cache_key] = (datetime.now(), iv_estimate)
            
            return round(iv_estimate, 2)
        
        except Exception as e:
            print(f"IV estimation error for {symbol}: {e}")
            return 20.0  # Fallback default
    
    def get_strike_ladder(self, spot: float, symbol: str = "NIFTY") -> List[float]:
        """
        Generate strike price ladder based on symbol
        
        Args:
            spot: Current spot price
            symbol: Trading symbol
        
        Returns:
            List of strike prices
        """
        config = OPTION_CHAIN_CONFIG
        strike_gap = config['strike_gap'].get(symbol, 50)
        strikes_above = config['strikes_above']
        strikes_below = config['strikes_below']
        
        # Round spot to nearest strike
        atm_strike = round(spot / strike_gap) * strike_gap
        
        # Generate strikes
        strikes = []
        for i in range(-strikes_below, strikes_above + 1):
            strike = atm_strike + (i * strike_gap)
            if strike > 0:
                strikes.append(strike)
        
        return sorted(strikes)
    
    def generate_option_chain(self, 
                             symbol: str,
                             spot: float,
                             expiry_date: datetime,
                             iv: Optional[float] = None) -> pd.DataFrame:
        """
        Generate complete option chain with prices and Greeks
        
        Args:
            symbol: Trading symbol
            spot: Current spot price
            expiry_date: Expiry date
            iv: Implied Volatility (if None, will estimate)
        
        Returns:
            DataFrame with option chain data
        """
        if iv is None:
            iv = self.estimate_iv_from_history(symbol)
        
        # Calculate days to expiry
        days_to_expiry = max(1, (expiry_date - datetime.now()).days)
        
        # Get strike ladder
        strikes = self.get_strike_ladder(spot, symbol)
        
        # Generate option chain
        chain_data = []
        
        for strike in strikes:
            # Calculate for Call
            call_price = calculate_option_price(spot, strike, days_to_expiry, iv, "CE")
            call_greeks = calculate_greeks(spot, strike, days_to_expiry, iv, "CE")
            
            # Calculate for Put
            put_price = calculate_option_price(spot, strike, days_to_expiry, iv, "PE")
            put_greeks = calculate_greeks(spot, strike, days_to_expiry, iv, "PE")
            
            # Determine moneyness
            if abs(strike - spot) < (OPTION_CHAIN_CONFIG['strike_gap'].get(symbol, 50) / 2):
                moneyness = "ATM"
            elif strike > spot:
                moneyness = "OTM"  # For calls
            else:
                moneyness = "ITM"  # For calls
            
            chain_data.append({
                'Strike': strike,
                'Moneyness': moneyness,
                'Call_Premium': round(call_price, 2),
                'Call_Delta': call_greeks.delta,
                'Call_Gamma': call_greeks.gamma,
                'Call_Theta': call_greeks.theta,
                'Call_Vega': call_greeks.vega,
                'Put_Premium': round(put_price, 2),
                'Put_Delta': put_greeks.delta,
                'Put_Gamma': put_greeks.gamma,
                'Put_Theta': put_greeks.theta,
                'Put_Vega': put_greeks.vega,
                'IV': iv,
                'Days_to_Expiry': days_to_expiry
            })
        
        df = pd.DataFrame(chain_data)
        return df
    
    def get_option_by_moneyness(self, 
                                spot: float,
                                symbol: str,
                                moneyness: str,
                                option_type: str = "CE") -> float:
        """
        Get strike price based on moneyness
        
        Args:
            spot: Current spot price
            symbol: Trading symbol
            moneyness: "ATM", "OTM1", "OTM2", "ITM1", "ITM2"
            option_type: "CE" or "PE"
        
        Returns:
            Strike price
        """
        strike_gap = OPTION_CHAIN_CONFIG['strike_gap'].get(symbol, 50)
        atm_strike = round(spot / strike_gap) * strike_gap
        
        if moneyness == "ATM":
            return atm_strike
        elif moneyness == "OTM1":
            return atm_strike + strike_gap if option_type == "CE" else atm_strike - strike_gap
        elif moneyness == "OTM2":
            return atm_strike + (2 * strike_gap) if option_type == "CE" else atm_strike - (2 * strike_gap)
        elif moneyness == "ITM1":
            return atm_strike - strike_gap if option_type == "CE" else atm_strike + strike_gap
        elif moneyness == "ITM2":
            return atm_strike - (2 * strike_gap) if option_type == "CE" else atm_strike + (2 * strike_gap)
        else:
            return atm_strike
    
    def calculate_option_contract(self,
                                  symbol: str,
                                  strike: float,
                                  option_type: OptionType,
                                  spot: float,
                                  days_to_expiry: int,
                                  iv: Optional[float] = None) -> OptionContract:
        """
        Create a complete OptionContract object with pricing and Greeks
        
        Args:
            symbol: Trading symbol
            strike: Strike price
            option_type: OptionType.CE or OptionType.PE
            spot: Current spot price
            days_to_expiry: Days until expiry
            iv: Implied Volatility (will estimate if None)
        
        Returns:
            OptionContract object
        """
        if iv is None:
            iv = self.estimate_iv_from_history(symbol)
        
        opt_type_str = "CE" if option_type == OptionType.CE else "PE"
        
        # Calculate premium and greeks
        premium = calculate_option_price(spot, strike, days_to_expiry, iv, opt_type_str)
        greeks = calculate_greeks(spot, strike, days_to_expiry, iv, opt_type_str)
        
        # Calculate expiry date
        expiry_date = datetime.now() + timedelta(days=days_to_expiry)
        
        contract = OptionContract(
            symbol=symbol,
            option_type=option_type,
            strike=strike,
            expiry_date=expiry_date,
            spot_price=spot,
            premium=round(premium, 2),
            iv=iv,
            greeks=greeks
        )
        
        return contract
    
    def calculate_breakeven(self,
                           strike: float,
                           premium: float,
                           option_type: str = "CE") -> float:
        """
        Calculate breakeven price for option
        
        Args:
            strike: Strike price
            premium: Option premium paid
            option_type: "CE" or "PE"
        
        Returns:
            Breakeven spot price
        """
        if option_type == "CE":
            return strike + premium
        else:
            return strike - premium
    
    def calculate_max_profit_loss(self,
                                  strike: float,
                                  premium: float,
                                  quantity: int,
                                  option_type: str = "CE",
                                  is_buyer: bool = True) -> Tuple[float, float]:
        """
        Calculate maximum profit and loss for option position
        
        Args:
            strike: Strike price
            premium: Option premium
            quantity: Number of lots
            option_type: "CE" or "PE"
            is_buyer: True if buying, False if selling
        
        Returns:
            Tuple of (max_profit, max_loss)
        """
        cost = premium * quantity
        
        if is_buyer:
            # Buyer: Limited loss (premium), unlimited profit
            max_loss = -cost
            max_profit = float('inf')  # Theoretically unlimited
        else:
            # Seller: Limited profit (premium), unlimited loss
            max_profit = cost
            max_loss = float('-inf')  # Theoretically unlimited
        
        return max_profit, max_loss

# Singleton instance
_options_pricer = None

def get_options_pricer() -> OptionsPricer:
    """Get singleton options pricer instance"""
    global _options_pricer
    if _options_pricer is None:
        _options_pricer = OptionsPricer()
    return _options_pricer
