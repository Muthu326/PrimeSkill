import os
import json
import time
from datetime import datetime
from pro_config import ALERTS_SENT_FILE, ACTIVE_SIGNALS_FILE, DAILY_STATS_FILE, DAILY_LIMITS

def load_json(filepath, default_val=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return default_val if default_val is not None else {}
    return default_val if default_val is not None else {}

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, default=str)

def load_alerts_sent():
    data = load_json(ALERTS_SENT_FILE, {})
    now = time.time()
    # Clean old alerts (older than 2 hours)
    return {k: v for k, v in data.items() if (now - (v.get('ts', 0) if isinstance(v, dict) else v)) < 7200}

def save_alerts_sent(data):
    save_json(ALERTS_SENT_FILE, data)

def load_active_signals():
    return load_json(ACTIVE_SIGNALS_FILE, [])

def save_active_signals(signals):
    save_json(ACTIVE_SIGNALS_FILE, signals)

def load_daily_stats():
    today = datetime.now().strftime('%Y-%m-%d')
    stats = load_json(DAILY_STATS_FILE, None)
    if stats and stats.get('date') == today:
        return stats
    return {'date': today, 'counts': {k: 0 for k in DAILY_LIMITS}}

def save_daily_stats(stats):
    save_json(DAILY_STATS_FILE, stats)

def get_friendly_name(symbol):
    if not symbol: return "N/A"
    symbol = str(symbol).strip().upper()
    overrides = {
        "HDFCBANK": "HDFC Bank", "RELIANCE": "Reliance", "SBIN": "SBI", "AXISBANK": "Axis Bank",
        "ICICIBANK": "ICICI Bank", "SUNPHARMA": "Sun Pharma", "TATASTEEL": "Tata Steel",
        "BHARTIARTL": "Airtel", "KOTAKBANK": "Kotak Bank", "M&M": "Mahindra & Mahindra",
        "BAJFINANCE": "Bajaj Finance", "BAJAJFINSV": "Bajaj Finserv", "MARUTI": "Maruti Suzuki",
        "ADANIENT": "Adani Ent", "ADANIPORTS": "Adani Ports", "TITAN": "Titan", "HAL": "HAL",
        "ASIANPAINT": "Asian Paints", "ULTRACEMCO": "UltraTech Cement", "RECLTD": "REC Ltd",
        "PFC": "PFC Ltd", 
        "NIFTY": "Nifty 50", "BANKNIFTY": "Bank Nifty", "SENSEX": "Sensex",
        "FINNIFTY": "Fin Nifty", "MIDCAPNIFTY": "Midcap Nifty",
        "^NSEI": "Nifty 50", "^NSEBANK": "Bank Nifty", "^BSESN": "Sensex",
    }
    return overrides.get(symbol, symbol.title())

def save_inst_results(data, elite_top_5=None, index_picks=None):
    from pro_config import INST_RESULTS_FILE
    from utils.cache_manager import ScanCacheManager
    try:
        # Save to main results file
        with open(INST_RESULTS_FILE, 'w') as f:
            json.dump(data, f, default=str)
        
        # Sync with Quick Scan Viewer
        cache_manager = ScanCacheManager()
        
        formatted_diamond = []
        if elite_top_5:
            for d in elite_top_5:
                formatted_diamond.append({
                    "Stock": d.get('display_name', d.get('symbol', 'N/A')),
                    "Price": d.get('spot', 0),
                    "Entry": d.get('premium', 0),
                    "SL": d.get('stop_loss', 0),
                    "Target": d.get('target', 0),
                    "Conf": d.get('score', 0),
                    "Strike": d.get('strike', ''),
                    "Type": d.get('type', ''),
                    "Signal": f"BUY {d.get('type', '')}"
                })
        
        # Extract list if data is dict summary
        scan_list = data.get("all", data) if isinstance(data, dict) else data
        
        cache_manager.save_scan_results(
            scan_data=scan_list,
            index_picks=index_picks or [],
            diamond_picks=formatted_diamond
        )
    except Exception as e:
        print(f"Error saving results: {e}")

def is_new_5min_candle():
    """📊 5-Min Candle Sync Properly"""
    from datetime import datetime
    return datetime.now().minute % 5 == 0
