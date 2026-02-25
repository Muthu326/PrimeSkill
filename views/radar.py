import streamlit as st
import pandas as pd
from datetime import datetime

def get_sector(ticker):
    t = ticker.upper()
    if "BANK" in t: return "BANK"
    if "FIN" in t or "BAJ" in t or "CHOLA" in t: return "FINANCE"
    if "AUTO" in t or "MOTORS" in t or "M&M" in t: return "AUTO"
    if "TCS" in t or "INFY" in t or "TECH" in t or "WIPRO" in t or "HCL" in t: return "IT"
    if "PHARM" in t or "LAB" in t or "CIPLA" in t or "DRREDDY" in t: return "PHARMA"
    if "STEEL" in t or "ALCO" in t or "COPPER" in t or "NMDC" in t: return "METAL"
    if "POWER" in t or "NTPC" in t or "OIL" in t or "ONGC" in t or "BPCL" in t: return "ENERGY"
    if "ITC" in t or "LEVER" in t or "BRIT" in t or "NESTLE" in t: return "FMCG"
    return "OTHERS"

def render_radar(data):
    """
    Renders the RADAR workspace
    """
    st.markdown("### 📋 Momentum Radar Workspace")
    st.markdown("### 🏆 Top Trade Setups (Pro Scan 180+ Stocks)")
    
    sector_performance = {
        "BANK": [], "FINANCE": [], "AUTO": [], "IT": [], "PHARMA": [], "METAL": [], "ENERGY": [], "FMCG": []
    }
    
    stock_rows = data.get('stock_rows', [])
    all_radar = []
    
    for r in stock_rows:
        sec = get_sector(r['Ticker'])
        if sec != "OTHERS":
            sector_performance[sec].append(r['Chg%'])
            
        if "BUY" in r['Scalp'] or "BUY" in r['Intraday']:
            is_call = "CALL" in r['Scalp'] or "CALL" in r['Intraday']
            pr = r['Price']
            atr_v = r.get('ATR', pr * 0.01)
            
            sl_val = pr - atr_v*1.2 if is_call else pr + atr_v*1.2
            t1_val = pr + atr_v if is_call else pr - atr_v
            t2_val = pr + atr_v*1.5 if is_call else pr - atr_v*1.5
            
            score = 0
            if r['ADX'] > 25: score += 30
            if (is_call and r['RSI'] > 60) or (not is_call and r['RSI'] < 40): score += 30
            if "HEAVY" in r['Vol Pressure']: score += 40
            
            step = 10 if pr < 1000 else 50
            strike_val = round(pr / step) * step
            st_t = "CE" if is_call else "PE"
            
            # 🔍 MTF Status
            from services.market_engine import get_mtf_confluence
            _, mtf_s = get_mtf_confluence(r['Ticker'])
            mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
            
            all_radar.append({
                "Stock": r['Stock'], "Price": pr,
                "Scalp": r['Scalp'], "Intraday": r['Intraday'],
                "Swing": r['Swing'], "Entry": pr,
                "SL": round(sl_val, 2), "T1": round(t1_val, 2), "T2": round(t2_val, 2),
                "Strike": f"{strike_val} {st_t}", "RSI": r['RSI'],
                "ADX": r['ADX'], "Conf%": score, "ST_Dir": r.get('ST_Direction', 0),
                "Trend": r['Trend'], "Pressure": r['Vol Pressure'],
                "MTF": f"{mtf_s} {mtf_icon}"
            })
    
    st.markdown("#### 🏭 Sector Performance (Live %)")
    sec_cols = st.columns(8)
    for i, (sec_name, vals) in enumerate(sector_performance.items()):
        if vals:
            avg_chg = sum(vals) / len(vals)
            s_clr = "#00e676" if avg_chg > 0 else "#ff1744"
            with sec_cols[i]:
                st.markdown(f"""
                <div style="background:#111;border:1px solid {s_clr};border-radius:8px;padding:10px;text-align:center;">
                    <div style="color:#aaa;font-size:0.7rem;">{sec_name}</div>
                    <div style="color:{s_clr};font-weight:bold;font-size:1rem;">{avg_chg:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("#### 🔥 High Confidence Setups")
    top = sorted([x for x in all_radar if x['Conf%'] >= 60], key=lambda x: x['Conf%'], reverse=True)[:6]
    
    if top:
        for t in top:
            bd = "#00e676" if "CE" in t['Strike'] else "#ff1744"
            bg = "rgba(0,230,118,0.12)" if "CE" in t['Strike'] else "rgba(255,23,68,0.12)"
            st.markdown(f"""<div class="trade-card" style="background:{bg}; border:1px solid {bd}; padding:15px; border-radius:10px; margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div><span style="font-size:1.3rem;font-weight:bold;color:white;">{t['Stock']}</span>
                    <span style="background:{bd};color:white;padding:3px 10px;border-radius:5px;margin-left:10px;font-size:0.8rem;">{t['Scalp']}</span>
                    <span style="color:#00f2ff;margin-left:10px;">🎯 {t['Strike']}</span>
                    <span style="color:#aaa;font-size:0.75rem;margin-left:10px;">🔍 {t['MTF']}</span></div>
                    <div style="color:#ffd740;font-weight:bold;font-size:1.2rem;">{t['Conf%']}% Confidence</div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px;background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;">
                    <div style="text-align:center;"><div style="color:#888;font-size:0.7rem;">ENTRY</div><div style="color:white;font-weight:bold;">₹{t['Price']}</div></div>
                    <div style="text-align:center;"><div style="color:#ff1744;font-size:0.7rem;">SL</div><div style="color:#ff1744;font-weight:bold;">₹{t['SL']}</div></div>
                    <div style="text-align:center;"><div style="color:#00e676;font-size:0.7rem;">T1</div><div style="color:#00e676;font-weight:bold;">₹{t['T1']}</div></div>
                    <div style="text-align:center;"><div style="color:#00e676;font-size:0.7rem;">T2</div><div style="color:#00e676;font-weight:bold;">₹{t['T2']}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("🔭 No high-confidence setups found.")
    
    st.markdown("### 📡 Full Radar Table")
    st.dataframe(pd.DataFrame(all_radar), use_container_width=True, hide_index=True)
