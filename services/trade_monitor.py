import logging
import time
import json
import os
from datetime import datetime
from utils.telegram_alert import send_telegram
from utils.helpers import get_friendly_name
from pro_config import SIGNATURE, DAILY_STATS_FILE

logger = logging.getLogger("TradeMonitor")

class TradeMonitor:
    def __init__(self):
        self.index_trades = {}
        self.stock_trades = {}
        self.SIGNATURE = SIGNATURE
        self.stats_file = DAILY_STATS_FILE
        self.stats = self.load_stats()

    def load_stats(self):
        """Loads persistent stats from file and ensures structure integrity"""
        default_stats = {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "max_gain": 0,
            "max_loss": 0,
            "by_strength": {
                "STRONG": {"wins": 0, "losses": 0},
                "MODERATE": {"wins": 0, "losses": 0},
                "MILD": {"wins": 0, "losses": 0}
            },
            "all_trades": []
        }
        
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    loaded = json.load(f)
                    # Deep Merge / Ensure Keys Exist
                    for k, v in default_stats.items():
                        if k not in loaded:
                            loaded[k] = v
                        elif isinstance(v, dict):
                            for sub_k, sub_v in v.items():
                                if sub_k not in loaded[k]:
                                    loaded[k][sub_k] = sub_v
                    return loaded
            except:
                pass
        return default_stats

    def save_stats(self):
        """Saves current session state to disk"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def register_trade(self, alert):
        """Register a new trade for monitoring"""
        symbol = alert.get('symbol', 'N/A')
        side = alert.get('type', 'N/A')
        strike = alert.get('strike', 'N/A')
        entry = alert.get('premium', 0)
        target = alert.get('target', 0)
        sl = alert.get('stop_loss', 0)
        option_key = alert.get('option_key')
        
        if not option_key:
            logger.warning(f"No option_key provided for monitoring {symbol}")
            return

        trade_data = {
            "symbol": symbol,
            "display_name": get_friendly_name(symbol),
            "side": side,
            "strike": strike,
            "entry": entry,
            "target": target,
            "stoploss": sl,
            "confidence": alert.get('score', 70),
            "status": "OPEN",
            "last_alert": None,
            "trade_type": "INDEX" if any(idx in symbol for idx in ["NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY"]) else "STOCK"
        }

        if trade_data["trade_type"] == "INDEX":
            self.index_trades[option_key] = trade_data
            logger.info(f"Registered INDEX trade for monitoring: {symbol} {strike} {side}")
        else:
            self.stock_trades[option_key] = trade_data
            logger.info(f"Registered STOCK trade for monitoring: {symbol} {strike} {side}")

    def monitor_index(self, option_key, ltp):
        trade = self.index_trades.get(option_key)
        if not trade or trade["status"] != "OPEN":
            return
        self.check_trade_logic(trade, option_key, ltp, trade_type="INDEX")

    def monitor_stock(self, option_key, ltp):
        trade = self.stock_trades.get(option_key)
        if not trade or trade["status"] != "OPEN":
            return
        self.check_trade_logic(trade, option_key, ltp, trade_type="STOCK")

    def check_trade_logic(self, trade, option_key, ltp, trade_type):
        entry = trade["entry"]
        target = trade["target"]
        stoploss = trade["stoploss"]
        symbol = trade["symbol"]
        side = trade["side"]
        strike = trade["strike"]
        conf = trade.get("confidence", 70)
        start_time = trade.get("entry_time", time.time())
        live_time = datetime.now().strftime("%I:%M:%S %p")
        
        # 🧪 Institutional Strength
        label = "🟢 MILD"
        if conf >= 85: label = "🔴 STRONG"
        elif conf >= 70: label = "🟡 MODERATE"

        gain_pct = ((ltp - entry) / entry) * 100
        hold_time = int((time.time() - start_time) / 60)

        # 🎯 TARGET ACHIEVED
        if ltp >= target:
            msg = (
                f"🎯 **TARGET ACHIEVED**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"INDEX: `{symbol}`\n"
                f"STRIKE: `{strike} {side}`\n\n"
                f"ENTRY: `₹{entry:.2f}`\n"
                f"EXIT: `₹{ltp:.2f}`\n\n"
                f"TOTAL GAIN: `+{gain_pct:.2f}%` 🟢\n"
                f"HOLD TIME: `{hold_time} MIN`\n\n"
                f"📊 PROBABILITY WAS: `{conf}%`\n"
                f"⚡ SIGNAL GRADE: {label}\n\n"
                f"⏰ {live_time}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{self.SIGNATURE}"
            )
            send_telegram(msg, channel="INDEX_TRADE")
            trade["status"] = "CLOSED"
            # Record Stats
            self.stats["total"] += 1
            self.stats["wins"] += 1
            self.stats["max_gain"] = max(self.stats["max_gain"], gain_pct)
            
            # Record Strength-based stats
            s_key = label.split(" ")[-1] # STRONG, MODERATE, MILD
            if s_key in self.stats["by_strength"]:
                self.stats["by_strength"][s_key]["wins"] += 1

            self.save_stats()
            return

        # ❌ EXIT – STOPLOSS
        if ltp <= stoploss:
            loss_pct = ((ltp - entry) / entry) * 100
            msg = (
                f"❌ **EXIT – STOPLOSS**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"INDEX: `{symbol}`\n"
                f"STRIKE: `{strike} {side}`\n\n"
                f"ENTRY: `₹{entry:.2f}`\n"
                f"EXIT: `₹{ltp:.2f}`\n\n"
                f"TOTAL LOSS: `{loss_pct:.2f}%` 🔴\n"
                f"HOLD TIME: `{hold_time} MIN`\n\n"
                f"⚡ STRENGTH WAS: {label}\n"
                f"⚠️ REVERSAL DETECTED\n\n"
                f"⏰ {live_time}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{self.SIGNATURE}"
            )
            send_telegram(msg, channel="INDEX_TRADE")
            trade["status"] = "CLOSED"
            
            # Record Stats
            self.stats["total"] += 1
            self.stats["losses"] += 1
            self.stats["max_loss"] = min(self.stats["max_loss"], loss_pct)
            
            # Record Strength-based stats
            s_key = label.split(" ")[-1]
            if s_key in self.stats["by_strength"]:
                self.stats["by_strength"][s_key]["losses"] += 1

            self.save_stats()
            return

        # 🚀 LIVE PERFORMANCE UPDATE (Progress > 60%)
        if target > entry:
            progress = (ltp - entry) / (target - entry)
            if progress >= 0.6 and trade["last_alert"] != "GOING":
                from services.news_engine import get_news_engine
                mode, _ = get_news_engine().get_market_mode()
                
                msg = (
                    f"📈 **LIVE PERFORMANCE UPDATE**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"INDEX: `{symbol}`\n"
                    f"STRIKE: `{strike} {side}`\n\n"
                    f"ENTRY: `₹{entry:.2f}`\n"
                    f"CMP: `₹{ltp:.2f}`\n"
                    f"RETURN: `+{gain_pct:.2f}%` 🟢\n\n"
                    f"TARGET PROGRESS: `{progress*100:.0f}%`\n\n"
                    f"⚡ STRENGTH: {label}\n"
                    f"🧠 MODE: `{mode}`\n\n"
                    f"⏰ {live_time}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{self.SIGNATURE}"
                )
                send_telegram(msg, channel="INDEX_TRADE")
                trade["last_alert"] = "GOING"

    def send_daily_summary(self):
        """Dispatches the End-of-Day Performance Report"""
        if self.stats["total"] == 0:
            return
            
        win_rate = (self.stats["wins"] / self.stats["total"]) * 100
        
        msg = (
            f"📊 **LIVE PERFORMANCE REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 DATE: `{datetime.now().strftime('%d-%b-%Y')}`\n\n"
            f"🎯 TOTAL TRADES: `{self.stats['total']}`\n"
            f"✅ TARGET HIT: `{self.stats['wins']}`\n"
            f"❌ STOPLOSS: `{self.stats['losses']}`\n"
            f"📈 ACCURACY: `{win_rate:.1f}%`\n\n"
            f"💰 BEST TRADE: `+{self.stats['max_gain']:.2f}%`\n"
            f"📉 MAX LOSS: `{self.stats['max_loss']:.2f}%`\n\n"
            f"🏛 System Performance: `STABLE`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{self.SIGNATURE}"
        )
        send_telegram(msg)
        logger.info("EOD Performance Summary Dispatched.")

    def send_concept_accuracy(self):
        """Dispatches an Institutional Concept Performance Breakdown"""
        s = self.stats["by_strength"]
        
        def calc_acc(key):
            total = s[key]["wins"] + s[key]["losses"]
            if total == 0: return "N/A"
            return f"{(s[key]['wins']/total)*100:.1f}%"

        msg = (
            f"🧠 **INSTITUTIONAL CONCEPT ACCURACY**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **MODEL PERFORMANCE TRACK**\n\n"
            f"🔴 **STRONG SIGNALS**\n"
            f"∟ Accuracy: `{calc_acc('STRONG')}`\n"
            f"∟ W: `{s['STRONG']['wins']}` | L: `{s['STRONG']['losses']}`\n\n"
            f"🟡 **MODERATE SIGNALS**\n"
            f"∟ Accuracy: `{calc_acc('MODERATE')}`\n"
            f"∟ W: `{s['MODERATE']['wins']}` | L: `{s['MODERATE']['losses']}`\n\n"
            f"🟢 **MILD SIGNALS**\n"
            f"∟ Accuracy: `{calc_acc('MILD')}`\n"
            f"∟ W: `{s['MILD']['wins']}` | L: `{s['MILD']['losses']}`\n\n"
            f"🏆 **CONCEPT OVERALL**: `{'WINNING' if self.stats['wins'] >= self.stats['losses'] else 'RECOVERING'}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{self.SIGNATURE}"
        )
        send_telegram(msg, channel="SENTIMENT")
        logger.info("Institutional Concept Accuracy Dispatched.")


# Singleton
_monitor = TradeMonitor()

def get_trade_monitor():
    return _monitor
