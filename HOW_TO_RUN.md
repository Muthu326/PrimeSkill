# 🚀 HOW TO RUN - Step by Step Guide
## PRIME SKILL F&O Options Trading System

**Created by:** MuthuKumar Krishnan  
**Location:** `C:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill`

---

## ⚡ QUICK START (3 Steps)

### **Step 1: Install Missing Dependencies (One Time Only)**

Open **Command Prompt** and run:

```bash
cd "C:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill"
pip install beautifulsoup4 python-dateutil tabulate
```

Wait for installation (30 seconds).

---

### **Step 2: Launch the System**

**Double-click this file:**
```
START_FULL_ENGINE.bat
```

This will:
1. ✅ Start **Background Scanner** (Telegram alerts)
2. ✅ Start **Dashboard** (Browser opens automatically)

---

### **Step 3: Access Dashboard**

Your browser will open automatically with:

**URL:** `http://localhost:8501`

If browser doesn't open, manually visit:
- `http://localhost:8501` OR
- `http://127.0.0.1:8501`

---

## 📱 ACCESS FROM MOBILE (Same WiFi)

### **Step 1: Find Your PC IP Address**

Open **Command Prompt** and type:
```bash
ipconfig
```

Look for **IPv4 Address**, example:
```
IPv4 Address: 192.168.1.100
```

### **Step 2: Access from Mobile Browser**

On your mobile phone (same WiFi):
```
http://192.168.1.100:8501
```
(Replace with your actual IP)

---

## 🖥️ DASHBOARD PAGES

Once dashboard opens, you'll see these pages:

### **1. 🏠 HOME**
- Market overview
- Live index prices (NIFTY, BANKNIFTY, SENSEX)
- Quick stats

### **2. 🔥 FIRE TRADE (BTST)**
- Buy Today Sell Tomorrow opportunities
- Bullish stocks with momentum
- Bearish stocks for shorting
- Entry/Target/Stop Loss levels

### **3. 📊 OPTION CHAIN**
- Live option premiums
- Strike price analysis
- Greeks (Delta, Gamma, Theta, Vega)

### **4. 🎯 STRATEGY HUB**
- Pre-built trading strategies
- Long Call, Long Put
- Bull Call Spread, Bear Put Spread
- Straddle, Strangle

### **5. 📈 RADAR**
- Top gainers/losers
- Momentum scanner
- Volume analysis

### **6. 📜 TRADE HISTORY**
- Past trades
- Win/Loss tracking
- Performance analytics

---

## 🤖 AUTOMATED ALERTS (Telegram)

The **Background Scanner** (`am_backend_scanner.py`) runs automatically and sends alerts to your Telegram.

### **What Alerts You'll Receive:**

1. **Market Open Alert** (9:00 AM)
2. **Strong Momentum Signals** (Every 5 minutes)
3. **BTST Opportunities** (3:00 PM)
4. **Market Close Summary** (3:30 PM)

### **Your Telegram Bot:**
- **Token:** `8252289647:AAG7L4-9m_eYFNAJDPgScxA_pNH4UKd-bAs`
- **Chat ID:** `5988809859`

---

## 📂 KEY FILES EXPLAINED

| File | Purpose | How to Use |
|------|---------|------------|
| **START_FULL_ENGINE.bat** | Main launcher | Double-click to start |
| **marsh_muthu_326_pro_terminal.py** | Dashboard entry point | Auto-launched by batch file |
| **am_backend_scanner.py** | Background alert system | Auto-launched by batch file |
| **config/config.py** | Settings & configuration | Edit to customize |
| **.env** | Telegram credentials | Already configured |
| **requirements.txt** | Python dependencies | Used for installation |

---

## 🛠️ TROUBLESHOOTING

### **Problem 1: Dashboard won't load**

**Check 1:** Is Python installed?
```bash
python --version
```
Should show: `Python 3.14.2`

**Check 2:** Are dependencies installed?
```bash
pip list | findstr streamlit
```

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

---

### **Problem 2: Port already in use**

**Error:** `Address already in use: 8501`

**Solution:** Kill existing process
```bash
netstat -ano | findstr :8501
taskkill /PID <process_id> /F
```

Or change port in batch file:
```bash
streamlit run marsh_muthu_326_pro_terminal.py --server.port 8502
```

---

### **Problem 3: No Telegram alerts**

**Check 1:** Is scanner running?
- Look for CMD window titled "AM SCANNER"

