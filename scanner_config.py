
# ==========================================
# ⚙️ MASTER SCANNER CONFIGURATION
# ==========================================

# 🏦 INDICES TO MONITOR
SCAN_INDICES = ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"]

# 📊 NIFTY 50 UNIVERSE (Fully Customizable)
NIFTY_50_STOCKS = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "ITC", "KOTAKBANK", "LT", "SBIN", "BHARTIARTL",
    "AXISBANK", "BAJFINANCE", "HINDUNILVR", "ASIANPAINT", "MARUTI", "TITAN", "HCLTECH", "M&M", "SUNPHARMA", "ADANIENT",
    "TATAMOTORS", "ULTRACEMCO", "ONGC", "JSWSTEEL", "POWERGRID", "ADANIPORTS", "TATASTEEL", "NTPC", "GRASIM", "BAJAJFINSV",
    "HDFCLIFE", "INDUSINDBK", "SBILIFE", "WIPRO", "HINDALCO", "COALINDIA", "EICHERMOT", "BPCL", "NESTLEIND", "BRITANNIA",
    "TECHM", "DIVISLAB", "CIPLA", "TATACONSUM", "APOLLOHOSP", "HEROMOTOCO", "BAJAJ-AUTO", "DRREDDY", "BEL", "TRENT"
]

# 🕒 INTERVAL SETTINGS
SCAN_INTERVAL = 60         # Loop logic sleep (seconds)
CANDLE_CYCLE = 300         # Candle analysis cycle (5 mins)
SUMMARY_INTERVAL = 900     # Pulse Alert & Macro Sync (15 mins)
MOVERS_TTL = 300           # RS Ranking refresh (5 mins)

# 🎯 TRADE SENSITIVITY
BREAKOUT_BUFFER = 0.002    # 0.2% price confirmation
PRICE_EVENT_TRIGGER = 0.003 # 0.3% jump for immediate scan
MIN_SCORE_ALERT = 55       # Minimum institutional score for notification
DIAMOND_SCORE = 85         # Score for Diamond classification

# 🌎 GLOBAL MARKET BASKET
GLOBAL_SENTIMENT_SYMBOLS = {
    "NASDAQ": "^IXIC",
    "S&P 500": "^GSPC",
    "DOW JONES": "^DJI"
}

# 👤 BRANDING
CEO_NAME = "MuthuKumar Krishnan."
COMPANY_NAME = "Prime Skill Devlopment"
SIGNATURE = f"**{COMPANY_NAME}**\nCEO : {CEO_NAME}"
