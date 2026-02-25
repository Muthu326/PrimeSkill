import streamlit as st
import pandas as pd

def render_fire_trade(data):
    """
    Renders the FIRE TRADE workspace
    """
    st.markdown("### 🔥 FIRE TRADE: BTST Predictions")
    sdf = data.get('sdf', pd.DataFrame())
    
    btst_bullish = []
    btst_bearish = []
    
    if not sdf.empty:
        from services.market_engine import get_expiry_details, option_premium_estimate, calculate_option_greeks, get_mtf_confluence
        
        for _, r in sdf.iterrows():
            if r.get('Pos_In_Range', 0.5) > 0.90 and r['Chg%'] > 1.5:
                btst_bullish.append(r)
            elif r.get('Pos_In_Range', 0.5) < 0.10 and r['Chg%'] < -1.5:
                btst_bearish.append(r)
        
        btst_bullish.sort(key=lambda x: x['Chg%'], reverse=True)
        btst_bearish.sort(key=lambda x: x['Chg%'])
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🟢 BULLISH BTST (Buy Stocks)")
            if btst_bullish:
                for r in btst_bullish[:10]:
                    entry_px = r['Price']
                    step_size = 50 if entry_px > 2000 else 10 if entry_px > 500 else 5
                    strike = round(entry_px / step_size) * step_size
                    
                    dte, exp_date, _ = get_expiry_details(r['Stock'])
                    iv_est = max(15, min(50, 30 + abs(r['RSI'] - 50) * 0.3))
                    premium = option_premium_estimate(entry_px, strike, iv_est, dte, "CE")
                    tgt = round(premium * 1.3, 2)
                    sl = round(premium * 0.9, 2)
                    
                    # MTF & Value
                    iv_val, tv_val, money_s = calculate_option_greeks(entry_px, strike, premium, "CE")
                    _, mtf_s = get_mtf_confluence(r['Ticker'])
                    mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"

                    st.success(f"**{r['Stock']}** | CMP: ₹{entry_px:.2f} (+{r['Chg%']:.2f}%)")
                    st.markdown(f"⚡ **{strike} CE** (Entry: ₹{premium:.1f}) | 🎯 Tgt: ₹{tgt} | 🛑 SL: ₹{sl}")
                    st.markdown(f"""<div style="font-size:0.7rem; color:#aaa; margin-bottom:10px;">
                        🔍 MTF: {mtf_s} {mtf_icon} | 💎 {money_s}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No strong Buying momentum found.")
        
        with c2:
            st.markdown("### 🔴 BEARISH BTST (Sell Stocks)")
            if btst_bearish:
                for r in btst_bearish[:10]:
                    entry_px = r['Price']
                    step_size = 50 if entry_px > 2000 else 10 if entry_px > 500 else 5
                    strike = round(entry_px / step_size) * step_size
                    
                    dte, exp_date, _ = get_expiry_details(r['Stock'])
                    iv_est = max(15, min(50, 30 + abs(r['RSI'] - 50) * 0.3))
                    premium = option_premium_estimate(entry_px, strike, iv_est, dte, "PE")
                    tgt = round(premium * 1.3, 2)
                    sl = round(premium * 0.9, 2)
                    
                    # MTF & Value
                    iv_val, tv_val, money_s = calculate_option_greeks(entry_px, strike, premium, "PE")
                    _, mtf_s = get_mtf_confluence(r['Ticker'])
                    mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"

                    st.error(f"**{r['Stock']}** | CMP: ₹{entry_px:.2f} ({r['Chg%']:.2f}%)")
                    st.markdown(f"⚡ **{strike} PE** (Entry: ₹{premium:.1f}) | 🎯 Tgt: ₹{tgt} | 🛑 SL: ₹{sl}")
                    st.markdown(f"""<div style="font-size:0.7rem; color:#aaa; margin-bottom:10px;">
                        🔍 MTF: {mtf_s} {mtf_icon} | 💎 {money_s}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No strong Selling momentum found.")
    else:
        st.warning("No data available for scan.")
