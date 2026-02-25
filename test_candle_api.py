
import requests
import os
import pandas as pd
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_candle_url():
    access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Target: MUTHOOTFIN (NSE_EQ|INE414G01012)
    key = "NSE_EQ|INE414G01012"
    fetch_interval = "1minute"
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Test WITH encoding
    encoded_key = urllib.parse.quote(key)
    url_enc = f"https://api.upstox.com/v2/historical-candle/{encoded_key}/{fetch_interval}/{to_date}/{from_date}"
    print(f"Testing WITH encoding: {url_enc}")
    resp_enc = requests.get(url_enc, headers=headers)
    print(f"Response Status: {resp_enc.status_code}")
    if resp_enc.status_code == 200:
        print(f"Success! Data points: {len(resp_enc.json().get('data', {}).get('candles', []))}")
    else:
        print(f"Error: {resp_enc.text}")

    # 2. Test WITHOUT encoding
    url_raw = f"https://api.upstox.com/v2/historical-candle/{key}/{fetch_interval}/{to_date}/{from_date}"
    print(f"\nTesting WITHOUT encoding: {url_raw}")
    resp_raw = requests.get(url_raw, headers=headers)
    print(f"Response Status: {resp_raw.status_code}")
    if resp_raw.status_code == 200:
        print(f"Success! Data points: {len(resp_raw.json().get('data', {}).get('candles', []))}")
    else:
        print(f"Error: {resp_raw.text}")

if __name__ == "__main__":
    test_candle_url()
