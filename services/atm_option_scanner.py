"""
ATM Option Scanner - Top 5 CE/PE Finder
Scans 180+ F&O stocks to find best ATM option opportunities
"""
import random
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.market_engine import (
    fetch_realtime_price, 
    get_real_option_price,
    get_days_to_expiry,
    calculate_indicators
)

# NSE F&O Stock Universe (180+ stocks)
NSE_FNO_STOCKS = [
    # Nifty 50
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", 
    "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "BAJFINANCE", "ASIANPAINT", "MARUTI",
    "SUNPHARMA", "TITAN", "ULTRACEMCO", "WIPRO", "NESTLEIND", "NTPC", "POWERGRID",
    "M&M", "HCLTECH", "TATASTEEL", "ADANIENT", "ADANIPORTS", "BAJAJFINSV", "TECHM",
    "ONGC", "COALINDIA", "JSWSTEEL", "BPCL", "GRASIM", "CIPLA", "DRREDDY", "DIVISLAB",
    "BRITANNIA", "EICHERMOT", "HEROMOTOCO", "APOLLOHOSP", "TATACONSUM", "SBILIFE",
    "HDFCLIFE", "BAJAJ-AUTO", "INDUSINDBK", "HINDALCO", "UPL", "LTIM",
    
    # Bank Nifty
    "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "PNB", "BANKBARODA", "AUBANK",
    
    # Fin Nifty  
    "ICICIPRULI", "MUTHOOTFIN", "CHOLAFIN", "ICICIGI", "SBICARD", "PFC", "RECLTD",
    "SHRIRAMFIN", "M&MFIN",
    
    # Midcap & Other FNO Stocks
    "MPHASIS", "VOLTAS", "PETRONET", "ABCAPITAL", "ASTRAL", "AUROPHARMA", "BATAINDIA",
    "CANBK", "COFORGE", "CONCOR", "CUB", "CUMMINSIND", "ESCORTS", "GMRINFRA",
    "GODREJPROP", "IPCALAB", "JUBLFOOD", "LICHSGFIN", "MRF", "MFSL", "NAVINFLUOR",
    "OBEROIRLTY", "PIIND", "TORNTPHARM", "TRENT", "DALBHARAT", "DIXON", "NAUKRI",
    "INDHOTEL", "PERSISTENT", "ZYDUSLIFE", "LODHA", "TIINDIA", "VEDL", "ADANIPOWER",
    "JSWENERGY", "ATGL", "IOC", "GAIL", "HINDPETRO", "SAIL", "NMDC", "NATIONALUM",
    "JINDALSTEL", "TATAMOTORS", "ASHOKLEY", "TVSMOTOR", "MOTHERSON", "BALKRISIND",
    "APOLLOTYRE", "MGL", "IGL", "TORNTPOWER", "TATAPOWER", "ADANIGREEN", "SUZLON",
    "IRCTC", "IRFC", "HAL", "BEL", "BHEL", "CESC", "ABB", "SIEMENS", "CROMPTON",
    "HAVELLS", "POLYCAB", "VOLTAS", "BERGEPAINT", "PIDILITIND", "KANSAINER",
    "LALPATHLAB", "METROPOLIS", "MAXHEALTH", "FORTIS", "AARTIIND", "DEEPAKNTR",
    "CLEAN", "FLUOROCHEM", "GNFC", "CHAMBLFERT", "COROMANDEL", "FACT", "GSFC",
    "TATACHEM", "ATUL", "SRF", "JUBILANT", "SYNGENE", "BIOCON", "ALKEM", "LUPIN",
    "GLENMARK", "TORNTPHARM", "CIPLA", "SUNPHARMA", "DRREDDY", "DIVISLAB", "AUROPHARMA",
    "GRANULES", "NATCOPHARM", "LAURUSLABS", "IPCALAB", "MANKIND", "ZYDUSLIFE",
    "INDIAMART", "NAUKRI", "ZOMATO", "POLICYBZR", "PAYTM", "DELHIVERY", "ZEEL",
    "PVR", "PVRINOX", "IDEA", "BHARTIARTL", "TATACOMM", "MARICO", "DABUR",
    "GODREJCP", "COLPAL", "EMAMILTD", "PAGEIND", "VBL", "TATACONSUM", "BRITANNIA",
    "NESTLEIND", "ITC", "HINDUNILVR", "BALKRISIND", "CEAT", "GOODYEAR", "JK",
    "BAJAJELEC", "CROMPTON", "HAVELLS", "INDIACEM", "ULTRACEMCO", "RAMCOCEM",
    "AMBUJACEM", "ACC", "SHREECEM", "HEIDELBERG", "JKCEMENT", "BIRLACEM",
]

