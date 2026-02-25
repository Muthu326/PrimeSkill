"""
P&L Calculator - Performance Tracking and Analytics
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd

from models.trade_models import Trade, Position, PerformanceMetrics, TradeStatus
from database import get_db_manager
from config.config import TRADING_CONFIG

class PnLCalculator:
    """
    Calculate and track Profit & Loss
    - Real-time P&L for open positions
    - Historical P&L analysis
    - Performance metrics
    """
    
    def __init__(self):
        self.db = get_db_manager()
    
    def calculate_realized_pnl(self, start_date: Optional[datetime] = None, 
                               end_date: Optional[datetime] = None) -> float:
        """
        Calculate realized P&L from closed trades
        
        Args:
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            Total realized P&L
        """
        # Get closed trades
        all_trades = self.db.get_trades(status=TradeStatus.CLOSED, limit=1000)
        
        # Filter by date if provided
        if start_date:
            all_trades = [t for t in all_trades if t.entry_time >= start_date]
        if end_date:
            all_trades = [t for t in all_trades if t.entry_time <= end_date]
        
        # Sum up P&L
        total_pnl = sum(t.pnl for t in all_trades if t.pnl is not None)
        
        return round(total_pnl, 2)
    
    def calculate_unrealized_pnl(self) -> float:
        """
        Calculate unrealized P&L from open positions
        
        Returns:
            Total unrealized P&L
        """
        positions = self.db.get_positions(active_only=True)
        
        total_unrealized = sum(p.pnl for p in positions if p.pnl is not None)
        
        return round(total_unrealized, 2)
    
    def get_daily_pnl(self, target_date: Optional[date] = None) -> float:
        """
        Get P&L for a specific day
        
        Args:
            target_date: Date to calculate (default: today)
        
        Returns:
            Daily P&L
        """
        if target_date is None:
            target_date = date.today()
        
        # Convert to datetime for comparison
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())
        
        # Get trades closed on this day
        closed_trades = self.db.get_trades(limit=1000)
        daily_trades = [
            t for t in closed_trades 
            if t.exit_time and start_dt <= t.exit_time <= end_dt
        ]
        
        daily_pnl = sum(t.pnl for t in daily_trades if t.pnl is not None)
        
        return round(daily_pnl, 2)
    
    def calculate_max_drawdown(self, trades: Optional[List[Trade]] = None) -> float:
        """
        Calculate maximum drawdown from peak
        
        Args:
            trades: List of trades (uses all if None)
        
        Returns:
            Maximum drawdown amount
        """
        if trades is None:
            trades = self.db.get_trades(status=TradeStatus.CLOSED, limit=1000)
        
        if not trades:
            return 0.0
        
        # Sort by exit time
        trades.sort(key=lambda t: t.exit_time if t.exit_time else datetime.now())
        
        # Calculate cumulative P&L
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in trades:
            if trade.pnl is not None:
                cumulative += trade.pnl
                if cumulative > peak:
                    peak = cumulative
                drawdown = peak - cumulative
                if drawdown > max_dd:
                    max_dd = drawdown
        
        return round(max_dd, 2)
    
    def get_performance_metrics(self, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        
        Args:
            start_date: Start date for calculation
            end_date: End date for calculation
        
        Returns:
            PerformanceMetrics object
        """
        # Get all closed trades
        all_trades = self.db.get_trades(status=TradeStatus.CLOSED, limit=1000)
        
        # Filter by date
        if start_date:
            all_trades = [t for t in all_trades if t.entry_time >= start_date]
        if end_date:
            all_trades = [t for t in all_trades if t.entry_time <= end_date]
        
        # Calculate metrics
        total_trades = len(all_trades)
        winning_trades = [t for t in all_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in all_trades if t.pnl and t.pnl < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        avg_profit = (sum(t.pnl for t in winning_trades) / win_count) if win_count > 0 else 0
        avg_loss = (sum(t.pnl for t in losing_trades) / loss_count) if loss_count > 0 else 0
        
        realized_pnl = sum(t.pnl for t in all_trades if t.pnl)
        unrealized_pnl = self.calculate_unrealized_pnl()
        total_pnl = realized_pnl + unrealized_pnl
        
        max_dd = self.calculate_max_drawdown(all_trades)
        
        total_capital = TRADING_CONFIG['initial_capital']
        roi = (total_pnl / total_capital * 100) if total_capital > 0 else 0
        
        metrics = PerformanceMetrics(
            date=end_date if end_date else datetime.now(),
            total_pnl=round(total_pnl, 2),
            realized_pnl=round(realized_pnl, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            trades_count=total_trades,
            win_count=win_count,
            loss_count=loss_count,
            win_rate=round(win_rate, 2),
            avg_profit=round(avg_profit, 2),
            avg_loss=round(avg_loss, 2),
            max_drawdown=max_dd,
            total_capital=total_capital,
            roi=round(roi, 2)
        )
        
        metrics.calculate_metrics()
        
        return metrics
    
    def get_pnl_series(self, days: int = 30) -> pd.DataFrame:
        """
        Get P&L time series for charting
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            DataFrame with date and cumulative P&L
        """
        # Get all closed trades
        trades = self.db.get_trades(status=TradeStatus.CLOSED, limit=1000)
        
        if not trades:
            return pd.DataFrame(columns=['Date', 'PnL', 'Cumulative_PnL'])
        
        # Sort by exit time
        trades.sort(key=lambda t: t.exit_time if t.exit_time else datetime.now())
        
        # Build series
        data = []
        cumulative = 0
        
        for trade in trades:
            if trade.exit_time and trade.pnl is not None:
                cumulative += trade.pnl
                data.append({
                    'Date': trade.exit_time.date(),
                    'PnL': trade.pnl,
                    'Cumulative_PnL': cumulative
                })
        
        if not data:
            return pd.DataFrame(columns=['Date', 'PnL', 'Cumulative_PnL'])
        
        df = pd.DataFrame(data)
        
        # Group by date
        df_grouped = df.groupby('Date').agg({
            'PnL': 'sum',
            'Cumulative_PnL': 'last'
        }).reset_index()
        
        # Filter last N days
        cutoff_date = date.today() - timedelta(days=days)
        df_grouped = df_grouped[df_grouped['Date'] >= cutoff_date]
        
        return df_grouped
    
    def get_strategy_performance(self) -> pd.DataFrame:
        """
        Get performance breakdown by strategy
        
        Returns:
            DataFrame with strategy-wise metrics
        """
        trades = self.db.get_trades(status=TradeStatus.CLOSED, limit=1000)
        strategies = self.db.get_all_strategies()
        
        strategy_data = []
        
        for strategy in strategies:
            strat_trades = [t for t in trades if t.strategy_id == strategy.id]
            
            if strat_trades:
                wins = [t for t in strat_trades if t.pnl and t.pnl > 0]
                losses = [t for t in strat_trades if t.pnl and t.pnl < 0]
                
                total_pnl = sum(t.pnl for t in strat_trades if t.pnl)
                win_rate = (len(wins) / len(strat_trades) * 100) if strat_trades else 0
                
                strategy_data.append({
                    'Strategy': strategy.name,
                    'Trades': len(strat_trades),
                    'Wins': len(wins),
                    'Losses': len(losses),
                    'Win_Rate': round(win_rate, 2),
                    'Total_PnL': round(total_pnl, 2),
                    'Avg_PnL': round(total_pnl / len(strat_trades), 2) if strat_trades else 0
                })
        
        return pd.DataFrame(strategy_data)
    
    def get_best_worst_trades(self, top_n: int = 5) -> Tuple[List[Trade], List[Trade]]:
        """
        Get top N best and worst trades
        
        Args:
            top_n: Number of trades to return
        
        Returns:
            Tuple of (best_trades, worst_trades)
        """
        trades = self.db.get_trades(status=TradeStatus.CLOSED, limit=1000)
        
        # Sort by P&L
        trades_with_pnl = [t for t in trades if t.pnl is not None]
        trades_with_pnl.sort(key=lambda t: t.pnl, reverse=True)
        
        best = trades_with_pnl[:top_n]
        worst = trades_with_pnl[-top_n:][::-1]  # Reverse to show worst first
        
        return best, worst
    
    def update_daily_performance(self):
        """Update performance metrics for today"""
        metrics = self.get_performance_metrics()
        self.db.save_performance(metrics)

# Singleton instance
_pnl_calculator = None

def get_pnl_calculator() -> PnLCalculator:
    """Get singleton P&L calculator instance"""
    global _pnl_calculator
    if _pnl_calculator is None:
        _pnl_calculator = PnLCalculator()
    return _pnl_calculator
