
import requests
import gzip
import io
import json

def check_duplicate_symbols():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"
    print("Downloading complete.json.gz...")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with gzip.open(io.BytesIO(response.content), 'rt', encoding='utf-8') as f:
            data = json.load(f)
            targets = ["MUTHOOTFIN", "SBIN", "HDFCBANK", "PNB"]
            results = {t: [] for t in targets}
            for item in data:
                sym = (item.get('trading_symbol') or item.get('tradingsymbol') or "").strip().upper()
                if sym in targets:
                    results[sym].append({
                        "key": item.get('instrument_key'),
                        "exchange": item.get('exchange'),
                        "segment": item.get('segment'),
                        "name": item.get('name')
                    })
            
            for sym, info in results.items():
                print(f"\n--- {sym} ---")
                for i in info:
                    print(i)

if __name__ == "__main__":
    check_duplicate_symbols()
