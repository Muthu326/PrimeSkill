import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def render_home(data):
    """
    Renders the HOME workspace
    """
    curr = data.get('curr')
    rsi_val = data.get('rsi_val', 50.0)
    adx_val = data.get('adx_val', 20.0)
    mom_speed = data.get('mom_speed', 50.0)
    market_power = data.get('market_power', "💤 WEAK")
    vol_pressure = data.get('vol_pressure', "⚪ NEUTRAL")
    pro_signal = data.get('pro_signal', "WAIT")
    price = data.get('price', 0.0)
    tgt = data.get('tgt', 0.0)
    sl = data.get('sl', 0.0)
    forecast = data.get('forecast', "N/A")
    smc = data.get('smc', "Neutral")
    ha_stat = data.get('ha_stat', "Neutral")
    pressure_stat = data.get('pressure_stat', "Neutral")
    sig_validity = data.get('sig_validity', "Neutral")
    support_lvl = data.get('support_lvl', 0.0)
    resistance_lvl = data.get('resistance_lvl', 0.0)
    pattern_now = data.get('pattern_now', "None")
    stock_rows = data.get('stock_rows', [])
    
    # 🎯 SUPER INDEX PICKS
    index_picks = st.session_state.get('index_picks', [])
    if index_picks:
        st.markdown("### 🎯 SUPER INDEX PICKS (Nifty, BankNifty, Sensex)")
        idx_cols = st.columns(len(index_picks))
        for i, pick in enumerate(index_picks):
            with idx_cols[i]:
                name = pick['Stock'].replace("^NSEI", "NIFTY 50").replace("^NSEBANK", "BANK NIFTY").replace("^BSESN", "SENSEX").replace("NIFTY_FIN_SERVICE", "FIN NIFTY").replace("NIFTY_MID_SELECT", "MIDCAP NIFTY")
                is_bull = "CE" in pick['Signal']
                is_bear = "PE" in pick['Signal']
                clr = "#00e676" if is_bull else "#ff1744" if is_bear else "#ffd740"
                bg_clr = "rgba(0,230,118,0.1)" if is_bull else "rgba(255,23,68,0.1)" if is_bear else "rgba(255,215,64,0.05)"
                
                # Strike suggestion
                spot = pick['Price']
                step = 50 if "BANK" in name or "SENSEX" in name else 50 if "NIFTY" in name else 10
                strike = round(spot / step) * step
                type_msg = pick['Signal'] if "WAIT" not in pick['Signal'] else "WAITING..."
                
                # 🔍 MTF & Value Analysis
                mtf_s = pick.get('MTF_Status', 'Neutral')
                mtf_icon = "🟢" if "Bullish" in mtf_s else "🔴" if "Bearish" in mtf_s else "🟡"
                
                from services.market_engine import calculate_option_greeks
                iv_v, tv_v, money_s = calculate_option_greeks(spot, strike, spot*0.02, "CE" if is_bull else "PE")

                st.markdown(f"""
                <div style="background:{bg_clr}; border-left:4px solid {clr}; padding:15px; border-radius:10px; text-align:center; height:240px; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                    <div style="color:#aaa; font-size:0.75rem; font-weight:bold; text-transform:uppercase;">{name}</div>
                    <div style="color:white; font-size:1.4rem; font-weight:900; margin:5px 0; text-shadow:0 0 10px {clr}33;">₹{spot:,.2f}</div>
                    <div style="color:{pick['Chg%'] > 0 and '#00e676' or '#ff1744'}; font-size:0.85rem; font-weight:bold;">{pick['Chg%']:+.2f}%</div>
                    <div style="background:{clr}22; color:{clr}; padding:4px; border-radius:5px; margin-top:10px; font-weight:800; font-size:0.8rem; border:1px solid {clr}44;">{type_msg}</div>
                    <div style="color:#00f2ff; font-size:0.75rem; font-weight:bold; margin-top:8px;">🎯 {strike} {is_bear and 'PE' or 'CE'}</div>
                    <div style="margin-top:8px; border-top:1px solid rgba(255,255,255,0.1); padding-top:8px; font-size:0.65rem; color:#888; text-align:left;">
                        <div>🔍 MTF: <span style="color:white;">{mtf_s} {mtf_icon}</span></div>
                        <div>💎 Value: <span style="color:white;">{money_s}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 💎 DIAMOND PICKS (Super Stocks)
        diamond_picks = st.session_state.get('diamond_picks', [])
        if diamond_picks:
            st.markdown("### 💎 DIAMOND JACKPOT PICKS (Super Stocks)")
            d_cols = st.columns(len(diamond_picks))
            for i, d_pick in enumerate(diamond_picks):
                with d_cols[i]:
                    d_clr = "#00e676" if d_pick['Type'] == "CE" else "#ff1744"
                    d_mtf = d_pick.get('MTF_Status', 'Neutral')
                    d_mtf_icon = "🟢" if "Bullish" in d_mtf else "🔴" if "Bearish" in d_mtf else "🟡"
                    
                    st.markdown(f"""
                    <div style="background:rgba(0,242,255,0.05); border:1px solid {d_clr}; padding:15px; border-radius:10px; text-align:center; position:relative; overflow:hidden;">
                        <div style="position:absolute; top:-10px; right:-10px; background:{d_clr}; color:black; padding:15px; transform:rotate(45deg); font-size:0.6rem; font-weight:bold;">SUPER</div>
                        <div style="color:{d_clr}; font-weight:900; font-size:1.2rem; margin-bottom:5px;">{d_pick['Stock']}</div>
                        <div style="color:white; font-size:1rem; font-weight:bold;">₹{d_pick['Price']:.2f}</div>
                        <div style="color:#00f2ff; font-size:0.8rem; margin:5px 0;">{d_pick['Signal']}</div>
                        <div style="background:{d_clr}33; color:{d_clr}; padding:2px 10px; border-radius:20px; font-size:0.7rem; font-weight:bold; display:inline-block; border:1px solid {d_clr}66;">Conf: {d_pick['Conf']:.0f}%</div>
                        <div style="margin-top:10px; font-size:0.65rem; color:#888;">🔍 MTF: <span style="color:white;">{d_mtf} {d_mtf_icon}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("---")

    h1, h2 = st.columns([2, 1])
    with h1:
        r1, r2, r3, r4 = st.columns(4)
        mc = "#00e676" if mom_speed > 55 else "#ff1744" if mom_speed < 45 else "#ffd740"
        r1.markdown(f'<div class="metric-card"><div class="sub-metric">Momentum Speed</div><div class="main-metric" style="color:{mc}">{mom_speed:.1f}</div></div>', unsafe_allow_html=True)
        r2.markdown(f'<div class="metric-card"><div class="sub-metric">Market Power</div><div class="main-metric" style="color:#00f2ff">{market_power}</div></div>', unsafe_allow_html=True)
        bp_cls = "bullish" if "BUY" in vol_pressure else "bearish"
        r3.markdown(f'<div class="metric-card"><div class="sub-metric">Volume Pressure</div><div class="main-metric {bp_cls}">{vol_pressure}</div></div>', unsafe_allow_html=True)
        ps_cls = "bullish" if "CALL" in pro_signal else "bearish" if "PUT" in pro_signal else ""
        r4.markdown(f'<div class="metric-card"><div class="sub-metric">Pro Signal</div><div class="main-metric {ps_cls}">{pro_signal}</div></div>', unsafe_allow_html=True)
    
    with h2:
        # 💎 DIAMOND JACKPOT METER
        j_score = 0
        if curr is not None:
             v_ratio = data.get('v_ratio', 1.0)
             is_bull_trend = price > float(curr.get('EMA50', price))
             is_bear_trend = price < float(curr.get('EMA50', price))
             is_bull_mom = rsi_val > 60
             is_bear_mom = rsi_val < 40
             is_strong = adx_val > 25
             is_high_vol = v_ratio > 1.5
             
             if is_bull_trend or is_bear_trend: j_score += 25
             if is_bull_mom or is_bear_mom: j_score += 25
             if is_strong: j_score += 25
             if is_high_vol: j_score += 25
             
             true_jackpot = (is_bull_trend and is_bull_mom and is_strong and is_high_vol) or \
                             (is_bear_trend and is_bear_mom and is_strong and is_high_vol)
             if true_jackpot: j_score = 100
        
        fig_j = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = j_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "💎 JACKPOT CONVICTION", 'font': {'size': 14, 'color': '#00f2ff'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#333"},
                'bar': {'color': "#00e676" if j_score >= 80 else "#ffd740" if j_score >= 50 else "#ff1744"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(255,23,68,0.1)'},
                    {'range': [60, 80], 'color': 'rgba(0,242,255,0.1)'},
                    {'range': [80, 100], 'color': 'rgba(0,230,118,0.2)'}],
                'threshold': {
                    'line': {'color': "#00f2ff", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}
            }
        ))
        fig_j.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"})
        
        container_class = "bullish-glow" if j_score >= 80 else ""
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
        st.plotly_chart(fig_j, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    sig_text = "ENTRY DETECTED" if "WAIT" not in pro_signal else "WATCHING MARKETS..."
    st.markdown(f'<div class="prediction-panel"><h2 style="color:#00f2ff;margin:0;font-size:2rem;text-shadow:0 0 10px #00f2ff">{sig_text}</h2><p style="color:#ccc;margin-top:5px;">RSI: {rsi_val:.1f} | ADX: {adx_val:.1f} | Speed: {mom_speed:.1f} | Forecast: {forecast}</p></div>', unsafe_allow_html=True)

    if "WAIT" not in pro_signal and price > 0:
        v_ratio = data.get('v_ratio', 1.0)
        st.markdown("### 🏹 Execution Targets")
        e1, e2, e3 = st.columns(3)
        e1.markdown(f'<div class="metric-card"><div class="sub-metric">Target</div><div class="main-metric bullish">₹{tgt:.2f}</div></div>', unsafe_allow_html=True)
        e2.markdown(f'<div class="metric-card"><div class="sub-metric">Stop Loss</div><div class="main-metric bearish">₹{sl:.2f}</div></div>', unsafe_allow_html=True)
        e3.markdown(f'<div class="metric-card"><div class="sub-metric">Vol Strength</div><div class="main-metric">{v_ratio:.2f}x</div></div>', unsafe_allow_html=True)

    # Full Analysis Table
    st.markdown("### 📋 Complete Market Analysis")
    analysis_data = {
        "Metric": ["Trend", "Heikin Ashi", "SMC/BOS", "Pattern", "VWAP Position", "Signal Validity", "Pressure", "Support", "Resistance", "Forecast"],
        "Value": [str(curr['Trend']) if curr is not None and 'Trend' in curr else "N/A", ha_stat, smc, pattern_now,
                  f"{'Above' if price > float(curr.get('VWAP', price)) else 'Below'} VWAP" if curr is not None and 'VWAP' in curr else "N/A",
                  sig_validity, pressure_stat, f"₹{support_lvl:.2f}", f"₹{resistance_lvl:.2f}", forecast]
    }
    st.dataframe(pd.DataFrame(analysis_data), use_container_width=True, hide_index=True)

    if stock_rows:
        stocks_df = pd.DataFrame(stock_rows)
        with st.expander("🔍 View All Constituent Data", expanded=True):
            st.dataframe(stocks_df, use_container_width=True, hide_index=True)

        call_stocks = stocks_df[stocks_df['Signal'].str.contains('CE', na=False)]
        put_stocks = stocks_df[stocks_df['Signal'].str.contains('PE', na=False)]
        wait_stocks = stocks_df[stocks_df['Signal'].str.contains('WAIT', na=False)]
        breakout_stocks = stocks_df[stocks_df['Signal'].str.contains('⚡', na=False)]
        bull_count = len(stocks_df[stocks_df['Trend'] == 'Bullish'])
        bear_count = len(stocks_df[stocks_df['Trend'] == 'Bearish'])
        rising = len(stocks_df[stocks_df['Chg%'] > 0])
        falling = len(stocks_df[stocks_df['Chg%'] < 0])

        bc1, bc2, bc3, bc4, bc5, bc6 = st.columns(6)
        bc1.markdown(f'<div class="metric-card" style="border-left:4px solid #00e676;"><div class="sub-metric">🟢 Bullish</div><div class="main-metric bullish">{bull_count}</div></div>', unsafe_allow_html=True)
        bc2.markdown(f'<div class="metric-card" style="border-left:4px solid #ff1744;"><div class="sub-metric">🔴 Bearish</div><div class="main-metric bearish">{bear_count}</div></div>', unsafe_allow_html=True)
        bc3.markdown(f'<div class="metric-card" style="border-left:4px solid #00e676;"><div class="sub-metric">📈 Rising</div><div class="main-metric bullish">{rising}</div></div>', unsafe_allow_html=True)
        bc4.markdown(f'<div class="metric-card" style="border-left:4px solid #ff1744;"><div class="sub-metric">📉 Falling</div><div class="main-metric bearish">{falling}</div></div>', unsafe_allow_html=True)
        bc5.markdown(f'<div class="metric-card" style="border-left:4px solid #00e676;"><div class="sub-metric">📗 BUY CE</div><div class="main-metric bullish">{len(call_stocks)}</div></div>', unsafe_allow_html=True)
        bc6.markdown(f'<div class="metric-card" style="border-left:4px solid #ff1744;"><div class="sub-metric">📕 BUY PE</div><div class="main-metric bearish">{len(put_stocks)}</div></div>', unsafe_allow_html=True)

        if not breakout_stocks.empty:
            st.markdown("### ⚡ PRIME MOMENTUM BREAKOUTS")
            m_cols = st.columns(min(len(breakout_stocks), 4))
            for i, (_, m_row) in enumerate(breakout_stocks.head(4).iterrows()):
                with m_cols[i]:
                    is_c = "CALL" in m_row['Signal']
                    card_clr = "#00e676" if is_c else "#ff1744"
                    st.markdown(f"""
                    <div style="background:rgba(0,10,20,0.8); border:1px solid {card_clr}; padding:12px; border-radius:10px; text-align:center;">
                        <div style="color:{card_clr}; font-weight:900; font-size:1.1rem;">⚡ {m_row['Stock']}</div>
                        <div style="color:white; font-size:0.8rem; margin:5px 0;">Price: ₹{m_row['Price']} ({m_row['Chg%']:+.2f}%)</div>
                        <div style="background:{card_clr}33; color:{card_clr}; padding:2px 5px; border-radius:4px; font-size:0.75rem; font-weight:800;">{m_row['Signal']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")

        st.markdown("### 🏆 Top 5 Best F&O Picks")
        best5_call = call_stocks.nlargest(5, 'Momentum') if len(call_stocks) > 0 else pd.DataFrame()
        best5_put = put_stocks.nsmallest(5, 'Momentum') if len(put_stocks) > 0 else pd.DataFrame()

        b5c1, b5c2 = st.columns(2)
        mkt_bias_ratio = len(call_stocks) / max(len(put_stocks), 1)
        is_bullish_bias = mkt_bias_ratio > 1.2
        is_bearish_bias = mkt_bias_ratio < 0.8
        bias_label = "BULLISH" if is_bullish_bias else "BEARISH" if is_bearish_bias else "NEUTRAL"

        from services.market_engine import option_premium_estimate, get_days_to_expiry

        with b5c1:
            st.markdown("#### 📗 Top 5 BUY CALL")
            if not best5_call.empty:
                for idx_b, brow in best5_call.iterrows():
                    spot = brow['Price']
                    strike_step = 50 if spot > 500 else 10 if spot > 100 else 5
                    atm_strike = round(spot / strike_step) * strike_step
                    iv_est = max(15, min(50, 30 + (brow['RSI'] - 50) * 0.3))
                    dte = get_days_to_expiry()
                    
                    adx_v = brow['ADX']
                    mom_v = brow.get('Momentum', 50)
                    rsi_v = brow['RSI']
                    
                    ce_premium = option_premium_estimate(spot, atm_strike, iv_est, dte, "CE")
                    ce_target = round(ce_premium * 1.30, 2)
                    ce_sl = round(ce_premium * 0.90, 2)
                    
                    trend_reversal = False
                    if rsi_v > 65 and mom_v < 50: trend_reversal = True
                    if rsi_v > 70 and adx_v < 20: trend_reversal = True
                    
                    if trend_reversal: ce_status = "🔄 TREND REVERSAL"; ce_st_clr = "#ff9800"
                    elif adx_v > 25 and rsi_v > 55 and mom_v > 55 and is_bullish_bias: ce_status = "🟢 STRONG BUY"; ce_st_clr = "#00e676"
                    elif adx_v > 25 and rsi_v > 55 and mom_v > 55: ce_status = "🟢 BUY"; ce_st_clr = "#00e676"
                    elif adx_v > 18 and rsi_v > 50: ce_status = "🟡 HOLD"; ce_st_clr = "#ffd740"
                    elif rsi_v > 70: ce_status = "🔴 EXIT (Overbought)"; ce_st_clr = "#ff1744"
                    elif is_bearish_bias and rsi_v < 55: ce_status = "🔴 EXIT (Bias Bearish)"; ce_st_clr = "#ff1744"
                    else: ce_status = "⏳ WAIT"; ce_st_clr = "#888"
                    
                    rr_ratio = round((ce_target - ce_premium) / max(ce_premium - ce_sl, 0.01), 1)
                    buyer_score = (rsi_v * 0.4) + (mom_v * 0.3) + (min(adx_v, 50) * 0.6)
                    buyer_pct = round(min(95, max(5, buyer_score)))
                    seller_pct = 100 - buyer_pct
                    
                    prem_score = 0
                    if adx_v > 25: prem_score += 2
                    if rsi_v > 55 and mom_v > 55: prem_score += 2
                    if is_bullish_bias: prem_score += 1
                    if iv_est > 25: prem_score += 1
                    if brow['Chg%'] > 0.5: prem_score += 1
                    if trend_reversal: prem_score -= 3
                    prem_chg_est = round(prem_score * 5, 0)
                    
                    if prem_chg_est > 10: prem_pred = f"📈 Premium ↑ (+{prem_chg_est:.0f}%)"; prem_clr = "#00e676"
                    elif prem_chg_est > 0: prem_pred = f"📊 Stable (+{prem_chg_est:.0f}%)"; prem_clr = "#ffd740"
                    else: prem_pred = f"📉 Premium ↓ ({prem_chg_est:.0f}%)"; prem_clr = "#ff1744"
                    
                    st.markdown(f"""
                    <div style="background:rgba(0,230,118,0.08);border:1px solid #00e676;border-radius:8px;padding:10px;margin:5px 0;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#00e676;font-weight:900;font-size:1.1rem;">{brow['Stock']}</span>
                            <span style="background:{ce_st_clr}22;color:{ce_st_clr};padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:800;">{ce_status}</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;margin-top:4px;">
                            <span style="color:white;font-weight:bold;">₹{spot:,.2f} <span style="color:#00e676;font-size:0.8rem;">({brow['Chg%']:+.2f}%)</span></span>
                            <span style="color:#555;font-size:0.7rem;">ATM {atm_strike} CE | IV:{iv_est:.0f}% | RR:{rr_ratio}:1</span>
                        </div>
                        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px;font-size:0.78rem;">
                            <div><span style="color:#888;">Entry:</span><br><span style="color:#00f2ff;font-weight:bold;font-size:0.9rem;">₹{ce_premium}</span></div>
                            <div><span style="color:#888;">Target:</span><br><span style="color:#00e676;font-weight:bold;font-size:0.9rem;">₹{ce_target}</span></div>
                            <div><span style="color:#888;">SL:</span><br><span style="color:#ff1744;font-weight:bold;font-size:0.9rem;">₹{ce_sl}</span></div>
                            <div><span style="color:#888;">ADX|RSI:</span><br><span style="color:#ffd740;font-weight:bold;">{adx_v:.0f} | {rsi_v:.0f}</span></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
                            <div style="flex:1;margin-right:8px;">
                                <div style="display:flex;justify-content:space-between;font-size:0.65rem;">
                                    <span style="color:#00e676;">Buyers {buyer_pct}%</span>
                                    <span style="color:#ff1744;">Sellers {seller_pct}%</span>
                                </div>
                                <div style="background:#333;border-radius:3px;height:4px;margin-top:2px;overflow:hidden;">
                                    <div style="background:#00e676;width:{buyer_pct}%;height:100%;"></div>
                                </div>
                            </div>
                            <span style="color:{prem_clr};font-size:0.65rem;font-weight:bold;white-space:nowrap;">{prem_pred}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No BUY CALL signals right now")

        with b5c2:
            st.markdown("#### 📕 Top 5 BUY PUT")
            if not best5_put.empty:
                for idx_b, brow in best5_put.iterrows():
                    spot = brow['Price']
                    strike_step = 50 if spot > 500 else 10 if spot > 100 else 5
                    atm_strike = round(spot / strike_step) * strike_step
                    iv_est = max(15, min(50, 30 + (50 - brow['RSI']) * 0.3))
                    dte = get_days_to_expiry()
                    
                    adx_v = brow['ADX']
                    mom_v = brow.get('Momentum', 50)
                    rsi_v = brow['RSI']
                    
                    pe_premium = option_premium_estimate(spot, atm_strike, iv_est, dte, "PE")
                    pe_target = round(pe_premium * 1.30, 2)
                    pe_sl = round(pe_premium * 0.90, 2)
                    
                    trend_reversal = False
                    if rsi_v < 35 and mom_v > 50: trend_reversal = True
                    if rsi_v < 30 and adx_v < 20: trend_reversal = True
                    
                    if trend_reversal: pe_status = "🔄 TREND REVERSAL"; pe_st_clr = "#ff9800"
                    elif adx_v > 25 and rsi_v < 45 and mom_v < 45 and is_bearish_bias: pe_status = "🟢 STRONG BUY"; pe_st_clr = "#00e676"
                    elif adx_v > 25 and rsi_v < 45 and mom_v < 45: pe_status = "🟢 BUY"; pe_st_clr = "#00e676"
                    elif adx_v > 18 and rsi_v < 50: pe_status = "🟡 HOLD"; pe_st_clr = "#ffd740"
                    elif rsi_v < 30: pe_status = "🔴 EXIT (Oversold)"; pe_st_clr = "#ff1744"
                    elif is_bullish_bias and rsi_v > 45: pe_status = "🔴 EXIT (Bias Bullish)"; pe_st_clr = "#ff1744"
                    else: pe_status = "⏳ WAIT"; pe_st_clr = "#888"
                    
                    rr_ratio = round((pe_target - pe_premium) / max(pe_premium - pe_sl, 0.01), 1)
                    seller_score = ((100 - rsi_v) * 0.4) + ((100 - mom_v) * 0.3) + (min(adx_v, 50) * 0.6)
                    seller_pct_pe = round(min(95, max(5, seller_score)))
                    buyer_pct_pe = 100 - seller_pct_pe
                    
                    prem_score = 0
                    if adx_v > 25: prem_score += 2
                    if rsi_v < 45 and mom_v < 45: prem_score += 2
                    if is_bearish_bias: prem_score += 1
                    if iv_est > 25: prem_score += 1
                    if brow['Chg%'] < -0.5: prem_score += 1
                    if trend_reversal: prem_score -= 3
                    prem_chg_est = round(prem_score * 5, 0)
                    
                    if prem_chg_est > 10: prem_pred = f"📈 Premium ↑ (+{prem_chg_est:.0f}%)"; prem_clr = "#00e676"
                    elif prem_chg_est > 0: prem_pred = f"📊 Stable (+{prem_chg_est:.0f}%)"; prem_clr = "#ffd740"
                    else: prem_pred = f"📉 Premium ↓ ({prem_chg_est:.0f}%)"; prem_clr = "#ff1744"
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,23,68,0.08);border:1px solid #ff1744;border-radius:8px;padding:10px;margin:5px 0;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#ff1744;font-weight:900;font-size:1.1rem;">{brow['Stock']}</span>
                            <span style="background:{pe_st_clr}22;color:{pe_st_clr};padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:800;">{pe_status}</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;margin-top:4px;">
                            <span style="color:white;font-weight:bold;">₹{spot:,.2f} <span style="color:#ff1744;font-size:0.8rem;">({brow['Chg%']:+.2f}%)</span></span>
                            <span style="color:#555;font-size:0.7rem;">ATM {atm_strike} PE | IV:{iv_est:.0f}% | RR:{rr_ratio}:1</span>
                        </div>
                        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px;font-size:0.78rem;">
                            <div><span style="color:#888;">Entry:</span><br><span style="color:#00f2ff;font-weight:bold;font-size:0.9rem;">₹{pe_premium}</span></div>
                            <div><span style="color:#888;">Target:</span><br><span style="color:#00e676;font-weight:bold;font-size:0.9rem;">₹{pe_target}</span></div>
                            <div><span style="color:#888;">SL:</span><br><span style="color:#ff1744;font-weight:bold;font-size:0.9rem;">₹{pe_sl}</span></div>
                            <div><span style="color:#888;">ADX|RSI:</span><br><span style="color:#ffd740;font-weight:bold;">{adx_v:.0f} | {rsi_v:.0f}</span></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
                            <div style="flex:1;margin-right:8px;">
                                <div style="display:flex;justify-content:space-between;font-size:0.65rem;">
                                    <span style="color:#00e676;">Buyers {buyer_pct_pe}%</span>
                                    <span style="color:#ff1744;">Sellers {seller_pct_pe}%</span>
                                </div>
                                <div style="background:#333;border-radius:3px;height:4px;margin-top:2px;overflow:hidden;">
                                    <div style="background:linear-gradient(90deg,#00e676,#ff1744);width:{seller_pct_pe}%;height:100%;"></div>
                                </div>
                            </div>
                            <span style="color:{prem_clr};font-size:0.65rem;font-weight:bold;white-space:nowrap;">{prem_pred}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No BUY PUT signals right now")

        st.markdown("### 📋 Full Stock List")
        fc1, fc2, fc3 = st.columns([2, 2, 2])
        with fc1: filter_mode = st.selectbox("🔍 Filter", ["📊 ALL STOCKS", "📗 BUY CALL Only", "📕 BUY PUT Only", "⏳ WAIT Only", "🏆 Best 5 CALL", "🏆 Best 5 PUT"], key="home_filter")
        with fc2: sort_col = st.selectbox("📈 Sort By", ["Chg%", "Price", "RSI", "ADX", "Momentum", "Stock"], key="home_sort_col")
        with fc3: sort_dir = st.selectbox("Order", ["⬇️ Descending (High→Low)", "⬆️ Ascending (Low→High)"], key="home_sort_dir")

        if "CALL Only" in filter_mode: display_df = call_stocks.copy()
        elif "PUT Only" in filter_mode: display_df = put_stocks.copy()
        elif "WAIT" in filter_mode: display_df = wait_stocks.copy()
        elif "Best 5 CALL" in filter_mode: display_df = best5_call.copy()
        elif "Best 5 PUT" in filter_mode: display_df = best5_put.copy()
        else: display_df = stocks_df.copy()

        asc = "Ascending" in sort_dir
        if sort_col in display_df.columns: display_df = display_df.sort_values(sort_col, ascending=asc)

        if not display_df.empty:
            table_html = '<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:0.82rem;">'
            headers = ["#","Stock","Price","Chg","Chg%","Trend","Signal","Scalp","Intraday","RSI","ADX","Mom","HA","Vol Pressure"]
            table_html += '<tr>'
            for h in headers: table_html += f'<th style="background:#111827;color:#aaa;padding:8px 6px;text-align:center;border-bottom:2px solid #333;font-size:0.7rem;position:sticky;top:0;">{h}</th>'
            table_html += '</tr>'
            for rank, (_, row) in enumerate(display_df.iterrows(), 1):
                is_bull = row['Trend'] == 'Bullish'; is_bear = row['Trend'] == 'Bearish'; is_rising = row['Chg%'] > 0
                row_bg = "rgba(0,230,118,0.08)" if is_bull else "rgba(255,23,68,0.08)" if is_bear else "rgba(255,255,255,0.02)"
                chg_clr = "#00e676" if is_rising else "#ff1744"
                trend_clr = "#00e676" if is_bull else "#ff1744" if is_bear else "#ffd740"
                sig_clr = "#00e676" if "CALL" in str(row['Signal']) else "#ff1744" if "PUT" in str(row['Signal']) else "#888"
                sig_bg = "rgba(0,230,118,0.2)" if "CALL" in str(row['Signal']) else "rgba(255,23,68,0.2)" if "PUT" in str(row['Signal']) else "transparent"
                rsi_clr = "#00e676" if row['RSI'] > 55 else "#ff1744" if row['RSI'] < 45 else "#ffd740"
                mom_clr = "#00e676" if row['Momentum'] > 55 else "#ff1744" if row['Momentum'] < 45 else "#ffd740"
                table_html += f'''<tr style="background:{row_bg};border-bottom:1px solid #1a1a2e;">
                    <td style="padding:7px 4px;color:#555;text-align:center;font-size:0.7rem;">{rank}</td>
                    <td style="padding:7px 6px;color:white;font-weight:bold;">{row['Stock']}</td>
                    <td style="padding:7px 6px;color:white;text-align:center;">₹{row['Price']:,.2f}</td>
                    <td style="padding:7px 6px;color:{chg_clr};text-align:center;font-weight:bold;">{row['Chg']:+.2f}</td>
                    <td style="padding:7px 6px;color:{chg_clr};text-align:center;font-weight:bold;">{row['Chg%']:+.2f}%</td>
                    <td style="padding:7px 6px;color:{trend_clr};text-align:center;font-weight:bold;">{"🟢" if is_bull else "🔴" if is_bear else "🟡"} {row['Trend']}</td>
                    <td style="padding:7px 6px;text-align:center;"><span style="background:{sig_bg};color:{sig_clr};padding:3px 8px;border-radius:4px;font-weight:800;font-size:0.75rem;">{row['Signal']}</span></td>
                    <td style="padding:7px 6px;color:{sig_clr};text-align:center;font-size:0.75rem;">{row['Scalp']}</td>
                    <td style="padding:7px 6px;color:{sig_clr};text-align:center;font-size:0.75rem;">{row['Intraday']}</td>
                    <td style="padding:7px 6px;color:{rsi_clr};text-align:center;font-weight:bold;">{row['RSI']}</td>
                    <td style="padding:7px 6px;color:white;text-align:center;">{row['ADX']}</td>
                    <td style="padding:7px 6px;color:{mom_clr};text-align:center;font-weight:bold;">{row['Momentum']}</td>
                    <td style="padding:7px 6px;color:{"#00e676" if "Bull" in str(row.get("HA", "")) else "#ff1744"};text-align:center;font-size:0.75rem;">{row.get('HA', 'N/A')}</td>
                    <td style="padding:7px 6px;text-align:center;font-size:0.75rem;">{row['Vol Pressure']}</td>
                </tr>'''
            table_html += '</table></div>'
            st.markdown(table_html, unsafe_allow_html=True)
