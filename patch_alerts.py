
import os

file_path = r"c:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill\am_backend_scanner.py"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_trade_alert = """def send_trade_alert(signal, is_update=False):
    \"\"\"💎 Premium Institutional Trade Alert Design\"\"\"
    title = f"🔔 *SIGNAL UPDATE*" if is_update else f"🔥 *NEW {signal['tag']}*"
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

# Replace lines 273 to 292 (indices 272 to 291)
# Note: Line numbers are 1-indexed.
start_idx = 272
end_idx = 292

# Ensure we are replacing the correct function
if "def send_trade_alert" in lines[start_idx]:
    lines[start_idx:end_idx] = [new_trade_alert + "\n"]
    
    # Also fix the broken emoji in 15min summary while we are at it
    # We saw it was around line 683 (index 682)
    for i in range(len(lines)):
        if " **BANKNIFTY**" in lines[i] and "∟ PCR:" in lines[i+1]:
             lines[i] = lines[i].replace(" **BANKNIFTY**", "📉 **BANKNIFTY**")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully updated am_backend_scanner.py")
else:
    print(f"Error: Could not find send_trade_alert at line 273. Found: {lines[start_idx]}")