**Check 2:** Is .env configured?
```bash
type .env
```

**Solution:** Restart scanner
```bash
python am_backend_scanner.py
```

---

### **Problem 4: Data not loading**

**Error:** "No data available"

**Possible causes:**
1. **No internet connection** - Check WiFi
2. **Market is closed** - Try during market hours (9:15 AM - 3:30 PM)
3. **yfinance rate limit** - Wait 2-3 minutes and refresh

**Solution:** Click "Refresh" button in dashboard

---

### **Problem 5: Mobile can't access**

**Check 1:** PC and mobile on same WiFi?

**Check 2:** Windows Firewall blocking?
- Go to: Windows Defender Firewall → Allow an app
- Add: `python.exe`

**Check 3:** Correct IP address?
```bash
ipconfig
```
Use IPv4 address, not IPv6

---

## 🎓 FIRST TRADE TUTORIAL

### **Scenario: Buy NIFTY Call Option**

**Step 1:** Go to **Strategy Hub** page

**Step 2:** Select **"Long Call"** strategy

**Step 3:** Choose symbol: **NIFTY**

**Step 4:** Review recommendation:
```
Strike: 21900 CE
Premium: ₹185
Target: ₹260 (+40%)
Stop Loss: ₹110 (-40%)
```

**Step 5:** Click **"Execute"** (Paper trading)

**Step 6:** Monitor in **Positions** page

**Step 7:** Close when target reached

---

## ⏰ DAILY ROUTINE

### **Morning (9:00 AM)**
1. Launch system: `START_FULL_ENGINE.bat`
2. Check Telegram morning alert
3. Review BTST signals from yesterday

### **During Market (9:15 AM - 3:30 PM)**
1. Monitor dashboard
2. Watch for momentum alerts
3. Execute high-conviction trades

### **Pre-Close (3:00 PM)**
1. Check **Fire Trade** page for BTST
2. Review option positions
3. Plan for next day

### **After Close (3:30 PM+)**
1. Review trade history
2. Check performance analytics
3. Read market close summary on Telegram

---

## 📊 UNDERSTANDING ALERTS

### **Sample Telegram Alert:**
```
🚨 STRONG BUY SIGNAL

📊 RELIANCE
💰 CMP: ₹2,450.00 (+2.3%)
📈 Momentum: 85/100
🔥 BTST Candidate

Strike: 2450 CE
Premium: ₹42
Target: ₹55 (+30%)
Stop Loss: ₹25 (-40%)

⏰ Entry: Tomorrow 9:20-10:00 AM
✅ Confidence: 78%
```

### **What to do:**
1. ✅ **High confidence (>75%)** → Consider entry
2. ⚠️ **Medium confidence (60-75%)** → Wait for confirmation
3. ❌ **Low confidence (<60%)** → Skip

---

## 🔒 SAFETY & DISCLAIMERS

⚠️ **IMPORTANT:**
1. This is **PAPER TRADING** only (no real money)
2. For **educational purposes** only
3. Trading involves **risk of loss**
4. Always use **stop loss**
5. Don't invest more than you can afford to lose

---

## 🆘 QUICK COMMANDS REFERENCE

| Task | Command |
|------|---------|
| **Install dependencies** | `pip install -r requirements.txt` |
| **Start dashboard only** | `streamlit run marsh_muthu_326_pro_terminal.py` |
| **Start scanner only** | `python am_backend_scanner.py` |
| **Check Python version** | `python --version` |
| **Check installed packages** | `pip list` |
| **Find PC IP** | `ipconfig` |
| **Kill port 8501** | `netstat -ano | findstr :8501` then `taskkill /PID <id> /F` |

---

## 📞 SUPPORT

**Created by:** MuthuKumar Krishnan  
**Organization:** PRIME SKILL DEVELOPMENT  

**Files to check:**
- `README.md` - Project overview
- `DEPLOYMENT_GUIDE_STREAMLIT.md` - Cloud deployment
- `.env` - Telegram configuration

---

## ✅ CHECKLIST BEFORE STARTING

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Missing packages installed (`beautifulsoup4`, `python-dateutil`, `tabulate`)
- [ ] `.env` file exists with Telegram credentials
- [ ] Internet connection active
- [ ] Directory: `C:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill`

**Ready?** Double-click `START_FULL_ENGINE.bat` 🚀

---

**Last Updated:** 21-Feb-2026  
**System Version:** PRIME SKILL Pro Terminal v2.0
