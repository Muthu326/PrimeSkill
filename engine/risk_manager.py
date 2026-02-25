from pro_config import DAILY_LIMITS

def risk_check(symbol, daily_stats, active_signals, vix_value, adx_value, power_mode=False):
    """
    Final risk gate before sending an alert.
    """
    total_trades = sum(daily_stats.get('counts', {}).values())
    
    # 1. Daily Limit
    if total_trades >= 15: # Total cap
        return False, "Daily trade limit reached"

    # 2. VIX Check
    if vix_value > 25 and not power_mode:
        return False, "VIX too high for standard breakout"

    # 3. Sideways Index Check
    if adx_value < 15:
        return False, "Index in strong sideways zone (ADX < 15)"

    # 4. Duplicate Check
    if any(s['symbol'] == symbol for s in active_signals):
        return False, "Signal already active for this symbol"

    return True, "Passed Risk Check"
