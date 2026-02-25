# 🎯 PRIME SKILL | ULTIMATE PRO TERMINAL

## Professional AI-Powered Trading Dashboard for F&O, Stocks & Commodity

**CEO:** MuthuKumar Krishnan  
**Organization:** PRIME SKILL DEVELOPMENT

---

## 🚀 Key Features

1. **Modular Workspace:** 12 specialized views including Home, Fire Trade (BTST), Option Chain, Radar, and Strategy Hub.
2. **AI Signal Engine:** Real-time momentum analysis, speed tracking, and automated trade entry detection.
3. **Automated Alerts:** Background scanner (`am_backend_scanner.py`) sends high-conviction signals to Telegram 24/7.
4. **Resilient Data:** Multi-threaded data engine with fallback logic and auto-refresh.
5. **Jackpot Conviction:** Advanced scoring system for identifying "Diamond" trade setups.

---

## 🛠️ Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Telegram:**
   Create a `.env` file and add your tokens:
   ```env
   TELEGRAM_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

---

## 🛰️ How to Use

### 1. Launch Everything (One-Click)
Double-click **`START_FULL_ENGINE.bat`**. This will:
- Start the **Automated Alert Scanner** (Background).
- Start the **Dashboard UI** (Browser).

### 2. Update the Website
Double-click **`PUBLISH_TO_WEBSITE.bat`**. This will:
- Sync all your latest changes to GitHub.
- Trigger an automatic update on Streamlit Cloud.

---

## 📁 File Structure (Latest)
- `marsh_muthu_326_pro_terminal.py`: The main dashboard entry point.
- `am_backend_scanner.py`: The background automated alerting system.
- `views/`: Modular rendering logic for each tab.
- `services/`: Core logic for calculations and data fetching.
- `config/`: Centralized settings and stock lists.

---
**Disclaimer:** For educational and paper trading purposes only. Trading involves risk.
