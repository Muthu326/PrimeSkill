# 🤖 AUTOMATION GUIDE
## Smart Trading Bot - No Need to Watch Market All Day!

**Created by:** MuthuKumar Krishnan  
**PRIME SKILL DEVELOPMENT**

---

## 🎯 What This Bot Does Automatically

### ✅ **Daily 4:30 PM Market Scan**
- Scans all 5 indices (NIFTY, SENSEX, BANKNIFTY, FINNIFTY, MIDCPNIFTY)
- Analyzes top 30 F&O stocks
- Predicts next day's CE/PE opportunities
- Sends comprehensive report to Telegram
- **You get exact entry, stop loss, target for tomorrow!**

### ✅ **Low Premium Scanner** (Every 2 Hours)
- Finds options at ₹3-15 with 5-10x potential
- Monitors deep OTM options that could explode
- Example: ₹5 option → ₹25 in one week
- Sends alerts when opportunities found

### ✅ **Theta Decay Monitor** (Every Hour)
- Watches your open positions
- Alerts when options losing value fast (near expiry)
- Suggests when to roll to next contract
- Prevents expiry losses

### ✅ **Position Updates** (Every 30 Minutes)
- Updates all position prices
- Checks stop-loss and targets
- Auto-executes when levels hit
- Monitors portfolio risk

### ✅ **Smart Notifications**
- **9:00 AM** - Morning reminder with action plan
- **3:30 PM** - Market close summary with P&L
- **4:30 PM** - Tomorrow's opportunities
- **Real-time** - Entry/exit alerts

---

## 🚀 How to Start the Bot

### **Option 1: One-Click Start**

Double-click: **`START_AUTO_BOT.bat`**

The bot will run in background and send all alerts to Telegram!

### **Option 2: Command Line**

```bash
cd "C:\Users\MuthuKumar Krishnan\OneDrive\Desktop\326\PrimeSkill"
python auto_trading_bot.py
```

### **Option 3: Test Individual Functions**

```bash
# Run daily scan immediately
python auto_trading_bot.py scan

# Run premium scanner
python auto_trading_bot.py premium

# Run theta monitor
python auto_trading_bot.py theta

# Test all functions
python auto_trading_bot.py test
```

---

## ⏰ Automated Schedule

The bot runs these tasks automatically:

| Time | Task | What It Does |
|------|------|--------------|
| **9:00 AM** | Morning Reminder | "Market opening in 30 min - Check signals!" |
| **9:15-3:30 PM** | Position Updates | Every 30 min - Check SL/targets |
| **10:00 AM** | Low Premium Scan | Find ₹3-15 options with 5x potential |
| **10:00-3:00 PM** | Theta Monitor | Check time decay hourly |
| **12:00 PM** | Low Premium Scan | Second scan of the day |
| **2:00 PM** | Low Premium Scan | Third scan (final) |
| **3:30 PM** | Market Close Summary | "Today's P&L: ₹XXX" |
| **4:30 PM** | 🎯 **DAILY SCAN** | **Tomorrow's CE/PE predictions!** |

---

## 📱 Sample Telegram Alerts

### **1. Daily 4:30 PM Report**

```
🎯 DAILY F&O OPPORTUNITIES REPORT
📅 Date: 20-Feb-2026
⏰ Generated at: 04:30 PM
========================================

📊 INDEX SIGNALS (Top Picks)

NIFTY50
  Spot: ₹21,550.00
  Signal: CALL (85% confidence)
  Strike: 21550
  Premium: ₹180.00
  Target: ₹324.00 (+80%)
  Stop Loss: ₹108.00 (-40%)
  RSI: 58 | IV: 18%
  Days to Expiry: 7

BANKNIFTY
  Spot: ₹46,800.00
  Signal: PUT (82% confidence)
  Strike: 46800
  Premium: ₹220.00
  Target: ₹396.00 (+80%)
  Stop Loss: ₹132.00 (-40%)
  RSI: 42 | IV: 22%
  Days to Expiry: 7

📈 TOP F&O STOCK OPPORTUNITIES

1. RELIANCE
   CALL @ ₹95.00 → Target: ₹171.00
   Confidence: 78% | RSI: 62

2. HDFCBANK
   PUT @ ₹110.00 → Target: ₹198.00
   Confidence: 76% | RSI: 44

========================================
✅ Total Opportunities: 5
📊 Indices: 2 signals
📈 Stocks: 3 signals

⚠️ Risk Management:
• Always use stop loss (-40%)
• Book profit at target (+80%)
• Max 2% capital per trade
• Avoid trading on expiry day

💡 Next Steps:
1. Review signals in dashboard
2. Place trades tomorrow morning (9:20-9:30 AM)
3. Monitor positions throughout the day
4. Book profits at targets

📱 Check dashboard for detailed analysis
```

