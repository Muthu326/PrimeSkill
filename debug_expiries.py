import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

from services.upstox_engine import get_upstox_engine

def debug_expiries():
    load_dotenv()
    engine = get_upstox_engine()
    
    indices = {
        "NIFTY": "NSE_INDEX|Nifty 50",
        "BANKNIFTY": "NSE_INDEX|Nifty Bank",
        "FINNIFTY": "NSE_INDEX|Nifty Fin Service",
        "SENSEX": "BSE_INDEX|SENSEX"
    }
    
    for label, key in indices.items():
        print(f"\n--- {label} ({key}) ---")
        try:
            # 1. Test SDK Expiries
            import upstox_client
            configuration = upstox_client.Configuration()
            configuration.access_token = engine.access_token
            api_client = upstox_client.ApiClient(configuration)
            options_api = upstox_client.OptionsApi(api_client)
            
            contracts = options_api.get_option_contracts(key)
            expiries = sorted(list(set(c.expiry.strftime("%Y-%m-%d") for c in contracts.data)))
            print(f"Total Raw Expiries: {len(expiries)}")
            print(f"First 5 Expiries: {expiries[:5]}")
            
            # 2. Test Strike Fetching
            spot = float(engine.get_market_quote([key], mode="ltp")[key]['last_price'])
            print(f"Current Spot: {spot}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_expiries()
