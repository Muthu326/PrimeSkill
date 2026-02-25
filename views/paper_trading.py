import streamlit as st
import pandas as pd

def render_paper_trading(data):
    """
    Renders the PAPER TRADING workspace
    """
    st.markdown("### 📈 Paper Trading Dashboard")
    st.caption("Risk-free virtual trading with real-time price tracking")
    
    portfolio = st.session_state.get('paper_portfolio', [])
    
    if not portfolio:
        st.info("No active paper trades. Top picks from the HOME tab are automatically added here.")
    else:
        st.markdown("#### 🏦 Current Portfolio")
        df = pd.DataFrame(portfolio)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary
        total_pnl = sum(t.get('current_pnl', 0) for t in portfolio)
        st.metric("Total Portfolio P&L", f"₹{total_pnl:.2f}", delta=f"{total_pnl:.2f}")

    st.markdown("---")
    st.subheader("🛠 Portfolio Controls")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Reset Portfolio", use_container_width=True):
            st.session_state['paper_portfolio'] = []
            st.rerun()
    with c2:
        st.button("Export to Excel", use_container_width=True)
