import logging
from utils.telegram_alert import send_telegram, format_alert
from pro_config import TELEGRAM_CHANNELS

logger = logging.getLogger("AlertRouter")

class AlertRouter:
    @staticmethod
    def route_index_trade(alert_data):
        """Sends NIFTY/BANKNIFTY entries to INDEX channel"""
        msg = format_alert(alert_data)
        return send_telegram(msg, channel="INDEX_TRADE")

    @staticmethod
    def route_stock_trade(alert_data):
        """Sends equity stock entries to STOCK channel"""
        msg = format_alert(alert_data)
        return send_telegram(msg, channel="STOCK_TRADE")

    @staticmethod
    def route_reversal(symbol, prev_sig, new_sig, strength):
        """Sends trend shift notifications to REVERSAL channel"""
        msg = (
            f"🔄 **REVERSAL CONFIRMED**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 **SYMBOL**: `{symbol}`\n"
            f"⬅️ **PREVIOUS**: `{prev_sig}`\n"
            f"➡️ **NEW SIGNAL**: `{new_sig}`\n\n"
            f"📊 **STRENGTH**: `{strength}/100`\n"
            f"⏱ **STABILITY**: `3 min confirm`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        return send_telegram(msg, channel="REVERSAL")

    @staticmethod
    def route_market_pulse(pulse_data):
        """Sends OI/PCR and global sentiment to PULSE channel"""
        msg = (
            f"📊 **MARKET PULSE UPDATE**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 **INDEX**: `{pulse_data.get('symbol')}`\n"
            f"⚖️ **PCR**: `{pulse_data.get('pcr')}`\n"
            f"🧠 **SENTIMENT**: `{pulse_data.get('sentiment')}`\n"
            f"🎯 **MAX PAIN**: `{pulse_data.get('max_pain')}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        return send_telegram(msg, channel="SENTIMENT")

    @staticmethod
    def route_news(event, impact, mode):
        """Sends News/Vol alerts to NEWS channel"""
        emoji = "🚨" if impact >= 80 else "⚡"
        msg = (
            f"{emoji} **MARKET EVENT: {event}**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 **IMPACT**: `{impact}`\n"
            f"🛡️ **MODE**: `{mode}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        return send_telegram(msg, channel="NEWS")

# Generic router function for easy access
def dispatch_alert(alert_type, **kwargs):
    if alert_type == "INDEX":
        return AlertRouter.route_index_trade(kwargs.get('alert'))
    elif alert_type == "STOCK":
        return AlertRouter.route_stock_trade(kwargs.get('alert'))
    elif alert_type == "REVERSAL":
        return AlertRouter.route_reversal(kwargs.get('symbol'), kwargs.get('prev_sig'), kwargs.get('new_sig'), kwargs.get('strength'))
    elif alert_type == "PULSE":
        return AlertRouter.route_market_pulse(kwargs.get('pulse'))
    elif alert_type == "NEWS":
        return AlertRouter.route_news(kwargs.get('event'), kwargs.get('impact'), kwargs.get('mode'))
