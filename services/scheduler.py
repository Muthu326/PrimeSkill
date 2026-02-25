import time
import logging
from datetime import datetime
from engine.intelligence_engine import get_intel_engine
from utils.telegram_alert import send_telegram
from utils.alert_router import dispatch_alert

logger = logging.getLogger("Scheduler")

class InstitutionalScheduler:
    def __init__(self):
        self.intel = get_intel_engine()
        self.reports_sent = {
            "blueprint": False,
            "global": False,
            "tactical": False
        }

    def run_blueprint(self):
        """Send Tomorrow Market Blueprint at 3:35 PM"""
        logger.info("Generating Tomorrow Market Blueprint...")
        nifty_intel = self.intel.calculate_tomorrow_bias("NIFTY")
        bank_intel = self.intel.calculate_tomorrow_bias("BANKNIFTY")
        
        if not nifty_intel: return

        msg = (
            f"🏛 **INSTITUTIONAL MARKET BLUEPRINT**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 DATE: `{datetime.now().strftime('%d-%b-%Y')}`\n\n"
            f"📊 **NIFTY 50 OUTLOOK**\n"
            f"∟ PCR: `{nifty_intel['pcr']}`\n"
            f"∟ MAX PAIN: `{nifty_intel['max_pain']}`\n"
            f"∟ BIAS: `{'🟢' if nifty_intel['bias'] == 'BULLISH' else '🔴'} {nifty_intel['bias']}`\n"
            f"∟ PROBABILITY: `{nifty_intel['prob']}%`\n\n"
            f"🚀 **CE ABOVE**: `{nifty_intel['ce_level']}`\n"
            f"🩸 **PE BELOW**: `{nifty_intel['pe_level']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏦 **BANKNIFTY**\n"
            f"∟ BIAS: `{bank_intel['bias'] if bank_intel else 'SIDEWAYS'}`\n"
            f"∟ PROBABILITY: `{bank_intel['prob'] if bank_intel else 50}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **STRATEGY**:\n"
            f"Wait for 9:20 AM candle confirmation.\n"
            f"Avoid blind gap trading.\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Prime Skill Development"
        )
        send_telegram(msg, channel="SENTIMENT")
        logger.info("Tomorrow Blueprint Dispatched.")

    def run_global_brief(self):
        """Send Early Morning Global Brief at 8:30 AM"""
        logger.info("Generating Global Pre-Market Brief...")
        data = self.intel.get_global_data()
        
        msg = (
            f"🌍 **GLOBAL PRE-MARKET BRIEF**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📈 **US MARKET**: `{data['us']}`\n"
            f"🌏 **ASIA**: `{data['asia']}`\n"
            f"🛢 **CRUDE**: `{data['crude']}`\n"
            f"💵 **DXY**: `{data['dxy']}`\n\n"
            f"📉 **INDIA VIX**: `{data['vix']}`\n\n"
            f"🎯 **GAP EXPECTATION**:\n"
            f"`{data['gap']}`\n\n"
            f"🛡️ **MARKET MODE**: `{data['mode']}`\n\n"
            f"✅ **Action**: No trade before 9:20 AM.\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        send_telegram(msg, channel="NEWS")
        logger.info("Global Brief Dispatched.")

    def run_tactical_plan(self):
        """Send Pre-Market Tactical Plan at 9:10 AM"""
        logger.info("Generating 9:10 AM Tactical Plan...")
        levels = self.intel.get_tactical_range("NIFTY")
        
        msg = (
            f"⚡ **PRE-MARKET TACTICAL PLAN**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 **NIFTY RANGE**:\n"
            f"`{levels['nifty_range']}`\n\n"
            f"📈 IF BREAK ABOVE → CE Momentum\n"
            f"📉 IF BREAK BELOW → PE Scalp\n\n"
            f"🏦 **BANKNIFTY**:\n"
            f"`{levels['bank_range']}`\n\n"
            f"🚀 **STOCKS TO WATCH**:\n"
            f"`{levels['stocks']}`\n\n"
            f"⏳ **RULE**: Wait for 9:20 AM candle.\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        send_telegram(msg, channel="INDEX_TRADE")
        logger.info("Tactical Plan Dispatched.")

    def check_schedule(self):
        """The heartbeat that checks time and triggers reports"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")

        # 1. Tomorrow Blueprint (3:35 PM)
        if time_str == "15:35" and not self.reports_sent["blueprint"]:
            self.run_blueprint()
            self.reports_sent["blueprint"] = True

        # 2. Morning Brief (8:30 AM)
        if time_str == "08:30" and not self.reports_sent["global"]:
            self.run_global_brief()
            self.reports_sent["global"] = True

        # 3. Tactical Plan (9:10 AM)
        if time_str == "09:10" and not self.reports_sent["tactical"]:
            self.run_tactical_plan()
            self.reports_sent["tactical"] = True

        # Reset flags at midnight
        if time_str == "00:00":
            self.reports_sent = {k: False for k in self.reports_sent}

# Singleton
_scheduler = InstitutionalScheduler()

def get_scheduler():
    return _scheduler
