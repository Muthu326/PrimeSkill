import json
import urllib.request
import urllib.parse
import logging
import time
from datetime import datetime
from pro_config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHANNELS, SIGNATURE, TEST_MODE

logger = logging.getLogger("TelegramAlert")

def send_telegram(message, channel="SENTIMENT"):
    """Base sender with Institutional Channel Routing"""
    if not TELEGRAM_TOKEN: return False
    
    # Get chat_id based on channel type, fallback to main chat_id
    chat_id = TELEGRAM_CHANNELS.get(channel, TELEGRAM_CHAT_ID)
    if not chat_id: return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id, 
            'text': message, 
            'parse_mode': 'Markdown'
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')).get('ok', False)
    except Exception as e:
        logger.error(f"Telegram Error ({channel}): {e}")
        return False

def format_alert(alert):
    """Generates the rich text for institutional trade alerts with 4-Layer Verification"""
    symbol = alert.get('symbol', 'N/A')
    side = alert.get('type', 'N/A')
    strike = alert.get('strike', 'N/A')
    entry = alert.get('premium', alert.get('entry', 0))
    target = alert.get('target', 0)
    sl = alert.get('stop_loss', 0)
    conf = alert.get('score', alert.get('confidence', 60))
    opt_key = alert.get('option_key', 'N/A')
    price_ts = alert.get('price_ts', time.time())
    
    now = time.time()
    live_time_str = datetime.now().strftime("%I:%M:%S %p")
    fetch_time_str = datetime.fromtimestamp(price_ts).strftime("%H:%M:%S")
    trade_id = f"{symbol}_{strike}{side}_{datetime.now().strftime('%H%M%S')}"

    # 🛑 1. Filter out low confidence signals
    if conf < 60:
        logger.warning(f"Signal suppressed: Low Confidence ({conf}%)")
        return None

    # 🛑 2. LIVE Price Staleness Check (Max 5 seconds)
    if not TEST_MODE and (now - price_ts > 10): # Relaxed slightly to 10s for API delay
        logger.warning(f"Signal suppressed: Stale Price (Age: {now - price_ts:.1f}s)")
        return None

    # 💎 3. Header Selection
    if TEST_MODE:
        header = "🧪 TEST SIGNAL (SIMULATION ONLY)"
        price_type = "Simulated Price"
        entry_label = "ENTRY (SIMULATED)"
    else:
        price_type = "Real LTP"
        entry_label = "ENTRY (Real LTP)"
        if conf >= 85:
            header = "💎 HIGH CONVICTION SIGNAL"
        elif conf >= 70:
            header = "⚡ HIGH PROBABILITY SIGNAL"
        else:
            header = "🚨 LIVE TRADE ALERT"

    # 📊 4. Strength Classification (🔴 STRONG, 🟡 MODERATE, 🟢 MILD)
    label = "🟢 MILD"
    if conf >= 85: label = "🔴 STRONG"
    elif conf >= 70: label = "🟡 MODERATE"

    msg = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 ASSET: `{symbol}`\n"
        f"🎟 OPTION: `{strike} {side}` {'🟢' if side == 'CE' else '🔴'}\n\n"
        f"💰 {entry_label}: `₹{entry:.2f}`\n"
        f"🎯 TARGET: `₹{target:.2f}`\n"
        f"🛡 STOPLOSS: `₹{sl:.2f}`\n\n"
        f"📊 PROBABILITY: `{conf}%`\n"
        f"⚡ STRENGTH: {label}\n"
        f"📈 SIGNAL SCORE: `{conf}/100`\n\n"
        f"🔎 **DATA VERIFICATION**\n"
        f"∟ Source: `Upstox WebSocket`\n"
        f"∟ Price Type: `{price_type}`\n"
        f"∟ Instrument: `{opt_key.split('|')[-1] if '|' in opt_key else opt_key}`\n"
        f"∟ Fetched At: `{fetch_time_str}`\n"
        f"∟ Mode: `{'TEST' if TEST_MODE else 'LIVE'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 TRADE ID: `{trade_id}`\n"
        f"⏰ LIVE TIME: `{live_time_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{SIGNATURE}"
    )
    
    if TEST_MODE:
        msg += "\n\n⚠️ **THIS IS NOT LIVE MARKET PRICE**"
        
    return msg

def send_trade_alert(alert):
    """Dispatches trade alerts with suppression check"""
    msg = format_alert(alert)
    if not msg:
        return False
        
    indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX", "MIDCPNIFTY"]
    channel = "INDEX_TRADE" if any(idx in alert['symbol'] for idx in indices) else "STOCK_TRADE"
    return send_telegram(msg, channel)

def send_reversal_alert(symbol, prev_sig, new_sig, strength):
    """Institutional Reversal Tracking Alert"""
    msg = (
        f"🔄 **REVERSAL CONFIRMED**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 **SYMBOL**: `{symbol}`\n"
        f"⬅️ **PREVIOUS**: `{prev_sig}`\n"
        f"➡️ **NEW SIGNAL**: `{new_sig}`\n\n"
        f"📊 **STRENGTH**: `{strength}/100`\n"
        f"⏱ **STABILITY**: `3 min confirm`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{SIGNATURE}"
    )
    return send_telegram(msg, "REVERSAL")

def send_news_alert(event, impact, mode, pause_min=0):
    """Breaking News/Volatility Shock Alert"""
    emoji = "🚨" if impact >= 80 else "⚡"
    msg = (
        f"{emoji} **MARKET EVENT DETECTED**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚩 **EVENT**: `{event}`\n"
        f"🔥 **IMPACT**: `{impact}`\n"
        f"🛡️ **MODE**: `{mode}`\n"
    )
    if pause_min > 0:
        msg += f"⏳ **PAUSE**: `{pause_min} mins`\n"
    
    msg += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ **TIME**: `{datetime.now().strftime('%H:%M:%S')}`\n"
        f"{SIGNATURE}"
    )
    return send_telegram(msg, "NEWS")
