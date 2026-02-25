import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

from services.upstox_engine import get_upstox_engine

def find_indices():
    load_dotenv()
    engine = get_upstox_engine()
    
    # Initialize mapper
    engine.initialize_mapper()
    
    search_terms = ["NIFTY", "BANK", "SENSEX", "FIN", "MIDCAP"]
    for term in search_terms:
        matches = engine.find_all_instruments(term)
        print(f"\n--- Matches for '{term}' ---")
        # Filter for INDEX keys
        index_matches = {s: k for s, k in matches.items() if "INDEX" in k}
        for s, k in list(index_matches.items())[:20]:
            print(f"{s}: {k}")

if __name__ == "__main__":
    find_indices()
