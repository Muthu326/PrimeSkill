-- F&O Options Trading System Database Schema
-- SQLite Database

-- Strategies Configuration Table
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    risk_level TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trades Table
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER,
    symbol TEXT NOT NULL,
    option_type TEXT NOT NULL,
    strike_price REAL NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    quantity INTEGER NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    status TEXT DEFAULT 'OPEN',
    pnl REAL,
    fees REAL DEFAULT 0,
    notes TEXT,
    stop_loss REAL,
    target REAL,
    max_profit REAL,
    max_loss REAL,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

-- CREATE INDEX ON trades FOR FASTER QUERIES
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time);

-- Positions Table (Current Active Positions)
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    option_type TEXT NOT NULL,
    strike_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    avg_price REAL NOT NULL,
    current_price REAL,
    pnl REAL,
    delta REAL,
    gamma REAL,
    theta REAL,
    vega REAL,
    rho REAL,
    max_loss REAL,
    max_profit REAL,
    breakeven REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trade_id) REFERENCES trades(id)
);

CREATE INDEX IF NOT EXISTS idx_positions_trade_id ON positions(trade_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    total_pnl REAL DEFAULT 0,
    realized_pnl REAL DEFAULT 0,
    unrealized_pnl REAL DEFAULT 0,
    trades_count INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    loss_count INTEGER DEFAULT 0,
    win_rate REAL DEFAULT 0,
    avg_profit REAL DEFAULT 0,
    avg_loss REAL DEFAULT 0,
    max_drawdown REAL DEFAULT 0,
    total_capital REAL DEFAULT 100000,
    roi REAL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_performance_date ON performance(date);

-- Market Data Cache Table
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    change_value REAL,
    change_percent REAL,
    high REAL,
    low REAL,
    volume INTEGER,
    iv REAL,
    rsi REAL,
    adx REAL,
    ema20 REAL,
    ema50 REAL,
    trend TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    symbol TEXT,
    severity TEXT DEFAULT 'INFO',
    triggered BOOLEAN DEFAULT 0,
    sent_telegram BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- Trade Signals Table (Strategy Recommendations)
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    confidence REAL NOT NULL,
    entry_price REAL,
    stop_loss REAL,
    target REAL,
    position_size INTEGER,
    risk_reward REAL,
    executed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_executed ON signals(executed);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);

-- Insert default strategies
INSERT OR IGNORE INTO strategies (id, name, type, description, risk_level, config) VALUES
(1, 'Long Call', 'LONG_CALL', 'Bullish strategy - Buy call option expecting price rise', 'MEDIUM', '{}'),
(2, 'Long Put', 'LONG_PUT', 'Bearish strategy - Buy put option expecting price fall', 'MEDIUM', '{}'),
(3, 'Bull Call Spread', 'BULL_CALL_SPREAD', 'Moderately bullish - Buy call, sell higher call', 'LOW', '{}'),
(4, 'Bear Put Spread', 'BEAR_PUT_SPREAD', 'Moderately bearish - Buy put, sell lower put', 'LOW', '{}'),
(5, 'Long Straddle', 'LONG_STRADDLE', 'High volatility play - Buy ATM call and put', 'HIGH', '{}'),
(6, 'Long Strangle', 'LONG_STRANGLE', 'Very high volatility - Buy OTM call and put', 'HIGH', '{}'),
(7, 'Iron Condor', 'IRON_CONDOR', 'Range-bound strategy - Sell credit spread on both sides', 'MEDIUM', '{}');
