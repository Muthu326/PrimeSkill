"""
Theta Decay Monitor - Expiry Rollover Alerts
Monitors options losing value to time decay
Suggests when to roll to next contract
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import urllib.request
import urllib.parse

from database import get_db_manager
from services.options_pricer import get_options_pricer
from services.market_engine import get_days_to_expiry, send_telegram
from models.trade_models import Position, TradeStatus
from config.config import TELEGRAM_CONFIG

class ThetaMonitor:
    """
    Monitors time decay on open positions
    - Alerts when theta decay accelerating
    - Suggests expiry rollover
    - Recommends next contract
    """
    
    def __init__(self):
        self.db = get_db_manager()
        self.pricer = get_options_pricer()
        self.theta_warning_threshold = -50  # Alert if theta < -50 per day
        self.days_to_expiry_warning = 3     # Alert if < 3 days to expiry
    
    def get_days_to_next_expiry(self) -> int:
        return get_days_to_expiry()
    
    def calculate_theta_impact(self, position: Position, days_to_expiry: int) -> Dict:
        """Calculate theta decay impact on position"""
        
        if not position.greeks or not position.current_price:
            return None
        
        theta = position.greeks.theta
        
        # Daily decay amount
        daily_decay = abs(theta) * position.quantity
        
        # Decay to expiry (total remaining time value loss)
        decay_to_expiry = daily_decay * days_to_expiry
        
        # Percentage of current value
        decay_pct = (daily_decay / position.current_price * 100) if position.current_price > 0 else 0
        
        # Severity
        if days_to_expiry <= 2:
            severity = "CRITICAL"
        elif days_to_expiry <= 4:
            severity = "HIGH"
        elif abs(theta) > 50:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        return {
            'position_id': position.id,
            'symbol': position.symbol,
            'strike': position.strike_price,
            'type': position.option_type.value,
            'theta': round(theta, 2),
            'daily_decay': round(daily_decay, 2),
            'decay_to_expiry': round(decay_to_expiry, 2),
            'decay_pct': round(decay_pct, 2),
            'days_to_expiry': days_to_expiry,
            'current_price': position.current_price,
            'severity': severity
        }
    
    def should_roll_position(self, theta_impact: Dict) -> bool:
        """Determine if position should be rolled to next expiry"""
        
        # Roll if:
        # 1. Less than 3 days to expiry AND position in profit
        # 2. Theta decay > 5% per day
        # 3. Critical severity
        
        if theta_impact['days_to_expiry'] <= 2:
            return True
        
        if theta_impact['decay_pct'] > 5.0:
            return True
        
        if theta_impact['severity'] == "CRITICAL":
            return True
        
        return False
    
    def get_rollover_recommendation(self, position: Position, spot: float) -> Optional[Dict]:
        """Recommend next contract for rollover"""
        
        # Close current position
        # Open new position in next weekly expiry
        
        # Get next expiry (7 days from now if we're in current week)
        current_days = self.get_days_to_next_expiry()
        
        if current_days <= 3:
            # Roll to next week
            next_expiry_days = current_days + 7
        else:
            # Stay in current week but different strike
            next_expiry_days = current_days
        
        # Same strike or adjust based on spot movement
        recommended_strike = position.strike_price
        
        # If far OTM and losing, suggest closer strike
        distance = abs(spot - position.strike_price)
        distance_pct = (distance / spot) * 100
        
        if distance_pct > 3 and position.pnl and position.pnl < 0:
            # Adjust strike closer to spot
            strike_gap = 50  # Assume NIFTY
            if "BANK" in position.symbol:
                strike_gap = 100
            
            # Move towards spot
            if position.strike_price > spot:
                recommended_strike = position.strike_price - strike_gap
            else:
                recommended_strike = position.strike_price + strike_gap
        
        # Calculate new premium
        iv = self.pricer.estimate_iv_from_history(position.symbol)
        
        if position.option_type.value == "CE":
            new_premium = self.pricer.bs_calculator.call_price(
                spot, recommended_strike, next_expiry_days/365, 0.06, iv/100
            )
        else:
            new_premium = self.pricer.bs_calculator.put_price(
                spot, recommended_strike, next_expiry_days/365, 0.06, iv/100
            )
        
        return {
            'action': 'ROLLOVER',
            'close_current': {
                'strike': position.strike_price,
                'current_price': position.current_price
            },
            'open_new': {
                'strike': recommended_strike,
                'premium': round(new_premium, 2),
                'days_to_expiry': next_expiry_days
            },
            'net_cost': round(new_premium - (position.current_price or 0), 2)
        }
    
    def monitor_all_positions(self) -> List[Dict]:
        """Monitor all open positions for theta decay"""
        
        positions = self.db.get_positions(active_only=True)
        
        if not positions:
            return []
        
        alerts = []
        days_to_expiry = self.get_days_to_next_expiry()
        
        for pos in positions:
            theta_impact = self.calculate_theta_impact(pos, days_to_expiry)
            
            if not theta_impact:
                continue
            
            # Check if alert needed
            if (theta_impact['severity'] in ['HIGH', 'CRITICAL'] or
                theta_impact['decay_pct'] > 3.0):
                
                # Get spot price (simplified - you'd fetch real price)
                spot = pos.strike_price  # Placeholder
                
                # Check if should roll
                should_roll = self.should_roll_position(theta_impact)
                
                if should_roll:
                    rollover_rec = self.get_rollover_recommendation(pos, spot)
                    theta_impact['rollover'] = rollover_rec
                
                alerts.append(theta_impact)
        
        return alerts
    
    def generate_alert_message(self, alerts: List[Dict]) -> str:
        """Generate alert message for theta decay"""
        
        if not alerts:
            return None
        
        msg = "⚠️ *THETA DECAY ALERT*\n\n"
        msg += "Your options are losing value to time decay:\n\n"
        
        for alert in alerts:
            msg += f"*{alert['symbol']} {alert['type']} {alert['strike']}*\n"
            msg += f"  Current: ₹{alert['current_price']:.2f}\n"
            msg += f"  Theta: ₹{abs(alert['theta']):.2f}/day\n"
            msg += f"  Daily Decay: ₹{alert['daily_decay']:.2f} ({alert['decay_pct']:.1f}%)\n"
            msg += f"  Days to Expiry: {alert['days_to_expiry']}\n"
            msg += f"  Severity: {alert['severity']}\n"
            
            if 'rollover' in alert:
                roll = alert['rollover']
                msg += f"\n  💡 *ROLLOVER SUGGESTION:*\n"
                msg += f"  • Close {alert['strike']} @ ₹{roll['close_current']['current_price']:.2f}\n"
                msg += f"  • Open {roll['open_new']['strike']} @ ₹{roll['open_new']['premium']:.2f}\n"
                msg += f"  • Net Cost: ₹{abs(roll['net_cost']):.2f}\n"
                msg += f"  • New Expiry: {roll['open_new']['days_to_expiry']} days\n"
            
            msg += "\n"
        
        msg += "⚡ *Action Required:*\n"
        msg += "• Close expiring positions ASAP\n"
        msg += "• Roll to next week if still bullish/bearish\n"
        msg += "• Or book whatever profit/loss remains\n\n"
        
        msg += "⏰ Theta decay accelerates in last 3 days!"
        
        return msg
    
    def send_alert(self, message: str):
        """Send theta decay alert via Telegram"""
        return send_telegram(TELEGRAM_CONFIG['token'], TELEGRAM_CONFIG['chat_id'], message)
    
    def run_monitoring(self):
        """Run theta monitoring and send alerts if needed"""
        
        print("⏱️ Monitoring Theta Decay...")
        
        alerts = self.monitor_all_positions()
        
        if alerts:
            print(f"⚠️ Found {len(alerts)} positions with high decay")
            
            message = self.generate_alert_message(alerts)
            
            if message:
                success = self.send_alert(message)
                
                if success:
                    print("✅ Theta alert sent!")
                else:
                    print("❌ Failed to send alert")
            
            return alerts
        else:
            print("✅ All positions healthy (theta OK)")
            return []

# Singleton
_theta_monitor = None

def get_theta_monitor() -> ThetaMonitor:
    """Get singleton theta monitor"""
    global _theta_monitor
    if _theta_monitor is None:
        _theta_monitor = ThetaMonitor()
    return _theta_monitor

# Test
if __name__ == "__main__":
    monitor = get_theta_monitor()
    alerts = monitor.run_monitoring()
    
    if alerts:
        msg = monitor.generate_alert_message(alerts)
        print("\n" + msg)
