
import os
from services.upstox_engine import get_upstox_engine
from dotenv import load_dotenv

load_dotenv()

def verify_prices():
    engine = get_upstox_engine()
    stocks = ["MUTHOOTFIN", "SBIN", "HDFCBANK", "PNB", "TCS", "RELIANCE"]
    
    keys = {}
    for s in stocks:
        k = engine.get_instrument_key(s)
        keys[s] = k
        print(f"Symbol: {s} -> Key: {k}")
    
    quotes = engine.get_market_quote(list(keys.values()), mode="ltp")
    for s, k in keys.items():
        price = quotes.get(k, {}).get('last_price', 'N/A')
        print(f"Price for {s} ({k}): ₹{price}")

if __name__ == "__main__":
    verify_prices()
