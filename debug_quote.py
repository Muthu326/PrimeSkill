import os
from dotenv import load_dotenv
import sys
sys.path.append(os.getcwd())
from services.upstox_engine import get_upstox_engine

load_dotenv()
engine = get_upstox_engine()
sym = "RELIANCE"
key = engine.get_instrument_key(sym)
print(f"DEBUG: Symbol {sym} -> Key {key}")

quotes = engine.get_market_quote([key], mode="full")
print(f"DEBUG: Quote for {key}: {quotes.get(key)}")

ltp_quotes = engine.get_market_quote([key], mode="ltp")
print(f"DEBUG: LTP Quote for {key}: {ltp_quotes.get(key)}")
