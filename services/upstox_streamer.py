import os
import threading
import time
from upstox_client.feeder.market_data_streamer_v3 import MarketDataStreamerV3
from upstox_client.feeder.streamer import Streamer
from upstox_client.api_client import ApiClient
from upstox_client.configuration import Configuration
from services.upstox_engine import get_upstox_engine

# 🏦 Global Memory Maps for high-speed access
LTP_CACHE = {}
LAST_UPDATE_CACHE = {}

class UpstoxStreamer:
    def __init__(self):
        self.streamer = None
        self.active_keys = set()
        self.lock = threading.Lock()
        self.is_running = False

    def on_message(self, data):
        """Callback for incoming tick data (already converted to dict by SDK)"""
        try:
            feeds = data.get('feeds', {})
            for key, feed in feeds.items():
                norm_key = key.replace(":", "|")
                
                # Extract LTP from ltpc mode structure
                ltp = None
                if 'ltpc' in feed:
                    ltp = feed['ltpc'].get('ltp')
                elif 'ff' in feed:
                    # In case it switches to full mode
                    market_ff = feed.get('ff', {}).get('marketFF', {})
                    ltp = market_ff.get('ltpc', {}).get('ltp')
                
                if ltp is not None:
                    # 🚀 INTEGRATE MONITORING LOGIC
                    from services.trade_monitor import get_trade_monitor
                    monitor = get_trade_monitor()
                    
                    if "|20" in norm_key: # Rough check for option contracts (e.g. NIFTY25FEB...)
                        # It's an option contract, check if we are monitoring it
                        monitor.monitor_index(norm_key, float(ltp))
                        monitor.monitor_stock(norm_key, float(ltp))

                    with self.lock:
                        LTP_CACHE[norm_key] = float(ltp)
                        LAST_UPDATE_CACHE[norm_key] = time.time()
        except Exception:
            pass

    def on_open(self):
        print("🟢 [WS] Upstox WebSocket Connected & Streaming")

    def on_error(self, error):
        print(f"🔴 [WS] Streamer Error: {error}")

    def on_close(self, status_code, message):
        print(f"⚪ [WS] Streamer Closed: {status_code} - {message}")
        self.is_running = False

    def start(self, initial_keys=None):
        """Starts the streamer in a background thread using official SDK v2"""
        if self.is_running:
            return
            
        def _run():
            try:
                self.is_running = True
                access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
                if not access_token:
                    print("❌ No Access Token for WebSocket")
                    return

                config = Configuration()
                config.access_token = access_token
                api_client = ApiClient(config)
                
                keys = list(initial_keys) if initial_keys else []
                self.active_keys.update(keys)
                
                # Batch 1: Start with first 100 keys
                initial_slice = keys[:100]
                self.streamer = MarketDataStreamerV3(
                    api_client=api_client,
                    instrumentKeys=initial_slice,
                    mode="ltpc"
                )
                
                # Register Event Listeners
                self.streamer.on(Streamer.Event["OPEN"], self.on_open)
                self.streamer.on(Streamer.Event["MESSAGE"], self.on_message)
                self.streamer.on(Streamer.Event["ERROR"], self.on_error)
                self.streamer.on(Streamer.Event["CLOSE"], self.on_close)
                
                self.streamer.connect()

                # Batch 2+: Subscribe remaining keys after connection
                if len(keys) > 100:
                    time.sleep(2) # Wait for open
                    for i in range(100, len(keys), 100):
                        batch = keys[i : i+100]
                        self.streamer.subscribe(batch, mode="ltpc")
                        time.sleep(0.5)
            except Exception as e:
                print(f"❌ Streamer Crash: {e}")
                self.is_running = False

        threading.Thread(target=_run, daemon=True).start()

    def subscribe(self, keys):
        """Add new keys to the stream on the fly"""
        if not self.streamer or not self.is_running:
            self.start(initial_keys=keys)
            return

        new_keys = [k for k in keys if k not in self.active_keys]
        if new_keys:
            try:
                # SDK use "ltpc" mode
                self.streamer.subscribe(new_keys, mode="ltpc")
                self.active_keys.update(new_keys)
            except:
                pass

    def stop(self):
        """Disconnect the streamer and cleanup"""
        if self.streamer and self.is_running:
            try:
                self.streamer.disconnect()
            except:
                pass
            self.streamer = None
            self.is_running = False
            self.active_keys = set()
            print("⚪ [WS] Streamer Stopped Manually")

# Singleton instance
_streamer = UpstoxStreamer()

def get_streamer():
    return _streamer

def get_live_ltp(instrument_key):
    """Instant lookup from cache with timestamp"""
    norm_key = instrument_key.replace(":", "|")
    return LTP_CACHE.get(norm_key), LAST_UPDATE_CACHE.get(norm_key)

def get_cache_info(instrument_key):
    """Returns (ltp, last_update_time)"""
    norm_key = instrument_key.replace(":", "|")
    return LTP_CACHE.get(norm_key), LAST_UPDATE_CACHE.get(norm_key)

def update_live_ltp(instrument_key, ltp):
    """Manual update for cache (e.g. from quote API) to support off-market testing"""
    norm_key = instrument_key.replace(":", "|")
    LTP_CACHE[norm_key] = float(ltp)
    LAST_UPDATE_CACHE[norm_key] = time.time()
