
import os

file_path = r"c:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill\am_backend_scanner.py"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_trade_alert = """def send_trade_alert(signal, is_update=False):
    \"\"\"💎 Premium Institutional Trade Alert Design with LIVE Indicator\"\"\"
    status_icon = "🟢 LIVE"
    title = f"🔔 *{status_icon} SIGNAL UPDATE*" if is_update else f"🔥 *{status_icon} NEW {signal['tag']}*"
    icon = "🟩" if signal['type'] == "CE" else "🟥"
    
    # Standardize data from signal dictionary
    entry_px = signal.get('entry', signal.get('premium', 0))
    conf_score = signal.get('confidence', signal.get('score', 0))
    fname = get_friendly_name(signal['symbol'])
    
    msg = (
        f"{title}\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"📍 **ASSET**: `{fname}`\\n"
        f"🎟️ **OPTION**: `{signal['strike']} {signal['type']}` {icon}\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"💰 **ENTRY**: `₹{entry_px:.2f}`\\n"
        f"🛡️ **STOPLOSS**: `₹{signal['stop_loss']:.2f}`\\n"
        f"🎯 **TARGET**: `₹{signal['target']:.2f}`\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"📊 **CONFIDENCE**: `{abs(conf_score)}%`\\n"
        f"⏳ **STATUS**: `{signal['status']}`\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"🏛️ [PLATFORM ACCESS]({AUTH_URL})\\n\\n"
        f"👤 *PrimeSkillDevelopment CEO*\\n"
        f"∟ *MuthuKumar krishnan*"
    )
    return send_telegram(msg)
"""

new_summary_alert = """def send_15min_summary(pcr_data, is_next_month=False):
    \"\"\"📩 Premium 15-Minute Market Pulse Alert with LIVE Indicator\"\"\"
    status_icon = "🟢 LIVE"
    o = pcr_data["overall"]
    n = pcr_data["NIFTY"]
    b = pcr_data["BANKNIFTY"]
    title = f"{status_icon} 🏛️ *INSTITUTIONAL PULSE (MARCH)*" if is_next_month else f"{status_icon} 🏛️ *MARKET SENTIMENT PULSE*"
    
    def fmt_oi(val):
        if val >= 10000000: return f"{val/10000000:.2f}Cr"
        if val >= 100000: return f"{val/100000:.2f}L"
        return str(val)

    msg = (
        f"{title}\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"🕙 **TIME**: `{datetime.now().strftime('%H:%M:%S')}`\\n"
        f"🎭 **BIAS**: `{o['bias']}`\\n"
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
        f"👤 *PrimeSkillDevelopment CEO*\\n"
        f"∟ *MuthuKumar krishnan*"
    )
    send_telegram(msg)
"""

# Replace lines
# Note: Line numbers are dynamic due to prev script, but we can search for the start line
for i in range(len(lines)):
    if "def send_trade_alert" in lines[i]:
        # Find the end of function (until next def or empty block)
        j = i + 1
        while j < len(lines) and "def " not in lines[j] and "# =" not in lines[j]:
            j += 1
        lines[i:j] = [new_trade_alert + "\n"]
        break

for i in range(len(lines)):
    if "def send_15min_summary" in lines[i]:
        j = i + 1
        while j < len(lines) and "def " not in lines[j] and "def " not in lines[j+1]:
            j += 1
        # Need to be careful with the inner fmt_oi
        lines[i:j+1] = [new_summary_alert + "\n"]
        break

# Update other loop alerts with 🟢 LIVE
for i in range(len(lines)):
    if 'send_telegram(f"🏛️ *Market Sentiment Pulse*' in lines[i]:
        lines[i] = lines[i].replace('🏛️ *Market Sentiment Pulse*', '🟢 LIVE 🏛️ *Market Sentiment Pulse*')
    if 'send_telegram(f"🏛 *SECTOR LEADERSHIP:' in lines[i]:
        lines[i] = lines[i].replace('🏛 *SECTOR LEADERSHIP:', '🟢 LIVE 🏛 *SECTOR LEADERSHIP:')
    if 'send_telegram(f"🌐 *INDEX BIAS:' in lines[i]:
        lines[i] = lines[i].replace('🌐 *INDEX BIAS:', '🟢 LIVE 🌐 *INDEX BIAS:')
    if 'send_telegram("⚡ *3PM Power Scan Running*"' in lines[i]:
        lines[i] = lines[i].replace('⚡ *3PM Power Scan Running*', '🟢 LIVE ⚡ *3PM Power Scan Running*')

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Successfully updated am_backend_scanner.py with LIVE indicators")
