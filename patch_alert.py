
import os

file_path = r"c:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill\am_backend_scanner.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = -1
end_line = -1
for i, line in enumerate(lines):
    if "def send_trade_alert" in line:
        start_line = i
    if start_line != -1 and "return send_telegram(msg)" in line:
        end_line = i
        break

if start_line != -1 and end_line != -1:
    # Notice we are defining the EXACT lines to be written back.
    # We use f-strings in the lines that need to be f-strings in am_backend_scanner.py
    new_func = [
        "def send_trade_alert(signal, is_update=False):\n",
        "    \"\"\"💎 Premium Institutional Trade Alert Design with LIVE Indicator\"\"\"\n",
        "    status_icon = \"🟢 LIVE\"\n",
        "    title = f\"🔔 *{status_icon} SIGNAL UPDATE*\" if is_update else f\"🔥 *{status_icon} NEW {signal['tag']}*\"\n",
        "    icon = \"🟩\" if signal['type'] == \"CE\" else \"🟥\"\n",
        "    \n",
        "    # Standardize data from signal dictionary\n",
        "    entry_px = signal.get('entry', signal.get('premium', 0))\n",
        "    conf_score = signal.get('confidence', signal.get('score', 0))\n",
        "    spot_px = signal.get('spot', 0)\n",
        "    fname = get_friendly_name(signal['symbol'])\n",
        "    \n",
        "    msg = (\n",
        "        f\"{title}\\n\"\n",
        "        f\"━━━━━━━━━━━━━━━━━━\\n\"\n",
        "        f\"📍 **ASSET**: `{fname}`\\n\"\n",
        "        f\"🎯 **SPOT PRICE**: `₹{spot_px:,.2f}`\\n\"\n",
        "        f\"🎟️ **ENTRY STRIKE**: `{signal['strike']} {signal['type']}` {icon}\\n\"\n",
        "        f\"━━━━━━━━━━━━━━━━━━\\n\"\n",
        "        f\"💰 **OPTION PREMIUM**: `₹{entry_px:.2f}`\\n\"\n",
        "        f\"🛡️ **STOPLOSS**: `₹{signal['stop_loss']:.2f}`\\n\"\n",
        "        f\"🎯 **TARGET**: `₹{signal['target']:.2f}`\\n\"\n",
        "        f\"━━━━━━━━━━━━━━━━━━\\n\"\n",
        "        f\"📊 **CONFIDENCE**: `{abs(conf_score)}%`\\n\"\n",
        "        f\"⏳ **STATUS**: `{signal['status']}`\\n\"\n",
        "        f\"━━━━━━━━━━━━━━━━━━\\n\"\n",
        "        f\"🏛️ [PLATFORM ACCESS]({AUTH_URL})\\n\\n\"\n",
        "        f\"👤 *PrimeSkillDevelopment CEO*\\n\"\n",
        "        f\"∟ *MuthuKumar krishnan*\"\n",
        "    )\n",
        "    return send_telegram(msg)\n"
    ]
    
    lines[start_line:end_line+1] = new_func

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully patched send_trade_alert.")
else:
    print("Could not find function.")
