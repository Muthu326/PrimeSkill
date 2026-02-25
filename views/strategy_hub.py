import streamlit as st
import pandas as pd
import yfinance as yf

def render_strategy_hub(data):
    """
    Renders the STRATEGY HUB workspace
    """
    st.markdown("<h3 style='text-align:center;color:#00f2ff;margin:0;'>🧠 PRIME SKILL OPTION BUYER HUB</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;font-size:0.9rem;'><b>CEO: MuthuKumar Krishnan</b> | Professional Option Buying Strategy</p>", unsafe_allow_html=True)
    
    pro_signal = data.get('pro_signal', "WAIT")
    trend_label = data.get('trend_label', "NEUTRAL")
    rsi_val = data.get('rsi_val', 50.0)
    v_ratio = data.get('v_ratio', 1.0)
    pressure_stat = data.get('pressure_stat', "NEUTRAL")
    price = data.get('price', 0.0)
    target = data.get('target', "NIFTY")

    hub_ready_score = 0
    reasons = []
    
    if ("CALL" in pro_signal and trend_label == "Bullish") or ("PUT" in pro_signal and trend_label == "Bearish"):
        hub_ready_score += 40; reasons.append("✅ TREND")
    if v_ratio > 1.2:
        hub_ready_score += 30; reasons.append("✅ VOLUME")
    if (rsi_val > 55 and "CALL" in pro_signal) or (rsi_val < 45 and "PUT" in pro_signal):
        hub_ready_score += 30; reasons.append("✅ MOMENTUM")
    
    hub_ready_label = "🟢 READY" if hub_ready_score >= 70 else "🟡 BUILDING" if hub_ready_score >= 40 else "🔴 NO SETUP"

    st.markdown("---")
    s1, s2 = st.columns([2, 1])
    with s1:
        st.markdown("#### 📋 Option Buying Checklist")
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("1. Price Action: Breakout/Reversal confirmed?", value=True)
            st.checkbox("2. Premium Behavior: IV is favorable?", value=True)
            st.checkbox("3. Trend: EMA alignment?", value=True)
        with c2:
            st.checkbox("4. Momentum: RSI direction matches?", value=True)
            st.checkbox("5. Participation: Volume > Average?", value=True)
            st.checkbox("6. Option Greeks: Delta > 0.45?", value=True)

    with s2:
        st.markdown("#### 🛑 Risk & Exit Rules")
        st.error("**Risk Management**")
        st.markdown("""
        - **Target:** Min 1:2 RR Ratio.
        - **Time Exit:** No move in 45 mins → EXIT.
        - **Stop Loss:** Strict 10-15% on premium.
        """)

    st.markdown("---")
    st.markdown("#### 🔍 5-Layer Deep Dive Analysis")
    try:
        tk_s = yf.Ticker(target)
        expiries_s = tk_s.options
        if expiries_s:
            exp_s = expiries_s[0]
            chain_s = tk_s.option_chain(exp_s)
            step_s = 50 if "NIFTY" in target.upper() else 100
            atm_s = round(price / step_s) * step_s
            
            ce_entry = float(chain_s.calls.loc[(chain_s.calls['strike']-atm_s).abs().idxmin()]['lastPrice'])
            pe_entry = float(chain_s.puts.loc[(chain_s.puts['strike']-atm_s).abs().idxmin()]['lastPrice'])
            ce_iv = float(chain_s.calls.loc[(chain_s.calls['strike']-atm_s).abs().idxmin()]['impliedVolatility']) * 100
            pe_iv = float(chain_s.puts.loc[(chain_s.puts['strike']-atm_s).abs().idxmin()]['impliedVolatility']) * 100
            avg_iv = (ce_iv + pe_iv) / 2
            
            st.markdown(f"""
            <div style="background:#0a0a1a;border:1px solid #222;border-radius:10px;padding:15px;margin-bottom:10px;">
                <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;text-align:center;">
                    <div><div style="color:#888;font-size:0.65rem;">📗 CALL</div><div style="color:#00e676;font-weight:900;">₹{ce_entry:.2f}</div></div>
                    <div><div style="color:#888;font-size:0.65rem;">📕 PUT</div><div style="color:#ff1744;font-weight:900;">₹{pe_entry:.2f}</div></div>
                    <div><div style="color:#888;font-size:0.65rem;">📊 IV</div><div style="color:#ffd740;font-weight:900;">{avg_iv:.1f}</div></div>
                    <div><div style="color:#888;font-size:0.65rem;">🏛️ INSTITUTIONAL</div><div style="color:#00f2ff;">{pressure_stat}</div></div>
                    <div><div style="color:#888;font-size:0.65rem;">🚀 READINESS</div><div style="color:#00e676;font-weight:900;">{hub_ready_score}%</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Additional strategy layers loading...")

    final_cl = "#00e676" if "CALL" in pro_signal else "#ff1744" if "PUT" in pro_signal else "#ffd740"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1b2a,#1b2838);border:2px solid {final_cl};border-radius:12px;padding:20px;text-align:center;">
        <div style="font-size:2.5rem;font-weight:900;color:{final_cl};">{pro_signal}</div>
        <div style="color:#888;font-size:0.75rem;">Checklist: {' | '.join(reasons) if reasons else 'NO SETUP'}</div>
    </div>
    """, unsafe_allow_html=True)