def get_atm_strike(spot_price):
    """Calculate ATM (At-The-Money) strike price"""
    if spot_price > 2000:
        step = 100
    elif spot_price > 500:
        step = 50
    elif spot_price > 100:
        step = 10
    else:
        step = 5
    
    atm = round(spot_price / step) * step
    return atm, step

def scan_stock_atm_options(stock_symbol):
    """
    Scan a single stock for ATM CE and PE options
    Returns dict with stock data and option prices
    """
    try:
        # Fetch spot price
        spot_data = fetch_realtime_price(stock_symbol, is_index=False)
        if not spot_data:
            return None
        
        spot_price = spot_data.get('lastprice', 0)
        if spot_price <= 0:
            return None
        
        # Calculate ATM strike
        atm_strike, strike_step = get_atm_strike(spot_price)
        
        # Get days to expiry
        days_to_expiry = get_days_to_expiry()
        
        # Estimate IV (simplified)
        iv = 30  # Default 30% IV
        
        # Get real option prices for ATM CE and PE
        ce_price = get_real_option_price(
            stock_symbol, atm_strike, "CE", 
            spot_price, iv, days_to_expiry
        )
        
        pe_price = get_real_option_price(
            stock_symbol, atm_strike, "PE",
            spot_price, iv, days_to_expiry
        )
        
        # Calculate premium as % of spot
        ce_premium_pct = (ce_price / spot_price) * 100
        pe_premium_pct = (pe_price / spot_price) * 100
        
        # Calculate potential profit (30% target)
        ce_target = round(ce_price * 1.30, 2)
        pe_target = round(pe_price * 1.30, 2)
        
        return {
            'stock': stock_symbol,
            'spot_price': spot_price,
            'atm_strike': atm_strike,
            'ce_price': ce_price,
            'pe_price': pe_price,
            'ce_premium_pct': ce_premium_pct,
            'pe_premium_pct': pe_premium_pct,
            'ce_target': ce_target,
            'pe_target': pe_target,
            'days_to_expiry': days_to_expiry,
            'total_premium': ce_price + pe_price,
            'ce_pe_ratio': ce_price / pe_price if pe_price > 0 else 0
        }
        
    except Exception as e:
        print(f"Error scanning {stock_symbol}: {e}")
        return None

def scan_all_fno_stocks(stock_list=None, max_stocks=180, max_workers=10):
    """
    Scan multiple F&O stocks in parallel
    
    Args:
        stock_list: List of stocks to scan (None = random selection)
        max_stocks: Maximum number of stocks to scan
        max_workers: Number of parallel workers
    
    Returns:
        DataFrame with all scanned stocks
    """
    # Select stocks
    if stock_list is None:
        # Random selection from universe
        available_stocks = NSE_FNO_STOCKS[:max_stocks]
        random.shuffle(available_stocks)
        stocks_to_scan = available_stocks[:max_stocks]
    else:
        stocks_to_scan = stock_list[:max_stocks]
    
    print(f"\n{'='*70}")
    print(f"🔍 SCANNING {len(stocks_to_scan)} F&O STOCKS FOR ATM OPTIONS")
    print(f"{'='*70}\n")
    
    results = []
    completed = 0
    
    # Parallel scanning
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_stock_atm_options, stock): stock 
            for stock in stocks_to_scan
        }
        
        for future in as_completed(futures):
            stock = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                completed += 1
                
                if completed % 20 == 0:
                    print(f"Progress: {completed}/{len(stocks_to_scan)} stocks scanned...")
                
            except Exception as e:
                print(f"Error processing {stock}: {e}")
    
    print(f"\n✅ Scan Complete: {len(results)} stocks with valid data\n")
    
    # Convert to DataFrame
    if results:
        df = pd.DataFrame(results)
        return df
    else:
        return pd.DataFrame()

