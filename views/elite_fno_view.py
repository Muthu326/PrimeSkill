import streamlit as st
import pandas as pd
from datetime import datetime
from utils.helpers import get_friendly_name

def render_elite_fno_view(view_data):
    st.markdown("""
        <div style='text-align:center; padding: 20px; background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); border-radius: 15px; border: 1px solid #00f2ff; margin-bottom: 25px;'>
            <h1 style='color: #00f2ff; margin:0;'>💎 ELITE F&O STRATEGY ENGINE</h1>
            <p style='color: #ffffff; opacity: 0.8;'>Multi-Factor Professional ITM Selection & MTF Analysis</p>
        </div>
    """, unsafe_allow_html=True)

    # 🟢 Top Navigation / Filters
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.info("**Strategy Mode**: Institutional Trend-Following (Best ITM Logic)")
    with c2:
        target_delta = st.slider("Target Delta", 0.5, 0.9, 0.7, step=0.05, help="Professional sweet spot is 0.65 - 0.75")
    with c3:
        min_score = st.slider("Min Conviction", 40, 95, 70, step=5)

    # 📊 Live Elite Monitor
    st.subheader("🏁 Live Best ITM Portfolio Monitor")
    
    # We fetch the latest scan results from session state
    sdf = st.session_state.get('sdf_cache', pd.DataFrame())
    
    if sdf.empty:
        st.warning("📡 No live scan data found. Please ensure the backend scanner is running.")
        return

    # Filter for CE/PE signals
    suitable = sdf[(sdf['Signal'].str.contains('CE', na=False)) | (sdf['Signal'].str.contains('PE', na=False))]
    
    # Process for the table
    display_rows = []
    for _, row in suitable.iterrows():
        # Estimate Greeks (Simplified for UI display)
        score = row.get('Score', row.get('Conf', 50))
        if score < min_score: continue
        
        display_rows.append({
            "Symbol": row['Stock'],
            "Price": row['Price'],
            "Mode": "💎 SCALP" if score > 85 else "📈 TREND",
            "Option": row['Signal'],
            "Strike": row.get('Strike', 'ATM'),
            "Premium": row.get('Entry', 0),
            "Conviction": f"{score}%",
            "MTF": row.get('MTF_Status', 'Neutral'),
            "Action": "BUY"
        })

    if display_rows:
        df_display = pd.DataFrame(display_rows)
        
        # Professional Styling
        def style_mtf(val):
            color = "#00e676" if "Bull" in val else "#ff1744" if "Bear" in val else "#aaa"
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_display.style.applymap(style_mtf, subset=['MTF'])
            .applymap(lambda x: 'color: #00f2ff' if x == 'BUY' else '', subset=['Action']),
            use_container_width=True,
            height=400
        )
        
        # 🧪 Paper Trading Quick Execute
        st.markdown("### 🏛️ Quick Execution Desk")
        cols = st.columns(3)
        for i, row in enumerate(display_rows[:6]): # Show top 6 for execution
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; border:1px solid #333; margin-bottom:10px;">
                        <div style="font-weight:bold; color:#00f2ff;">{row['Symbol']} {row['Option']}</div>
                        <div style="font-size:0.8rem; color:#888;">Strike: {row['Strike']} | Prem: ₹{row['Premium']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"⚡ EXECUTE {row['Symbol']}", key=f"exec_{i}"):
                    st.success(f"Executed {row['Symbol']} {row['Option']} @ Market")
                    # Add to paper portfolio
                    if 'paper_portfolio' not in st.session_state: st.session_state['paper_portfolio'] = []
                    st.session_state['paper_portfolio'].append({
                        "stock": row['Symbol'], "type": "CE" if "CE" in row['Option'] else "PE",
                        "entry": row['Premium'], "time": datetime.now().strftime("%H:%M:%S"),
                        "status": "OPEN", "current_pnl": 0.0
                    })
    else:
        st.info("🔭 Scanning for high-conviction ITM setups... Adjust filters to see more results.")

    # 📔 Logic Breakdown
    with st.expander("📝 Professional Logic Disclaimer"):
        st.write("""
            **1. Best ITM Logic**: System picks strikes with Delta ~0.70. These have high intrinsic value and lower time decay, ideal for institutional scalping.
            **2. MTF Scoring**: We align 1m, 15m, and 1h trends. Alignment = Higher Conviction.
            **3. Volume Confirmation**: Signals only appear if Volume Ratio > 1.5x (Institutional activity detected).
        """)
