"""
Trading Engine - Paper Trading Execution System
Handles trade placement, position management, and lifecycle
"""
from datetime import datetime
from typing import List, Optional
import urllib.request
import urllib.parse
import json

from models.trade_models import Trade, Position, StrategySignal, OptionType, TradeStatus, Greeks
from database import get_db_manager
from config.config import TRADING_CONFIG, TELEGRAM_CONFIG
from services.options_pricer import get_options_pricer

class TradingEngine:
    """
    Paper Trading Engine
    - Execute trades based on signals
    - Manage positions
    - Track entries and exits
    """
    
    def __init__(self):
        self.db = get_db_manager()
        self.options_pricer = get_options_pricer()
    
    def calculate_fees(self, premium: float, quantity: int) -> float:
        """
        Calculate trading fees (brokerage, STT, exchange charges)
        
        Args:
            premium: Option premium
            quantity: Number of lots
        
        Returns:
            Total fees
        """
        # Brokerage
        brokerage = TRADING_CONFIG['brokerage_per_lot'] * quantity
        
        # STT (on sell side, but we'll apply simplified version)
        turnover = premium * quantity
        stt = turnover * TRADING_CONFIG['stt_percent']
        
        # Exchange charges
        exchange = turnover * TRADING_CONFIG['exchange_charges']
        
        total_fees = brokerage + stt + exchange
        return round(total_fees, 2)
    
    def place_trade(self, signal: StrategySignal) -> Optional[int]:
        """
        Place a trade based on strategy signal
        
        Args:
            signal: StrategySignal from strategy engine
        
        Returns:
            Trade ID if successful, None otherwise
        """
        # Get strategy ID
        strategies = self.db.get_all_strategies()
        strategy = next((s for s in strategies if s.type == signal.strategy_type), None)
        
        if not strategy:
            print(f"Strategy {signal.strategy_type} not found in database")
            return None
        
        # For multi-leg strategies, we need to handle each leg
        # For now, implementing simple single-leg trades (Long Call/Put)
        
        if len(signal.option_legs) == 1:
            # Single leg strategy
            leg = signal.option_legs[0]
            
            option_type = OptionType.CE if leg['type'] == 'CE' else OptionType.PE
            strike = leg['strike']
            premium = leg['premium']
            
            # Calculate fees
            fees = self.calculate_fees(premium, signal.position_size)
            
            # Calculate risk metrics
            stop_loss = signal.stop_loss
            target = signal.target
            max_profit = signal.max_profit if signal.max_profit != float('inf') else premium * 3  # Cap at 3x for display
            max_loss = signal.max_loss
            
            # Create trade object
            trade = Trade(
                strategy_id=strategy.id,
                symbol=signal.symbol,
                option_type=option_type,
                strike_price=strike,
                entry_price=premium,
                quantity=signal.position_size,
                entry_time=datetime.now(),
                status=TradeStatus.OPEN,
                fees=fees,
                notes=signal.notes,
                stop_loss=stop_loss,
                target=target,
                max_profit=max_profit,
                max_loss=max_loss
            )
            
            # Save to database
            trade_id = self.db.save_trade(trade)
            trade.id = trade_id
            
            # Create position
            position = Position(
                trade_id=trade_id,
                symbol=signal.symbol,
                option_type=option_type,
                strike_price=strike,
                quantity=signal.position_size,
                avg_price=premium,
                current_price=premium,
                pnl=0.0,
                greeks=None,  # Will be updated later
                max_loss=max_loss,
                max_profit=max_profit,
                breakeven=self.options_pricer.calculate_breakeven(strike, premium, leg['type'])
            )
            
            position_id = self.db.save_position(position)
            
            # Send alert
            self._send_trade_alert(trade, "ENTRY")
            
            return trade_id
        
        else:
            # Multi-leg strategy (Spreads, Straddles, etc.)
            # TODO: Implement multi-leg trade execution
            print(f"Multi-leg strategies not yet implemented in trading engine")
            return None
    
    def close_position(self, position_id: int, exit_price: float, reason: str = "Manual Close") -> bool:
        """
        Close an open position
        
        Args:
            position_id: Position ID to close
            exit_price: Current/exit price
            reason: Reason for closing
        
        Returns:
            True if successful
        """
        # Get position
        positions = self.db.get_positions(active_only=True)
        position = next((p for p in positions if p.id == position_id), None)
        
        if not position:
            print(f"Position {position_id} not found or already closed")
            return False
        
        # Get associated trade
        trades = self.db.get_trades()
        trade = next((t for t in trades if t.id == position.trade_id), None)
        
        if not trade:
            print(f"Trade {position.trade_id} not found")
            return False
        
        # Update trade
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.pnl = trade.calculate_pnl(exit_price)
        trade.notes = f"{trade.notes} | Exit: {reason}" if trade.notes else f"Exit: {reason}"
        
        # Determine status
        if trade.pnl >= 0:
            trade.status = TradeStatus.CLOSED
        else:
            if abs(trade.pnl) >= abs(trade.max_loss) * 0.8:  # 80% of max loss
                trade.status = TradeStatus.STOPPED
            else:
                trade.status = TradeStatus.CLOSED
        
        # Save trade
        self.db.update_trade(trade)
        
        # Delete position
        self.db.delete_position(position_id)
        
        # Send alert
        self._send_trade_alert(trade, "EXIT")
        
        return True
    
    def update_positions(self, symbol: str, current_price: float, days_to_expiry: int, iv: Optional[float] = None):
        """
        Update all open positions for a symbol with current prices and Greeks
        
        Args:
            symbol: Trading symbol
            current_price: Current spot price
            days_to_expiry: Days to expiry
            iv: Implied volatility (will estimate if None)
        """
        if iv is None:
            iv = self.options_pricer.estimate_iv_from_history(symbol)
        
        positions = self.db.get_positions(active_only=True)
        symbol_positions = [p for p in positions if p.symbol == symbol]
        
        for position in symbol_positions:
            # Recalculate option price
            opt_type = "CE" if position.option_type == OptionType.CE else "PE"
            
            new_price = self.options_pricer.bs_calculator.call_price(
                current_price, position.strike_price, days_to_expiry/365, 0.06, iv/100
            ) if opt_type == "CE" else self.options_pricer.bs_calculator.put_price(
                current_price, position.strike_price, days_to_expiry/365, 0.06, iv/100
            )
            
            # Calculate Greeks
            greeks = self.options_pricer.bs_calculator.calculate_greeks(
                current_price, position.strike_price, days_to_expiry/365, 0.06, iv/100, opt_type
            )
            
            # Update position
            position.current_price = round(new_price, 2)
            position.greeks = greeks
            position.update_pnl()
            
            # Save to database
            self.db.update_position(position)
            
            # Check for stop loss or target hit
            if position.pnl is not None:
                trade = next((t for t in self.db.get_trades() if t.id == position.trade_id), None)
                
                if trade:
                    # Check stop loss
                    if trade.stop_loss and position.current_price <= trade.stop_loss:
                        self.close_position(position.id, position.current_price, "Stop Loss Hit")
                    
                    # Check target
                    elif trade.target and position.current_price >= trade.target:
                        self.close_position(position.id, position.current_price, "Target Reached")
    
    def get_active_positions(self) -> List[Position]:
        """Get all active positions"""
        return self.db.get_positions(active_only=True)
    
    def get_portfolio_greeks(self) -> Greeks:
        """
        Calculate aggregate portfolio Greeks
        
        Returns:
            Greeks object with portfolio totals
        """
        positions = self.get_active_positions()
        
        total_delta = 0.0
        total_gamma = 0.0
        total_theta = 0.0
        total_vega = 0.0
        total_rho = 0.0
        
        for pos in positions:
            if pos.greeks:
                total_delta += pos.greeks.delta * pos.quantity
                total_gamma += pos.greeks.gamma * pos.quantity
                total_theta += pos.greeks.theta * pos.quantity
                total_vega += pos.greeks.vega * pos.quantity
                total_rho += pos.greeks.rho * pos.quantity
        
        return Greeks(
            delta=round(total_delta, 4),
            gamma=round(total_gamma, 4),
            theta=round(total_theta, 4),
            vega=round(total_vega, 4),
            rho=round(total_rho, 4)
        )
    
    def _send_trade_alert(self, trade: Trade, alert_type: str):
        """Send Telegram alert for trade"""
        try:
            if alert_type == "ENTRY":
                message = f"🎯 *TRADE ENTRY*\n\n"
                message += f"Symbol: *{trade.symbol}*\n"
                message += f"Type: {trade.option_type.value}\n"
                message += f"Strike: {trade.strike_price}\n"
                message += f"Entry: ₹{trade.entry_price}\n"
                message += f"Qty: {trade.quantity}\n"
                message += f"Stop Loss: ₹{trade.stop_loss}\n"
                message += f"Target: ₹{trade.target}\n"
                message += f"Max Loss: ₹{trade.max_loss}\n"
                message += f"\n{trade.notes}"
            
            else:  # EXIT
                pnl_emoji = "✅" if trade.pnl >= 0 else "❌"
                message = f"{pnl_emoji} *TRADE EXIT*\n\n"
                message += f"Symbol: *{trade.symbol}*\n"
                message += f"Type: {trade.option_type.value}\n"
                message += f"Entry: ₹{trade.entry_price}\n"
                message += f"Exit: ₹{trade.exit_price}\n"
                message += f"P&L: *₹{trade.pnl}*\n"
                message += f"ROI: {((trade.pnl/trade.entry_price)*100):.1f}%\n"
                message += f"\n{trade.notes}"
            
            # Send via Telegram
            url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['token']}/sendMessage"
            data = urllib.parse.urlencode({
                'chat_id': TELEGRAM_CONFIG['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=10) as response:
                pass
        
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")

# Singleton instance
_trading_engine = None

def get_trading_engine() -> TradingEngine:
    """Get singleton trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = TradingEngine()
    return _trading_engine
