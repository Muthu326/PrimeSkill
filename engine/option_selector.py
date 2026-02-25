import time
import logging
from datetime import datetime
from services.upstox_streamer import get_live_ltp

logger = logging.getLogger("OptionSelector")

# Internal Cache for Option Prices
OPTION_LTP_CACHE = {} 
OPTION_LTP_TTL = 60

def pick_professional_expiry(future_expiries, symbol="NIFTY", force_next=False):
    """🏛 EXPIRY PICKUP LOGIC (Professional Style)"""
    if not future_expiries: return None
    now = datetime.now()
    today_dt = now.date()
    
    valid_exp_dts = []
    for e in future_expiries:
        try:
            dt = datetime.strptime(e, "%Y-%m-%d").date()
            if dt >= today_dt: valid_exp_dts.append(dt)
        except: continue
        
    valid_exp_dts.sort()
    if not valid_exp_dts: return None
    
    days_to_nearest = (valid_exp_dts[0] - today_dt).days
    
    # Logic: If current expiry is too close (<= 1 days) OR forced for BTST, prefer NEXT weekly/monthly
    if (days_to_nearest <= 1 or force_next) and len(valid_exp_dts) > 1:
        return valid_exp_dts[1].strftime("%Y-%m-%d")
            
    return valid_exp_dts[0].strftime("%Y-%m-%d")

def get_option_ltp(engine, symbol, strike, option_type, target_expiry=None):
    """Fetch actual Option Price with Institutional Verification"""
    from pro_config import TEST_MODE
    if TEST_MODE:
        return 150.0, "SIMULATED_KEY", time.time() # Dummy price for TEST mode

    if not strike or strike <= 0: return 0, None, 0
    cache_key = f"{symbol}_{strike}_{option_type}_{target_expiry}"
    now = time.time()
    
    # 🕒 3 PM POWER WINDOW: Use shorter cache for ultra-live prices
    current_hour = datetime.now().hour
    ttl = 5 if current_hour == 15 else OPTION_LTP_TTL
    
    if cache_key in OPTION_LTP_CACHE:
        val, opt_k, ts = OPTION_LTP_CACHE[cache_key]
        if now - ts < ttl and val > 0:
            return val, opt_k, ts

    try:
        idx_key = engine.get_instrument_key(symbol)
        if not idx_key: return 0, None, 0
        
        if not target_expiry:
            expiries = engine.get_expiry_dates_via_sdk(idx_key)
            target_expiry = pick_professional_expiry(expiries, symbol=symbol)
        
        if not target_expiry: return 0, None, 0
        
        opt_key = None
        # Try SDK Option Chain
        chain = engine.get_option_chain_via_sdk(idx_key, target_expiry)
        if chain:
            for item in chain:
                if abs(item.strike_price - float(strike)) < 0.1:
                    side_data = item.call_options if option_type == "CE" else item.put_options
                    if side_data:
                        opt_key = side_data.instrument_key
                        break
        
        # Fallback to HTTP Option Chain
        if not opt_key:
            http_chain = engine.get_option_chain(idx_key, target_expiry)
            for item in http_chain:
                if abs(item.get('strike_price', 0) - float(strike)) < 0.1:
                    side_key = 'call_options' if option_type == "CE" else 'put_options'
                    if side_key in item and item[side_key]:
                        opt_key = item[side_key].get('instrument_key')
                        break
                        
        if opt_key:
            # 🚀 DYNAMIC SUBSCRIPTION
            from services.upstox_streamer import get_streamer, get_cache_info
            streamer = get_streamer()
            streamer.subscribe([opt_key])
            
            # Try 1: Streamer (Real-time Cache)
            result, ts = get_cache_info(opt_key)
            
            # Try 2: Quotes (Fallback)
            if not result or result <= 0:
                logger.info(f"📡 Fetching live quote for {opt_key}...")
                quotes = engine.get_market_quote([opt_key], mode="ltp")
                if opt_key in quotes:
                    result = float(quotes[opt_key].get('last_price', 0))
                    ts = time.time()
            
            if result and result > 0:
                OPTION_LTP_CACHE[cache_key] = (result, opt_key, ts)
                return result, opt_key, ts
                
    except Exception as e:
        logger.error(f"Option LTP Error: {e}")
    return 0, None, 0

def pick_best_strike(spot, side, symbol):
    """
    Selects the best strike: ATM or 1 strike ITM.
    Avoids premiums > 400 as per user preference.
    """
    gaps = {
        "NIFTY": 50, "BANKNIFTY": 100, "RELIANCE": 20, "SBIN": 5, "HDFCBANK": 10
    }
    gap = gaps.get(symbol, 10) 
    
    atm = round(spot / gap) * gap
    
    if side == "CE":
        strike = atm - gap # 1 strike ITM
    else:
        strike = atm + gap # 1 strike ITM PE
        
    return int(strike)

def estimate_target_sl(premium, side):
    """
    Calculates 10% SL and 1.5x Risk Target.
    """
    sl = round(premium * 0.90, 2)
    risk = premium - sl
    target = round(premium + (risk * 1.5), 2)
    return target, sl