### **2. Low Premium Alert**

```
💎 LOW PREMIUM OPPORTUNITIES (₹3-15)

These options have 5-10x potential:

1. NIFTY CE 22000
   Premium: ₹8.50
   Target: ₹42.50 (5.0x)
   Distance: 2.1% OTM
   Score: 85/100
   Days: 7

2. BANKNIFTY PE 46000
   Premium: ₹12.00
   Target: ₹60.00 (5.0x)
   Distance: 1.7% OTM
   Score: 82/100
   Days: 7

⚠️ Risk Warning:
Deep OTM options are high risk. Only use 1-2% capital per trade.
These can expire worthless if market doesn't move.

💡 Strategy:
• Buy only with strong technical confirmation
• Book partial profits at 3x
• Let runners go for 5-10x
• Cut loss if premium drops 50%
```

### **3. Theta Decay Alert**

```
⚠️ THETA DECAY ALERT

Your options are losing value to time decay:

NIFTY CE 21500
  Current: ₹95.00
  Theta: ₹45.00/day
  Daily Decay: ₹45.00 (47.4%)
  Days to Expiry: 2
  Severity: CRITICAL

  💡 ROLLOVER SUGGESTION:
  • Close 21500 @ ₹95.00
  • Open 21600 @ ₹110.00
  • Net Cost: ₹15.00
  • New Expiry: 9 days

⚡ Action Required:
• Close expiring positions ASAP
• Roll to next week if still bullish/bearish
• Or book whatever profit/loss remains

⏰ Theta decay accelerates in last 3 days!
```

---

## 🎯 Your Daily Trading Routine (Fully Automated)

### **Evening (Previous Day) - 4:30 PM**
1. ✅ Bot scans market automatically
2. ✅ You receive Telegram alert with tomorrow's signals
3. ✅ Review signals at your convenience (no rush)

### **Next Morning - 9:00 AM**
1. ✅ Bot sends morning reminder
2. ✅ Check dashboard: `http://localhost:8501`
3. ✅ Go to "Strategy Selector"
4. ✅ Signals already loaded from yesterday's scan

### **9:20-9:30 AM - Trade Execution**
1. Click "Execute" on recommended strategies
2. Bot places trades and sends Telegram confirmation
3. **Done! You can close laptop now**

### **During Market Hours - Bot Works**
- ✅ Updates positions every 30 minutes
- ✅ Checks stop-loss and targets automatically
- ✅ Monitors theta decay
- ✅ Sends alerts if action needed

### **Evening - 3:30 PM**
- ✅ Market closes
- ✅ Bot sends P&L summary
- ✅ Review performance

### **4:30 PM**
- ✅ Tomorrow's scan arrives
- **Cycle repeats!**

---

## 💡 Advanced: Run Bot 24/7 on Cloud

Want the bot to run even when your PC is off?

### **Option 1: Keep PC On (Simple)**
- Just keep `START_AUTO_BOT.bat` running
- Minimize window
- Bot runs all day

### **Option 2: Cloud Server (Advanced)**
1. **Google Cloud / AWS / DigitalOcean**
2. **Upload code to server**
3. **Run:** `nohup python auto_trading_bot.py &`
4. **Bot runs 24/7 even if you close laptop!**

### **Option 3: Raspberry Pi (Budget)**
- Run on Raspberry Pi at home
- Very low power consumption
- Always-on trading bot

---

## 📊 What Gets Automated vs What You Do

### ✅ **Bot Does Automatically:**
- Market scanning (indices + stocks)
- Technical analysis (RSI, EMA, ADX, etc.)
- Signal generation
- Position monitoring
- Stop-loss/target checking
- Theta decay tracking
- Alert sending (Telegram)
- Performance tracking

