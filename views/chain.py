import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

def render_chain(data):
    """
    Renders the CHAIN workspace
    """
    pro_signal = data.get('pro_signal', "WAIT")
    price = data.get('price', 0.0)
    tgt = data.get('tgt', 0.0)
    sl = data.get('sl', 0.0)
    target = data.get('target', "NIFTY") # This is the ticker symbol/index ticker
    
    sig_bg = "rgba(0,230,118,0.15)" if "CALL" in pro_signal else "rgba(255,23,68,0.15)" if "PUT" in pro_signal else "rgba(255,215,64,0.1)"
    sig_bd = "#00e676" if "CALL" in pro_signal else "#ff1744" if "PUT" in pro_signal else "#ffd740"
    st.markdown(f"""
    <div style="background:{sig_bg};border:2px solid {sig_bd};border-radius:10px;padding:12px;text-align:center;margin-bottom:15px;">
        <span style="font-size:1.5rem;font-weight:900;color:{sig_bd};text-shadow:0 0 10px {sig_bd}50;">⚡ F&O SIGNAL: {pro_signal}</span>
        <span style="color:#aaa;margin-left:15px;">Entry: ₹{price:,.2f} | Target: ₹{tgt:,.2f} | SL: ₹{sl:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    try:
        tk = yf.Ticker(target)
        expiries = tk.options
        if expiries:
            sel_exp = st.selectbox("📅 Select Expiry Date", expiries[:5], key="fno_expiry")
            days_to_exp = max((datetime.strptime(sel_exp, "%Y-%m-%d") - datetime.now()).days, 1)
            st.caption(f"⏳ Days to Expiry: **{days_to_exp}** | Expiry: **{sel_exp}**")

            chain = tk.option_chain(sel_exp)
            calls = chain.calls.copy()
            puts = chain.puts.copy()

            step = 50 if "NIFTY" in target.upper() else 100
            atm = round(price / step) * step if price > 0 else calls['strike'].median()

            rng = 500 if "NIFTY" in target.upper() else 300
            calls = calls[(calls['strike'] >= atm - rng) & (calls['strike'] <= atm + rng)].copy()
            puts = puts[(puts['strike'] >= atm - rng) & (puts['strike'] <= atm + rng)].copy()

            def calc_greeks(row, is_call=True):
                iv = float(row.get('impliedVolatility', 0.3))
                s = float(row['strike'])
                ltp = float(row.get('lastPrice', 0))
                delta = np.clip(0.5 + 0.01 * (price - s) if is_call else -0.5 + 0.01 * (price - s), -1, 1)
                theta = -(iv * ltp * 0.1) / max(days_to_exp, 1)
                gamma = max(0.001, 0.05 - abs(price - s) * 0.0001)
                return round(delta, 3), round(theta, 2), round(gamma, 4)

            def classify_moneyness(strike, is_call=True):
                diff = price - strike if is_call else strike - price
                if abs(diff) < step: return "ATM"
                elif diff > 0: return "ITM"
                else: return "OTM"

            def premium_signal(row, is_call=True):
                ltp = float(row.get('lastPrice', 0))
                bid = float(row.get('bid', 0)); ask = float(row.get('ask', 0))
                oi = float(row.get('openInterest', 0)); vol = float(row.get('volume', 0))
                spread = ask - bid if ask > 0 and bid > 0 else 999
                if is_call:
                    if vol > 0 and oi > 0 and spread < ltp * 0.1: return "🟢 BULLISH"
                    elif spread > ltp * 0.3: return "🔴 BEARISH"
                    else: return "🟡 NEUTRAL"
                else:
                    if vol > 0 and oi > 0 and spread < ltp * 0.1: return "🔴 BEARISH"
                    elif spread > ltp * 0.3: return "🟢 BULLISH"
                    else: return "🟡 NEUTRAL"

            if not calls.empty:
                calls[['Delta','Theta','Gamma']] = calls.apply(lambda r: pd.Series(calc_greeks(r, True)), axis=1)
                calls['Moneyness'] = calls['strike'].apply(lambda s: classify_moneyness(s, True))
                calls['Premium_Signal'] = calls.apply(lambda r: premium_signal(r, True), axis=1)
                calls['Premium'] = calls['lastPrice'].round(2)

            if not puts.empty:
                puts[['Delta','Theta','Gamma']] = puts.apply(lambda r: pd.Series(calc_greeks(r, False)), axis=1)
                puts['Moneyness'] = puts['strike'].apply(lambda s: classify_moneyness(s, False))
                puts['Premium_Signal'] = puts.apply(lambda r: premium_signal(r, False), axis=1)
                puts['Premium'] = puts['lastPrice'].round(2)

            st.markdown("### 💰 Option Premium Overview")
            best_ce_strike = atm; best_pe_strike = atm
            best_ce_prem = 0.0; best_pe_prem = 0.0

            if not calls.empty:
                atm_calls = calls[calls['Moneyness'] == 'ATM']
                if not atm_calls.empty:
                    best_ce_strike = float(atm_calls.iloc[0]['strike'])
                    best_ce_prem = float(atm_calls.iloc[0]['lastPrice'])
            if not puts.empty:
                atm_puts = puts[puts['Moneyness'] == 'ATM']
                if not atm_puts.empty:
                    best_pe_strike = float(atm_puts.iloc[0]['strike'])
                    best_pe_prem = float(atm_puts.iloc[0]['lastPrice'])

            oc1, oc2, oc3, oc4 = st.columns(4)
            ce_clr = "#00e676" if "CALL" in pro_signal else "#aaa"
            oc1.markdown(f'<div class="metric-card" style="border-left:4px solid #00e676;"><div class="sub-metric">📗 CE Premium (ATM {best_ce_strike:.0f})</div><div class="main-metric" style="color:{ce_clr};">₹{best_ce_prem:.2f}</div></div>', unsafe_allow_html=True)
            pe_clr = "#ff1744" if "PUT" in pro_signal else "#aaa"
            oc2.markdown(f'<div class="metric-card" style="border-left:4px solid #ff1744;"><div class="sub-metric">📕 PE Premium (ATM {best_pe_strike:.0f})</div><div class="main-metric" style="color:{pe_clr};">₹{best_pe_prem:.2f}</div></div>', unsafe_allow_html=True)
            
            total_ce_oi = float(calls['openInterest'].sum()) if not calls.empty and 'openInterest' in calls.columns else 1
            total_pe_oi = float(puts['openInterest'].sum()) if not puts.empty and 'openInterest' in puts.columns else 1
            pcr_oi = total_pe_oi / max(total_ce_oi, 1)
            pcr_color = "#00e676" if pcr_oi > 1.1 else "#ff1744" if pcr_oi < 0.8 else "#ffd740"
            pcr_label = "BULLISH" if pcr_oi > 1.1 else "BEARISH" if pcr_oi < 0.8 else "NEUTRAL"
            oc3.markdown(f'<div class="metric-card" style="border-left:4px solid {pcr_color};"><div class="sub-metric">📊 PCR (OI Based)</div><div class="main-metric" style="color:{pcr_color};">{pcr_oi:.2f} ({pcr_label})</div></div>', unsafe_allow_html=True)
            
            action_text = "BUY CALL CE" if "CALL" in pro_signal else "BUY PUT PE" if "PUT" in pro_signal else "WAIT"
            action_clr = "#00e676" if "CALL" in pro_signal else "#ff1744" if "PUT" in pro_signal else "#ffd740"
            oc4.markdown(f'<div class="metric-card" style="border-left:4px solid {action_clr};"><div class="sub-metric">🎯 F&O Action</div><div class="main-metric" style="color:{action_clr};">{action_text}</div></div>', unsafe_allow_html=True)

            rec_strike = atm
            rec_type = "CE" if "CALL" in pro_signal else "PE" if "PUT" in pro_signal else "CE/PE"
            rec_prem = best_ce_prem if "CALL" in pro_signal else best_pe_prem if "PUT" in pro_signal else max(best_ce_prem, best_pe_prem)

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d1b2a,#1b2838);border:2px solid {action_clr};border-radius:12px;padding:18px;margin:10px 0;text-align:center;">
                <div style="font-size:0.8rem;color:#888;">🎯 RECOMMENDED OPTION TRADE</div>
                <div style="font-size:2rem;font-weight:900;color:{action_clr};margin:8px 0;">{rec_strike:.0f} {rec_type}</div>
                <div style="font-size:1.2rem;color:white;">Premium: <span style="color:{action_clr};font-weight:bold;">₹{rec_prem:.2f}</span></div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px;">
                    <div><div style="color:#888;font-size:0.65rem;">ENTRY</div><div style="color:white;font-weight:bold;">₹{rec_prem:.2f}</div></div>
                    <div><div style="color:#00e676;font-size:0.65rem;">TARGET</div><div style="color:#00e676;font-weight:bold;">₹{rec_prem*1.3:.2f}</div></div>
                    <div><div style="color:#ff1744;font-size:0.65rem;">STOP LOSS</div><div style="color:#ff1744;font-weight:bold;">₹{rec_prem*0.7:.2f}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📊 Full Option Chain (Premium + Greeks + Signal)")
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("#### 📗 CALLS (CE)", unsafe_allow_html=True)
                if not calls.empty:
                    call_disp = calls[['strike','Premium','Moneyness','Premium_Signal','Delta','Theta','Gamma','openInterest','volume','impliedVolatility']].copy()
                    call_disp.columns = ['Strike','Premium ₹','Type','Signal','Delta','Theta','Gamma','OI','Vol','IV']
                    call_disp['IV'] = (call_disp['IV'] * 100).round(1)
                    st.dataframe(call_disp, use_container_width=True, hide_index=True)
            with cc2:
                st.markdown("#### 📕 PUTS (PE)", unsafe_allow_html=True)
                if not puts.empty:
                    put_disp = puts[['strike','Premium','Moneyness','Premium_Signal','Delta','Theta','Gamma','openInterest','volume','impliedVolatility']].copy()
                    put_disp.columns = ['Strike','Premium ₹','Type','Signal','Delta','Theta','Gamma','OI','Vol','IV']
                    put_disp['IV'] = (put_disp['IV'] * 100).round(1)
                    st.dataframe(put_disp, use_container_width=True, hide_index=True)

            if not calls.empty and not puts.empty:
                fig_oi = go.Figure()
                fig_oi.add_trace(go.Bar(x=calls['strike'], y=calls['openInterest'], name='CE OI', marker_color='#00e676', opacity=0.7))
                fig_oi.add_trace(go.Bar(x=puts['strike'], y=puts['openInterest'], name='PE OI', marker_color='#ff1744', opacity=0.7))
                fig_oi.add_vline(x=price, line_dash="dash", line_color="#00f2ff", annotation_text=f"Spot ₹{price:,.2f}")
                fig_oi.update_layout(template="plotly_dark", height=350, barmode='group', margin=dict(l=0,r=0,b=40,t=30))
                st.plotly_chart(fig_oi, use_container_width=True)
        else:
            st.warning("⚠️ No option data available for this ticker.")
    except Exception as e:
        st.error(f"❌ Option chain error: {e}")
