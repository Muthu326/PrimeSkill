import streamlit as st
import pandas as pd

def render_trade_management(data):
    """
    Renders the TRADE MANAGEMENT workspace
    """
    st.markdown("### 📋 Trade Management & Performance")
    
    trades = data.get('trades', [])
    history = data.get('history', [])
    
    tab1, tab2 = st.tabs(["📊 Active Trades", "📜 History"])
    
    with tab1:
        if trades:
            for i, t in enumerate(trades):
                if t.get('status') == 'ACTIVE':
                    pnl = t.get('pnl', 0)
                    clr = "#00e676" if pnl >= 0 else "#ff1744"
                    
                    with st.container():
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        c1.markdown(f"**{t['stock']} {t.get('strike','')}**")
                        c2.markdown(f"Entry: ₹{t['entry_price']:.2f}")
                        c3.markdown(f"P&L: <span style='color:{clr}; font-weight:bold;'>{pnl:+.2f}%</span>", unsafe_allow_html=True)
                        
                        if c4.button("🚪 EXIT", key=f"exit_{i}_{t['stock']}", use_container_width=True):
                            # Call the global order function (assumed imported or available in data)
                            # In this architecture, it's best to use a callback or session state flag
                            st.session_state[f"exit_trigger_{i}"] = True
                            st.rerun()
                            
                    st.divider()
        else:
            st.info("No active trades found.")
            
    with tab2:
        if history:
            st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
        else:
            st.info("No trade history found.")

    st.markdown("---")
    st.subheader("📈 Performance Metrics")
    m1, m2, m3 = st.columns(3)
    
    total_trades = len(history)
    wins = sum(1 for t in history if t.get('status') == 'TARGET_HIT')
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    m1.metric("Total Trades", total_trades)
    m2.metric("Win Rate", f"{win_rate:.1f}%")
    # Calculate actual P&L from history
    total_pnl = sum(t.get('pnl', 0) for t in history)
    m3.metric("Net P&L", f"{total_pnl:+.2f}%", delta=f"{total_pnl:.2f}%")
