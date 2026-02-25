"""
Database Manager for F&O Options Trading System
Handles all database operations using SQLite
"""
import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from config.config import DB_PATH
from models import (
    Strategy, Trade, Position, PerformanceMetrics,
    StrategyType, TradeStatus, OptionType, RiskLevel, Greeks
)

class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        with self.get_connection() as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
    
    # ==================== STRATEGY OPERATIONS ====================
    
    def get_all_strategies(self, active_only: bool = True) -> List[Strategy]:
        """Get all strategies"""
        query = "SELECT * FROM strategies"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY id"
        
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            
        strategies = []
        for row in rows:
            config = json.loads(row['config']) if row['config'] else {}
            strategy = Strategy(
                id=row['id'],
                name=row['name'],
                type=StrategyType[row['type']],
                description=row['description'],
                risk_level=RiskLevel[row['risk_level']],
                active=bool(row['active']),
                config=config,
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            strategies.append(strategy)
        
        return strategies
    
    def get_strategy_by_id(self, strategy_id: int) -> Optional[Strategy]:
        """Get strategy by ID"""
        strategies = self.get_all_strategies(active_only=False)
        for s in strategies:
            if s.id == strategy_id:
                return s
        return None
    
    # ==================== TRADE OPERATIONS ====================
    
    def save_trade(self, trade: Trade) -> int:
        """Save a new trade to database"""
        query = """
            INSERT INTO trades (
                strategy_id, symbol, option_type, strike_price, entry_price,
                exit_price, quantity, entry_time, exit_time, status,
                pnl, fees, notes, stop_loss, target, max_profit, max_loss
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                trade.strategy_id,
                trade.symbol,
                trade.option_type.value,
                trade.strike_price,
                trade.entry_price,
                trade.exit_price,
                trade.quantity,
                trade.entry_time.isoformat(),
                trade.exit_time.isoformat() if trade.exit_time else None,
                trade.status.value,
                trade.pnl,
                trade.fees,
                trade.notes,
                trade.stop_loss,
                trade.target,
                trade.max_profit,
                trade.max_loss
            ))
            trade_id = cursor.lastrowid
        
        return trade_id
    
    def update_trade(self, trade: Trade):
        """Update existing trade"""
        query = """
            UPDATE trades SET
                exit_price = ?, exit_time = ?, status = ?,
                pnl = ?, notes = ?
            WHERE id = ?
        """
        
        with self.get_connection() as conn:
            conn.execute(query, (
                trade.exit_price,
                trade.exit_time.isoformat() if trade.exit_time else None,
                trade.status.value,
                trade.pnl,
                trade.notes,
                trade.id
            ))
    
    def get_trades(self, 
                   symbol: Optional[str] = None,
                   status: Optional[TradeStatus] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: int = 100) -> List[Trade]:
        """Get trades with optional filters"""
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if start_date:
            query += " AND entry_time >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND entry_time <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY entry_time DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        
        trades = []
        for row in rows:
            trade = Trade(
                id=row['id'],
                strategy_id=row['strategy_id'],
                symbol=row['symbol'],
                option_type=OptionType[row['option_type']],
                strike_price=row['strike_price'],
                entry_price=row['entry_price'],
                exit_price=row['exit_price'],
                quantity=row['quantity'],
                entry_time=datetime.fromisoformat(row['entry_time']),
                exit_time=datetime.fromisoformat(row['exit_time']) if row['exit_time'] else None,
                status=TradeStatus[row['status']],
                pnl=row['pnl'],
                fees=row['fees'],
                notes=row['notes'],
                stop_loss=row['stop_loss'],
                target=row['target'],
                max_profit=row['max_profit'],
                max_loss=row['max_loss']
            )
            trades.append(trade)
        
        return trades
    
    def get_open_trades(self, symbol: Optional[str] = None) -> List[Trade]:
        """Get all open trades"""
        return self.get_trades(symbol=symbol, status=TradeStatus.OPEN)
    
    # ==================== POSITION OPERATIONS ====================
    
    def save_position(self, position: Position) -> int:
        """Save position to database"""
        query = """
            INSERT INTO positions (
                trade_id, symbol, option_type, strike_price, quantity,
                avg_price, current_price, pnl, delta, gamma, theta, vega, rho,
                max_loss, max_profit, breakeven, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        greeks = position.greeks
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                position.trade_id,
                position.symbol,
                position.option_type.value,
                position.strike_price,
                position.quantity,
                position.avg_price,
                position.current_price,
                position.pnl,
                greeks.delta if greeks else None,
                greeks.gamma if greeks else None,
                greeks.theta if greeks else None,
                greeks.vega if greeks else None,
                greeks.rho if greeks else None,
                position.max_loss,
                position.max_profit,
                position.breakeven,
                datetime.now().isoformat()
            ))
            position_id = cursor.lastrowid
        
        return position_id
    
    def update_position(self, position: Position):
        """Update position prices and P&L"""
        query = """
            UPDATE positions SET
                current_price = ?, pnl = ?,
                delta = ?, gamma = ?, theta = ?, vega = ?, rho = ?,
                updated_at = ?
            WHERE id = ?
        """
        
        greeks = position.greeks
        with self.get_connection() as conn:
            conn.execute(query, (
                position.current_price,
                position.pnl,
                greeks.delta if greeks else None,
                greeks.gamma if greeks else None,
                greeks.theta if greeks else None,
                greeks.vega if greeks else None,
                greeks.rho if greeks else None,
                datetime.now().isoformat(),
                position.id
            ))
    
    def get_positions(self, active_only: bool = True) -> List[Position]:
        """Get all positions"""
        query = "SELECT p.*, t.status FROM positions p JOIN trades t ON p.trade_id = t.id"
        if active_only:
            query += " WHERE t.status = 'OPEN'"
        query += " ORDER BY p.updated_at DESC"
        
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
        
        positions = []
        for row in rows:
            greeks = Greeks(
                delta=row['delta'] or 0.0,
                gamma=row['gamma'] or 0.0,
                theta=row['theta'] or 0.0,
                vega=row['vega'] or 0.0,
                rho=row['rho'] or 0.0
            )
            
            position = Position(
                id=row['id'],
                trade_id=row['trade_id'],
                symbol=row['symbol'],
                option_type=OptionType[row['option_type']],
                strike_price=row['strike_price'],
                quantity=row['quantity'],
                avg_price=row['avg_price'],
                current_price=row['current_price'],
                pnl=row['pnl'],
                greeks=greeks,
                max_loss=row['max_loss'],
                max_profit=row['max_profit'],
                breakeven=row['breakeven'],
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
            positions.append(position)
        
        return positions
    
    def delete_position(self, position_id: int):
        """Delete position (when trade is closed)"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM positions WHERE id = ?", (position_id,))
    
    # ==================== PERFORMANCE OPERATIONS ====================
    
    def save_performance(self, metrics: PerformanceMetrics):
        """Save or update daily performance metrics"""
        query = """
            INSERT OR REPLACE INTO performance (
                date, total_pnl, realized_pnl, unrealized_pnl,
                trades_count, win_count, loss_count, win_rate,
                avg_profit, avg_loss, max_drawdown, total_capital, roi
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            conn.execute(query, (
                metrics.date.date().isoformat(),
                metrics.total_pnl,
                metrics.realized_pnl,
                metrics.unrealized_pnl,
                metrics.trades_count,
                metrics.win_count,
                metrics.loss_count,
                metrics.win_rate,
                metrics.avg_profit,
                metrics.avg_loss,
                metrics.max_drawdown,
                metrics.total_capital,
                metrics.roi
            ))
    
    def get_performance_history(self, days: int = 30) -> List[PerformanceMetrics]:
        """Get performance history"""
        query = """
            SELECT * FROM performance
            ORDER BY date DESC
            LIMIT ?
        """
        
        with self.get_connection() as conn:
            rows = conn.execute(query, (days,)).fetchall()
        
        metrics_list = []
        for row in rows:
            metrics = PerformanceMetrics(
                date=datetime.fromisoformat(row['date']),
                total_pnl=row['total_pnl'],
                realized_pnl=row['realized_pnl'],
                unrealized_pnl=row['unrealized_pnl'],
                trades_count=row['trades_count'],
                win_count=row['win_count'],
                loss_count=row['loss_count'],
                win_rate=row['win_rate'],
                avg_profit=row['avg_profit'],
                avg_loss=row['avg_loss'],
                max_drawdown=row['max_drawdown'],
                total_capital=row['total_capital'],
                roi=row['roi']
            )
            metrics_list.append(metrics)
        
        return metrics_list
    
    # ==================== ALERT OPERATIONS ====================
    
    def save_alert(self, alert_type: str, message: str, symbol: Optional[str] = None, severity: str = "INFO"):
        """Save alert to database"""
        query = """
            INSERT INTO alerts (type, message, symbol, severity)
            VALUES (?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            conn.execute(query, (alert_type, message, symbol, severity))
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        query = """
            SELECT * FROM alerts
            ORDER BY created_at DESC
            LIMIT ?
        """
        
        with self.get_connection() as conn:
            rows = conn.execute(query, (limit,)).fetchall()
        
        return [dict(row) for row in rows]
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_trade_statistics(self) -> Dict[str, Any]:
        """Get overall trade statistics"""
        query = """
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN status = 'CLOSED' AND pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN status = 'CLOSED' AND pnl < 0 THEN 1 ELSE 0 END) as losses,
                AVG(CASE WHEN status = 'CLOSED' AND pnl > 0 THEN pnl END) as avg_win,
                AVG(CASE WHEN status = 'CLOSED' AND pnl < 0 THEN pnl END) as avg_loss,
                SUM(CASE WHEN status = 'CLOSED' THEN pnl ELSE 0 END) as total_realized_pnl,
                MAX(pnl) as best_trade,
                MIN(pnl) as worst_trade
            FROM trades
        """
        
        with self.get_connection() as conn:
            row = conn.execute(query).fetchone()
        
        stats = dict(row)
        if stats['total_trades'] > 0:
            closed_trades = stats['wins'] + stats['losses']
            stats['win_rate'] = (stats['wins'] / closed_trades * 100) if closed_trades > 0 else 0
        else:
            stats['win_rate'] = 0
        
        return stats
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old market data and alerts"""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        with self.get_connection() as conn:
            conn.execute("DELETE FROM market_data WHERE timestamp < ?", (cutoff_date.isoformat(),))
            conn.execute("DELETE FROM alerts WHERE created_at < ? AND triggered = 1", (cutoff_date.isoformat(),))

# Singleton instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
