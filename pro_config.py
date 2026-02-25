import os
from datetime import time
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# ⚙️ SYSTEM SETTINGS
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
TEST_MODE = os.getenv("TEST_MODE", "True").lower() == "true"

# 🏛️ INSTITUTIONAL ALERT CHANNELS
TELEGRAM_CHANNELS = {
    "SENTIMENT": os.getenv("TG_CHANNEL_SENTIMENT", TELEGRAM_CHAT_ID),
    "INDEX_TRADE": os.getenv("TG_CHANNEL_INDEX", TELEGRAM_CHAT_ID),
    "STOCK_TRADE": os.getenv("TG_CHANNEL_STOCK", TELEGRAM_CHAT_ID),
    "REVERSAL": os.getenv("TG_CHANNEL_REVERSAL", TELEGRAM_CHAT_ID),
    "NEWS": os.getenv("TG_CHANNEL_NEWS", TELEGRAM_CHAT_ID)
}

REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501")

AUTH_URL = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={UPSTOX_API_KEY}&redirect_uri={REDIRECT_URI}"

# ==========================================
# 🏛 MARKET UNIVERSE
# ==========================================
SCAN_INDICES = ["NIFTY", "BANKNIFTY", "SENSEX"]  # Added SENSEX as requested

# User-requested NIFTY 50 Universe
NIFTY_50_STOCKS = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", 
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL", 
    "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", 
    "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", 
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC", 
    "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT", 
    "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC", 
    "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA", 
    "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS", "TECHM", 
    "TITAN", "ULTRACEMCO", "UPL", "WIPRO"
]

# ==========================================
# ⚖️ RISK & LIMITS
# ==========================================
DAILY_LIMITS = {
    "DIAMOND": 5,
    "TOP": 8,
    "BEST": 10,
    "GOOD": 15,
    "INDEX_BIAS": 10,
    "MEGA": 3
}

SUMMARY_INTERVAL = 900  # 15 mins
CANDLE_CYCLE = 300      # 5 mins

# ==========================================
# 📂 FILE PATHS
# ==========================================
data_dir = "data"
ALERTS_SENT_FILE = ".inst_alerts_sent.json"
INST_RESULTS_FILE = os.path.join(data_dir, "inst_scanner_results.json")
ACTIVE_SIGNALS_FILE = os.path.join(data_dir, "active_signals.json")
DAILY_STATS_FILE = ".daily_stats.json"

# ==========================================
# 🎨 UI & STYLES
# ==========================================
SIGNATURE = "\n👤 *PrimeSkillDevelopment CEO : MuthuKumar krishnan*"
