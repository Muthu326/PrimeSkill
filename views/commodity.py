import streamlit as st
import pandas as pd
import yfinance as yf

def render_commodity(data):
    """
    Renders the COMMODITY workspace
    """
    st.markdown("### 🛢 Commodity Market Analysis (Live)")
    st.caption("Tracking Gold, Silver, Crude Oil and Natural Gas")
    
    commodities = {
        "Gold (GC=F)": "GC=F",
        "Silver (SI=F)": "SI=F",
        "Crude Oil (CL=F)": "CL=F",
        "Natural Gas (NG=F)": "NG=F"
    }
    
    c1, c2, c3, c4 = st.columns(4)
    cols = [c1, c2, c3, c4]
    
    for i, (name, ticker) in enumerate(commodities.items()):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if not hist.empty:
                last_p = hist['Close'].iloc[-1]
                prev_p = hist['Close'].iloc[-2]
                chg = last_p - prev_p
                pct = (chg / prev_p) * 100
                cols[i].metric(name, f"${last_p:,.2f}", f"{pct:+.2f}%")
        except:
            cols[i].error(f"Error fetching {name}")

    st.markdown("---")
    st.subheader("🌋 US Market Correlation")
    st.info("Commodities often show inverse correlation with the USD Index (DX-Y.NYB)")
