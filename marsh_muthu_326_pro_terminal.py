# -*- coding: utf-8 -*-
# marsh_muthu_326_pro_terminal.py
# ==========================================
# 🎯 PRIME SKILL DEVELOPMENT | ULTIMATE PRO TERMINAL
# CEO: MuthuKumar Krishnan
# ==========================================
import streamlit as st
import re
import yfinance as yf
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from contextlib import contextmanager
import os
import sys

# 🚀 ENSURE MODULE PATHS ARE CORRECT FOR STREAMLIT CLOUD
# This fixes "ModuleNotFoundError: models" by adding current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dotenv import load_dotenv
load_dotenv()

import urllib.request
import urllib.parse
import json
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.market_engine import (
    flatten_columns, option_premium_estimate, fetch_realtime_price,
    get_days_to_expiry, load_data, calculate_indicators,
    get_comprehensive_scan, get_index_price, send_telegram,
    get_real_option_price
)
from views.home import render_home
from views.fire_trade import render_fire_trade
from views.radar import render_radar
from views.chain import render_chain
from views.paper_trading import render_paper_trading
from views.conviction import render_conviction
from views.pro_engine import render_pro_engine
from views.chart import render_chart
from views.strategy_hub import render_strategy_hub
from views.fno import render_fno
from views.commodity import render_commodity
from views.trade_management import render_trade_management
from views.plans import render_plans
from views.institutional_view import render_institutional_view
from views.elite_fno_view import render_elite_fno_view
from utils.cache_manager import ScanCacheManager

# 🛡️ GLOBAL STABILITY FIX: Robust st.spinner patch for Python 3.13/3.14
@contextmanager
def st_spinner_patch(text="Loading..."):
    # Use st.status as it's more stable in multi-threaded/new environments
    # We ensure single-yield and proper exception propagation
    try:
        # Check if st.status exists (Streamlit 1.24+)
        if hasattr(st, "status"):
            with st.status(text, expanded=False) as status:
                yield
                status.update(label=f"✅ {text} Complete", state="complete", expanded=False)
        else:
            # Fallback for older Streamlit
            with st.empty():
                st.markdown(f"⏳ {text}")
                yield
    except GeneratorExit:
        # This is expected when the context manager is closed
        raise
    except Exception:
        # Re-raise any user-land exceptions so the calling code knows something failed
        raise

st.spinner = st_spinner_patch


st.set_page_config(layout="wide", page_title="PRIME SKILL DEV | Ultimate Terminal", page_icon="🎯", initial_sidebar_state="expanded")

