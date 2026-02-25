"""
ATM Scanner View - Streamlit Integration
Displays top 5 CE/PE options from 180+ F&O stocks
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add services to path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from services.atm_option_scanner import (
    scan_all_fno_stocks,
    get_top_5_ce_pe,
    NSE_FNO_STOCKS
)

def render_atm_scanner():
    """Main ATM Scanner View"""
    
    st.title("🎯 ATM Options Scanner")
    st.markdown("**Find Top 5 Call & Put Options from 180+ F&O Stocks**")
    st.markdown("---")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ Scanner Settings")
        
        max_stocks = st.slider(
            "Stocks to Scan",
            min_value=50,
            max_value=180,
            value=180,
            step=10,
            help="Number of stocks to scan from F&O universe"
        )
        
        max_workers = st.slider(
            "Parallel Workers",
            min_value=5,
            max_value=20,
            value=15,
            step=1,
            help="Higher = faster but may hit API limits"
        )
        
        scan_button = st.button("🔍 Start Scan", type="primary", use_container_width=True)
    
    # Main content area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("F&O Universe", f"{len(NSE_FNO_STOCKS)} Stocks")
    with col2:
        st.metric("Scanning", f"{max_stocks} Stocks")
    with col3:
        st.metric("Target", "Top 5 CE + Top 5 PE")
    
    # Run scan
    if scan_button or 'scan_results' not in st.session_state:
        st.session_state['scan_results'] = None
    
    if scan_button:
        with st.spinner(f"🔍 Scanning {max_stocks} stocks... This may take 30-60 seconds..."):
            try:
                # Scan stocks
                df = scan_all_fno_stocks(
                    max_stocks=max_stocks,
                    max_workers=max_workers
                )
                
                if not df.empty:
                    # Get top 5 CE and PE
                    top_5_ce, top_5_pe = get_top_5_ce_pe(df)
                    
                    # Store in session
                    st.session_state['scan_results'] = {
                        'ce': top_5_ce,
                        'pe': top_5_pe,
                        'timestamp': datetime.now(),
                        'stocks_scanned': len(df)
                    }
                    
                    st.success(f"✅ Scan Complete! Found {len(df)} stocks with valid data")
                else:
                    st.error("❌ No data available. Check market hours or connectivity.")
                    
            except Exception as e:
                st.error(f"❌ Error during scan: {e}")
    
    # Display results
    if st.session_state.get('scan_results'):
        results = st.session_state['scan_results']
        
        st.markdown("---")
        st.markdown(f"**Last Scan:** {results['timestamp'].strftime('%d-%m-%Y %H:%M:%S')} | "
                   f"**Stocks Scanned:** {results['stocks_scanned']}")
        
        # Top 5 CE
        st.markdown("### 🟢 TOP 5 CALL OPTIONS (CE) - ATM")
        if results['ce'] is not None and not results['ce'].empty:
            # Style dataframe
            ce_styled = results['ce'].style.format({
                'Spot': '₹{:.2f}',
                'Strike': '{:.0f}',
                'Entry': '₹{:.2f}',
                'Target': '₹{:.2f}',
                'Premium%': '{:.2f}%',
                'DTE': '{:.0f}'
            }).background_gradient(subset=['Entry'], cmap='Greens')
            
            st.dataframe(ce_styled, use_container_width=True, hide_index=True)
            
            # Download button
            csv_ce = results['ce'].to_csv(index=False)
            st.download_button(
                label="📥 Download CE Data",
                data=csv_ce,
                file_name=f"top5_ce_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No valid Call options found")
        
        st.markdown("---")
        
        # Top 5 PE
        st.markdown("### 🔴 TOP 5 PUT OPTIONS (PE) - ATM")
        if results['pe'] is not None and not results['pe'].empty:
            # Style dataframe
            pe_styled = results['pe'].style.format({
                'Spot': '₹{:.2f}',
                'Strike': '{:.0f}',
                'Entry': '₹{:.2f}',
                'Target': '₹{:.2f}',
                'Premium%': '{:.2f}%',
                'DTE': '{:.0f}'
            }).background_gradient(subset=['Entry'], cmap='Reds')
            
            st.dataframe(pe_styled, use_container_width=True, hide_index=True)
            
            # Download button
            csv_pe = results['pe'].to_csv(index=False)
            st.download_button(
                label="📥 Download PE Data",
                data=csv_pe,
                file_name=f"top5_pe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No valid Put options found")
        
        # Insights
        st.markdown("---")
        st.markdown("### 📊 Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if results['ce'] is not None and not results['ce'].empty:
                avg_ce_premium = results['ce']['Entry'].mean()
                st.metric("Avg CE Premium", f"₹{avg_ce_premium:.2f}")
                
                best_ce_stock = results['ce'].iloc[0]['Stock']
                best_ce_entry = results['ce'].iloc[0]['Entry']
                st.info(f"🏆 Best CE: **{best_ce_stock}** @ ₹{best_ce_entry:.2f}")
        
        with col2:
            if results['pe'] is not None and not results['pe'].empty:
                avg_pe_premium = results['pe']['Entry'].mean()
                st.metric("Avg PE Premium", f"₹{avg_pe_premium:.2f}")
                
                best_pe_stock = results['pe'].iloc[0]['Stock']
                best_pe_entry = results['pe'].iloc[0]['Entry']
                st.info(f"🏆 Best PE: **{best_pe_stock}** @ ₹{best_pe_entry:.2f}")
    
    else:
        st.info("👆 Click '🔍 Start Scan' to find top ATM options")
        
        st.markdown("---")
        st.markdown("### 📖 How It Works")
        st.markdown("""
        1. **Scans 180+ F&O stocks** from NSE
        2. **Calculates ATM strikes** for each stock
        3. **Fetches real option prices** (CE & PE)
        4. **Ranks by premium value** and percentage
        5. **Returns top 5 CE and top 5 PE** options
        
        **Perfect for:**
        - Intraday options trading
        - ATM straddle/strangle strategies
        - Quick opportunity screening
        """)
