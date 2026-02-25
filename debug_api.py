import os
import requests
from dotenv import load_dotenv
import sys
sys.path.append(os.getcwd())
from services.upstox_engine import get_upstox_engine

load_dotenv()
engine = get_upstox_engine()
sym = "RELIANCE"
key = engine.get_instrument_key(sym)
print(f"DEBUG: Symbol {sym} -> Key {key}")

# Test V3 LTP directly
url = f"https://api.upstox.com/v3/market-quote/ltp"
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {engine.access_token}'
}
params = {'instrument_key': key}
response = requests.get(url, headers=headers, params=params)
print(f"DEBUG: V3 LTP Response: {response.status_code}")
print(f"DEBUG: V3 LTP Data: {response.json()}")

# Test V2 Quotes directly
url_v2 = f"https://api.upstox.com/v2/market-quote/quotes"
params_v2 = {'symbol': key}
response_v2 = requests.get(url_v2, headers=headers, params=params_v2)
print(f"DEBUG: V2 Quotes Response: {response_v2.status_code}")
print(f"DEBUG: V2 Quotes Data: {response_v2.json()}")
