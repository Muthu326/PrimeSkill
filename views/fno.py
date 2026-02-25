import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

FNO_RESULTS_FILE = "data/fno_scanner_results.json"

def render_fno(data):
    """
    Renders the F&O Alpha Scanner (Implementation of User Workflow)
    """
    st.markdown("### 📊 F&O ALPHA SCANNER (180+ STOCKS)")
    st.markdown("---")

    if not os.path.exists(FNO_RESULTS_FILE):
        st.info("⌛ Initializing Deep Scan for 180+ F&O stocks... This takes ~2 mins per cycle.")
        st.stop()

    try:
        with open(FNO_RESULTS_FILE, 'r') as f:
            fno_data = json.load(f)
    except Exception as e:
        st.error(f"Error loading scanner data: {e}")
        st.stop()

    results = fno_data.get('results', [])
    last_update = fno_data.get('last_update', 'Unknown')
    
    if last_update != 'Unknown':
        last_update = datetime.fromisoformat(last_update).strftime("%H:%M:%S")

    # Metrics Summary
    m1, m2, m3 = st.columns(3)
    m1.metric("Active Signals", len([r for r in results if r['Signal'] != 'None']))
    m2.metric("Top Bias", "BULLISH" if len([r for r in results if r['Bias'] == 'Bullish']) > len([r for r in results if r['Bias'] == 'Bearish']) else "BEARISH")
    m3.metric("Last Full Scan", last_update)

    if results:
        df = pd.DataFrame(results)
        
        # Format OI for display
        def fmt_oi(val):
            if val >= 10000000: return f"{val/10000000:.2f} Cr"
            if val >= 100000: return f"{val/100000:.2f} L"
            return str(int(val))

        # Add styled columns
        df['CE OI'] = df['CE_OI'].apply(fmt_oi)
        df['PE OI'] = df['PE_OI'].apply(fmt_oi)
        
        # Reorder and filter columns
        display_cols = ["Stock", "PCR", "Bias", "CE OI", "PE OI", "Signal", "RSI", "Vol", "LTP"]
        df_display = df[display_cols]

        # Apply coloring
        def highlight_signal(row):
            if row.Signal == "Long CE":
                return ['background-color: rgba(0, 230, 118, 0.2)'] * len(row)
            elif row.Signal == "Short PE":
                return ['background-color: rgba(255, 23, 68, 0.2)'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_display.style.apply(highlight_signal, axis=1),
            use_container_width=True,
            height=600
        )
        
        # Download Option
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Today's Alpha Report",
            csv,
            "fno_alpha_report.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.warning("All stocks currently Neutral. No Technical + OI Confluence detected.")

    # Educational Footer
    with st.expander("📝 Scanner Intelligence Logic"):
        st.markdown("""
        **Alpha Workflow Applied:**
        1. **OI Pulse**: Separate cumulative OI calculated for CE and PE legs.
        2. **Technical Confluence**: Signals only trigger when RSI + EMA Trend align with OI Bias.
        3. **Entry Filter**: 
           - **Long CE**: Bullish Bias + RSI < 70 + Buying Volume Spike.
           - **Short PE**: Bearish Bias + RSI > 30 + Selling Volume Spike.
        """)
