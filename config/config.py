"""
Configuration file for F&O Options Trading System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "trades.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Trading Configuration
TRADING_CONFIG = {
    "initial_capital": 100000,  # Starting capital in INR
    "max_position_size": 0.20,  # Max 20% of capital per position
    "max_daily_loss": 0.02,     # Max 2% daily loss
    "max_positions": 5,         # Maximum concurrent positions
    "default_quantity": 1,      # Default lot size
    "brokerage_per_lot": 20,    # Brokerage per lot (INR)
    "stt_percent": 0.0005,      # STT 0.05% on sell side
    "exchange_charges": 0.0003, # Exchange charges 0.03%
}

# Risk Management
RISK_LIMITS = {
    "max_loss_per_trade": 0.05,     # Max 5% loss per trade
    "stop_loss_percent": 0.40,      # Stop loss at 40% of premium
    "target_profit_percent": 0.80,  # Target at 80% profit
    "trailing_stop_percent": 0.20,  # Trailing stop 20%
}

# Strategy Configuration
STRATEGY_PARAMS = {
    "LONG_CALL": {
        "min_rsi": 40,
        "max_rsi": 60,
        "min_adx": 25,
        "trend": "BULLISH",
        "iv_regime": "LOW_TO_NORMAL",
        "strike_selection": "ATM_TO_OTM1",  # ATM or 1 strike OTM
    },
    "LONG_PUT": {
        "min_rsi": 40,
        "max_rsi": 60,
        "min_adx": 25,
        "trend": "BEARISH",
        "iv_regime": "LOW_TO_NORMAL",
        "strike_selection": "ATM_TO_OTM1",
    },
    "BULL_CALL_SPREAD": {
        "min_rsi": 45,
        "trend": "MODERATELY_BULLISH",
        "iv_regime": "HIGH",
        "buy_strike": "ATM",
        "sell_strike": "OTM2",  # 2 strikes OTM
    },
    "BEAR_PUT_SPREAD": {
        "max_rsi": 55,
        "trend": "MODERATELY_BEARISH",
        "iv_regime": "HIGH",
        "buy_strike": "ATM",
        "sell_strike": "OTM2",
    },
    "LONG_STRADDLE": {
        "min_rsi": 45,
        "max_rsi": 55,
        "trend": "NEUTRAL",
        "iv_regime": "LOW",
        "expected_move": "HIGH",
        "strike_selection": "ATM",
    },
    "LONG_STRANGLE": {
        "trend": "NEUTRAL",
        "iv_regime": "LOW",
        "expected_move": "VERY_HIGH",
        "call_strike": "OTM1",
        "put_strike": "OTM1",
    },
    "IRON_CONDOR": {
        "trend": "RANGE_BOUND",
        "iv_regime": "HIGH",
        "range_low": "OTM2",
        "range_high": "OTM2",
        "wing_width": 1,  # 1 strike width for wings
    },
}

# Telegram Configuration (from existing scanner)
TELEGRAM_CONFIG = {
    "token": os.getenv("TELEGRAM_TOKEN"),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
}

# Market Data
SYMBOLS = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE",
    "MIDCPNIFTY": "NIFTY_MID_SELECT",
    "SENSEX": "^BSESN",
}

# Option Chain Parameters
OPTION_CHAIN_CONFIG = {
    "strikes_above": 10,    # Strikes above spot
    "strikes_below": 10,    # Strikes below spot
    "strike_gap": {
        "NIFTY": 50,
        "BANKNIFTY": 100,
        "FINNIFTY": 50,
        "MIDCAPNIFTY": 25,
        "SENSEX": 100,
    }
}

# Technical Indicator Parameters
INDICATOR_PARAMS = {
    "ema_fast": 20,
    "ema_slow": 50,
    "ema_trend": 200,
    "rsi_period": 14,
    "adx_period": 14,
    "atr_period": 14,
    "supertrend_period": 10,
    "supertrend_multiplier": 3,
    "support_resistance_period": 20,
}

# IV Regime Thresholds
IV_THRESHOLDS = {
    "LOW": 15,
    "NORMAL": 25,
    "HIGH": 35,
    "VERY_HIGH": 50,
}

# Expiry Settings
EXPIRY_CONFIG = {
    "min_days_to_expiry": 2,   # Don't trade if < 2 days to expiry
    "max_days_to_expiry": 30,  # Don't trade if > 30 days to expiry
    "preferred_days": 7,       # Prefer weekly expiry
}

# Black-Scholes Parameters
BS_PARAMS = {
    "risk_free_rate": 0.06,  # 6% risk-free rate (India)
    "dividend_yield": 0.01,  # 1% dividend yield
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    "auto_refresh_interval": 30,  # seconds
    "chart_height": 400,
    "mobile_breakpoint": 768,
}

# Alert Thresholds
ALERT_CONFIG = {
    "profit_alert": 0.50,      # Alert at 50% profit
    "loss_alert": 0.30,        # Alert at 30% loss
    "greek_threshold": {
        "delta": 0.70,         # Alert if position delta > 0.70
        "gamma": 0.10,         # Alert if gamma > 0.10
    }
}

# Standard Stock Lists
NIFTY_50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TATAPOWER.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NESTLEIND.NS","NTPC.NS","POWERGRID.NS","M&M.NS","HCLTECH.NS","TATASTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","BAJAJFINSV.NS","TECHM.NS","ONGC.NS","COALINDIA.NS","JSWSTEEL.NS","BPCL.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","APOLLOHOSP.NS","TATACONSUM.NS","SBILIFE.NS","HDFCLIFE.NS","BAJAJ-AUTO.NS","INDUSINDBK.NS","HINDALCO.NS","UPL.NS","LTIM.NS"]
SENSEX = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TATAPOWER.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NESTLEIND.NS","NTPC.NS","POWERGRID.NS","M&M.NS","HCLTECH.NS","TATASTEEL.NS","TECHM.NS","BAJAJFINSV.NS","INDUSINDBK.NS","JSWSTEEL.NS"]
BANKNIFTY = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","INDUSINDBK.NS","BANDHANBNK.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","PNB.NS","BANKBARODA.NS","AUBANK.NS"]
FINNIFTY = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS","MUTHOOTFIN.NS","CHOLAFIN.NS","ICICIGI.NS","SBICARD.NS","PFC.NS","RECLTD.NS","SHRIRAMFIN.NS","M&MFIN.NS","INDUSINDBK.NS","PNB.NS"]
MIDCAPNIFTY = ["MPHASIS.NS","VOLTAS.NS","PETRONET.NS","ABCAPITAL.NS","ASTRAL.NS","AUROPHARMA.NS","BATAINDIA.NS","CANBK.NS","COFORGE.NS","CONCOR.NS","CUB.NS","CUMMINSIND.NS","ESCORTS.NS","GMRINFRA.NS","GODREJPROP.NS","IPCALAB.NS","JUBLFOOD.NS","L&TFH.NS","LICHSGFIN.NS","MRF.NS","MFSL.NS","NAM-INDIA.NS","NAVINFLUOR.NS","OBEROIRLTY.NS","PIIND.NS"]
# Standard Stock Lists
NIFTY_50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TATAPOWER.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NESTLEIND.NS","NTPC.NS","POWERGRID.NS","M&M.NS","HCLTECH.NS","TATASTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","BAJAJFINSV.NS","TECHM.NS","ONGC.NS","COALINDIA.NS","JSWSTEEL.NS","BPCL.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","APOLLOHOSP.NS","TATACONSUM.NS","SBILIFE.NS","HDFCLIFE.NS","BAJAJ-AUTO.NS","INDUSINDBK.NS","HINDALCO.NS","UPL.NS","LTIM.NS"]
SENSEX = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TATAPOWER.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NESTLEIND.NS","NTPC.NS","POWERGRID.NS","M&M.NS","HCLTECH.NS","TATASTEEL.NS","TECHM.NS","BAJAJFINSV.NS","INDUSINDBK.NS","JSWSTEEL.NS"]
BANKNIFTY = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","INDUSINDBK.NS","BANDHANBNK.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","PNB.NS","BANKBARODA.NS","AUBANK.NS"]
FINNIFTY = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS","MUTHOOTFIN.NS","CHOLAFIN.NS","ICICIGI.NS","SBICARD.NS","PFC.NS","RECLTD.NS","SHRIRAMFIN.NS","M&MFIN.NS","INDUSINDBK.NS","PNB.NS"]
MIDCAPNIFTY = ["MPHASIS.NS","VOLTAS.NS","PETRONET.NS","ABCAPITAL.NS","ASTRAL.NS","AUROPHARMA.NS","BATAINDIA.NS","CANBK.NS","COFORGE.NS","CONCOR.NS","CUB.NS","CUMMINSIND.NS","ESCORTS.NS","GMRINFRA.NS","GODREJPROP.NS","IPCALAB.NS","JUBLFOOD.NS","L&TFH.NS","LICHSGFIN.NS","MRF.NS","MFSL.NS","NAM-INDIA.NS","NAVINFLUOR.NS","OBEROIRLTY.NS","PIIND.NS"]

STOCK_NAME_MAP = {
    "INDIANB": "Indian Bank", "UNIONBANK": "Union Bank Of India", "ADANIPORTS": "Adani Ports", 
    "AMBER": "Amber Enterprises", "CUMMINSIND": "Cummins India", "POLICYBZR": "PB Fintech", 
    "AXISBANK": "Axis Bank", "HDFCLIFE": "HDFC Life", "PNB": "Punjab National Bank", 
    "BHARATFORG": "Bharat Forge", "SBILIFE": "SBI Life", "ICICIPRULI": "ICICI Pru Life", 
    "CHOLAFIN": "Cholamandalam", "MFSL": "Max Financial", "CANBK": "Canara Bank", 
    "KOTAKBANK": "Kotak Bank", "POWERINDIA": "Hitachi Energy", "TATACONSUM": "Tata Consumer", 
    "BANKBARODA": "Bank Of Baroda", "HDFCBANK": "HDFC Bank", "LUPIN": "Lupin", 
    "ICICIGI": "ICICI Lombard", "IOC": "Indian Oil", "EICHERMOT": "Eicher Motors", 
    "HINDUNILVR": "Hindustan Unilever", "ADANIENT": "Adani Enterprises", "NESTLEIND": "Nestle India", 
    "BANKINDIA": "Bank Of India", "BPCL": "Bharat Petroleum", "HINDPETRO": "HPCL", 
    "TVSMOTOR": "TVS Motor", "SBIN": "State Bank Of India", "MAXHEALTH": "Max Healthcare", 
    "DRREDDY": "Dr. Reddy's", "ADANIGREEN": "Adani Green", "FORTIS": "Fortis Healthcare", 
    "ASHOKLEY": "Ashok Leyland", "SIEMENS": "Siemens Limited", "MUTHOOTFIN": "Muthoot Finance", 
    "KFINTECH": "KFin Tech", "POWERGRID": "Power Grid", "SONACOMS": "Sona BLW", 
    "CONCOR": "Container Corp", "M&M": "Mahindra & Mahindra", "TORNTPHARM": "Torrent Pharma", 
    "DALBHARAT": "Dalmia Bharat", "SHRIRAMFIN": "Shriram Finance", "HDFCAMC": "HDFC AMC", 
    "GODREJCP": "Godrej Consumer", "JSWSTEEL": "JSW Steel", "GRASIM": "Grasim Industries", 
    "HINDZINC": "Hindustan Zinc", "BHARTIARTL": "Bharti Airtel", "SHREECEM": "Shree Cements", 
    "UNITDSPR": "United Spirits", "PAGEIND": "Page Industries", "BAJAJHLDNG": "Bajaj Holdings", 
    "ZYDUSLIFE": "Zydus Life", "DELHIVERY": "Delhivery Ltd", "LICI": "LIC", 
    "TORNTPOWER": "Torrent Power", "ICICIBANK": "ICICI Bank", "LTF": "L&T Finance", 
    "BAJFINANCE": "Bajaj Finance", "GMRAIRPORT": "GMR Airports", "MARICO": "Marico Limited", 
    "MARUTI": "Maruti Suzuki", "PIDILITIND": "Pidilite Industries", "CGPOWER": "CG Power", 
    "PFC": "Power Finance", "BAJAJ-AUTO": "Bajaj Auto", "AUROPHARMA": "Aurobindo Pharma", 
    "APOLLOHOSP": "Apollo Hospitals", "KEI": "Kei Industries", "ABCAPITAL": "Aditya Birla Capital", 
    "TITAN": "Titan Company", "PAYTM": "Paytm", "HEROMOTOCO": "Hero Motocorp", 
    "PIIND": "PI Industries", "PHOENIXLTD": "Phoenix Mills", "TMPV": "Tata Motors PV", 
    "360ONE": "360 ONE", "LT": "Larsen & Toubro", "PRESTIGE": "Prestige Estates", 
    "NTPC": "NTPC Limited", "PPLPHARMA": "Piramal Pharma", "BANDHANBNK": "Bandhan Bank", 
    "RELIANCE": "Reliance Industries", "TATAPOWER": "Tata Power", "VBL": "Varun Beverages", 
    "CDSL": "CDSL", "MANAPPURAM": "Manappuram Finance", "AMBUJACEM": "Ambuja Cements", 
    "NYKAA": "Nykaa", "MANKIND": "Mankind Pharma", "LODHA": "Lodha Developers", 
    "SBICARD": "SBI Cards", "ALKEM": "Alkem Laboratories", "ULTRACEMCO": "UltraTech Cement", 
    "SUPREMEIND": "Supreme Industries", "CAMS": "CAMS", "COLPAL": "Colgate Palmolive", 
    "ASIANPAINT": "Asian Paints", "MCX": "MCX India", "BLUESTARCO": "Blue Star", 
    "KALYANKJIL": "Kalyan Jewellers", "ADANIENSOL": "Adani Energy", "BOSCHLTD": "Bosch Limited", 
    "DIVISLAB": "Divi's Labs", "APLAPOLLO": "APL Apollo", "DABUR": "Dabur India", 
    "POLYCAB": "Polycab India", "CROMPTON": "Crompton Greaves", "RVNL": "RVNL", 
    "PETRONET": "Petronet LNG", "LICHSGFIN": "LIC Housing", "SUNPHARMA": "Sun Pharma", 
    "VOLTAS": "Voltas Limited", "BIOCON": "Biocon Limited", "ASTRAL": "Astral Ltd", 
    "VEDL": "Vedanta Limited", "NBCC": "NBCC India", "BHEL": "BHEL", 
    "JINDALSTEL": "Jindal Steel", "HUDCO": "HUDCO", "FEDERALBNK": "Federal Bank", 
    "INDHOTEL": "Indian Hotels", "SOLARINDS": "Solar Industries", "GODREJPROP": "Godrej Properties", 
    "BAJAJFINSV": "Bajaj Finserv", "NATIONALUM": "NALCO", "IRFC": "IRFC", 
    "HAVELLS": "Havells India", "INDIGO": "Interglobe Aviation", "EXIDEIND": "Exide Industries", 
    "IEX": "IEX", "ANGELONE": "Angel One", "WAAREEENER": "Waaree Energies", 
    "RECLTD": "REC Ltd", "BRITANNIA": "Britannia Industries", "JUBLFOOD": "Jubilant Food", 
    "COALINDIA": "Coal India", "TATASTEEL": "Tata Steel", "PNBHOUSING": "PNB Housing", 
    "DLF": "DLF Limited", "LAURUSLABS": "Laurus Labs", "ITC": "ITC Limited", 
    "UNOMINDA": "Uno Minda", "YESBANK": "Yes Bank", "DMART": "Avenue Supermarts", 
    "BSE": "BSE", "SUZLON": "Suzlon Energy", "MOTHERSON": "Samvardhana Motherson", 
    "GLENMARK": "Glenmark Pharma", "PREMIERENE": "Premier Energies", "PGEL": "PG Electroplast", 
    "NHPC": "NHPC Limited", "PATANJALI": "Patanjali Foods", "TATATECH": "Tata Technologies", 
    "SRF": "SRF Limited", "JSWENERGY": "JSW Energy", "BEL": "Bharat Electronics", 
    "HINDALCO": "Hindalco", "IRCTC": "IRCTC", "SAIL": "SAIL", "TRENT": "Trent Limited", 
    "JIOFIN": "Jio Financial", "IREDA": "IREDA", "INDUSTOWER": "Indus Towers", 
    "GAIL": "GAIL", "NAUKRI": "Info Edge", "TCS": "TCS", "OFSS": "Oracle Financial", 
    "ABB": "ABB India", "OBEROIRLTY": "Oberoi Realty", "CIPLA": "Cipla Limited", 
    "SAMMAANCAP": "Sammaan Capital", "PERSISTENT": "Persistent Systems", "HCLTECH": "HCL Tech", 
    "SYNGENE": "Syngene International", "MAZDOCK": "Mazagon Dock", "INDUSINDBK": "IndusInd Bank", 
    "ETERNAL": "Eternal Ltd", "NMDC": "NMDC Limited", "KAYNES": "Kaynes Tech", 
    "NUVAMA": "Nuvama Wealth", "OIL": "Oil India", "SWIGGY": "Swiggy", "TECHM": "Tech Mahindra", 
    "TIINDIA": "Tube Investments", "TATAELXSI": "Tata Elxsi", "RBLBANK": "RBL Bank", 
    "IDEA": "Vodafone Idea", "KPITTECH": "KPIT Tech", "LTIM": "LTI Mindtree", 
    "ONGC": "ONGC", "INFY": "Infosys", "INOXWIND": "Inox Wind", "DIXON": "Dixon Tech", 
    "MPHASIS": "Mphasis", "WIPRO": "Wipro Limited", "HAL": "HAL", "BDL": "BDL", 
    "COFORGE": "Coforge", "AUBANK": "AU Bank", "UPL": "UPL Limited", "IDFCFIRSTB": "IDFC First Bank"
}

ALL_FO_STOCKS = [f"{s}.NS" for s in STOCK_NAME_MAP.keys()]


INDEX_MAP = {
    "ALL F&O": {"ticker": "^NSEI", "google_sym": "NIFTY_50", "stocks": ALL_FO_STOCKS},
    "NIFTY 50": {"ticker": "^NSEI", "google_sym": "NIFTY_50", "stocks": NIFTY_50},
    "SENSEX": {"ticker": "^BSESN", "google_sym": "SENSEX", "stocks": SENSEX},
    "BANKNIFTY": {"ticker": "^NSEBANK", "google_sym": "NIFTY_BANK", "stocks": BANKNIFTY},
    "FINNIFTY": {"ticker": "NIFTY_FIN_SERVICE.NS", "google_sym": "NIFTY_FIN_SERVICE", "stocks": FINNIFTY},
    "MIDCAPNIFTY": {"ticker": "NIFTY_MID_SELECT.NS", "google_sym": "NIFTY_MID_SELECT", "stocks": MIDCAPNIFTY},
}

HEAVYWEIGHTS = ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "AXISBANK.NS"]

INDEX_WEIGHTS = {
    "NIFTY": {
        "RELIANCE.NS": 9.3, "HDFCBANK.NS": 9.1, "ICICIBANK.NS": 7.9, "INFY.NS": 5.9, 
        "TCS.NS": 4.1, "ITC.NS": 3.9, "SBIN.NS": 3.3, "BHARTIARTL.NS": 3.2, 
        "LT.NS": 3.1, "AXISBANK.NS": 3.0
    },
    "BANKNIFTY": {
        "HDFCBANK.NS": 29.0, "ICICIBANK.NS": 23.0, "SBIN.NS": 10.0, 
        "AXISBANK.NS": 9.5, "KOTAKBANK.NS": 9.0, "INDUSINDBK.NS": 6.5
    },
    "SENSEX": {
        "HDFCBANK.NS": 12.5, "RELIANCE.NS": 11.5, "ICICIBANK.NS": 9.5, 
        "INFY.NS": 8.0, "LT.NS": 4.8, "TCS.NS": 4.5, "ITC.NS": 4.2, 
        "AXISBANK.NS": 3.8, "KOTAKBANK.NS": 3.5, "SBIN.NS": 3.2
    }
}

TRADING_QUOTES = [
    "The trend is your friend until it bends.",
    "Trading is not about being right, it's about making money.",
    "Cut your losses short and let your profits run.",
    "Risk comes from not knowing what you're doing.",
    "Every trade is a lesson. Some are just more expensive than others.",
    "The stock market is a device for transferring money from the impatient to the patient.",
    "Never risk more than you can afford to lose.",
    "Confidence comes from discipline and training.",
    "Trade what you see, not what you think."
]
