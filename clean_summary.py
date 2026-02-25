
import os

file_path = r"c:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill\am_backend_scanner.py"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of the mess (send_15min_summary)
start_idx = -1
for i in range(len(lines)):
    if "def send_15min_summary" in lines[i]:
        start_idx = i
        break

if start_idx != -1:
    # Find the end of the mess (before get_nifty_movers)
    end_idx = -1
    for i in range(start_idx, len(lines)):
        if "def get_nifty_movers" in lines[i]:
            end_idx = i
            break
    
    if end_idx != -1:
        new_summary_logic = """def get_global_market_pulse():
    \"\"\"🌎 Institutional Global Sentiment (Robust Fetch)\"\"\"
    results = {}
    try:
        symbols = list(GLOBAL_SENTIMENT_SYMBOLS.values())
        data = yf.download(symbols, period="2d", interval="5m", progress=False)
        if data.empty: return results
        
        # Check if we have 'Close' multi-index or single index
        close_data = data['Close']
        for name, sym in GLOBAL_SENTIMENT_SYMBOLS.items():
            if sym in close_data.columns:
                series = close_data[sym].dropna()
                if len(series) >= 2:
                    last_px = series.iloc[-1]
                    prev_px = series.iloc[-2]
                    chg = ((last_px - prev_px) / prev_px) * 100
                    results[name] = {"px": round(last_px, 2), "chg": round(chg, 2)}
    except: pass
    return results

def send_15min_summary(pcr_data, is_next_month=False):
    \"\"\"📩 Premium 15-Minute Market Pulse Alert with Global Context\"\"\"
    status_icon = "🟢 LIVE"
    o = pcr_data["overall"]
    n = pcr_data["NIFTY"]
    b = pcr_data["BANKNIFTY"]
    global_pulse = get_global_market_pulse()
    
    title = f"{status_icon} 🏛️ *INSTITUTIONAL PULSE (MARCH)*" if is_next_month else f"{status_icon} 🏛️ *MARKET SENTIMENT PULSE*"
    
    def fmt_oi(val):
        if val >= 10000000: return f"{val/10000000:.2f}Cr"
        if val >= 100000: return f"{val/100000:.2f}L"
        return str(val)

    global_str = ""
    for name, data in global_pulse.items():
        icon = "📈" if data['chg'] > 0 else "📉"
        global_str += f"∟ {name}: `{data['chg']:.2f}%` {icon}\\n"

    msg = (
        f"{title}\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"🕙 **TIME**: `{datetime.now().strftime('%H:%M:%S')}`\\n"
        f"🎭 **BIAS**: `{o['bias']}`\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"🌎 **GLOBAL CONTEXT**\\n"
        f"{global_str if global_str else '∟ Syncing Global Data...'}\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"📈 **NIFTY 50**\\n"
        f"∟ PCR: `{n['pcr']}`\\n"
        f"∟ CE: `{fmt_oi(n['ce_oi'])}` | PE: `{fmt_oi(n['pe_oi'])}`\\n\\n"
        f"📉 **BANKNIFTY**\\n"
        f"∟ PCR: `{b['pcr']}`\\n"
        f"∟ CE: `{fmt_oi(b['ce_oi'])}` | PE: `{fmt_oi(b['pe_oi'])}`\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"📊 **TOTAL PCR**: `{o['pcr']}`\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"🏛️ [OPEN TERMINAL]({AUTH_URL})\\n\\n"
        f"{SIGNATURE}"
    )
    send_telegram(msg)
"""
        lines[start_idx:end_idx] = [new_summary_logic + "\n"]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Successfully cleaned up and updated am_backend_scanner.py")
else:
    print("Error: Could not find send_15min_summary")
