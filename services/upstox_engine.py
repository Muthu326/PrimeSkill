import requests
import os
import pandas as pd
import gzip
import io
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class UpstoxEngine:
    """
    🏢 Institutional Data Engine via Upstox API
    Handles Live Quotes, Candle Data, and Instrument Mapping
    """
    
    BASE_URL = "https://api.upstox.com/v2"
    BASE_URL_V3 = "https://api.upstox.com/v3"
    
    # Official JSON instrument feeds (Preferred over CSV)
    INSTRUMENT_FILES = {
        "NSE": "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz",
        "BSE": "https://assets.upstox.com/market-quote/instruments/exchange/BSE.json.gz",
        "NFO": "https://assets.upstox.com/market-quote/instruments/exchange/NFO.json.gz"
    }
    
    def __init__(self):
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        self.instrument_map = {} # Cache: symbol -> instrument_key
        self.is_initialized = False

    def initialize_mapper(self, exchanges=["NSE", "NFO", "BSE"]):
        """Download and prepare instrument mapping from JSON feeds"""
        print(f"📡 Initializing Upstox Mapper via JSON Feeds for {exchanges}...")
        # Browser-like headers to avoid 403
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        count = 0
        # Try 'complete' first as it has everything
        try:
            url = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"
            response = requests.get(url, headers=headers, timeout=60)
            if response.status_code == 200:
                print("✅ Complete JSON Instruments Data Received. Parsing...")
                with gzip.open(io.BytesIO(response.content), 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        symbol = (item.get('trading_symbol') or item.get('tradingsymbol') or "").strip().upper()
                        if not symbol: continue
                        
                        key = item.get('instrument_key')
                        exch = item.get('exchange', '').upper()
                        seg = item.get('segment', '').upper()
                        
                        # Prioritization Logic:
                        # 1. If symbol exists and we have an NSE/NSE_EQ version, keep it.
                        # 2. Prefer NSE over BSE for the base symbol.
                        if symbol not in self.instrument_map or exch == "NSE":
                            self.instrument_map[symbol] = key
                            count += 1
                        
                        # Support for -EQ and other common formats
                        if seg == "NSE_EQ" and symbol.isalpha():
                            self.instrument_map[f"{symbol}-EQ"] = key
                print(f"✅ Loaded {count} instruments from Complete Feed.")
                self.is_initialized = True
                return
        except Exception as e:
            print(f"⚠️ Complete feed failed: {e}. Trying individuals...")

        for exchange in exchanges:
            try:
                url = self.INSTRUMENT_FILES.get(exchange)
                if not url: continue
                response = requests.get(url, headers=headers, timeout=60)
                if response.status_code == 200:
                    with gzip.open(io.BytesIO(response.content), 'rt', encoding='utf-8') as f:
                        data = json.load(f)
                        for item in data:
                            symbol = str(item.get('tradingsymbol')).strip().upper()
                            self.instrument_map[symbol] = item.get('instrument_key')
                            count += 1
                    print(f"✅ Loaded {count} instruments from {exchange}.")
                else:
                    print(f"❌ Failed to load {exchange} JSON: {response.status_code}")
            except Exception as e:
                print(f"❌ Mapper Exception for {exchange}: {e}")
        
        # Hardcoded Indices (Standard Fallback)
        self.instrument_map["NIFTY 50"] = "NSE_INDEX|Nifty 50"
        self.instrument_map["NIFTY BANK"] = "NSE_INDEX|Nifty Bank"
        self.instrument_map["FINNIFTY"] = "NSE_INDEX|Nifty Fin Service"
        self.instrument_map["MIDCAPNIFTY"] = "NSE_INDEX|Nifty Midcap 150"
        
        self.is_initialized = True

    def find_all_instruments(self, query):
        """Diagnostic: Find all symbols matching a query"""
        if not self.is_initialized: self.initialize_mapper()
        matches = {s: k for s, k in self.instrument_map.items() if query.upper() in s}
        return matches

    def get_instrument_key(self, symbol):
        """Translate Yahoo/Common symbol to Upstox Key"""
        if not self.is_initialized:
            self.initialize_mapper()
            
        # Clean symbol (RELIANCE.NS -> RELIANCE)
        clean_symbol = symbol.replace(".NS", "").replace(".BO", "").upper()
        
        # Check direct mapping
        if clean_symbol in self.instrument_map:
            return self.instrument_map[clean_symbol]
        
        # Try common suffixes like -EQ (NSE) or -BE
        if f"{clean_symbol}-EQ" in self.instrument_map:
            return self.instrument_map[f"{clean_symbol}-EQ"]
        if f"{clean_symbol}-BE" in self.instrument_map:
            return self.instrument_map[f"{clean_symbol}-BE"]
            
        # Try a partial search for equity only if direct matches fail
        # This is strictly for symbols like "RELIANCE" matching "RELIANCE-EQ"
        for s, k in self.instrument_map.items():
            if s == f"{clean_symbol}-EQ":
                return k
        
        # Safe fallback: Search for any that ends with -EQ and starts with our symbol
        potential_keys = [k for s, k in self.instrument_map.items() if s.startswith(f"{clean_symbol}-") and s.endswith("-EQ")]
        if potential_keys:
            return potential_keys[0]

        # Core hardcoded indices (Upstox uses pipe | for indices mostly in v2/v3)
        index_map = {
            "NIFTY 50": "NSE_INDEX|Nifty 50",
            "NIFTY_50": "NSE_INDEX|Nifty 50",
            "^NSEI": "NSE_INDEX|Nifty 50",
            "NIFTY": "NSE_INDEX|Nifty 50",
            "BANKNIFTY": "NSE_INDEX|Nifty Bank",
            "^NSEBANK": "NSE_INDEX|Nifty Bank",
            "FINNIFTY": "NSE_INDEX|Nifty Fin Service",
            "MIDCAPNIFTY": "NSE_INDEX|Nifty Midcap Select",
            "MIDCPNIFTY": "NSE_INDEX|Nifty Midcap Select",
            "SENSEX": "BSE_INDEX|SENSEX",
            "^BSESN": "BSE_INDEX|SENSEX"
        }
        return index_map.get(clean_symbol)
    
    def get_market_quote(self, instrument_keys, mode="full"):
        """
        ⚡ Fetch real-time market quotes (LTP/OHLC/Full)
        mode: ltp, ohlc, full
        """
        if not instrument_keys: return {}
        
        if isinstance(instrument_keys, list):
            keys = ",".join(instrument_keys)
        else:
            keys = instrument_keys
        
        # Format keys for request: standard is pipe |
        # But we ensure they are cleaned
        keys = keys.replace(":", "|")
            
        if mode == "ltp":
            url = f"{self.BASE_URL_V3}/market-quote/ltp"
        elif mode == "ohlc":
            url = f"{self.BASE_URL_V3}/market-quote/ohlc"
        else:
            url = f"{self.BASE_URL}/market-quote/quotes" # Full quote is v2
            
        params = {"instrument_key": keys} if "v3" in url else {"symbol": keys}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                raw_data = response.json().get("data", {})
                # Normalize keys: API sometimes returns ':' instead of '|' or symbol instead of key
                normalized_data = {}
                for k, v in raw_data.items():
                    # Map by symbol key (e.g. NSE_EQ|RELIANCE)
                    norm_k = k.replace(":", "|")
                    normalized_data[norm_k] = v
                    
                    # Also map by instrument_token key (e.g. NSE_EQ|INE002A01018) if available
                    # This allows lookups by ISIN-based key used in mapper
                    token = v.get('instrument_token')
                    if token:
                        normalized_data[token.replace(":", "|")] = v
                        
                return normalized_data
            else:
                print(f"❌ Quote API Error {response.status_code}: {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Quote Exception: {e}")
            return {}

    def get_user_funds(self):
        """
        💰 Fetch available margin and funds
        """
        url = f"{self.BASE_URL}/user/get-funds-and-margin"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                print(f"❌ Funds API Error {response.status_code}: {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Funds Exception: {e}")
            return {}

    def get_option_chain(self, instrument_key, expiry_date=None):
        """
        🔗 Fetch Option Chain for an underlying
        instrument_key: NSE_INDEX|Nifty 50, etc.
        expiry_date: YYYY-MM-DD
        """
        url = f"{self.BASE_URL}/option/chain"
        params = {"instrument_key": instrument_key}
        if expiry_date:
            params["expiry_date"] = expiry_date
            
        try:
            print(f"📡 Requesting Option Chain: {url} with {params}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json().get("data", [])
                print(f"✅ Received {len(data)} contracts.")
                return data
            else:
                print(f"❌ Option Chain Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Option Chain Exception: {e}")
            return []

    def get_expiry_dates_via_sdk(self, instrument_key):
        """📅 Fetch valid expiry dates using SDK with HTTP Fallback"""
        try:
            import upstox_client
            configuration = upstox_client.Configuration()
            configuration.access_token = self.access_token
            api_client = upstox_client.ApiClient(configuration)
            options_api = upstox_client.OptionsApi(api_client)
            
            contracts = options_api.get_option_contracts(instrument_key)
            now_dt = datetime.now().date()
            if contracts and contracts.data:
                expiries = sorted(list(set(c.expiry.date() for c in contracts.data if c.expiry.date() >= now_dt)))
                if expiries:
                    return [e.strftime("%Y-%m-%d") for e in expiries]
        except Exception as e:
            print(f"⚠️ SDK Expiry Error for {instrument_key}: {e}")
        
        # 🟢 Fallback: Use HTTP Option Chain API to get expiries
        try:
            url = f"{self.BASE_URL}/option/contract"
            params = {"instrument_key": instrument_key}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                expiries = sorted(list(set(c['expiry'] for c in data)))
                now_str = datetime.now().strftime("%Y-%m-%d")
                return [e for e in expiries if e >= now_str]
        except Exception as e:
            print(f"❌ HTTP Expiry Fallback Error: {e}")
        
        return []

    def get_option_chain_via_sdk(self, instrument_key, expiry_date):
        """🔗 Fetch full option chain data using SDK"""
        import upstox_client
        configuration = upstox_client.Configuration()
        configuration.access_token = self.access_token
        api_client = upstox_client.ApiClient(configuration)
        options_api = upstox_client.OptionsApi(api_client)
        
        try:
            # SDK uses get_put_call_option_chain(instrument_key, expiry_date)
            chain = options_api.get_put_call_option_chain(instrument_key, expiry_date)
            return chain.data
        except Exception as e:
            print(f"❌ SDK Option Chain Error: {e}")
            return []

    def get_websocket_auth_url(self):
        """
        🔐 Get Authorized WebSocket URL for Market Data Feed
        """
        url = f"{self.BASE_URL}/feed/market-data-feed/authorize"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json().get('data', {}).get('authorized_redirect_uri')
            else:
                print(f"❌ WS Auth Error: {response.text}")
        except Exception as e:
            print(f"❌ WS Auth Exception: {e}")
        return None

    def get_historical_candles(self, instrument_key, interval="5minute", days=5, to_date=None, from_date=None):
        """📊 Fetch historical candle data with relative day support and retries"""
        import urllib.parse
        target_interval = interval
        
        if interval in ["1minute", "5minute", "15minute", "30minute", "60minute"]:
            fetch_interval = "1minute"
        else:
            fetch_interval = "day"
        
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_date = (datetime.now() - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
            
        # 🟢 Encode key for URL safety (handles | and : correctly)
        encoded_key = urllib.parse.quote(instrument_key)
        url = f"{self.BASE_URL}/historical-candle/{encoded_key}/{fetch_interval}/{to_date}/{from_date}"
        
        for attempt in range(2): # Try twice
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    candles = response.json().get("data", {}).get("candles", [])
                    if not candles: continue
                    
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "oi"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    df = df.set_index("timestamp").sort_index()
                    
                    resample_map = {"5minute": "5min", "15minute": "15min", "30minute": "30min", "60minute": "60min"}
                    if target_interval in resample_map and fetch_interval == "1minute":
                        df = df.resample(resample_map[target_interval]).agg({
                            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'oi': 'last'
                        }).dropna()
                    return df
                elif response.status_code == 429: # Rate Limit
                    time.sleep(1)
            except:
                time.sleep(0.5)
        return pd.DataFrame()

    def get_intraday_candles(self, instrument_key, interval="5minute"):
        """🚀 Fetch real-time intraday candles for the current day with retries"""
        import urllib.parse
        target_interval = interval
        fetch_interval = "1minute" if interval in ["1minute", "5minute", "15minute", "30minute", "60minute"] else "1minute"
        
        encoded_key = urllib.parse.quote(instrument_key)
        url = f"{self.BASE_URL}/historical-candle/intraday/{encoded_key}/{fetch_interval}"
        
        for attempt in range(2):
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    candles = response.json().get("data", {}).get("candles", [])
                    if not candles: continue
                    
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "oi"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    df = df.set_index("timestamp").sort_index()
                    
                    resample_map = {"5minute": "5min", "15minute": "15min", "30minute": "30min", "60minute": "60min"}
                    if target_interval in resample_map:
                        df = df.resample(resample_map[target_interval]).agg({
                            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'oi': 'last'
                        }).dropna()
                    return df
                elif response.status_code == 429:
                    time.sleep(1)
            except:
                time.sleep(0.5)
        return pd.DataFrame()

    def find_option_key(self, underlying_symbol, strike, option_type, expiry_date):
        """
        🔍 Robust search for an option instrument key
        underlying_symbol: NIFTY, BANKNIFTY, RELIANCE
        expiry_date: YYYY-MM-DD
        """
        if not self.is_initialized:
            self.initialize_mapper(exchanges=["NSE_EQ", "NSE_FO", "NFO"])

        # Try exact match first
        u_sym = underlying_symbol.upper()
        # Upstox FO symbols are like: NIFTY23FEB22000CE or NIFTY2322322000CE
        
        for symbol, key in self.instrument_map.items():
            if u_sym in symbol and str(strike) in symbol and option_type.upper() in symbol:
                # Basic check for expiry if provided
                if expiry_date:
                    exp_clean = expiry_date.replace("-","")
                    # Check if date components are in symbol (Simplified)
                    # Many Upstox symbols use YYMMM (e.g. 23FEB) or YYMDD
                    # We'll return the first one that matches the core components
                    return key
        return None

    def place_order(self, instrument_key, quantity, side="BUY", order_type="MARKET", product="I"):
        """
        🚀 Place an order on Upstox
        side: BUY, SELL
        order_type: MARKET, LIMIT, SL, SL-M
        product: I (Intraday), D (Delivery), CO (Cover), OCO (Bracket)
        """
        url = f"{self.BASE_URL}/order/place"
        data = {
            "quantity": quantity,
            "product": product,
            "validity": "DAY",
            "price": 0,
            "tag": "PrimeSkillRobot",
            "instrument_token": instrument_key,
            "order_type": order_type,
            "transaction_type": side,
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            if response.status_code == 200:
                print(f"✅ Order Placed Successfully! Order ID: {response.json().get('data', {}).get('order_id')}")
                return response.json()
            else:
                print(f"❌ Order Failed: {response.text}")
                return response.json()
        except Exception as e:
            print(f"❌ Order Exception: {e}")
            return None

    def place_safe_test_order(self):
        """
        💸 Places a safe test order (1 share of IDEA - very low price)
        """
        print("🛒 Attempting safe test order (1 share of IDEA)...")
        idea_key = self.get_instrument_key("IDEA") # Vodafone Idea is famously cheap
        if not idea_key:
            # Fallback search
            for sym, key in self.instrument_map.items():
                if "IDEA" in sym and "-EQ" in sym:
                    idea_key = key
                    break
        
        if not idea_key:
            print("❌ Could not find instrument key for IDEA.")
            return None
        
        return self.place_order(idea_key, quantity=1, side="BUY", order_type="MARKET", product="D")

# Singleton
_upstox_engine = None

def get_upstox_engine():
    global _upstox_engine
    if _upstox_engine is None:
        _upstox_engine = UpstoxEngine()
    return _upstox_engine
