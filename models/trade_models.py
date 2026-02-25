"""
Data models for F&O Options Trading System
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Literal, Dict, Any
from enum import Enum

class OptionType(Enum):
    CE = "CE"  # Call European
    PE = "PE"  # Put European

class StrategyType(Enum):
    LONG_CALL = "LONG_CALL"
    LONG_PUT = "LONG_PUT"
    BULL_CALL_SPREAD = "BULL_CALL_SPREAD"
    BEAR_PUT_SPREAD = "BEAR_PUT_SPREAD"
    LONG_STRADDLE = "LONG_STRADDLE"
    LONG_STRANGLE = "LONG_STRANGLE"
    IRON_CONDOR = "IRON_CONDOR"

class TradeStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    STOPPED = "STOPPED"  # Stop loss hit

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TrendType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    RANGE_BOUND = "RANGE_BOUND"

@dataclass
class Greeks:
    """Option Greeks"""
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)

@dataclass
class Strategy:
    """Trading Strategy Configuration"""
    name: str
    type: StrategyType
    risk_level: RiskLevel
    description: Optional[str] = None
    active: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['type'] = self.type.value
        data['risk_level'] = self.risk_level.value
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class Trade:
    """Individual Trade"""
    strategy_id: int
    symbol: str
    option_type: OptionType
    strike_price: float
    entry_price: float
    quantity: int
    exit_price: Optional[float] = None
    entry_time: datetime = field(default_factory=datetime.now)
    exit_time: Optional[datetime] = None
    status: TradeStatus = TradeStatus.OPEN
    pnl: Optional[float] = None
    fees: float = 0.0
    notes: Optional[str] = None
    id: Optional[int] = None
    
    # Additional fields for analysis
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['option_type'] = self.option_type.value
        data['status'] = self.status.value
        data['entry_time'] = self.entry_time.isoformat()
        if self.exit_time:
            data['exit_time'] = self.exit_time.isoformat()
        return data
    
    def calculate_pnl(self, current_price: Optional[float] = None) -> float:
        """Calculate P&L for this trade"""
        exit_px = current_price if current_price is not None else self.exit_price
        if exit_px is None:
            return 0.0
        
        # Long option: profit when price goes up
        gross_pnl = (exit_px - self.entry_price) * self.quantity
        net_pnl = gross_pnl - self.fees
        return round(net_pnl, 2)

@dataclass
class Position:
    """Current Open Position"""
    trade_id: int
    symbol: str
    option_type: OptionType
    strike_price: float
    quantity: int
    avg_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    greeks: Optional[Greeks] = None
    id: Optional[int] = None
    updated_at: Optional[datetime] = None
    
    # Risk metrics
    max_loss: Optional[float] = None
    max_profit: Optional[float] = None
    breakeven: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['option_type'] = self.option_type.value
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        if self.greeks:
            data['greeks'] = self.greeks.to_dict()
        return data
    
    def update_pnl(self):
        """Update P&L based on current price"""
        if self.current_price is not None:
            gross_pnl = (self.current_price - self.avg_price) * self.quantity
            self.pnl = round(gross_pnl, 2)

@dataclass
class PerformanceMetrics:
    """Daily/Periodic Performance Metrics"""
    date: datetime
    total_pnl: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    trades_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    total_capital: float = 100000.0
    roi: float = 0.0
    
    def calculate_metrics(self):
        """Recalculate derived metrics"""
        if self.trades_count > 0:
            self.win_rate = round((self.win_count / self.trades_count) * 100, 2)
        if self.total_capital > 0:
            self.roi = round((self.total_pnl / self.total_capital) * 100, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['date'] = self.date.isoformat()
        return data

@dataclass
class MarketCondition:
    """Market Analysis Result"""
    symbol: str
    spot_price: float
    trend: TrendType
    rsi: float
    adx: float
    iv: float
    iv_regime: str  # LOW, NORMAL, HIGH, VERY_HIGH
    support: Optional[float] = None
    resistance: Optional[float] = None
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    supertrend: Optional[float] = None
    signal: Optional[str] = None  # BUY, SELL, NEUTRAL
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['trend'] = self.trend.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class OptionContract:
    """Option Contract Details"""
    symbol: str
    option_type: OptionType
    strike: float
    expiry_date: datetime
    spot_price: float
    premium: float
    iv: float
    greeks: Greeks
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: int = 0
    open_interest: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['option_type'] = self.option_type.value
        data['expiry_date'] = self.expiry_date.isoformat()
        data['greeks'] = self.greeks.to_dict()
        return data

@dataclass
class StrategySignal:
    """Trading Signal from Strategy Engine"""
    strategy_type: StrategyType
    symbol: str
    action: str  # BUY, SELL, HOLD, CLOSE
    confidence: float
    entry_price: float
    stop_loss: float
    target: float
    position_size: int
    max_loss: float
    max_profit: float
    risk_reward: float
    market_condition: MarketCondition
    option_legs: list = field(default_factory=list)  # For multi-leg strategies
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['strategy_type'] = self.strategy_type.value
        data['market_condition'] = self.market_condition.to_dict()
        data['timestamp'] = self.timestamp.isoformat()
        return data