### 👤 **You Only Do:**
- Review signals (takes 2 minutes)
- Click "Execute" on trades you like
- Make final decision (bot suggests, you decide)
- Review end-of-day performance

**Total time: ~10 minutes per day!**

---

## 🔧 Configuration Options

Edit `config/config.py` to customize bot behavior:

```python
# How often to scan
SCAN_INTERVALS = {
    "daily_scan": "16:30",      # 4:30 PM
    "premium_scan_hours": 2,    # Every 2 hours
    "theta_check_hours": 1,     # Every hour
    "position_update_min": 30,  # Every 30 minutes
}

# Alert preferences
ALERT_CONFIG = {
    "morning_reminder": True,
    "market_close_summary": True,
    "theta_alerts": True,
    "premium_alerts": True,
    "daily_scan_report": True,
}

# Telegram
TELEGRAM_CONFIG = {
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
}
```

---

## 📱 WhatsApp Integration (Optional)

### **Enable WhatsApp Alerts:**

**Method 1: CallMeBot (Free)**

1. Save **+34 644 17 04 03** to your contacts as "CallMeBot"
2. Send this message via WhatsApp: 
   ```
   I allow callmebot to send me messages
   ```
3. You'll receive an API key
4. Add to `config/config.py`:
   ```python
   WHATSAPP_CONFIG = {
       "phone": "YOUR_PHONE_WITH_COUNTRY_CODE",  # e.g., "919876543210"
       "apikey": "YOUR_API_KEY_FROM_CALLMEBOT"
   }
   ```

**Method 2: Twilio (Paid, Official)**
- Sign up at twilio.com
- Get WhatsApp Business API
- More reliable but costs ~$1/month

---

## 🐛 Troubleshooting

### **Bot Not Sending Alerts**

**Check:**
1. Is bot running? (Window should be open)
2. Is Telegram token correct in config?
3. Test manually: `python auto_trading_bot.py test`

### **Bot Stopped**

**Restart:**
- Double-click `START_AUTO_BOT.bat` again
- Check for errors in console

### **Missing Scans**

**Fix:**
- Bot must be running during scheduled time
- If PC was off at 4:30 PM, scan won't run
- Run manually: `python auto_trading_bot.py scan`

---

## 📊 Bot Logs

All bot activity is logged. Check console output:

```
[16:30:00] 📊 Running Daily Scan...
[16:30:15] ✅ NIFTY: CALL @ 180
[16:30:18] ✅ BANKNIFTY: PUT @ 220
[16:30:25] ✅ Daily scan complete: 5 signals
[16:30:30] ✅ Telegram alert sent!
```

---

## 🎯 Success Metrics

**With Bot Running:**
- ✅ Never miss 4:30 PM daily scan
- ✅ Never miss low premium opportunities
- ✅ Never lose to theta decay (get alerts)
- ✅ Never miss stop-loss/targets
- ✅ Save 4+ hours daily of market watching

**Manual Trading:**
- ❌ Have to watch market all day
- ❌ Miss opportunities
- ❌ Forget to close positions
- ❌ Lose to theta decay

---

## 🚀 Quick Start Checklist

Before running bot for first time:

- [ ] `pip install -r requirements.txt` completed
- [ ] Telegram bot token configured
- [ ] Dashboard tested (`streamlit run fo_options_app.py`)
- [ ] Know your timezone (IST assumed)
- [ ] Read this guide completely
- [ ] Ready to receive alerts!

**Then:**

1. Double-click `START_AUTO_BOT.bat`
2. Wait for 4:30 PM (or run test: `python auto_trading_bot.py test`)
3. Check Telegram for alert
4. ✅ You're automated!

---

## 📞 Support

**Bot Commands:**
```bash
python auto_trading_bot.py         # Run continuously
python auto_trading_bot.py scan    # Run daily scan now
python auto_trading_bot.py premium # Run premium scan now
python auto_trading_bot.py theta   # Run theta monitor now
python auto_trading_bot.py test    # Test all functions
```

---

## 🎉 You're Now a Smart Trader!

**Before:** Watch market 6+ hours daily, miss opportunities, manual analysis

**After:** Bot works 24/7, you spend 10 minutes daily, never miss signals!

---

**Created with ❤️ for traders who value their time!**

*Let the bot do the hard work. You make the decisions.*