def get_top_5_ce_pe(df):
    """
    Get top 5 CE and top 5 PE options based on multiple criteria
    
    Ranking Criteria:
    - Premium value (higher is better for profit potential)
    - Premium % of spot (reasonable range)
    - Liquidity proxy (stocks with consistent pricing)
    """
    if df.empty:
        return None, None
    
    # Filter valid options (premium > 0)
    valid_df = df[(df['ce_price'] > 0) & (df['pe_price'] > 0)].copy()
    
    if valid_df.empty:
        return None, None
    
    # Calculate scoring for CE
    valid_df['ce_score'] = (
        valid_df['ce_price'] * 0.5 +  # Absolute premium value
        valid_df['ce_premium_pct'] * 2  # Premium % weight
    )
    
    # Calculate scoring for PE
    valid_df['pe_score'] = (
        valid_df['pe_price'] * 0.5 +
        valid_df['pe_premium_pct'] * 2
    )
    
    # Get top 5 CE
    top_5_ce = valid_df.nlargest(5, 'ce_score')[
        ['stock', 'spot_price', 'atm_strike', 'ce_price', 'ce_target', 
         'ce_premium_pct', 'days_to_expiry']
    ].copy()
    top_5_ce.columns = ['Stock', 'Spot', 'Strike', 'Entry', 'Target', 'Premium%', 'DTE']
    
    # Get top 5 PE
    top_5_pe = valid_df.nlargest(5, 'pe_score')[
        ['stock', 'spot_price', 'atm_strike', 'pe_price', 'pe_target',
         'pe_premium_pct', 'days_to_expiry']
    ].copy()
    top_5_pe.columns = ['Stock', 'Spot', 'Strike', 'Entry', 'Target', 'Premium%', 'DTE']
    
    return top_5_ce, top_5_pe

def display_results(top_5_ce, top_5_pe):
    """Display top 5 CE and PE in formatted tables"""
    print("\n" + "="*70)
    print("🏆 TOP 5 CALL OPTIONS (CE) - ATM")
    print("="*70)
    if top_5_ce is not None and not top_5_ce.empty:
        print(top_5_ce.to_string(index=False))
    else:
        print("No valid CE options found")
    
    print("\n" + "="*70)
    print("🏆 TOP 5 PUT OPTIONS (PE) - ATM")
    print("="*70)
    if top_5_pe is not None and not top_5_pe.empty:
        print(top_5_pe.to_string(index=False))
    else:
        print("No valid PE options found")
    
    print("\n" + "="*70)
    print(f"✅ Scan completed at {datetime.now().strftime('%H:%M:%S')}")
    print("="*70 + "\n")

def main():
    """Main execution"""
    print("\n🚀 PRIME SKILL - ATM OPTIONS SCANNER")
    print("Scanning 180+ F&O Stocks for Best ATM Call & Put Options\n")
    
    # Scan all stocks
    df = scan_all_fno_stocks(max_stocks=180, max_workers=15)
    
    if df.empty:
        print("❌ No data available. Check market hours or connectivity.")
        return
    
    # Get top 5 CE and PE
    top_5_ce, top_5_pe = get_top_5_ce_pe(df)
    
    # Display results
    display_results(top_5_ce, top_5_pe)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if top_5_ce is not None:
        top_5_ce.to_csv(f'data/top5_ce_{timestamp}.csv', index=False)
    if top_5_pe is not None:
        top_5_pe.to_csv(f'data/top5_pe_{timestamp}.csv', index=False)
    
    print("📁 Results saved to data/ folder")

if __name__ == "__main__":
    main()
