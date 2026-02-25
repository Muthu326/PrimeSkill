
import os
from services.upstox_engine import get_upstox_engine
from dotenv import load_dotenv

load_dotenv()

def debug_symbols():
    engine = get_upstox_engine()
    symbols = ["MUTHOOTFIN", "NIFTY", "BANKNIFTY", "RELIANCE"]
    for s in symbols:
        key = engine.get_instrument_key(s)
        print(f"Symbol: {s} -> Key: {key}")

if __name__ == "__main__":
    debug_symbols()
