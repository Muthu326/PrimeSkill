
import yfinance as yf
from scanner_config import GLOBAL_SENTIMENT_SYMBOLS

def get_global_market_pulse():
    print(f"📡 Fetching Global Sentiment for: {list(GLOBAL_SENTIMENT_SYMBOLS.keys())}")
    results = {}
    try:
        data = yf.download(list(GLOBAL_SENTIMENT_SYMBOLS.values()), period="1d", interval="5m", progress=False)
        for name, sym in GLOBAL_SENTIMENT_SYMBOLS.items():
            if ch := data.get('Close'):
                if sym in ch.columns:
                    last_px = ch[sym].iloc[-1]
                    # Attempt to get prev for change
                    if len(ch) >= 2:
                         prev_px = ch[sym].iloc[-2]
                    else:
                         prev_px = last_px
                    chg = ((last_px - prev_px) / prev_px) * 100
                    results[name] = {"px": round(last_px, 2), "chg": round(chg, 2)}
    except Exception as e:
        print(f"Error: {e}")
    return results

pulse = get_global_market_pulse()
print(f"🌍 Global Market Pulse: {pulse}")
