"""
Black-Scholes Option Pricing and Greeks Calculator
Institutional-quality implementation for accurate option valuation
"""
import math
from typing import Tuple
from models import Greeks

def norm_cdf(x: float) -> float:
    """Cumulative distribution function for the standard normal distribution"""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def norm_pdf(x: float) -> float:
    """Probability density function for the standard normal distribution"""
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x**2)

class BlackScholesCalculator:
    """
    Black-Scholes-Merton model for European options
    Calculates option price and all Greeks
    """
    
    @staticmethod
    def calculate_d1_d2(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> Tuple[float, float]:
        """
        Calculate d1 and d2 for Black-Scholes formula
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry (in years)
            r: Risk-free rate (annual)
            sigma: Implied volatility (annual)
            q: Dividend yield (annual)
        
        Returns:
            Tuple of (d1, d2)
        """
        if T <= 0:
            # Option expired
            return 0.0, 0.0
        
        d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        return d1, d2
    
    @classmethod
    def call_price(cls, S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> float:
        """
        Calculate European Call Option Price
        
        Formula: C = S * e^(-qT) * N(d1) - K * e^(-rT) * N(d2)
        """
        if T <= 0:
            return max(0, S - K)
        
        d1, d2 = cls.calculate_d1_d2(S, K, T, r, sigma, q)
        
        call_price = (S * math.exp(-q * T) * norm_cdf(d1) - 
                     K * math.exp(-r * T) * norm_cdf(d2))
        
        return max(0, call_price)
    
    @classmethod
    def put_price(cls, S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> float:
        """
        Calculate European Put Option Price
        
        Formula: P = K * e^(-rT) * N(-d2) - S * e^(-qT) * N(-d1)
        """
        if T <= 0:
            return max(0, K - S)
        
        d1, d2 = cls.calculate_d1_d2(S, K, T, r, sigma, q)
        
        put_price = (K * math.exp(-r * T) * norm_cdf(-d2) - 
                    S * math.exp(-q * T) * norm_cdf(-d1))
        
        return max(0, put_price)
    
    @classmethod
    def calculate_greeks(cls, S: float, K: float, T: float, r: float, sigma: float, 
                        option_type: str = "CE", q: float = 0.0) -> Greeks:
        """
        Calculate all option Greeks
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate
            sigma: Implied volatility
            option_type: "CE" for call, "PE" for put
            q: Dividend yield
        
        Returns:
            Greeks object with delta, gamma, theta, vega, rho
        """
        if T <= 0:
            # Option expired - intrinsic value only
            if option_type == "CE":
                delta = 1.0 if S > K else 0.0
            else:
                delta = -1.0 if S < K else 0.0
            
            return Greeks(delta=delta, gamma=0, theta=0, vega=0, rho=0)
        
        d1, d2 = cls.calculate_d1_d2(S, K, T, r, sigma, q)
        
        # Delta
        if option_type == "CE":
            delta = math.exp(-q * T) * norm_cdf(d1)
        else:
            delta = -math.exp(-q * T) * norm_cdf(-d1)
        
        # Gamma (same for both call and put)
        gamma = (math.exp(-q * T) * norm_pdf(d1)) / (S * sigma * math.sqrt(T))
        
        # Theta (time decay)
        term1 = -(S * norm_pdf(d1) * sigma * math.exp(-q * T)) / (2 * math.sqrt(T))
        
        if option_type == "CE":
            term2 = -r * K * math.exp(-r * T) * norm_cdf(d2)
            term3 = q * S * math.exp(-q * T) * norm_cdf(d1)
            theta = (term1 + term2 + term3) / 365  # Daily theta
        else:
            term2 = r * K * math.exp(-r * T) * norm_cdf(-d2)
            term3 = -q * S * math.exp(-q * T) * norm_cdf(-d1)
            theta = (term1 + term2 + term3) / 365  # Daily theta
        
        # Vega (same for both)
        vega = (S * math.exp(-q * T) * norm_pdf(d1) * math.sqrt(T)) / 100  # Per 1% change in IV
        
        # Rho
        if option_type == "CE":
            rho = (K * T * math.exp(-r * T) * norm_cdf(d2)) / 100  # Per 1% change in rate
        else:
            rho = -(K * T * math.exp(-r * T) * norm_cdf(-d2)) / 100
        
        return Greeks(
            delta=round(delta, 4),
            gamma=round(gamma, 4),
            theta=round(theta, 4),
            vega=round(vega, 4),
            rho=round(rho, 4)
        )
    
    @classmethod
    def implied_volatility(cls, option_price: float, S: float, K: float, T: float, 
                          r: float, option_type: str = "CE", q: float = 0.0) -> float:
        """
        Calculate Implied Volatility using Newton-Raphson method
        
        Args:
            option_price: Market price of option
            S, K, T, r: Standard BS parameters
            option_type: "CE" or "PE"
            q: Dividend yield
        
        Returns:
            Implied Volatility (annual)
        """
        if T <= 0:
            return 0.0
        
        # Initial guess
        sigma = 0.3  # 30% IV
        max_iterations = 100
        tolerance = 0.0001
        
        for _ in range(max_iterations):
            if option_type == "CE":
                price = cls.call_price(S, K, T, r, sigma, q)
            else:
                price = cls.put_price(S, K, T, r, sigma, q)
            
            diff = price - option_price
            
            if abs(diff) < tolerance:
                return round(sigma, 4)
            
            # Vega for Newton-Raphson
            d1, _ = cls.calculate_d1_d2(S, K, T, r, sigma, q)
            vega = S * math.exp(-q * T) * norm_pdf(d1) * math.sqrt(T)
            
            if vega < 0.0001:  # Avoid division by very small number
                break
            
            # Update sigma
            sigma = sigma - diff / vega
            
            # Ensure sigma stays positive
            if sigma <= 0:
                sigma = 0.01
        
        return round(sigma, 4)

def calculate_option_price(spot: float, strike: float, days_to_expiry: int, 
                          iv: float, option_type: str = "CE", 
                          risk_free_rate: float = 0.06) -> float:
    """
    Wrapper function for quick option price calculation
    
    Args:
        spot: Current spot price
        strike: Strike price
        days_to_expiry: Days until expiry
        iv: Implied Volatility (as percentage, e.g., 20 for 20%)
        option_type: "CE" or "PE"
        risk_free_rate: Annual risk-free rate
    
    Returns:
        Option premium
    """
    T = days_to_expiry / 365.0
    sigma = iv / 100.0
    
    if option_type == "CE":
        return BlackScholesCalculator.call_price(spot, strike, T, risk_free_rate, sigma)
    else:
        return BlackScholesCalculator.put_price(spot, strike, T, risk_free_rate, sigma)

def calculate_greeks(spot: float, strike: float, days_to_expiry: int,
                    iv: float, option_type: str = "CE",
                    risk_free_rate: float = 0.06) -> Greeks:
    """
    Wrapper function for quick Greeks calculation
    
    Args:
        spot: Current spot price
        strike: Strike price
        days_to_expiry: Days until expiry
        iv: Implied Volatility (as percentage)
        option_type: "CE" or "PE"
        risk_free_rate: Annual risk-free rate
    
    Returns:
        Greeks object
    """
    T = days_to_expiry / 365.0
    sigma = iv / 100.0
    
    return BlackScholesCalculator.calculate_greeks(spot, strike, T, risk_free_rate, sigma, option_type)

# Quick test function
if __name__ == "__main__":
    # Test with NIFTY example
    spot = 21500
    strike = 21500  # ATM
    days = 7
    iv = 18  # 18% IV
    
    print("=" * 50)
    print("BLACK-SCHOLES CALCULATOR TEST")
    print("=" * 50)
    print(f"Spot: {spot}, Strike: {strike}, Days: {days}, IV: {iv}%")
    print()
    
    # Call option
    call_price = calculate_option_price(spot, strike, days, iv, "CE")
    call_greeks = calculate_greeks(spot, strike, days, iv, "CE")
    
    print("CALL OPTION (CE):")
    print(f"  Premium: ₹{call_price:.2f}")
    print(f"  Delta: {call_greeks.delta:.4f}")
    print(f"  Gamma: {call_greeks.gamma:.4f}")
    print(f"  Theta: ₹{call_greeks.theta:.2f} (daily decay)")
    print(f"  Vega: ₹{call_greeks.vega:.2f} (per 1% IV change)")
    print()
    
    # Put option
    put_price = calculate_option_price(spot, strike, days, iv, "PE")
    put_greeks = calculate_greeks(spot, strike, days, iv, "PE")
    
    print("PUT OPTION (PE):")
    print(f"  Premium: ₹{put_price:.2f}")
    print(f"  Delta: {put_greeks.delta:.4f}")
    print(f"  Gamma: {put_greeks.gamma:.4f}")
    print(f"  Theta: ₹{put_greeks.theta:.2f} (daily decay)")
    print(f"  Vega: ₹{put_greeks.vega:.2f} (per 1% IV change)")
    print("=" * 50)
