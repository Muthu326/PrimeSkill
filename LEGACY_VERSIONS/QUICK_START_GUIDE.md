# 🚀 QUICK START GUIDE
## F&O Options Trading System

**Created by:** MuthuKumar Krishnan  
**PRIME SKILL DEVELOPMENT**

---

## ⚡ 5-Minute Setup

### Step 1: Install Python Dependencies

Open Command Prompt in the PrimeSkill folder and run:

```bash
pip install -r requirements.txt
```

**Wait for installation to complete (2-3 minutes)**

---

### Step 2: Launch the Dashboard

**Option A:** Double-click `START_FO_OPTIONS.bat`

**Option B:** Run in Command Prompt:
```bash
streamlit run fo_options_app.py
```

**The dashboard will open automatically in your browser!**

URL: `http://localhost:8501`

---

## 📱 First-Time User Guide

### 1. Dashboard Overview (Main Page)

When you first open the app, you'll see:

✅ **Market Overview** - Live prices for NIFTY, BANKNIFTY, FINNIFTY, SENSEX  
✅ **Portfolio Summary** - Your P&L, win rate, positions  
✅ **Active Positions** - Currently open trades (empty at first)  
✅ **Risk Alerts** - System warnings and suggestions

**Action:** Familiarize yourself with the layout. Everything updates in real-time!

---

### 2. Find Your First Trade (Strategy Selector)

**Click "🎯 Strategy Selector" in sidebar**

**Step-by-step:**

1. **Select Symbol:** Choose NIFTY or BANKNIFTY
2. **Days to Expiry:** Keep default (7 days for weekly)
3. **Click the screen** - System analyzes market automatically
4. **Review Recommendations:**
   - System shows best strategies for current market
   - Sorted by confidence (highest first)
   - See entry price, stop loss, target

**Example Recommendation:**

```
LONG_CALL - Confidence: 85%
Entry: ₹180
Stop Loss: ₹108 (40% loss)
Target: ₹324 (80% profit)
Risk:Reward: 1:2.0
Max Loss: ₹180
Max Profit: Unlimited

Option Legs:
- BUY CE @ Strike 21500 - Premium: ₹180.00

Bullish trend detected. RSI: 58, ADX: 32, IV: 18%
```

5. **Click "Execute LONG_CALL"** to place trade

✅ **Trade Placed!** You'll see:
- Success message
- Trade ID
- Telegram alert sent (if configured)

---

### 3. Monitor Your Position

**Click "📈 Positions" in sidebar**

You'll see:

- **Portfolio Greeks:** Delta, Gamma, Theta (time decay), Vega
- **Position Details:**
  - Entry price vs Current price
  - Real-time P&L (updates every 30 seconds)
  - Greeks for each position
  - Max profit/loss

**Closing a Position:**

1. Click the expander for your position
2. Review current P&L
3. Click "Close Position" button
4. ✅ Position closed! P&L locked in

**System automatically closes positions when:**
- Stop loss hit (-40% of premium)
- Target reached (+80% profit)

---

### 4. Check Your Performance

**Click "📉 Analytics" in sidebar**

**You'll see:**

📊 **Cumulative P&L Chart** - Your equity curve over time  
📊 **Strategy Performance** - Which strategies work best  
🏆 **Best Trades** - Your top 5 winners  
❌ **Worst Trades** - Trades to learn from

**Key Metrics:**
- Total P&L
- Win Rate %
- Average Profit per trade
- Maximum Drawdown

---

## 🎯 Strategy Quick Reference

### When to Use Each Strategy

**1. LONG CALL** → Expecting big UP move
- Market: Strong bullish trend
- Entry: When RSI 40-60, ADX > 25
- Risk: Premium paid
- Best: Before bullish news/events

**2. LONG PUT** → Expecting big DOWN move
- Market: Strong bearish trend
- Entry: When RSI 40-60, ADX > 25
- Risk: Premium paid
- Best: Before bearish news/breakdowns

**3. BULL CALL SPREAD** → Moderate UP move expected
- Market: Moderately bullish
- Entry: High IV environments
- Risk: Net debit (limited)
- Best: Reduces cost vs Long Call

**4. BEAR PUT SPREAD** → Moderate DOWN move expected
- Market: Moderately bearish
- Entry: High IV environments
- Risk: Net debit (limited)
- Best: Reduces cost vs Long Put

**5. LONG STRADDLE** → BIG move either direction
- Market: Neutral (unsure of direction)
- Entry: Before major events, Low IV
- Risk: Both premiums
- Best: Budget, RBI, Election results

**6. LONG STRANGLE** → VERY BIG move either direction
- Market: Neutral
- Entry: Very low IV
- Risk: Both premiums (cheaper than straddle)
- Best: Extreme volatility expected

---

## 💡 Pro Tips for Beginners

### ✅ DO's

1. **Start with 1 position** - Learn before scaling
2. **Follow system recommendations** - Trust the analysis
3. **Respect stop losses** - Don't hold losing trades
4. **Take profits at targets** - Don't be greedy
5. **Review trade history** - Learn from every trade
6. **Check risk alerts** - Monitor daily loss limit