# ==========================================
# 🔑 SMART AUTH SYNC (Daily Token Logic)
# ==========================================
def handle_upstox_auth():
    """🤝 Seamlessly syncs Upstox Token from Cloud URL"""
    from pro_config import UPSTOX_API_KEY, REDIRECT_URI
    import requests
    
    # 1. Detect if Upstox just redirected us with a code
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        st.sidebar.info("🔄 Syncing fresh Upstox Session...")
        
        # 2. Exchange Code for Access Token
        token_url = "https://api.upstox.com/v2/login/authorization/token"
        payload = {
            'code': auth_code,
            'client_id': UPSTOX_API_KEY,
            'client_secret': os.getenv("UPSTOX_API_SECRET"),
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        try:
            resp = requests.post(token_url, data=payload)
            res_data = resp.json()
            
            if "access_token" in res_data:
                # 3. Store in Session & OS Environment for the whole engine
                new_token = res_data["access_token"]
                st.session_state['UPSTOX_ACCESS_TOKEN'] = new_token
                os.environ['UPSTOX_ACCESS_TOKEN'] = new_token
                st.sidebar.success("✅ Upstox Sync Successful!")
                # Clean URL for cleaner experience
                st.query_params.clear()
            else:
                st.sidebar.error(f"❌ Sync Failed: {res_data.get('errors', [{}])[0].get('message', 'Unknown Error')}")
        except Exception as e:
            st.sidebar.error(f"⚠️ Auth Error: {e}")

# Call auth handler early
handle_upstox_auth()

def clean_symbol_name(symbol):
    """🧹 Professional Symbol Formatter (e.g., HDFCBANK -> HDFC BANK)"""
    if not isinstance(symbol, str): return symbol
    s = symbol.strip().upper().replace(".NS", "")
    replacements = {
        "HDFCBANK": "HDFC BANK", "ICICIBANK": "ICICI BANK", "KOTAKBANK": "KOTAK BANK", 
        "AXISBANK": "AXIS BANK", "INDUSINDBK": "INDUSIND BANK", "BANDHANBNK": "BANDHAN BANK",
        "IDFCFIRSTB": "IDFC FIRST BANK", "BANKBARODA": "BANK OF BARODA", "BANKINDIA": "BANK OF INDIA",
        "PNB": "PNB", "CANBK": "CANARA BANK", "FEDERALBNK": "FEDERAL BANK", "AUBANK": "AU BANK",
        "TITAN": "TITAN", "RELIANCE": "RELIANCE", "ASHOKLEY": "ASHOK LEYLAND", "APOLLOHOSP": "APOLLO HOSP",
        "BAJAJFINSV": "BAJAJ FINSERV", "BAJFINANCE": "BAJAJ FINANCE", "BHARTIARTL": "BHARTI AIRTEL",
        "HEROMOTOCO": "HERO MOTOCORP", "M&M": "M&M", "MARUTI": "MARUTI SUZUKI", "TATASTEEL": "TATA STEEL",
        "ULTRACEMCO": "ULTRATECH CEMENT", "TATACONSUM": "TATA CONSUMER", "JSWSTEEL": "JSW STEEL",
        "HINDUNILVR": "HINDUSTAN UNILEVER", "ADANIENT": "ADANI ENT", "ADANIPORTS": "ADANI PORTS",
        "COALINDIA": "COAL INDIA", "POWERGRID": "POWER GRID", "SUNPHARMA": "SUN PHARMA",
        "HDFCLIFE": "HDFC LIFE", "SBILIFE": "SBI LIFE", "SBIN": "SBI",
        "NIFTY_FIN_SERVICE": "FIN NIFTY", "NIFTY_MID_SELECT": "MIDCAP NIFTY",
        "^NSEI": "NIFTY 50", "^NSEBANK": "BANK NIFTY", "^BSESN": "SENSEX",
        "NIFTY": "NIFTY 50", "BANKNIFTY": "BANK NIFTY", "SENSEX": "SENSEX"
    }
    for k, v in replacements.items():
        if s == k: return v
    return s

# ==========================================
# ⚙️ CORE ENGINE (Functions Moved to Top)
# ==========================================
# Engine functions imported from services.market_engine

def send_eod_report(token, chat_id, sdf):
    """
    📊 Generates and sends a comprehensive Market Analysis & Prediction report.
    """
    if sdf.empty: return "No data available for analysis"
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # 1. Market Breadth
    bulls_df = sdf[sdf['Signal'].str.contains('CE', na=False)]
    bears_df = sdf[sdf['Signal'].str.contains('PE', na=False)]
    bulls = len(bulls_df)
    bears = len(bears_df)
    mkt_bias = "BULLISH" if bulls > bears * 1.5 else "BEARISH" if bears > bulls * 1.5 else "NEUTRAL/CONSOLIDATING"
    
    # 2. Top Gainers & Losers
    top5_gainers = sdf.nlargest(5, 'Chg%')[['Stock', 'Chg%']].to_dict('records')
    top5_losers = sdf.nsmallest(5, 'Chg%')[['Stock', 'Chg%']].to_dict('records')
    
    gainers_str = "\n".join([f"• {g['Stock']}: +{g['Chg%']}%" for g in top5_gainers])
    losers_str = "\n".join([f"• {l['Stock']}: {l['Chg%']}%" for l in top5_losers])
    
    # 3. Tomorrow's Watchlist (Highest Momentum)
    watchlist_ce = bulls_df.nlargest(3, 'Momentum')[['Stock', 'Signal']].to_dict('records')
    watchlist_pe = bears_df.nlargest(3, 'Momentum')[['Stock', 'Signal']].to_dict('records')
    
    watch_ce_str = "\n".join([f"🚀 {c['Stock']} ({c['Signal']})" for c in watchlist_ce]) if watchlist_ce else "None - Wait for Pullback"
    watch_pe_str = "\n".join([f"📉 {p['Stock']} ({p['Signal']})" for p in watchlist_pe]) if watchlist_pe else "None - Market Strong"

    # 4. Prediction & Strategy
    if mkt_bias == "BULLISH":
        pred_desc = "Strong momentum shift detected; Bullish bias for tomorrow."
        strat_hint = "Buy Call on dips near Support levels."
    elif mkt_bias == "BEARISH":
        pred_desc = "Sell pressure dominating; Bearish bias for tomorrow."
        strat_hint = "Buy Put on peaks near Resistance levels."
    else:
        pred_desc = "Market indecisive; Range-bound session likely."
        strat_hint = "Wait for breakout of today's High/Low."

    # 5. Full Signal Summary (Requested: "full list need")
    ce_list = bulls_df['Stock'].tolist()[:15] # Top 15 for telegram length
    pe_list = bears_df['Stock'].tolist()[:15]
    
    ce_summary = ", ".join(ce_list) if ce_list else "None"
    pe_summary = ", ".join(pe_list) if pe_list else "None"

    eod_msg = (
        f"📊 *DAILY MARKET ANALYSIS & TOMORROW'S OUTLOOK*\n"
        f"📅 {today_date} | ⏰ {datetime.now().strftime('%H:%M %p')}\n"
        f"━━━━━━━━━━━━━━\n"
        f"🚀 *Market Bias:* {mkt_bias}\n"
        f"📈 {bulls} CE (Buy) | 📉 {bears} PE (Sell)\n"
        f"━━━━━━━━━━━━━━\n"
        f"💎 *ACTIVE CE SIGNALS:* \n{ce_summary}\n\n"
        f"💀 *ACTIVE PE SIGNALS:* \n{pe_summary}\n"
        f"━━━━━━━━━━━━━━\n"
        f"🔮 *CORE WATCHLIST FOR TOMORROW:*\n"
        f"CE Targets: {watch_ce_str}\n"
        f"PE Targets: {watch_pe_str}\n"
        f"━━━━━━━━━━━━━━\n"
        f"🔮 *TOMORROW'S PREDICTION:*\n"
        f"Outlook: *{pred_desc}*\n"
        f"Strategy: *{strat_hint}*"
        f"\n━━━━━━━━━━━━━━\n"
        f"**Prime Skill Devlopment**\nCEO : MuthuKumar Krishnan."
    )
    return send_telegram(token, chat_id, eod_msg)

# ==========================================
# 📊 DATA DEFINITIONS (ALL INDICES)
# ==========================================
NIFTY_50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TATAPOWER.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NESTLEIND.NS","NTPC.NS","POWERGRID.NS","M&M.NS","HCLTECH.NS","TATASTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","BAJAJFINSV.NS","TECHM.NS","ONGC.NS","COALINDIA.NS","JSWSTEEL.NS","BPCL.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","APOLLOHOSP.NS","TATACONSUM.NS","SBILIFE.NS","HDFCLIFE.NS","BAJAJ-AUTO.NS","INDUSINDBK.NS","HINDALCO.NS","UPL.NS","LTIM.NS"]
SENSEX = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TATAPOWER.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NESTLEIND.NS","NTPC.NS","POWERGRID.NS","M&M.NS","HCLTECH.NS","TATASTEEL.NS","TECHM.NS","BAJAJFINSV.NS","INDUSINDBK.NS","JSWSTEEL.NS"]
BANKNIFTY = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","INDUSINDBK.NS","BANDHANBNK.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","PNB.NS","BANKBARODA.NS","AUBANK.NS"]
FINNIFTY = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS","MUTHOOTFIN.NS","CHOLAFIN.NS","ICICIGI.NS","SBICARD.NS","PFC.NS","RECLTD.NS","SHRIRAMFIN.NS","M&MFIN.NS","INDUSINDBK.NS","PNB.NS"]
MIDCAPNIFTY = ["MPHASIS.NS","VOLTAS.NS","PETRONET.NS","ABCAPITAL.NS","ASTRAL.NS","AUROPHARMA.NS","BATAINDIA.NS","CANBK.NS","COFORGE.NS","CONCOR.NS","CUB.NS","CUMMINSIND.NS","ESCORTS.NS","GMRINFRA.NS","GODREJPROP.NS","IPCALAB.NS","JUBLFOOD.NS","L&TFH.NS","LICHSGFIN.NS","MRF.NS","MFSL.NS","NAM-INDIA.NS","NAVINFLUOR.NS","OBEROIRLTY.NS","PIIND.NS"]
ALL_FO_STOCKS = [
    "360ONE.NS", "ABB.NS", "ABCAPITAL.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ALKEM.NS", "AMBER.NS", "AMBUJACEM.NS", "ANGELONE.NS", "APLAPOLLO.NS", "APOLLOHOSP.NS", "ASHOKLEY.NS",
    "ASIANPAINT.NS", "ASTRAL.NS", "AUBANK.NS", "AUROPHARMA.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJAJFINSV.NS",
    "BAJFINANCE.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "BDL.NS", "BEL.NS", "BHARATFORG.NS",
    "BHARTIARTL.NS", "BHEL.NS", "BIOCON.NS", "BLUESTARCO.NS", "BOSCHLTD.NS", "BPCL.NS", "BRITANNIA.NS",
    "BSE.NS", "CAMS.NS", "CANBK.NS", "CDSL.NS", "CGPOWER.NS", "CHOLAFIN.NS", "CIPLA.NS", "COALINDIA.NS",
    "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "CROMPTON.NS", "CUMMINSIND.NS", "CYIENT.NS", "DABUR.NS",
    "DALBHARAT.NS", "DELHIVERY.NS", "DIVISLAB.NS", "DIXON.NS", "DLF.NS", "DMART.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "FORTIS.NS", "GAIL.NS", "GLENMARK.NS", "GMRAIRPORT.NS",
    "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "HAL.NS", "HAVELLS.NS", "HCLTECH.NS", "HDFCAMC.NS",
    "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HFCL.NS", "HINDALCO.NS", "HINDPETRO.NS", "HINDUNILVR.NS",
    "HINDZINC.NS", "HUDCO.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDEA.NS", "IDFCFIRSTB.NS",
    "IEX.NS", "IGL.NS", "IIFL.NS", "INDHOTEL.NS", "INDIANB.NS", "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS",
    "INFY.NS", "INOXWIND.NS", "IOC.NS", "IRCTC.NS", "IREDA.NS", "IRFC.NS", "ITC.NS", "JINDALSTEL.NS",
    "JIOFIN.NS", "JSWENERGY.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KALYANKJIL.NS", "KAYNES.NS", "KEI.NS",
    "KFINTECH.NS", "KOTAKBANK.NS", "KPITTECH.NS", "LAURUSLABS.NS", "LICHSGFIN.NS", "LICI.NS", "LODHA.NS",
    "LT.NS", "LTF.NS", "LTIM.NS", "LUPIN.NS", "M&M.NS", "MANAPPURAM.NS", "MANKIND.NS", "MARICO.NS",
    "MARUTI.NS", "MAXHEALTH.NS", "MAZDOCK.NS", "MCX.NS", "MFSL.NS", "MOTHERSON.NS", "MPHASIS.NS",
    "MUTHOOTFIN.NS", "NATIONALUM.NS", "NAUKRI.NS", "NBCC.NS", "NCC.NS", "NESTLEIND.NS", "NHPC.NS",
    "NMDC.NS", "NTPC.NS", "NUVAMA.NS", "NYKAA.NS", "OBEROIRLTY.NS", "OFSS.NS", "OIL.NS", "ONGC.NS",
    "PAGEIND.NS", "PATANJALI.NS", "PAYTM.NS", "PERSISTENT.NS", "PETRONET.NS", "PFC.NS", "PGEL.NS",
    "PHOENIXLTD.NS", "PIDILITIND.NS", "PIIND.NS", "PNB.NS", "PNBHOUSING.NS", "POLICYBZR.NS", "POLYCAB.NS",
    "POWERGRID.NS", "POWERINDIA.NS", "PPLPHARMA.NS", "PRESTIGE.NS", "RBLBANK.NS", "RECLTD.NS",
    "RELIANCE.NS", "RVNL.NS", "SAIL.NS", "SBICARD.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS",
    "SHRIRAMFIN.NS", "SIEMENS.NS", "SOLARINDS.NS", "SONACOMS.NS", "SRF.NS", "SUNPHARMA.NS",
    "SUPREMEIND.NS", "SUZLON.NS", "SYNGENE.NS", "TATACONSUM.NS", "TATAELXSI.NS", "TATAMOTORS.NS",
    "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS", "TCS.NS", "TECHM.NS", "TIINDIA.NS", "TITAGARH.NS",
    "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TVSMOTOR.NS", "ULTRACEMCO.NS",
    "UNIONBANK.NS", "UNITDSPR.NS", "UNOMINDA.NS", "UPL.NS", "VBL.NS", "VEDL.NS", "VOLTAS.NS",
    "WIPRO.NS", "YESBANK.NS", "ZYDUSLIFE.NS"
]
INDEX_MAP = {
    "ALL F&O": {"ticker": "^NSEI", "google_sym": "NIFTY_50", "stocks": ALL_FO_STOCKS},
    "NIFTY 50": {"ticker": "^NSEI", "google_sym": "NIFTY_50", "stocks": NIFTY_50},
    "SENSEX": {"ticker": "^BSESN", "google_sym": "SENSEX", "stocks": SENSEX},
    "BANKNIFTY": {"ticker": "^NSEBANK", "google_sym": "NIFTY_BANK", "stocks": BANKNIFTY},
    "FINNIFTY": {"ticker": "NIFTY_FIN_SERVICE.NS", "google_sym": "NIFTY_FIN_SERVICE", "stocks": FINNIFTY},
    "MIDCAPNIFTY": {"ticker": "NIFTY_MID_SELECT.NS", "google_sym": "NIFTY_MID_SELECT", "stocks": MIDCAPNIFTY},
}

HEAVYWEIGHTS = ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS", "ITC.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS", "AXISBANK.NS"]

TRADING_QUOTES = [
    "🚀 Trade the process, not the profit.",
    "💎 Discipline is the bridge between goals and mastery.",
    "📊 Focus on setups, the money will follow.",
    "🏁 Pips are earned through patience.",
    "🛡️ Risk comes from not knowing what you're doing.",
    "✨ Your trading plan is your only boss.",
    "🏆 Success is a series of small wins repeated daily."
]

# Global data holders
if 'sdf_cache' not in st.session_state:
    st.session_state['sdf_cache'] = pd.DataFrame()
if 'paper_portfolio' not in st.session_state:
    st.session_state['paper_portfolio'] = []
if 'virtual_capital' not in st.session_state:
    st.session_state['virtual_capital'] = 100000.0

# ⚡ INSTANT LOAD: Initialize cache manager
cache_mgr = ScanCacheManager()

# Load cached data immediately for instant page load
if st.session_state['sdf_cache'].empty:
    cached_scan, cached_idx, cached_diamond = cache_mgr.load_scan_results()
    if cached_scan:
        st.session_state['sdf_cache'] = pd.DataFrame(cached_scan)
        st.session_state['index_picks'] = cached_idx
        st.session_state['diamond_picks'] = cached_diamond

sdf = st.session_state['sdf_cache']
stock_rows = []

# ==========================================
# ⏱ REFRESH CONTROL (Optimized with Toggle)
# ==========================================
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state['auto_refresh_enabled'] = True # Default to ON for live trading

refresh_interval = 30000 if st.session_state['auto_refresh_enabled'] else None # 30 Secs for near-live
refresh_counter = st_autorefresh(interval=refresh_interval, key="datarefresh") if refresh_interval else 0

# ==========================================
# ⏱ LIVE DATA STATUS (Sidebar)
# ==========================================
st.sidebar.markdown("### 🏛 Institutional Account")
from pro_config import AUTH_URL
st.sidebar.markdown(f"""
    <a href="{AUTH_URL}" target="_self">
        <button style="width:100%; height:40px; background-color:#1cffff; color:black; border:none; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:15px;">
            🔐 SYNC UPSTOX SESSION
        </button>
    </a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⏱ Live Data Engine")

# Auto-refresh toggle
auto_refresh_toggle = st.sidebar.toggle(
    "🔄 Auto-Refresh (5 min)", 
    value=st.session_state['auto_refresh_enabled'],
    help="Enable automatic data refresh every 5 minutes. Disable for faster page loads."
)
st.session_state['auto_refresh_enabled'] = auto_refresh_toggle

# Status display
# Status display
if st.session_state['auto_refresh_enabled']:
    st.sidebar.success(f"✅ Sync Success: {st.session_state.get('last_sync', 'Syncing...')}")
    if refresh_counter:
        # Show a small countdown til next sync
        st.sidebar.caption(f"Next pulse in ~30s (Cycle: {refresh_counter})")
else:
    st.sidebar.warning(f"⚠️ Manual Mode: Press R to Refresh")

# 🧭 SMART NAVIGATION
nav_options = [
    "🏠 HOME", "🏛️ INSTITUTIONAL", "💎 ELITE F&O", "🔥 FIRE TRADE", "📡 RADAR", "💎 CHAIN", "📈 PAPER TRADING", 
    "💎 CONVICTION", "💪 PRO ENGINE", "📊 CHART", "🧠 STRATEGY HUB", 
    "📉 F&O", "🛢 COMMODITY", "📋 TRADE MGMT", "💎 PLANS & ACCESS"
]
sel_nav = st.sidebar.selectbox("🧭 Workspace", nav_options, index=0)

# 📊 GLOBAL FILTERS
index_options = list(INDEX_MAP.keys())
sel_idx = st.sidebar.selectbox("📊 Index Filter", index_options, index=0)
stk_list = INDEX_MAP[sel_idx]["stocks"]

# 🚅 SPEED OPTIMIZATION
if 'lite_mode_enabled' not in st.session_state:
    st.session_state['lite_mode_enabled'] = True
lite_mode = st.sidebar.toggle("⚡ LITE MODE (Super-Fast)", value=st.session_state['lite_mode_enabled'], help="Scans only top 50 stocks for 2x speed")
st.session_state['lite_mode_enabled'] = lite_mode
limit = 50 if lite_mode else (150 if sel_nav != "🔥 FIRE TRADE" else 200)

# ⚙️ TELEGRAM CONFIG
with st.sidebar.expander("🤖 TELEGRAM ALERTS", expanded=False):
    tg_token = st.text_input("Bot Token", value=st.session_state.get('tg_token', os.getenv('TELEGRAM_TOKEN', '8252289647:AAG7L4-9m_eYFNAJDPgScxA_pNH4UKd-bAs')), type="password")
    tg_chat_id = st.text_input("Chat ID", value=st.session_state.get('tg_chat_id', os.getenv('TELEGRAM_CHAT_ID', '5988809859')))
    tg_auto = st.toggle("Auto-Send (50%+)", value=st.session_state.get('tg_auto_active', True))
    st.session_state['tg_token'] = tg_token
    st.session_state['tg_chat_id'] = tg_chat_id
    st.session_state['tg_auto_active'] = tg_auto

# 📉 MARKET STATUS (Hide for heavy views to save space/time)
if sel_nav in ["🏠 HOME", "📡 RADAR"]:
    # Show cache info
    cache_age = cache_mgr.get_cache_age()
    if cache_age < 60:
        cache_status = f"📦 Cache: {cache_age:.0f} min ago" if cache_age >= 1 else "📦 Cache: Just now"
        st.sidebar.caption(cache_status)
    
    st.sidebar.markdown("""
    <div style="background:#001524; border:1px solid #00f2ff; padding:10px; border-radius:5px; margin-bottom:15px;">
        <h4 style="color:#00f2ff; margin:0; text-align:center;">🛰️ BG SCANNER</h4>
        <p style="color:#aaa; font-size:0.7rem; margin:5px 0 0 0; text-align:center;">Telegram Alerts Active</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state['sdf_cache'].empty:
        sdf_side = st.session_state['sdf_cache']
        with st.sidebar.expander("📊 MARKET STRENGTH", expanded=True):
            bull_c = len(sdf_side[sdf_side['Signal'].str.contains('CE', na=False)])
            bear_c = len(sdf_side[sdf_side['Signal'].str.contains('PE', na=False)])
            bias = "BULLISH" if bull_c > bear_c * 1.5 else "BEARISH" if bear_c > bull_c * 1.5 else "NEUTRAL"
            bias_clr = "#00e676" if bias == "BULLISH" else "#ff1744" if bias == "BEARISH" else "#ffd740"
            st.markdown(f"""<div style="text-align:center; margin-bottom:10px;"><span style="color:#888; font-size:0.7rem;">STRATEGIC BIAS</span><br><span style="color:{bias_clr}; font-weight:900; font-size:1.2rem;">{bias}</span></div>
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:12px;"><span style="color:#00e676;">📈 {bull_c} CE</span><span style="color:#ff1744;">📉 {bear_c} PE</span></div>""", unsafe_allow_html=True)

stk_list = INDEX_MAP[sel_idx]["stocks"]

# Global data holders (Moved to Top)

# BACKGROUND SCANNER: Runs for Home, Fire Trade, or for Auto-Alerts
should_scan = (sel_nav in ["🏠 HOME", "🔥 FIRE TRADE", "📡 RADAR"]) or (refresh_counter % 1 == 0) # Scan every sync turn

if should_scan:
    with st.status("🛰️ Scanning Markets & Analyzing Momentum...", expanded=False) as status:
        effective_list = stk_list[:limit] if len(stk_list) > limit else stk_list
        
        # Super Index Picks (Nifty, BankNifty, Sensex)
        index_tickers = ["^NSEI", "^NSEBANK", "^BSESN", "NIFTY_FIN_SERVICE.NS", "NIFTY_MID_SELECT.NS"]
        total_scan_list = list(set(effective_list + index_tickers))
        
        stock_rows = get_comprehensive_scan(tuple(total_scan_list))
        
        if stock_rows:
            sdf = pd.DataFrame(stock_rows)
            st.session_state['sdf_cache'] = sdf # Persist for sidebar
            
            # Extract Super Index Picks for display
            indices_only = sdf[sdf['Ticker'].isin(index_tickers)]
            index_picks_data = indices_only.to_dict('records')
            st.session_state['index_picks'] = index_picks_data
            
                        # Super Stock Logic (Heavyweights with High Momentum)
            super_stocks = sdf[sdf['Ticker'].isin(HEAVYWEIGHTS)]
            diamond_picks = []
            for _, row in super_stocks.iterrows():
                try:
                    adx_val = row.get('ADX', 0)
                    rsi_val = row.get('RSI', 50)
                    
                    if pd.isna(adx_val) or pd.isna(rsi_val): continue
                    
                    conf = min(95, max(40, adx_val + abs(rsi_val-50)))
                    chg_pct = row.get('Chg%', 0)
                    if pd.isna(chg_pct): chg_pct = 0
                    
                    if conf >= 80 and abs(chg_pct) > 1.5:
                        a_price = row['Price']
                        if pd.isna(a_price) or a_price <= 0: continue
                        
                        a_type = "CE" if "CE" in str(row['Signal']) else "PE"
                        a_step = 50 if a_price > 500 else 10 if a_price > 100 else 5
                        a_strike = round(a_price / a_step) * a_step
                        a_iv = max(15, min(50, 30 + abs(rsi_val - 50) * 0.3))
                        
                        from services.market_engine import get_expiry_details
                        dte, _, _ = get_expiry_details(row['Stock'])
                        a_entry = get_real_option_price(row['Stock'], a_strike, a_type, a_price, a_iv, dte)
                        
                        if not pd.isna(a_entry) and a_entry > 0:
                            diamond_picks.append({
                                "Stock": row['Stock'],
                                "Signal": row['Signal'],
                                "Price": row['Price'],
                                "Conf": conf,
                                "Type": a_type,
                                "Entry": a_entry,
                                "SL": round(a_entry * 0.90, 2),
                                "Target": round(a_entry * 1.30, 2),
                                "Strike": a_strike,
                                "MTF_Status": row.get('MTF_Status', 'Neutral')
                            })
                except Exception as e:
                    continue
                    
                    diamond_picks.append({
                        "Stock": row['Stock'],
                        "Signal": row['Signal'],
                        "Price": row['Price'],
                        "Conf": conf,
                        "Type": a_type,
                        "Entry": a_entry,
                        "SL": round(a_entry * 0.90, 2),
                        "Target": round(a_entry * 1.30, 2),
                        "Strike": a_strike
                    })
            st.session_state['diamond_picks'] = diamond_picks

            st.session_state['last_sync'] = datetime.now().strftime('%H:%M:%S')
            
            # 💾 SAVE TO CACHE: Instant load next time!
            cache_mgr.save_scan_results(
                scan_data=stock_rows,
                index_picks=index_picks_data,
                diamond_picks=diamond_picks
            )
            status.update(label="✅ Scan Complete & Cached!", state="complete")
        # 📱 AUTO DISPATCH: Send Alerts for ALL Suitable CE/PE
        if tg_auto and tg_token and tg_chat_id:
            if 'last_alert_sent' not in st.session_state:
                st.session_state['last_alert_sent'] = {}
            # Catch all recommendations: Scalps, Breakouts, and Trend Reversals
            suitable = sdf[(sdf['Signal'].str.contains('CE', na=False)) | (sdf['Signal'].str.contains('PE', na=False))]
            for _, row in suitable.iterrows():
                try:
                    ticker_key = f"{row['Stock']}_{row['Signal']}"
                    # Prevent spam: only alert once every 30 mins for the same signal
                    last_time = st.session_state['last_alert_sent'].get(ticker_key)
                    now = datetime.now()
                    if last_time is None or (now - last_time).seconds > 1800:
                        a_name = row['Stock']; a_price = row['Price']
                        if pd.isna(a_price) or a_price <= 0: continue
                        
                        a_type = "CE" if "CE" in str(row['Signal']) else "PE"
                        a_step = 50 if a_price > 500 else 10 if a_price > 100 else 5
                        a_strike = round(a_price / a_step) * a_step
                        
                        rsi_val = row.get('RSI', 50)
                        if pd.isna(rsi_val): rsi_val = 50
                        a_iv = max(15, min(50, 30 + abs(rsi_val - 50) * 0.3))
                        
                        from services.market_engine import get_expiry_details, estimate_target_time, calculate_option_greeks
                        dte, exp_date, exp_week = get_expiry_details(a_name)
                        a_entry = get_real_option_price(a_name, a_strike, a_type, a_price, a_iv, dte)
                        if pd.isna(a_entry) or a_entry <= 0: continue
                        
                        a_tgt = round(a_entry * 1.30, 2) 
                        a_sl = round(a_entry * 0.90, 2) 
                        
                        # Value Analysis (IV/TV)
                        iv_val, tv_val, money_status = calculate_option_greeks(a_price, a_strike, a_entry, a_type)
                        
                        # 🔍 MTF Status
                        mtf_s = row.get('MTF_Status', 'Neutral')
                        mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
                        
                        est_time = estimate_target_time(row['Signal'], row['ADX'])
                        conf_score = min(95, max(40, row['ADX'] + abs(row['RSI']-50)))
                        
                        import random
                        quote = random.choice(TRADING_QUOTES)
                        
                        # Determine Heading & Status
                        if "ANTICIPATION" in row['Signal']:
                            h_type = "⏳ BREAKOUT ANTICIPATION"
                            status_txt = "Waiting for Breakout Levels"
                            wait_txt = "Stay Alert for Next 30 Mins"
                        else:
                            h_type = "🎯 SCALPING ALERT" if "SCALP" in row['Signal'] else "🚀 INTRADAY ALERT"
                            status_txt = "Ready for Next 5 Minutes to Buy"
                            wait_txt = "Maximum Wait: 30 Mins"
    
                        # 🎯 QUALITY TIER CLASSIFICATION (Above 50% = Worth Trading)
                        if conf_score < 50: continue # Filter below 50% win chance
                        
                        # Determine Quality Tier
                        if conf_score >= 85:
                            quality_tier = "💎 DIAMOND"
                            tier_desc = "HIGHEST QUALITY - Strong Buy"
                        elif conf_score >= 75:
                            quality_tier = "🏆 TOP PICK"
                            tier_desc = "VERY HIGH QUALITY - Recommended"
                        elif conf_score >= 65:
                            quality_tier = "⭐ BEST CALL"
                            tier_desc = "HIGH QUALITY - Good Entry"
                        else:  # 50-64%
                            quality_tier = "⚡ GOOD CHANCE"
                            tier_desc = "MODERATE - Consider Entry"
                        
                        # Get MTF status
                        from services.market_engine import get_mtf_confluence
                        mtf_s, mtf_status = get_mtf_confluence(row['Ticker'])
                        mtf_icon = "🟢" if "Bullish" in mtf_status else "🔴" if "Bearish" in mtf_status else "🟡"
                        
                        a_clean_name = clean_symbol_name(a_name)
                        is_test = os.getenv("TEST_MODE", "false").lower() == "true"
                        status_icon = "🧪 TEST" if is_test else "🟢 LIVE"
                        trend_emoji = "🚀" if a_type == "CE" else "🩸"
                        call_pe_icon = "🍏 CE (CALL)" if a_type == "CE" else "🍎 PE (PUT)"
                        
                        alert_msg = (
                            f"🔔 {status_icon} | {quality_tier} *{a_clean_name}* {a_type}\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"🎯 *QUALITY*: {tier_desc}\n"
                            f"🔥 *WIN CHANCE*: {conf_score:.0f}% 💎\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"📅 *EXPIRY*: `{exp_date}`\n"
                            f"🏢 *ASSET*: {a_clean_name}\n"
                            f"🎫 *OPTION*: `{a_strike} {call_pe_icon}` {trend_emoji}\n"
                            f"🕒 *TIME*: `{now.strftime('%I:%M %p')}`\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"✅ *DECISION*: **BUY NOW** 📥\n"
                            f"📥 *ENTRY*: ₹{a_entry:.2f} ✅\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"👤 *PrimeSkillDevelopment CEO : MuthuKumar krishnan*"
                        )
                        send_telegram(tg_token, tg_chat_id, alert_msg)
                        st.session_state['last_alert_sent'][ticker_key] = now
                except Exception as e:
                    continue

        # ==========================================
        # 📊 EOD AUTOMATED MARKET REPORT (5:00 PM)
        # ==========================================
        now = datetime.now()
        is_weekday = now.weekday() < 5
        is_eod_time = now.hour == 17 and now.minute >= 0
        last_eod_date = st.session_state.get('last_eod_date')
        today_date = now.strftime('%Y-%m-%d')
        
        # --- 🏆 BEST PICK LOGIC (Moved outside EOD for 24/7 scanning) ---
        best_r = None
        conf = 0
        b_name = "N/A"; o_type = "N/A"; b_strike = "N/A"; b_entry = 0; b_tgt = 0; b_sl = 0

        c_stocks = sdf[sdf['Signal'].str.contains('CE', na=False)]
        p_stocks = sdf[sdf['Signal'].str.contains('PE', na=False)]

        if not c_stocks.empty:
            best_call = c_stocks.nlargest(1, 'Momentum').iloc[0]
            call_conf = min(95, max(40, best_call['ADX'] + abs(best_call['RSI']-50)))
        else:
            best_call = None; call_conf = 0

        if not p_stocks.empty:
            best_put = p_stocks.nsmallest(1, 'Momentum').iloc[0]
            put_conf = min(95, max(40, best_put['ADX'] + abs(best_put['RSI']-50)))
        else:
            best_put = None; put_conf = 0

        if best_call is not None and (best_put is None or call_conf >= put_conf):
            best_r = best_call; conf = call_conf; o_type = "CE"
        elif best_put is not None:
            best_r = best_put; conf = put_conf; o_type = "PE"
        
        if best_r is not None:
            b_name = best_r['Stock']; b_price = best_r['Price']
            b_step = 50 if b_price > 500 else 10 if b_price > 100 else 5
            b_strike = round(b_price / b_step) * b_step
            b_iv = max(15, min(50, 30 + abs(best_r['RSI'] - 50) * 0.3))
            dte = get_days_to_expiry()
            b_entry = get_real_option_price(b_name, b_strike, o_type, b_price, b_iv, dte)
            # Requested: Target & Stop Loss 10% Protocol
            b_tgt = round(b_entry * 1.30, 2) # Target (+30%)
            b_sl = round(b_entry * 0.90, 2)  # SL (-10%)

            if conf >= 85: concept = "DIAMOND CALL"
            elif best_r.get('Rank', 1) == 1: concept = "TOP CALL"
            else: concept = "HIGH CONFIDENCE"
            
            # Determine if this is high quality for auto-send (>= 65%)
            is_best_call = (conf >= 65)
            st.session_state['conf_ready'] = is_best_call
            st.session_state['trade_confidence'] = conf # Store for sidebar display
            
            # Enhanced Alert Msg for "No Watch" Trade
            from services.market_engine import get_expiry_details, estimate_target_time, calculate_option_greeks
            dte, exp_date, exp_week = get_expiry_details(b_name)
            
            # Value Analysis (IV/TV)
            iv_val, tv_val, money_status = calculate_option_greeks(b_price, b_strike, b_entry, o_type)
            
            # 🔍 MTF Status
            mtf_s = best_r.get('MTF_Status', 'Neutral')
            mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
            
            est_time = estimate_target_time(str(best_r.get('Signal', '')), best_r.get('ADX', 25))
            import random
            quote = random.choice(TRADING_QUOTES)
            
            # 🎯 QUALITY TIER CLASSIFICATION
            if conf >= 85:
                quality_tier = "💎 DIAMOND"
                tier_desc = "HIGHEST QUALITY - Strong Buy"
            elif conf >= 75:
                quality_tier = "🏆 TOP PICK"
                tier_desc = "VERY HIGH QUALITY - Recommended"
            elif conf >= 65:
                quality_tier = "⭐ BEST CALL"
                tier_desc = "HIGH QUALITY - Good Entry"
            else:  # 50-64%
                quality_tier = "⚡ GOOD CHANCE"
                tier_desc = "MODERATE - Consider Entry"

            # 🔍 MTF & Value Analysis
            from services.market_engine import get_mtf_confluence, get_expiry_details, calculate_option_greeks
            mtf_s, mtf_status = get_mtf_confluence(best_r['Ticker'])
            mtf_icon = "🟢" if "Bullish" in mtf_status else "🔴" if "Bearish" in mtf_status else "🟡"
            
            dte, exp_date, _ = get_expiry_details(b_name)
            b_clean_name = clean_symbol_name(b_name)
            iv_val, tv_val, money_status = calculate_option_greeks(b_price, b_strike, b_entry, o_type)

            st.session_state['tg_idx_msg'] = (
                f"{quality_tier} *{b_clean_name}* {o_type.replace('CE', 'CALL').replace('PE', 'PUT')}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎯 *QUALITY*: {tier_desc}\n"
                f"🔥 *WIN CHANCE*: {conf:.0f}% | {quality_tier}\n"
                f"━━━━━━━━━━━━━━\n"
                f"📅 *EXPIRY*: `{exp_date}`\n"
                f"📊 *STOCK*: {b_clean_name}\n"
                f"📍 *STRIKE PRICE*: **`{b_strike} {o_type.replace('CE', 'CALL').replace('PE', 'PUT')}`**\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ *ACTION*: **BUY {o_type.replace('CE', 'CALL').replace('PE', 'PUT')}**\n"
                f"📥 *ENTRY*: ₹{b_entry:.2f}\n"
                f"🎯 *TARGET*: ₹{b_tgt:.2f} (+30%)\n"
                f"🛑 *STOP LOSS*: ₹{b_sl:.2f} (-10%)\n\n"
                f"💎 *VALUE ANALYSIS*\n"
                f"├─ Moneyness: {money_status}\n"
                f"├─ Intrinsic: ₹{iv_val}\n"
                f"└─ Time Value: ₹{tv_val}\n\n"
                f"🔍 *MTF STATUS*: {mtf_status} {mtf_icon}\n"
                f"⏰ *EST. TIME*: {est_time}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 *Prime Skill | Marsh Muthu 326*"
            )
            with st.sidebar.container():
                st.markdown(f"#### 💎 BEST: {b_name} {o_type}")
                st.write(f"📥 Entry: **₹{b_entry}** | 🎯 Tgt: **₹{b_tgt}**")
            
            # --- 📱 AUTO DISPATCH: Send Alerts for ALL Suitable CE/PE ---
            if tg_auto and tg_token and tg_chat_id:
                if 'last_alert_sent' not in st.session_state:
                    st.session_state['last_alert_sent'] = {}
                
                suitable = sdf[(sdf['Signal'].str.contains('CE', na=False)) | (sdf['Signal'].str.contains('PE', na=False))]
                for _, row in suitable.iterrows():
                    ticker_key = f"{row['Stock']}_{row['Signal']}"
                    last_time = st.session_state['last_alert_sent'].get(ticker_key)
                    now = datetime.now()
                    if last_time is None or (now - last_time).seconds > 1800:
                        a_name = row['Stock']; a_price = row['Price']
                        a_type = "CE" if "CE" in row['Signal'] else "PE"
                        a_step = 50 if a_price > 500 else 10 if a_price > 100 else 5
                        a_strike = round(a_price / a_step) * a_step
                        a_iv = max(15, min(50, 30 + abs(row['RSI'] - 50) * 0.3))
                        from services.market_engine import get_expiry_details, estimate_target_time, calculate_option_greeks
                        dte, exp_date, exp_week = get_expiry_details(a_name)
                        a_entry = get_real_option_price(a_name, a_strike, a_type, a_price, a_iv, dte)
                        a_tgt = round(a_entry * 1.30, 2) # Target (+30%)
                        a_sl = round(a_entry * 0.90, 2)  # SL (-10%)
                        
                        # Value Analysis (IV/TV)
                        iv_val, tv_val, money_status = calculate_option_greeks(a_price, a_strike, a_entry, a_type)
                        
                        # 🔍 MTF Status
                        mtf_s = row.get('MTF_Status', 'Neutral')
                        mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
                        
                        est_time = estimate_target_time(row['Signal'], row['ADX'])
                        conf_score = min(95, max(40, row['ADX'] + abs(row['RSI']-50)))
                        
                        # Filter below 50% win chance
                        if conf_score < 50: continue
                        
                        # 🎯 QUALITY TIER CLASSIFICATION
                        if conf_score >= 85:
                            quality_tier = "💎 DIAMOND"
                            tier_desc = "HIGHEST QUALITY - Strong Buy"
                        elif conf_score >= 75:
                            quality_tier = "🏆 TOP PICK"
                            tier_desc = "VERY HIGH QUALITY - Recommended"
                        elif conf_score >= 65:
                            quality_tier = "⭐ BEST CALL"
                            tier_desc = "HIGH QUALITY - Good Entry"
                        else:  # 50-64%
                            quality_tier = "⚡ GOOD CHANCE"
                            tier_desc = "MODERATE - Consider Entry"
                        
                        # Get MTF status
                        from services.market_engine import get_mtf_confluence
                        _, mtf_status = get_mtf_confluence(row['Ticker'])
                        mtf_icon = "🟢" if "Bullish" in mtf_status else "🔴" if "Bearish" in mtf_status else "🟡"
                        
                        a_clean_name = clean_symbol_name(a_name)
                        alert_msg = (
                            f"{quality_tier} *{a_clean_name}* {a_type}\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"🎯 *QUALITY*: {tier_desc}\n"
                            f"🔥 *WIN CHANCE*: {conf_score:.0f}% | {quality_tier}\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"📅 *EXPIRY*: `{exp_date}`\n"
                            f"📊 *STOCK*: {a_clean_name}\n"
                            f"📍 *STRIKE*: `{a_strike} {a_type}`\n"
                            f"━━━━━━━━━━━━━━\n"
                        f"✅ *ACTION*: **BUY {a_type.replace('CE', 'CALL').replace('PE', 'PUT')}**\n"
                        f"📍 *STRIKE PRICE*: **`{a_strike} {a_type.replace('CE', 'CALL').replace('PE', 'PUT')}`**\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"📥 *ENTRY*: ₹{a_entry:.2f}\n"
                        )
                        send_telegram(tg_token, tg_chat_id, alert_msg)
                        st.session_state['last_alert_sent'][ticker_key] = now

            # --- 📊 EOD AUTOMATED MARKET REPORT (5:00 PM) ---
            now = datetime.now()
            is_weekday = now.weekday() < 5
            is_eod_time = (now.hour == 17 and now.minute >= 0)
            last_eod_date = st.session_state.get('last_eod_date')
            today_date = now.strftime('%Y-%m-%d')
            
            if is_weekday and is_eod_time and last_eod_date != today_date and tg_auto and tg_token and tg_chat_id:
                res = send_eod_report(tg_token, tg_chat_id, sdf)
                if res == True:
                    st.session_state['last_eod_date'] = today_date

            # --- 🏆 BEST PICK LOGIC (For Sidebar Display) ---
            best_r = None; conf = 0
            b_name = "N/A"; o_type = "N/A"; b_strike = "N/A"; b_entry = 0; b_tgt = 0; b_sl = 0

            c_stocks = sdf[sdf['Signal'].str.contains('CE', na=False)]
            p_stocks = sdf[sdf['Signal'].str.contains('PE', na=False)]

            if not c_stocks.empty:
                best_call = c_stocks.nlargest(1, 'Momentum').iloc[0]
                call_conf = min(95, max(40, best_call['ADX'] + abs(best_call['RSI']-50)))
            else:
                best_call = None; call_conf = 0

            if not p_stocks.empty:
                best_put = p_stocks.nsmallest(1, 'Momentum').iloc[0]
                put_conf = min(95, max(40, best_put['ADX'] + abs(best_put['RSI']-50)))
            else:
                best_put = None; put_conf = 0

            if best_call is not None and (best_put is None or call_conf >= put_conf):
                best_r = best_call; conf = call_conf; o_type = "CE"
            elif best_put is not None:
                best_r = best_put; conf = put_conf; o_type = "PE"
            
            if best_r is not None:
                b_name = best_r['Stock']; b_price = best_r['Price']
                b_step = 50 if b_price > 500 else 10 if b_price > 100 else 5
                b_strike = round(b_price / b_step) * b_step
                b_iv = max(15, min(50, 30 + abs(best_r['RSI'] - 50) * 0.3))
                from services.market_engine import get_expiry_details, estimate_target_time, calculate_option_greeks
                dte, exp_date, exp_week = get_expiry_details(b_name)
                b_entry = get_real_option_price(b_name, b_strike, o_type, b_price, b_iv, dte)
                b_tgt = round(b_entry * 1.30, 2); b_sl = round(b_entry * 0.90, 2)

                # Value Analysis (IV/TV)
                iv_val, tv_val, money_status = calculate_option_greeks(b_price, b_strike, b_entry, o_type)
                
                # 🔍 MTF Status
                mtf_s = best_r.get('MTF_Status', 'Neutral')
                mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
                
                est_time = estimate_target_time(str(best_r.get('Signal', '')), best_r.get('ADX', 25))
                st.session_state['conf_ready'] = (conf >= 65)
                st.session_state['trade_confidence'] = conf
                
                import random
                quote = random.choice(TRADING_QUOTES)
                h_type = "🏆 SUPER INDEX PICK" if any(idx in b_name for idx in ["NIFTY", "SENSEX"]) else "💎 STRENGTH PICK"
                if "ANTICIPATION" in str(best_r.get('Signal', '')): h_type = "⏳ BREAKOUT ANTICIPATION"
                
                b_clean_name = clean_symbol_name(b_name)
                st.session_state['tg_idx_msg'] = (
                    f"*{h_type}*\n\n"
                    f"📅 Expiry Date : {exp_date}\n\n"
                    f"📊 Stock Name : {b_clean_name}\n"
                    f"🔹 Current Spot Price : ₹{b_price:.2f}\n"
                    f"📍 Strike Price : **{b_strike} {o_type.replace('CE', 'CALL').replace('PE', 'PUT')}**\n\n"
                    f"✅ Decision : **BUY {o_type.replace('CE', 'CALL').replace('PE', 'PUT')}**\n"
                    f"📥 ENTRY : ₹{b_entry:.2f}\n"
                    f"🎯 TARGET : ₹{b_tgt:.2f}\n"
                    f"🛑 SL : ₹{b_sl:.2f}\n\n"
                    f"💎 *Value Analysis*\n"
                    f"├─ Moneyness: {money_status}\n"
                    f"├─ Intrinsic Value (IV): ₹{iv_val}\n"
                    f"└─ Time Value (TV): ₹{tv_val}\n\n"
                    f"🔍 *MTF Status*: {mtf_s} {mtf_icon}\n\n"
                    f"⚡ Status : Ready for Next 5-10 Minutes to Buy\n"
                    f"⏰ Time : Maximum Wait 30 Mins\n"
                    f"🎯 Target Achieved Time : {est_time}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"💡 _{quote}_\n"
                    f"✨ *PrimeSkillDevelopment*\n"
                    f"👑 *CEO : MuthuKumar Krishnan*"
                )
                
                # Best Pick Sidebar UI
                with st.sidebar.container():
                    st.markdown(f"#### 💎 BEST: {b_clean_name} {o_type}")
                    st.write(f"📥 Entry: **₹{b_entry}** | 🎯 Tgt: **₹{b_tgt}**")
                    st.write(f"🛑 SL: **₹{b_sl:.2f}** | 🔥 Conf: **{conf:.0f}%**")
                
                # Store for live tracking
                st.session_state['best_trade_info'] = {
                    'stock': b_name, 'type': o_type, 'strike': f"{b_strike} {o_type}",
                    'entry': b_entry, 'target': b_tgt, 'sl': b_sl, 'confidence': conf,
                    'ticker': best_r['Ticker']
                }

            status.update(label=f"✅ Sync Success: {st.session_state.get('last_sync', 'Now')}", state="complete")
        else:
            status.update(label="⚠️ Sync Partial (Limited Data)", state="error")
else:
    st.sidebar.caption(f"⏱ Last Sync: {st.session_state.get('last_sync', 'Never')}")
    st.sidebar.caption("❌ Scanner Offline (Check Internet)")

# =============================================
# 📱 TELEGRAM AUTO ALERT — 100% Automatic!
# No manual clicking, messages arrive instantly
# =============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Auto Alert (Telegram)")
st.sidebar.caption("💡 100% automatic — no manual clicking!")

# Setup guide expander
with st.sidebar.expander("📋 How to Setup (One Time)"):
    st.markdown("""
    **Step 1:** Open Telegram → Search `@BotFather`
    
    **Step 2:** Send `/newbot` → Give it a name like `MarshMuthu326Bot`
    
    **Step 3:** Copy the **Bot Token** (looks like `123456:ABC-DEF...`)
    
    **Step 4:** Search your bot in Telegram & send it any message (like `hi`)
    
    **Step 5:** Get your **Chat ID**:
    - Open browser: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
    - Find `"chat":{"id": 123456789}` — that's your Chat ID
    
    **Step 6:** Enter Bot Token & Chat ID in sidebar → Done! ✅
    """)

# Telegram Config moved to top.

# DEBUG STATUS (Sidebar) - Moved here to ensure vars exist
with st.sidebar.expander("🛠️ DEBUG & CONNECTION"):
    if tg_token and tg_chat_id:
        st.write("✅ Bot Configured")
    else:
        st.error("❌ Token/ChatID Missing")
    
    if 'stock_rows' in locals() and stock_rows:
        st.write(f"📊 Last Scan: {len(stock_rows)} Stocks")
    else:
        st.warning("⚠️ Scan Pending...")

    if st.button("🚀 FORCE CONNECTION TEST"):
        res = send_telegram(tg_token, tg_chat_id, "🔔 *CONNECTION TEST:* Terminal is LIVE and scanning!")
        if res == True: 
            st.success("✅ Message Sent Successfully!")
        else: 
            st.error(f"Error: {res}")
            if "401" in str(res):
                st.info("💡 **FIX:** Your Bot Token is incorrect. Please generate a new one from @BotFather.")
        
    if st.button("📊 FORCE EOD ANALYSIS"):
        if not sdf.empty:
            res = send_eod_report(tg_token, tg_chat_id, sdf)
            if res == True: st.success("EOD Report Sent!")
            else: st.error(f"Error: {res}")
        else:
            st.warning("Scan some stocks first to generate the report!")

# Initialize timer — FILE BASED so it survives page refresh
import os
TG_TIMER_FILE = os.path.join(os.path.dirname(__file__), '.tg_last_send')
TG_COUNT_FILE = os.path.join(os.path.dirname(__file__), '.tg_send_count')
TRADE_TRACKER_FILE = os.path.join(os.path.dirname(__file__), '.trade_tracker.json')
TRADE_HISTORY_FILE = os.path.join(os.path.dirname(__file__), '.trade_history.json')

def save_send_time():
    with open(TG_TIMER_FILE, 'w') as f:
        f.write(datetime.now().isoformat())

def load_send_time():
    try:
        if os.path.exists(TG_TIMER_FILE):
            with open(TG_TIMER_FILE, 'r') as f:
                return datetime.fromisoformat(f.read().strip())
    except:
        pass
    return None

def save_send_count(count):
    with open(TG_COUNT_FILE, 'w') as f:
        f.write(str(count))

def load_send_count():
    try:
        if os.path.exists(TG_COUNT_FILE):
            with open(TG_COUNT_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def load_trades():
    try:
        if os.path.exists(TRADE_TRACKER_FILE):
            with open(TRADE_TRACKER_FILE, 'r') as f:
                return json.loads(f.read())
    except:
        pass
    return []

def save_trades(trades):
    with open(TRADE_TRACKER_FILE, 'w') as f:
        f.write(json.dumps(trades, indent=2, default=str))

def load_history():
    try:
        if os.path.exists(TRADE_HISTORY_FILE):
            with open(TRADE_HISTORY_FILE, 'r') as f:
                return json.loads(f.read())
    except:
        pass
    return []

def save_history(history):
    with open(TRADE_HISTORY_FILE, 'w') as f:
        f.write(json.dumps(history, indent=2, default=str))

def calc_confidence(row, is_call, bullish_bias, bearish_bias):
    """Detailed confidence score based on confluence of multiple indicators"""
    score = 0
    
    # 1. Trend Alignment (Supertrend & EMA)
    st_dir = row.get('ST_Direction', 0)
    if is_call and st_dir == 1: score += 15
    elif not is_call and st_dir == -1: score += 15
    
    # EMA Alignment (Price vs EMA20)
    price = row.get('Close', 0)
    ema20 = row.get('EMA20', 0)
    if is_call and price > ema20: score += 10
    elif not is_call and price < ema20: score += 10
    
    # 2. Momentum (RSI & MACD)
    rsi = row.get('RSI', 50)
    if is_call:
        if 55 < rsi < 70: score += 15
        elif 70 <= rsi < 85: score += 10
    else:
        if 30 < rsi < 45: score += 15
        elif 15 <= rsi <= 30: score += 10
        
    macd_hist = row.get('MACD_Hist', 0)
    if is_call and macd_hist > 0: score += 10
    elif not is_call and macd_hist < 0: score += 10
    
    # 3. Volatility & Participation (Volume & ADX)
    adx = row.get('ADX', 20)
    if adx > 25: score += 15
    elif adx > 20: score += 10
    
    vol_strong = row.get('VolStrong', False)
    if vol_strong: score += 15
    
    # 4. Bias & VWAP
    vwap = row.get('VWAP', 0)
    if is_call and price > vwap: score += 10
    elif not is_call and price < vwap: score += 10
    
    if is_call and bullish_bias: score += 10
    elif not is_call and bearish_bias: score += 10
    
    return min(100, score)

def is_market_hours():
    now = datetime.now()
    if now.weekday() > 4: return False
    mopen = now.replace(hour=9, minute=15, second=0, microsecond=0)
    mclose = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return mopen <= now <= mclose

def clean_old_trades(trades, history):
    now = datetime.now()
    active = []
    for t in trades:
        if t.get('status') in ['TARGET_HIT', 'SL_HIT', 'EXIT_FORCED']:
            exit_t = datetime.fromisoformat(t.get('exit_time', now.isoformat()))
            if (now - exit_t).days >= 2:
                history.append(t)
                continue
        active.append(t)
    return active, history

def get_success_ratio(history, days=None, min_conf=0):
    now = datetime.now()
    filt = history
    if days:
        filt = [h for h in filt if (now - datetime.fromisoformat(h.get('exit_time', now.isoformat()))).days <= days]
    
    # Filter by confidence if specified
    if min_conf > 0:
        filt = [h for h in filt if h.get('confidence', 0) >= min_conf]
        
    if not filt: return 0, 0, 0
    tgts = sum(1 for h in filt if h.get('status') == 'TARGET_HIT')
    return tgts, len(filt), round(tgts / max(len(filt), 1) * 100, 1)

# Load persisted values into session state
if 'tg_last_send' not in st.session_state:
    st.session_state['tg_last_send'] = load_send_time()
if 'tg_send_count' not in st.session_state:
    st.session_state['tg_send_count'] = load_send_count()


# Send Test button
if st.sidebar.button("🧪 Send Test", key="tg_test_btn"):
    if tg_token and tg_chat_id:
        # Dynamic sample based on current market state if possible
        bias_label = "Neutral" # Default
        if 'sdf' in locals() and not sdf.empty:
            call_stocks = sdf[sdf['Signal'].str.contains('CALL', na=False)]
            put_stocks = sdf[sdf['Signal'].str.contains('PUT', na=False)]
            mkt_bias_ratio = len(call_stocks) / max(len(put_stocks), 1)
            if mkt_bias_ratio > 1.2: bias_label = "BULLISH"
            elif mkt_bias_ratio < 0.8: bias_label = "BEARISH"
        
        # Use latest real alert if available
        if 'tg_idx_msg' in st.session_state:
            real_msg = st.session_state['tg_idx_msg'].replace('%0A', '\n')
            test_msg = (
                "🧪 *PRIME SKILL TEST (LATEST SCAN)*\n"
                f"━━━━━━━━━━━━━━\n"
                f"{real_msg}\n"
                f"━━━━━━━━━━━━━━\n"
                f"_Verified by MARSH MUTHU 326_"
            )
        else:
            # Realistic Simulation
            test_msg = (
                "🧪 *PRIME SKILL TEST ALERT*\n"
                "🎯 *MARSH MUTHU 326 TERMINAL*\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
                "━━━━━━━━━━━━━━\n"
                f"📡 Market Bias: *{bias_label}*\n"
                "💎 *DIAMOND SETUP DETECTED*\n"
                "⚡ Stock: *RELIANCE* 3000 CE\n"
                "💰 Premium: ₹25.00\n"
                "🎯 Target: ₹35.00 | 🛑 SL: ₹18.00\n"
                "━━━━━━━━━━━━━━\n"
                "✅ Telegram Auto-Alert is WORKING!\n"
                "_Test by MARSH MUTHU 326_"
            )
        result = send_telegram(tg_token, tg_chat_id, test_msg)
        if result == True:
            st.session_state['tg_last_send'] = datetime.now()
            st.session_state['tg_send_count'] += 1
            save_send_time()
            save_send_count(st.session_state['tg_send_count'])
            st.sidebar.success("✅ Test sent! Check your Telegram!")
        else:
            st.sidebar.error(f"❌ Failed: {result}")
    else:
        st.sidebar.warning("⚠️ Enter Bot Token & Chat ID first")

# Send Market Data Now
if st.sidebar.button("📤 Send Market Data", key="tg_send_btn_man", use_container_width=True):
    if 'tg_idx_msg' in st.session_state and tg_token and tg_chat_id:
        msg = st.session_state['tg_idx_msg']
        with st.sidebar:
            with st.spinner("🚀 Sending best pick to Telegram..."):
                result = send_telegram(tg_token, tg_chat_id, msg)
        if result == True:
            st.sidebar.success("✅ ALERT SENT!")
            st.session_state['tg_last_send'] = datetime.now()
            save_send_time()
        else:
            st.sidebar.error(f"❌ FAILED: {result}")
    else:
        st.sidebar.warning("⚡ Scanner busy... Try in 5 sec.")

if st.sidebar.button("🚀 Send Best Pick Alert", key="tg_best_btn_man_2", use_container_width=True):
    if 'tg_idx_msg' in st.session_state and tg_token and tg_chat_id:
        msg = st.session_state['tg_idx_msg']
        with st.sidebar:
            with st.spinner("💎 Processing Best Pick..."):
                result = send_telegram(tg_token, tg_chat_id, msg)
        if result == True:
            st.sidebar.success("✅ BEST PICK SENT!")
            st.session_state['tg_last_send'] = datetime.now()
            save_send_time()
        else:
            st.sidebar.error(f"❌ Failed: {result}")
    else:
        st.sidebar.warning("⏳ Data not ready. Wait for scan.")

# ========== SMART AUTO-SEND: 1-MIN CHECK, MARKET HOURS, 65% CONFIDENCE ==========
if tg_auto and tg_token and tg_chat_id:
    now = datetime.now()
    last = load_send_time()
    time_since = int((now - last).total_seconds()) if last else 999
    # ===== 9:30 AM START CHECK =====
    mkt_open = is_market_hours()
    # Ensure scanning alerts only start after 9:30 AM for stability
    scanning_allowed = mkt_open and (now.hour > 9 or (now.hour == 9 and now.minute >= 30))

    active_trades = load_trades()
    trade_history = load_history()
    active_trades, trade_history = clean_old_trades(active_trades, trade_history)
    should_check = True # Initialize check flag for active monitor

    # ===== FIRE TRADE ALERT (3:00 PM) =====
    # Check if time is between 15:00 and 15:05
    if mkt_open and now.hour == 15 and 0 <= now.minute <= 5:
        last_fire_date = st.session_state.get('last_fire_date', '')
        today_str = now.strftime('%Y-%m-%d')
        
        if last_fire_date != today_str:
            # Send One-Time Alert
            st.session_state['last_fire_date'] = today_str
            
            # Rapid Mini-Scan (Top 10 Heavyweights)
            mini_fire_list = ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "ICICIBANK.NS", 
                              "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "AXISBANK.NS"]
            fire_msg = f"🔥 *SUPER FIRE TRADE (3:00 PM)*\n🚀 *BTST / OVERNIGHT JACKPOTS*\n━━━━━━━━━━━━━━━━━━\n"
            
            try:
                # Quick check
                f_data = yf.download(" ".join(mini_fire_list), period='2d', interval='15m', group_by='ticker', progress=False)
                has_picks = False
                for ft in mini_fire_list:
                    try:
                        f_df = f_data[ft].dropna() if len(mini_fire_list)>1 else f_data.dropna()
                        if len(f_df) < 5: continue
                        f_close = float(f_df['Close'].iloc[-1])
                        f_open = float(f_df['Open'].iloc[0]) # approx day open
                        f_chg = (f_close - f_open) / f_open * 100
                        
                        if abs(f_chg) > 1.0: # Significant move
                            o_type = "CE" if f_chg > 0 else "PE"
                            f_step = 50 if f_close > 500 else 10 if f_close > 100 else 5
                            f_strike = round(f_close / f_step) * f_step
                            f_entry = round(f_close * 0.015, 2) # Sample calculation for premium
                            f_tgt = round(f_entry * 1.5, 2)
                            f_sl = round(f_entry * 0.7, 2)
                            
                            from services.market_engine import get_expiry_details, estimate_target_time, calculate_option_greeks, get_mtf_confluence
                            dte, exp_date, exp_week = get_expiry_details(ft)
                            est_time = estimate_target_time("FIRE", 35) # High conviction
                            
                            # Value Analysis (IV/TV)
                            iv_val, tv_val, money_status = calculate_option_greeks(f_close, f_strike, f_entry, o_type)
                            
                            # 🔍 MTF Status
                            mtf_score, mtf_s = get_mtf_confluence(ft)
                            mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
                            
                            fire_msg += (
                                f"*📗 BTST / OVERNIGHT PICK*\n\n"
                                f"📅 Expiry Date : {exp_date}\n\n"
                                f"📊 Stock Name : {ft.replace('.NS','')}\n"
                                f"🔹 Current Spot Price : ₹{f_close:.2f}\n"
                                f"📍 Strike Price : {f_strike} {o_type}\n\n"
                                f"✅ Decision : BUY {o_type}\n"
                                f"📥 ENTRY : ₹{f_entry:.2f}\n"
                                f"🎯 TARGET : ₹{f_tgt:.2f}\n"
                                f"🛑 SL : ₹{f_sl:.2f}\n\n"
                                f"💎 *Value Analysis*\n"
                                f"├─ Moneyness: {money_status}\n"
                                f"├─ Intrinsic Value (IV): ₹{iv_val}\n"
                                f"└─ Time Value (TV): ₹{tv_val}\n\n"
                                f"🔍 *MTF Status*: {mtf_s} {mtf_icon}\n\n"
                                f"⚡ Status : Take Position Before 3:25 PM\n"
                                f"⏰ Time : Max Hold: Next Morning\n"
                                f"🎯 Target Achieved Time : {est_time}\n\n"
                            )
                            has_picks = True
                    except: pass
                
                if not has_picks:
                    fire_msg += "⚠️ No Major Heavyweights Moving >1%.\n"
                    
                import random
                quote = random.choice(TRADING_QUOTES)
                fire_msg += f"━━━━━━━━━━━━━━━━━━\n💡 _{quote}_\n🚀 _Automated by MARSH MUTHU 326_"
                send_telegram(tg_token, tg_chat_id, fire_msg)
            except:
                pass


    # ===== MONITOR ACTIVE TRADES FOR TARGET/SL/HOLD =====
    if mkt_open and should_check and active_trades:
        for trade in active_trades:
            if trade.get('status') in ['TARGET_HIT', 'SL_HIT', 'EXIT_FORCED']:
                continue
            stock_ticker = trade.get('ticker', '')
            try:
                live_data = yf.download(stock_ticker, period='1d', interval='1m', progress=False)
                if hasattr(live_data, 'columns') and isinstance(live_data.columns, pd.MultiIndex):
                    live_data.columns = live_data.columns.get_level_values(0)
                if live_data.empty:
                    continue
                live_price = float(live_data['Close'].iloc[-1])
                entry_price = trade.get('entry_price', 0)
                target_price = trade.get('target', 0)
                sl_price = trade.get('sl', 0)
                pnl_pct = round((live_price - entry_price) / max(entry_price, 0.01) * 100, 2)
                is_call = trade.get('type') == 'CE'

                # TARGET HIT
                target_hit = (is_call and live_price >= target_price) or (not is_call and live_price <= target_price)
                if target_hit and not trade.get('target_sent'):
                    trade['status'] = 'TARGET_HIT'
                    trade['exit_time'] = now.isoformat()
                    trade['exit_price'] = live_price
                    trade['pnl'] = pnl_pct
                    trade['target_sent'] = True
                    opt_e = '📗' if is_call else '📕'
                    opt_t = 'CE' if is_call else 'PE'
                    tgt_msg = (
                        f"🎯 *TARGET ACHIEVED!* 🎉\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"{opt_e} *{trade['stock']}* {trade.get('strike','')} {opt_t}\n"
                        f"📥 Entry: ₹{entry_price} → 🎯 ₹{live_price:.2f}\n"
                        f"💰 *P&L: +{abs(pnl_pct)}%*\n"
                        f"⏰ {now.strftime('%H:%M')} | Conf: {trade.get('confidence',0)}%\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"_✅ Trade Closed - Target Hit_"
                    )
                    send_telegram(tg_token, tg_chat_id, tgt_msg)
                    
                    # Sync with Paper Portfolio UI
                    if 'paper_portfolio' in st.session_state:
                        for p in st.session_state['paper_portfolio']:
                            if p['stock'] == trade['stock'] and p['status'] == 'OPEN':
                                p['status'] = 'CLOSED (TARGET)'
                                p['current_pnl'] = round((live_price - entry_price) * 100, 2) # Sample P&L calculation

                # STOP LOSS HIT
                sl_hit = (is_call and live_price <= sl_price) or (not is_call and live_price >= sl_price)
                if sl_hit and not trade.get('sl_sent') and not trade.get('target_sent'):
                    trade['status'] = 'SL_HIT'
                    trade['exit_time'] = now.isoformat()
                    trade['exit_price'] = live_price
                    trade['pnl'] = pnl_pct
                    trade['sl_sent'] = True
                    opt_e = '📗' if is_call else '📕'
                    opt_t = 'CE' if is_call else 'PE'
                    sl_msg = (
                        f"🛑 *STOP LOSS HIT!* ⚠️\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"{opt_e} *{trade['stock']}* {trade.get('strike','')} {opt_t}\n"
                        f"📥 Entry: ₹{entry_price} → 🛑 ₹{live_price:.2f}\n"
                        f"💔 *P&L: {pnl_pct}%*\n"
                        f"⏰ {now.strftime('%H:%M')}\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"_❌ Trade Closed - SL Hit_"
                    )
                    send_telegram(tg_token, tg_chat_id, sl_msg)

                    # Sync with Paper Portfolio UI
                    if 'paper_portfolio' in st.session_state:
                        for p in st.session_state['paper_portfolio']:
                            if p['stock'] == trade['stock'] and p['status'] == 'OPEN':
                                p['status'] = 'CLOSED (SL)'
                                p['current_pnl'] = round((live_price - entry_price) * 100, 2)

                # HOLD + MILESTONE + TREND REVERSAL CHECK (every 1 min)
                if trade.get('status') == 'ACTIVE':
                    opt_e = '📗' if is_call else '📕'
                    opt_t = 'CE' if is_call else 'PE'

                    # 💎 Milestone Logic: Send alert for every ₹0.50 increase
                    last_milestone = trade.get('last_milestone', entry_price)
                    if (is_call and live_price >= last_milestone + 0.50) or (not is_call and live_price <= last_milestone - 0.50):
                        trade['last_milestone'] = live_price
                        milestone_msg = (
                            f"🔔 *PRICE UPDATE* | {trade['stock']}\n"
                            f"⚡ Current: *₹{live_price:.2f}* reached!\n"
                            f"📈 Move: *{pnl_pct:+.1f}%* since entry\n"
                            f"🎯 Target: ₹{target_price} | 🛑 SL: ₹{sl_price}"
                        )
                        send_telegram(tg_token, tg_chat_id, milestone_msg)

                    # SMART EXIT: Check Trend Reversal
                    should_exit = False
                    exit_reason = ""

                    if len(live_data) >= 4:
                        # Simple RSI/Momentum reversal check using last few price points
                        last4 = live_data['Close'].iloc[-4:].values
                        rev_down = last4[0] < last4[1] and last4[2] > last4[3] # Peak formed
                        rev_up = last4[0] > last4[1] and last4[2] < last4[3] # Bottom formed
                        
                        if is_call and rev_down and pnl_pct > 2:
                            should_exit = True
                            exit_reason = "🔄 Trend Reversal Detected (Peak)"
                        elif not is_call and rev_up and pnl_pct > 2:
                            should_exit = True
                            exit_reason = "🔄 Trend Reversal Detected (Bottom)"
                        elif is_call and pnl_pct < -5:
                            should_exit = True
                            exit_reason = "Loss >5%, trend weakening"
                        elif not is_call and pnl_pct > 5:
                            should_exit = True
                            exit_reason = "Loss >5%, trend weakening"

                    if should_exit and not trade.get('exit_sent'):
                        trade['status'] = 'EXIT_FORCED'
                        trade['exit_time'] = now.isoformat()
                        trade['exit_price'] = live_price
                        trade['pnl'] = pnl_pct
                        trade['exit_sent'] = True
                        exit_msg = (
                            f"🚨 *EXIT NOW!* ⚠️\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"{opt_e} *{trade['stock']}* {trade.get('strike','')} {opt_t}\n"
                            f"📥 Entry: ₹{entry_price} → 📤 ₹{live_price:.2f}\n"
                            f"💔 *P&L: {pnl_pct:+.1f}%*\n"
                            f"📉 Reason: {exit_reason}\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"_🚨 Exit immediately - Trend Reversed_"
                        )
                        send_telegram(tg_token, tg_chat_id, exit_msg)

                        # Sync with Paper Portfolio UI
                        if 'paper_portfolio' in st.session_state:
                            for p in st.session_state['paper_portfolio']:
                                if p['stock'] == trade['stock'] and p['status'] == 'OPEN':
                                    p['status'] = 'CLOSED (REVERSAL)'
                                    p['current_pnl'] = round((live_price - entry_price) * 100, 2)
                    else:
                        # STATUS HOLD ALERT
                        if int(now.minute) % 15 == 0 and int(now.second) < 5: # Periodic update
                            hold_msg = (
                                f"⏳ *HOLD UPDATE* | {trade['stock']}\n"
                                f"━━━━━━━━━━━━━━\n"
                                f"⚡ Current: *₹{live_price:.2f}*\n"
                                f"📈 P&L: *{pnl_pct:+.1f}%*\n"
                                f"🎯 Tgt: ₹{target_price} | 🛑 SL: ₹{sl_price}\n"
                                f"💪 Status: *CONTINUE TO HOLD*"
                            )
                            send_telegram(tg_token, tg_chat_id, hold_msg)
            except:
                continue
        save_trades(active_trades)
        save_history(trade_history)

    # ===== NEW ENTRY ALERTS (Only Best Call @ 65%+ every 5 min) =====
    if scanning_allowed and time_since >= 300:
        if st.session_state.get('conf_ready', False) and 'tg_idx_msg' in st.session_state:
            send_telegram(tg_token, tg_chat_id, st.session_state['tg_idx_msg'])
            save_send_time()
            st.session_state['tg_send_count'] = load_send_count() + 1
            save_send_count(st.session_state['tg_send_count'])
        
        # Add BEST pick to Tracker if confidence >=65
        best_info = st.session_state.get('best_trade_info', {})
        if best_info and best_info.get('confidence', 0) >= 65:
            existing = [t['stock'] for t in active_trades if t.get('status') == 'ACTIVE']
            if best_info.get('stock') not in existing:
                new_trade = {
                    'stock': best_info.get('stock', 'N/A'),
                    'ticker': best_info.get('ticker', ''),
                    'type': best_info.get('type', 'CE'),
                    'strike': f"{best_info.get('strike', 'N/A')}",
                    'entry_price': best_info.get('entry', 0),
                    'target': best_info.get('target', 0),
                    'sl': best_info.get('sl', 0),
                    'confidence': best_info.get('confidence', 0),
                    'entry_time': now.isoformat(),
                    'status': 'ACTIVE',
                    'target_sent': False,
                    'sl_sent': False,
                    'last_milestone': best_info.get('entry', 0)
                }
                active_trades.append(new_trade)
                save_trades(active_trades)
                
                # Also add to Paper Portfolio session state for the UI tracker
                paper_trade = {
                    'stock': best_info.get('stock', 'N/A'),
                    'type': best_info.get('type', 'CE'),
                    'time': now.strftime('%H:%M'),
                    'status': 'OPEN',
                    'entry': best_info.get('entry', 0),
                    'target': best_info.get('target', 0),
                    'sl': best_info.get('sl', 0),
                    'current_pnl': 0
                }
                if 'paper_portfolio' not in st.session_state:
                    st.session_state['paper_portfolio'] = []
                
                # Check for duplicates in session state
                if not any(p['stock'] == paper_trade['stock'] and p['time'] == paper_trade['time'] for p in st.session_state['paper_portfolio']):
                    st.session_state['paper_portfolio'].append(paper_trade)
    elif time_since >= 300:
        save_send_time()

    # Countdown
    last_file = load_send_time()
    elapsed = int((now - last_file).total_seconds()) if last_file else 0
    next_check = max(0, 60 - (elapsed % 60))
    next_alert = max(0, 300 - elapsed)

    d_h, d_t, d_pct = get_success_ratio(trade_history, 1)
    w_h, w_t, w_pct = get_success_ratio(trade_history, 7)
    m_h, m_t, m_pct = get_success_ratio(trade_history, 30)
    conf_now = st.session_state.get('trade_confidence', 0)
    n_active = len([t for t in active_trades if t.get('status') == 'ACTIVE'])

    st.sidebar.success(f"🟢 {'📈 LIVE' if mkt_open else '🌙 CLOSED'} | Conf: {conf_now}%")
    st.sidebar.caption(f"📊 Sent: {load_send_count()} | Active: {n_active}")
    st.sidebar.caption(f"🎯 Min 65% | {'✅ PASS' if conf_now >= 65 else '❌ WAIT'}")
    st.sidebar.caption(f"⏱ Check: {next_check}s | Alert: {next_alert//60}m")
    if last_file:
        st.sidebar.caption(f"🕐 Last: {last_file.strftime('%H:%M:%S')}")
    st.sidebar.caption(f"📈 D:{d_pct}% W:{w_pct}% M:{m_pct}%")

    with st.sidebar.expander("🔍 Confidence Decoder"):
        st.markdown("""
        <div style="font-size:0.75rem;color:#aaa;">
        <b>How we calculate Score:</b><br>
        • <b>Trend (30%):</b> Price > EMA50 & Supertrend<br>
        • <b>Momentum (30%):</b> RSI > 60 (Buy) or < 40 (Sell)<br>
        • <b>Volatility (20%):</b> ADX > 25 (Strong Trend)<br>
        • <b>Volume (20%):</b> Vol > 1.5x Avg (Big Players)<br>
        <i>💎 Diamond Trade requires ALL to match!</i>
        </div>
        """, unsafe_allow_html=True)

    # Store for dashboard display
    st.session_state['active_trades'] = active_trades
    st.session_state['trade_history'] = trade_history
    st.session_state['success_daily'] = d_pct
    st.session_state['success_weekly'] = w_pct
    st.session_state['success_monthly'] = m_pct

    # Status footer
    conf_now = st.session_state.get('trade_confidence', 0)
    n_active = len([t for t in active_trades if t.get('status') == 'ACTIVE'])
    st.sidebar.markdown(f"""
    <div style="background:#001524; color:#00f2ff; padding:5px; border-radius:5px; font-size:10px; text-align:center; border:1px solid #1f2937;">
        🔄 Sync: 60s | Conf:{conf_now}% | Active:{n_active}
    </div>
    """, unsafe_allow_html=True)

elif tg_auto and (not tg_token or not tg_chat_id):
    st.sidebar.warning("⚠️ Enter Bot Token & Chat ID")
elif tg_auto:
    st.sidebar.info("⏳ Waiting for Market Data...")
st.sidebar.markdown("---")

# --- DESIGN SYSTEM ---
st.markdown("""
<style>
.stApp { background-color: #050510; color: #ffffff; }
.index-box { 
    background: rgba(17, 24, 39, 0.7); 
    padding: 10px; 
    border-radius: 8px; 
    min-width: 130px; 
    margin:4px; 
    border:1px solid #1f2937; 
    text-align:center; 
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.index-box:hover { transform: translateY(-5px); border-color: #00f2ff; box-shadow: 0 0 15px rgba(0,242,255,0.2); }
.bullish-shadow { border-bottom: 3px solid #00e676; box-shadow:0 4px 10px rgba(0,230,118,0.15);}
.bearish-shadow { border-bottom: 3px solid #ff1744; box-shadow:0 4px 10px rgba(255,23,68,0.15);}
.metric-card { 
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.8), rgba(22, 33, 62, 0.8)); 
    padding:12px; 
    border-radius:10px; 
    text-align:center; 
    margin-bottom:8px; 
    border:1px solid #333; 
    box-shadow:0 4px 12px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
    animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(0, 230, 118, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0); } }
.bullish-glow { animation: pulse 2s infinite; }
.bullish { color:#00e676 !important; font-weight:800; text-shadow: 0 0 5px rgba(0,230,118,0.5);}
.bearish { color:#ff1744 !important; font-weight:800; text-shadow: 0 0 5px rgba(255,23,68,0.5);}
.main-metric { font-size:1.4rem; font-weight:900; color:#FFFFFF !important; text-shadow: 0 0 10px rgba(255,255,255,0.2);}
.sub-metric { font-size:0.75rem; color:#FFFFFF !important; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;}
.index-label { font-size:0.75rem; color:#FFFFFF !important; font-weight:700; text-transform: uppercase; letter-spacing:0.5px;}
.index-price { font-size:1.2rem; font-weight:900; color:#FFFFFF !important;}
.prediction-panel { 
    background: rgba(0,0,0,0.5); 
    border-radius:12px; 
    padding:20px; 
    border:1px solid #444; 
    margin:10px 0; 
    text-align:center;
    box-shadow: inset 0 0 20px rgba(0,242,255,0.05);
}
.trade-card { border-radius:10px; padding:15px; margin-bottom:12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid #333;}
.stTabs [data-baseweb="tab"] { 
    padding:8px 12px; 
    background-color:rgba(26, 26, 46, 0.5); 
    border-radius:5px; 
    margin:2px; 
    border:1px solid #333; 
    font-size:0.85rem;
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"]:hover { background-color: rgba(0,242,255,0.1); border-color: #00f2ff; }
</style>
""", unsafe_allow_html=True)

# Index boxes removed as per user request (speeds up load)
# active_indices = {k: v for k, v in INDEX_MAP.items() if k != "ALL F&O"}
# idx_cols = st.columns(len(active_indices))
# for i, (name, cfg) in enumerate(active_indices.items()):
#     with idx_cols[i]:
#         last_p, first_p, used_ticker = get_index_price(name, cfg["ticker"])
#         if last_p is not None and first_p is not None and first_p != 0:
#             chg = last_p - first_p
#             pct = (chg / first_p) * 100
#             cls = "bullish-shadow" if chg > 0 else "bearish-shadow" if chg < 0 else ""
#             clr = "#00e676" if chg > 0 else "#ff1744" if chg < 0 else "#888"
#             st.markdown(f'''
#                 <div class="index-box {cls}">
#                     <div class="index-label">{name}</div>
#                     <div class="index-price">{last_p:,.2f}</div>
#                     <div style="font-size:0.85rem;color:{clr};font-weight:bold;">{chg:+.2f} ({pct:+.2f}%)</div>
#                 </div>
#             ''', unsafe_allow_html=True)
#         else:
#             st.markdown(f'<div class="index-box"><div style="color:#aaa">{name}</div><div style="color:#666">No Data</div></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
st.markdown("<h2 style='text-align:center; color:#00f2ff; margin:10px 0;'>🎯 MARSH MUTHU 326 ULTIMATE TERMINAL</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 3, 1])
with c1: sel_tf = st.selectbox("⏱ Interval", ["1m","5m","15m"], index=1)
with c2:
    # Uses sel_idx and stk_list defined in the sidebar for consistency
    if sel_nav in ["🏠 HOME", "🔥 FIRE TRADE", "📡 RADAR"]:
        sel_stk = st.selectbox("📊 Stock Selection", ["-- INDEX --"] + [s.replace(".NS","") for s in stk_list])
    else:
        sel_stk = st.selectbox("📊 Stock Selection", ["-- INDEX --"] + [s.replace(".NS","") for s in ALL_FO_STOCKS]) 
with c3: st.button("🔄 REFRESH", on_click=lambda: st.cache_data.clear(), use_container_width=True)

# ==========================================
# 🚀 LOAD & ANALYZE
# ==========================================
target = INDEX_MAP[sel_idx]["ticker"] if sel_stk == "-- INDEX --" else sel_stk + ".NS"
main_df = calculate_indicators(load_data(target, sel_tf))

# --- Safe defaults ---
pro_signal = "WAIT"; mom_speed = 50.0; price = tgt = sl = 0.0
rsi_val = adx_val = 0.0; market_power = "💤 WEAK"; v_ratio = 1.0
curr = None; scalp_sig = intra_sig = swing_sig = forecast = smc = ha_stat = "N/A"
vol_pressure = "⚪ NEUTRAL"; pressure_stat = "Neutral"; sig_validity = "Neutral"
support_lvl = resistance_lvl = 0.0
pattern_now = "None"
atr = 0.0

if not main_df.empty and len(main_df) > 20:
    curr = main_df.iloc[-1]
    rsi_val = float(curr['RSI']); adx_val = float(curr['ADX'])
    price = float(curr['Close'])
    v_ratio = float(curr['VolRatio']) if 'VolRatio' in curr.index else 1.0
    
    # Accurate Momentum Speed (Pine Script Logic)
    mom_speed = float(curr.get('MomentumSpeed', 50.0))
    
    atr = float((main_df['High'] - main_df['Low']).rolling(14).mean().iloc[-1])

    if "CALL" in str(curr['Signal']):
        tgt = price + (atr * 1.5); sl = price - (atr * 1.2)
    elif "PUT" in str(curr['Signal']):
        tgt = price - (atr * 1.5); sl = price + (atr * 1.2)
    else:
        tgt = sl = price

    pro_signal = str(curr['Signal'])
    market_power = "🔥 STRONG" if adx_val > 25 else "⚡ MODERATE" if adx_val > 18 else "💤 WEAK"

    forecast = str(curr.get('Forecast', 'Wait'))
    smc = str(curr.get('SMC', 'Neutral'))
    ha_stat = str(curr.get('HA_Status', 'Neutral'))
    vol_pressure = str(curr.get('Vol_Pressure', '⚪ NEUTRAL'))
    pressure_stat = str(curr.get('PressureStatus', 'Neutral'))
    sig_validity = str(curr.get('SignalValidity', 'Neutral'))
    support_lvl = float(curr.get('Support', price * 0.99))
    resistance_lvl = float(curr.get('Resistance', price * 1.01))
    pattern_now = str(curr.get('Pattern', 'None'))
    scalp_sig = str(curr.get('Signal', 'WAIT')) # Default to main signal if specific not found
    intra_sig = str(curr.get('Signal', 'WAIT'))
    swing_sig = str(curr.get('Forecast', 'WAIT')) # Swing often linked to forecast

# -------- 4. DASHBOARD LAYOUT --------

# Title & Header
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🚀 PRIME SKILL DEVELOPMENT")
    st.markdown("**CEO: MuthuKumar Krishnan** | *Automated AI Trading Terminal*")
with c2:
    if is_market_hours():
        st.success("🟢 MARKET OPEN")
    else:
        st.error("🔴 MARKET CLOSED")

# Sidebar
st.sidebar.title("PRIME SKILL")
st.sidebar.markdown("---")

# --- SIDEBAR: WhatsApp Alerts ---
st.sidebar.markdown("---")
st.sidebar.subheader("📱 WhatsApp Alerts")
user_phone = st.sidebar.text_input("Mobile", value="919629888326")
if "WAIT" not in pro_signal and price > 0:
    msg = f"*MARSH MUTHU 326*%0A*{sel_stk if sel_stk != '-- INDEX --' else sel_idx}*%0A*Signal:* {pro_signal}%0A*Price:* {price:.2f}%0A*Target:* {tgt:.2f}%0A*SL:* {sl:.2f}"
    if st.sidebar.button("🚀 Send Current Alert", key="wa_curr", use_container_width=True):
        st.sidebar.markdown(f'<meta http-equiv="refresh" content="0; url=https://wa.me/{user_phone}?text={msg}">', unsafe_allow_html=True)

if 'tg_idx_msg' in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.success("🏆 Best Pick Alert Ready")
    best_msg_wa = urllib.parse.quote(st.session_state['tg_idx_msg'].replace('\n', '\n'))
    if st.sidebar.button("💎 Send Best Pick Alert", key="wa_best", use_container_width=True):
        st.sidebar.markdown(f'<meta http-equiv="refresh" content="0; url=https://wa.me/{user_phone}?text={best_msg_wa}">', unsafe_allow_html=True)

# ==========================================
# 🏠 HOME WORKSPACE
# ==========================================
# COLLECT DATA FOR VIEWS
view_data = {
    'curr': curr, 'rsi_val': rsi_val, 'adx_val': adx_val, 'v_ratio': v_ratio,
    'mom_speed': mom_speed, 'market_power': market_power, 'vol_pressure': vol_pressure,
    'pro_signal': pro_signal, 'price': price, 'tgt': tgt, 'sl': sl, 'forecast': forecast,
    'smc': smc, 'ha_stat': ha_stat, 'pressure_stat': pressure_stat, 
    'sig_validity': sig_validity, 'support_lvl': support_lvl, 'resistance_lvl': resistance_lvl,
    'pattern_now': pattern_now, 'stock_rows': stock_rows, 'sel_idx': sel_idx,
    'target': target, 'main_df': main_df, 'sdf': sdf,
    'trades': load_trades(), 'history': load_history()
}

# --- RENDER SELECTED WORKSPACE ---
if sel_nav == "🏠 HOME":
    render_home(view_data)

elif sel_nav == "🏛️ INSTITUTIONAL":
    render_institutional_view(view_data)

elif sel_nav == "💎 ELITE F&O":
    render_elite_fno_view(view_data)

# ==========================================
# 💎 PREMIUM OPTION CHAIN WORKSPACE
# ==========================================
elif sel_nav == "💎 CHAIN":
    render_chain(view_data)

# ==========================================
# 💪 PRO ENGINE WORKSPACE
# ==========================================
elif sel_nav == "💪 PRO ENGINE":
    render_pro_engine(view_data)

# -------- 📡 RADAR SCAN --------
elif sel_nav == "📡 RADAR":
    render_radar(view_data)

# -------- 📊 CHART --------
elif sel_nav == "📊 CHART":
    render_chart(view_data)

# ==========================================
# 🧠 STRATEGY HUB TAB (5-Row Professional View)
# ==========================================
elif sel_nav == "🧠 STRATEGY HUB":
    render_strategy_hub(view_data)

# ==========================================
# 📊 F&O ANALYSIS TAB
# ==========================================
elif sel_nav == "📉 F&O":
    render_fno(view_data)

# ==========================================
# 🌾 COMMODITY TAB
# ==========================================
elif sel_nav == "🛢 COMMODITY":
    render_commodity(view_data)

# -------- 🔥 FIRE TRADE (BTST) --------
elif sel_nav == "🔥 FIRE TRADE":
    render_fire_trade(view_data)

# ==========================================
# 📈 PERFORMANCE & PAPER TRADING
# ==========================================
elif sel_nav == "📈 PAPER TRADING":
    render_paper_trading(view_data)

    st.markdown("#### 📋 AUTO-TRACKER (Signals Sent to Telegram)")
    if st.session_state['paper_portfolio']:
        paper_df = pd.DataFrame(st.session_state['paper_portfolio'])
        # Sort by latest
        paper_df = paper_df.iloc[::-1]
        
        # Display as a premium list
        for idx, t in paper_df.iterrows():
            clr = "#00e676" if t['type'] == 'CE' else "#ff1744"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border:1px solid #333; border-radius:8px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:bold; color:{clr};">{t['stock']} {t['type']} (Sent @ {t['time']})</span>
                    <span style="color:#aaa; font-size:0.8rem;">Status: {t['status']}</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(4,1fr); margin-top:5px; font-size:0.85rem;">
                    <div>Entry: ₹{t['entry']:.2f}</div>
                    <div>Target: ₹{t['target']:.2f}</div>
                    <div>SL: ₹{t['sl']:.2f}</div>
                    <div style="color:#00f2ff; font-weight:bold;">P&L: ₹{t['current_pnl']:.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to close trade manually for testing capital growth
            if t['status'] == 'OPEN':
                if st.button(f"Close {t['stock']} Trade", key=f"close_{idx}"):
                    # Simulate 20% average win
                    profit = 2000.0 # 20% on 10k allocation
                    st.session_state['virtual_capital'] += profit
                    st.session_state['paper_portfolio'][idx]['status'] = 'CLOSED'
                    st.session_state['paper_portfolio'][idx]['current_pnl'] = profit
                    st.rerun()
    else:
        st.info("📡 No alerts sent yet. Every 'Best Call' sent to Telegram will be automatically tracked here for 1 Lakh Capital analysis.")

    # 🛡️ INSTITUTIONAL MONEY MANAGEMENT
    st.markdown("---")
    st.markdown("#### 🛡️ RISK & FUND MANAGEMENT PROTOCOL")
    rm1, rm2, rm3 = st.columns(3)
    with rm1:
        st.info("**CAPITAL ALLOCATION**\n- Capital: ₹1,00,000\n- Per Trade: ₹10,000 (10%)\n- Max Open: 2 Trades")
    with rm2:
        st.warning("**RISK CONTROL**\n- SL Per Trade: 10%\n- SL Amount: ₹1,000\n- Max Daily Loss: ₹2,000")
    with rm3:
        st.success("**TARGET STRATEGY**\n- Target Per Trade: 40%\n- Profit: ₹4,000\n- Goal: ₹25,000 (Weekly)")

    st.markdown("#### 📊 TARGET REACH ANALYSIS")
    req_wins = round(25000 / 4000, 1)
    st.markdown(f"""
    <div style="background:rgba(0,230,118,0.1); border:1px solid #00e676; border-radius:10px; padding:15px;">
        <h4 style="margin:0; color:#00e676;">How to reach ₹25,000 Weekly Target?</h4>
        <p style="color:#aaa; margin-top:10px;">
            To hit your 25% weekly ROI goal with <b>Fund-Based Management</b>:<br>
            1. You need approximately <b>{req_wins} high-conviction wins</b> (average 40% gain).<br>
            2. At <b>₹10,000 allocation</b> per trade, each "Jackpot" hit brings you closer by ₹4,000 - ₹10,000.<br>
            3. Stick to the <b>Best Calls Only</b> picked by the AI to maintain a >65% Win Rate.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1a1a2e;border-radius:10px;padding:15px;margin-top:15px;border:1px solid #333;">
        <div style="color:#00f2ff;font-weight:bold;margin-bottom:8px;">📋 System Features:</div>
        <div style="color:#aaa;font-size:0.85rem;line-height:1.6;">
            • <b>AUTO-TRACKER ACTIVE</b> - Every 'Best Call' sent to Telegram is logged below automatically.<br>
            • <b>Weekly Target Fokus:</b> System scans for signals specifically optimized for the ₹25k goal.<br>
            • <b>Risk-Weighted Entry:</b> Trades are only picked if the RR ratio is > 1:3.<br>
            • <b>Confidence Filter:</b> Only trades with ≥65% score are alerted & tracked<br>
            • <b>Auto-Cleanup:</b> Completed trades vanish after 48 hours
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------- 💎 CONVICTION RADAR (Diamond Jackpot) --------
elif sel_nav == "💎 CONVICTION":
    render_conviction(view_data)

# ==========================================
# 📋 TRADE MANAGEMENT
# ==========================================
elif sel_nav == "📋 TRADE MGMT":
    render_trade_management(view_data)

# ==========================================
# 🏛️ INSTITUTIONAL ELITE WORKSPACE
# ==========================================
elif sel_nav == "🏛️ INSTITUTIONAL":
    render_institutional_view()

# -------- 💎 PLANS & ACCESS --------
elif sel_nav == "💎 PLANS & ACCESS":
    render_plans(view_data)

st.divider()
st.caption("© 2026 MARSH MUTHU 326 | Ultimate Pro Terminal v3.0 | Scalping + Intraday + Swing + Commodity")
