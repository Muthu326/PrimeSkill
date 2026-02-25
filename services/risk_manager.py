"""
Risk Manager - Portfolio Risk Management and Limits
"""
from datetime import datetime, date
from typing import Dict, Optional, Tuple

from models.trade_models import Greeks
from database import get_db_manager
from config.config import TRADING_CONFIG, RISK_LIMITS
from services.pnl_calculator import get_pnl_calculator
from services.trading_engine import TradingEngine

class RiskManager:
    """
    Risk Management System
    - Position size limits
    - Daily loss limits
    - Portfolio exposure tracking
    - Risk alerts
    """
    
    def __init__(self):
        self.db = get_db_manager()
        self.pnl_calc = get_pnl_calculator()
    
    def check_position_limit(self) -> Tuple[bool, str]:
        """
        Check if adding new position exceeds limits
        
        Returns:
            Tuple of (allowed, message)
        """
        active_positions = self.db.get_positions(active_only=True)
        max_positions = TRADING_CONFIG['max_positions']
        
        if len(active_positions) >= max_positions:
            return False, f"Maximum {max_positions} positions allowed. Close existing positions first."
        
        return True, "OK"
    
    def check_daily_loss_limit(self) -> Tuple[bool, str]:
        """
        Check if daily loss limit is breached
        
        Returns:
            Tuple of (allowed, message)
        """
        daily_pnl = self.pnl_calc.get_daily_pnl()
        max_daily_loss = TRADING_CONFIG['initial_capital'] * TRADING_CONFIG['max_daily_loss']
        
        if daily_pnl < -max_daily_loss:
            return False, f"Daily loss limit reached (₹{abs(daily_pnl):.2f} / ₹{max_daily_loss:.2f}). No new trades allowed today."
        
        return True, "OK"
    
    def check_position_size(self, premium: float, quantity: int) -> Tuple[bool, str]:
        """
        Check if position size is within risk limits
        
        Args:
            premium: Option premium
            quantity: Number of lots
        
        Returns:
            Tuple of (allowed, message)
        """
        position_cost = premium * quantity
        max_position_size = TRADING_CONFIG['initial_capital'] * TRADING_CONFIG['max_position_size']
        
        if position_cost > max_position_size:
            return False, f"Position size too large (₹{position_cost:.2f} > ₹{max_position_size:.2f}). Reduce quantity."
        
        return True, "OK"
    
    def check_all_limits(self, premium: float, quantity: int = 1) -> Tuple[bool, str]:
        """
        Check all risk limits before placing trade
        
        Args:
            premium: Option premium
            quantity: Number of lots
        
        Returns:
            Tuple of (allowed, message)
        """
        # Check position count
        allowed, msg = self.check_position_limit()
        if not allowed:
            return False, msg
        
        # Check daily loss
        allowed, msg = self.check_daily_loss_limit()
        if not allowed:
            return False, msg
        
        # Check position size
        allowed, msg = self.check_position_size(premium, quantity)
        if not allowed:
            return False, msg
        
        return True, "All risk checks passed"
    
    def calculate_portfolio_risk(self) -> Dict[str, float]:
        """
        Calculate portfolio risk metrics
        
        Returns:
            Dict with risk metrics
        """
        positions = self.db.get_positions(active_only=True)
        
        total_exposure = 0
        total_max_loss = 0
        total_current_value = 0
        
        for pos in positions:
            exposure = pos.avg_price * pos.quantity
            total_exposure += exposure
            
            if pos.max_loss:
                total_max_loss += pos.max_loss
            
            if pos.current_price:
                total_current_value += pos.current_price * pos.quantity
        
        # Get unrealized P&L
        unrealized_pnl = self.pnl_calc.calculate_unrealized_pnl()
        
        # Calculate portfolio Greeks
        portfolio_greeks = self.get_portfolio_greeks()
        
        return {
            'total_exposure': round(total_exposure, 2),
            'current_value': round(total_current_value, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'max_potential_loss': round(total_max_loss, 2),
            'portfolio_delta': portfolio_greeks.delta,
            'portfolio_gamma': portfolio_greeks.gamma,
            'portfolio_theta': portfolio_greeks.theta,
            'portfolio_vega': portfolio_greeks.vega,
            'risk_percentage': round((abs(total_max_loss) / TRADING_CONFIG['initial_capital']) * 100, 2) if total_max_loss else 0
        }
    
    def get_portfolio_greeks(self) -> Greeks:
        """
        Get aggregated portfolio Greeks
        
        Returns:
            Greeks object with portfolio totals
        """
        # This uses the trading engine's method
        from services.trading_engine import get_trading_engine
        engine = get_trading_engine()
        return engine.get_portfolio_greeks()
    
    def get_risk_alerts(self) -> list:
        """
        Get current risk alerts
        
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Check daily loss
        daily_pnl = self.pnl_calc.get_daily_pnl()
        max_daily_loss = TRADING_CONFIG['initial_capital'] * TRADING_CONFIG['max_daily_loss']
        
        if daily_pnl < -max_daily_loss * 0.8:  # 80% of limit
            alerts.append({
                'severity': 'HIGH',
                'message': f"⚠️ Daily loss approaching limit: ₹{abs(daily_pnl):.2f} / ₹{max_daily_loss:.2f}"
            })
        
        # Check position count
        positions = self.db.get_positions(active_only=True)
        max_positions = TRADING_CONFIG['max_positions']
        
        if len(positions) >= max_positions * 0.8:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f"⚠️ Position limit approaching: {len(positions)} / {max_positions}"
            })
        
        # Check portfolio Greeks
        greeks = self.get_portfolio_greeks()
        
        if abs(greeks.delta) > 0.70:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f"⚠️ High portfolio Delta: {greeks.delta:.2f} (directional risk)"
            })
        
        if abs(greeks.theta) > 100:
            alerts.append({
                'severity': 'INFO',
                'message': f"ℹ️ High time decay: ₹{abs(greeks.theta):.2f}/day"
            })
        
        return alerts
    
    def suggest_hedge(self) -> Optional[str]:
        """
        Suggest hedge based on portfolio Greeks
        
        Returns:
            Hedge suggestion string or None
        """
        greeks = self.get_portfolio_greeks()
        
        # High positive delta - portfolio is too bullish
        if greeks.delta > 0.70:
            return "Portfolio is heavily bullish (Delta > 0.70). Consider buying PUT options to hedge."
        
        # High negative delta - portfolio is too bearish
        elif greeks.delta < -0.70:
            return "Portfolio is heavily bearish (Delta < -0.70). Consider buying CALL options to hedge."
        
        # High gamma - large price sensitivity
        elif abs(greeks.gamma) > 0.10:
            return f"High Gamma ({greeks.gamma:.2f}). Delta will change rapidly with price movement. Monitor closely."
        
        # High negative theta - losing money to time decay
        elif greeks.theta < -50:
            return f"High time decay (₹{abs(greeks.theta):.2f}/day). Consider closing long options or selling options to collect premium."
        
        return None

# Singleton instance
_risk_manager = None

def get_risk_manager() -> RiskManager:
    """Get singleton risk manager instance"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager()
    return _risk_manager
