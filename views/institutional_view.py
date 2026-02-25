import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

INST_RESULTS_FILE = "data/inst_scanner_results.json"

def render_institutional_view():
    st.markdown("## 🏛️ INSTITUTIONAL ELITE SCANNER")
    st.markdown("---")
    
    if not os.path.exists(INST_RESULTS_FILE):
        st.info("⌛ Waiting for background scanner to generate Institutional reports...")
        st.stop()
        
    try:
        with open(INST_RESULTS_FILE, 'r') as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"Error loading scanner data: {e}")
        st.stop()
        
    last_update = data.get('last_update', 'Unknown')
    if last_update != 'Unknown':
        last_update = datetime.fromisoformat(last_update).strftime("%H:%M:%S")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Signals Found", len(data.get('all', [])))
    col2.metric("Elite Picks", len(data.get('top5', [])))
    col3.metric("Last Pulse", last_update)

    st.markdown("### 🧬 PCR SENTIMENT PULSE")
    pcr = data.get('pcr', {})
    if pcr:
        pcol1, pcol2, pcol3 = st.columns(3)
        targets = [("NIFTY", pcol1), ("BANKNIFTY", pcol2), ("OVERALL", pcol3)]
        
        for label, col in targets:
            stats = pcr.get(label if label != "OVERALL" else "overall", {})
            pcr_val = stats.get('pcr', 0)
            ce_oi = stats.get('ce_oi', 0)
            pe_oi = stats.get('pe_oi', 0)
            
            def fmt_oi(val):
                if val >= 10000000: return f"{val/10000000:.2f}Cr"
                if val >= 100000: return f"{val/100000:.2f}L"
                return str(int(val))

            with col:
                p_clr = "#00e676" if pcr_val > 1.2 else "#ff1744" if pcr_val < 0.8 else "#ffd740"
                st.markdown(f"""
                <div style="background:rgba(0,0,0,0.2); border:1px solid {p_clr}88; border-radius:8px; padding:10px; text-align:center;">
                    <div style="color:#aaa; font-size:0.8rem;">{label} PCR</div>
                    <div style="font-size:1.8rem; font-weight:bold; color:{p_clr};">{pcr_val}</div>
                    <div style="font-size:0.7rem; color:#888;">
                        <span style="color:#ff1744;">C: {fmt_oi(ce_oi)}</span> | 
                        <span style="color:#00e676;">P: {fmt_oi(pe_oi)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📊 Waiting for the next 15-minute PCR sync...")

    st.markdown("### 🌐 INDEX WEIGHTAGE BIAS")
    index_bias = data.get('index_bias', [])
    if index_bias:
        bcols = st.columns(len(index_bias))
        for i, bias in enumerate(index_bias):
            with bcols[i]:
                clr = "#00e676" if bias['type'] == "CE" else "#ff1744"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.08); border:2px solid {clr}; border-radius:10px; padding:15px; text-align:center;">
                    <div style="font-size:1.1rem; font-weight:bold;">{bias['index']}</div>
                    <div style="font-size:1.8rem; font-weight:900; color:{clr};">{bias['type']} BIAS</div>
                    <div style="font-size:0.9rem; margin-top:5px;">Power: {bias['bias_pct']:.1f}%</div>
                    <div style="font-size:0.7rem; color:#aaa; margin-top:10px; text-align:left;">
                        <b>Heavyweights:</b><br>
                        {"<br>".join(bias['components'][:4])}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No clear index bias detected from heavyweights.")

    st.markdown("---")
    st.markdown("### 🏆 ELITE TOP 5 (Institutional Strategy)")
    top5 = data.get('top5', [])
    
    if top5:
        cols = st.columns(len(top5))
        for i, entry in enumerate(top5):
            with cols[i]:
                clr = "#00e676" if entry['type'] == "CE" else "#ff1744"
                
                # Dynamic Tag Logic for UI
                tag = "ELITE"
                score = entry.get('score', 0)
                mtf = entry.get('mtf', '')
                if score > 82 and "Strong" in mtf: tag = "💎 DIAMOND"
                elif score > 85: tag = "🏆 TOP PICK"
                
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid {clr}55; border-radius:10px; padding:15px; text-align:center; border-top: 4px solid {clr};">
                    <div style="font-size:0.7rem; color:{clr}; font-weight:bold; margin-bottom:5px;">{tag}</div>
                    <div style="font-size:0.8rem; color:#aaa;">{entry['symbol']}</div>
                    <div style="font-size:1.2rem; font-weight:bold; color:{clr};">{entry['strike']} {entry['type']}</div>
                    <div style="font-size:1.5rem; font-weight:900; margin:10px 0;">₹{entry['premium']}</div>
                    <div style="font-size:0.6rem; color:#888; margin-bottom:10px;">Expiry: {entry.get('expiry', 'N/A')}</div>
                    <div style="background:{clr}22; color:{clr}; border-radius:15px; font-size:0.7rem; padding:2px 8px; display:inline-block; margin-bottom:10px;">
                        Score: {entry['score']}
                    </div>
                    <div style="font-size:0.75rem; color:#aaa; text-align:left;">
                        • RSI: {entry['rsi']}<br>
                        • Vol: {entry['vol']}x<br>
                        • Decay: {entry['decay']}%<br>
                        • MTF: {entry['mtf']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Execution buttons
                if st.button(f"Quick Buy {entry['symbol']}", key=f"buy_inst_{i}"):
                    st.success(f"🚀 Buying {entry['symbol']} {entry['strike']} {entry['type']} @ ₹{entry['premium']}")
    else:
        st.warning("No Elite signals found with low decay risk. Market might be in consolidation.")

    st.markdown("---")
    st.markdown("### 📡 ALL INSTITUTIONAL SIGNALS")
    
    all_signals = data.get('all', [])
    if all_signals:
        df = pd.DataFrame(all_signals)
        # Custom Display for Table
        df_ui = df.copy()
        
        # Extract MTF Signals into readable strings
        def format_mtf(sig_dict):
            if not isinstance(sig_dict, dict): return "WAIT"
            parts = []
            if sig_dict.get('Scalping') != "WAIT": parts.append(f"S: {sig_dict['Scalping']}")
            if sig_dict.get('Intraday') != "WAIT": parts.append(f"I: {sig_dict['Intraday']}")
            if sig_dict.get('Swing') != "WAIT": parts.append(f"W: {sig_dict['Swing']}")
            return " | ".join(parts) if parts else "WAIT"

        df_ui['MTF Synergy'] = df_ui['mtf_signals'].apply(format_mtf)
        
        # Reorder columns
        cols = ["symbol", "type", "strike", "premium", "MTF Synergy", "score", "mtf", "rsi", "vol", "time"]
        available_cols = [c for c in cols if c in df_ui.columns]
        df_ui = df_ui[available_cols]
        
        # Styling
        def style_rows(row):
            color = 'background-color: rgba(0, 230, 118, 0.1)' if row['type'] == 'CE' else 'background-color: rgba(255, 23, 68, 0.1)'
            return [color] * len(row)
        
        st.dataframe(df_ui.style.apply(style_rows, axis=1), use_container_width=True)
    else:
        st.info("No active signals in the current scan cycle.")

    # Strategy Guide
    with st.expander("📚 Institutional Scalper Guide", expanded=False):
        st.markdown("""
        #### 🏛️ Strategy Protocol
        1. **Entry Logic**: RSI > 60 (CE) or < 40 (PE) + EMA(5) crossing EMA(20) + 1.5x Volume Spike.
        2. **Elite Filtering**: Scores are calculated based on RSI deviation from 50 and Volume Ratio.
        3. **Decay Risk (D-RISK)**: We automatically filter out contracts where Time Value is > 75% of the premium (Safe Zone).
        4. **MTF Confluence**: High probability signals align with 15m and Hourly trends.
        5. **Manual Execution**: Use the Quick Buy button for immediate 1-click execution.
        """)