### ❌ DON'Ts

1. **Don't overtrade** - Max 5 positions
2. **Don't ignore stop losses** - System auto-closes, but watch manually
3. **Don't average down** - Don't add to losing positions
4. **Don't trade without signal** - Wait for recommendations
5. **Don't risk more than 20%** - System blocks but be aware
6. **Don't trade near expiry** - Avoid last 2 days (time decay accelerates)

---

## 🔧 Configuration Tips

### Adjust Capital

**File:** `config/config.py`

```python
TRADING_CONFIG = {
    "initial_capital": 100000,  # Change to your amount
}
```

### Adjust Risk Limits

```python
RISK_LIMITS = {
    "stop_loss_percent": 0.40,      # 40% SL (increase for more risk)
    "target_profit_percent": 0.80,  # 80% target
}
```

### Setup Telegram Alerts

1. Create Telegram bot via @BotFather
2. Get your bot token
3. Get your chat ID
4. Update `config/config.py`:

```python
TELEGRAM_CONFIG = {
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
}
```

---

## 📱 Mobile Access

**The dashboard is mobile-responsive!**

### On Mobile Device:

1. **Find your computer's IP address:**
   - Windows: `ipconfig` (look for IPv4)
   - Example: `192.168.1.100`

2. **On mobile browser, go to:**
   ```
   http://YOUR_IP:8501
   ```
   Example: `http://192.168.1.100:8501`

3. **Bookmark it** for quick access!

**Note:** Both devices must be on same WiFi network

---

## 🐛 Common Issues & Fixes

### Issue: "streamlit: command not found"

**Fix:** Reinstall streamlit
```bash
pip install --upgrade streamlit
```

### Issue: Dashboard shows errors

**Fix 1:** Delete database and restart
```bash
del data\trades.db
streamlit run fo_options_app.py
```

**Fix 2:** Check Python version (need 3.9+)
```bash
python --version
```

### Issue: No market data loading

**Fix:** Internet required for yfinance. Check connection.

---

## 📊 Understanding the Numbers

### Option Price

**Premium = Intrinsic Value + Time Value**

- **Intrinsic:** In-the-money amount
- **Time Value:** Premium above intrinsic

**Example:**
- NIFTY @ 21500
- 21500 CE (Call) @ ₹200
- Intrinsic: ₹0 (ATM)
- Time Value: ₹200

### Greeks Simplified

**Delta (0 to 1 for calls, -1 to 0 for puts)**
- How much option price changes per ₹1 move in stock
- ATM ≈ 0.50
- Deep ITM ≈ 1.00
- Deep OTM ≈ 0.00

**Gamma**
- How fast Delta changes
- Highest for ATM options

**Theta (negative)**
- Daily time decay
- Options lose value every day
- Accelerates near expiry

**Vega**
- Sensitivity to IV changes
- Higher for ATM options
- Good when expecting volatility increase

---

## 🎓 Learning Path

### Week 1: Basics
- Run system, explore dashboard
- Place 1-2 paper trades
- Understand P&L calculation
- Review trade history

### Week 2: Strategy Testing
- Try different strategies
- Compare Long Call vs Bull Call Spread
- Test in different market conditions
- Track win rate

### Week 3: Risk Management
- Test stop losses
- See what happens at daily loss limit
- Practice position sizing
- Monitor Greeks

### Week 4: Advanced
- Analyze strategy performance
- Optimize entry/exit timing
- Develop personal rules
- Start creating trading plan

---

## 📞 Next Steps

**After you're comfortable with paper trading:**

1. **Review your stats** - Min 50 trades
2. **Identify best strategies** - What works for you?
3. **Build discipline** - Stick to rules
4. **Learn continuously** - Markets always changing
5. **Consider real trading** - ONLY after consistent paper trading success

**Remember:**
- This is educational software
- No guarantee of profits
- Options involve substantial risk
- Consult professionals before real trading

---

## 📈 Success Metrics to Track

**After 1 Month:**
- [ ] 30+ paper trades completed
- [ ] Win rate > 50%
- [ ] Following risk rules consistently
- [ ] Understand all 6 strategies
- [ ] Can explain P&L on every trade

**After 3 Months:**
- [ ] 100+ paper trades
- [ ] Win rate > 55%
- [ ] Positive cumulative P&L
- [ ] Max drawdown < 15%
- [ ] Developed personal trading rules

---

## ✅ Launch Checklist

Before you start trading:

- [ ] Python and dependencies installed
- [ ] Dashboard launches successfully
- [ ] Can see market data
- [ ] Placed and closed test trade
- [ ] Understand stop loss and target
- [ ] Reviewed risk limits in settings
- [ ] Read strategy descriptions
- [ ] Telegram alerts configured (optional)

**You're ready to trade! 🚀**

---

**Created by MuthuKumar Krishnan | PRIME SKILL DEVELOPMENT**

*Happy Trading! Remember: The goal is to learn, not to win every trade.*

---
