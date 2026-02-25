"""
F&O Options Trading Dashboard
Professional Options Trading System with Strategy Engine

Created by: MuthuKumar Krishnan
PRIME SKILL DEVELOPMENT
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import existing terminal functions
try:
    from services.market_engine import (
        fetch_realtime_price, load_data, calculate_indicators,
        get_days_to_expiry
    )
    from marsh_muthu_326_pro_terminal import st_spinner_patch
    st.spinner = st_spinner_patch
except Exception as e:
    st.warning(f"Could not import from main terminal: {e}")
    # Fallback stubs
    def fetch_realtime_price(symbol, is_index=True):
        return {'lastprice': 21500, 'prevclose': 21450}
    def get_days_to_expiry():
        return 7

# Import our services
from database import get_db_manager
from services import (
    get_options_pricer, get_strategy_engine, get_trading_engine,
    get_pnl_calculator, get_risk_manager
)
from models import StrategyType, TradeStatus, OptionType
from config.config import SYMBOLS, TRADING_CONFIG, DASHBOARD_CONFIG

# ==================== PAGE CONFIG ====================
st.set_page_config(
    layout="wide",
    page_title="F&O Options Trading | PRIME SKILL",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    
    .profit {
        color: #00C851;
        font-weight: bold;
    }
    
    .loss {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Disclaimer */
    .disclaimer {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
    }
    
    /* Strategy cards */
    .strategy-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: white;
    }
    
    .strategy-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZE SERVICES ====================
@st.cache_resource
def init_services():
    """Initialize all services (cached)"""
    db = get_db_manager()
    pricer = get_options_pricer()
    strategy_engine = get_strategy_engine()
    trading_engine = get_trading_engine()
    pnl_calc = get_pnl_calculator()
    risk_mgr = get_risk_manager()
    
    return {
        'db': db,
        'pricer': pricer,
        'strategy': strategy_engine,
        'trading': trading_engine,
        'pnl': pnl_calc,
        'risk': risk_mgr
    }

services = init_services()

# ==================== HELPER FUNCTIONS ====================

def get_market_data(symbol):
    """Get current market data for symbol"""
    try:
        # Try to use real data
        if symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"]:
            data = fetch_realtime_price(symbol, is_index=True)
            if data:
                return {
                    'price': data['lastprice'],
                    'prev_close': data.get('prevclose', data['lastprice']),
                    'change': data['lastprice'] - data.get('prevclose', data['lastprice']),
                    'change_pct': ((data['lastprice'] - data.get('prevclose', data['lastprice'])) / data.get('prevclose', 1)) * 100
                }
        
        # Fallback
        return {
            'price': 21500,
            'prev_close': 21450,
            'change': 50,
            'change_pct': 0.23
        }
    except:
        return {'price': 21500, 'prev_close': 21450, 'change': 50, 'change_pct': 0.23}

def format_pnl(pnl):
    """Format P&L with color"""
    if pnl >= 0:
        return f'<span class="profit">₹{pnl:,.2f}</span>'
    else:
        return f'<span class="loss">₹{pnl:,.2f}</span>'

# ==================== SIDEBAR ====================

with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=PRIME+SKILL", use_column_width=True)
    st.title("🎯 F&O Options Trading")
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ PAPER TRADING ONLY</strong><br>
        This is a simulation system. No real money involved.
        Past performance does not guarantee future results.
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🎯 Strategy Selector", "📈 Positions", "📜 Trade History", "📉 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    # Quick stats in sidebar
    st.markdown("---")
    st.subheader("Quick Stats")
    
    try:
        metrics = services['pnl'].get_performance_metrics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total P&L", f"₹{metrics.total_pnl:,.0f}", 
                     delta=f"{metrics.roi:.1f}%")
        with col2:
            st.metric("Win Rate", f"{metrics.win_rate:.1f}%",
                     delta=f"{metrics.win_count}W/{metrics.loss_count}L")
        
        st.metric("Open Positions", len(services['trading'].get_active_positions()))
    
    except Exception as e:
        st.error(f"Error loading stats: {e}")

# ==================== MAIN CONTENT ====================

if page == "📊 Dashboard":
    st.title("📊 Trading Dashboard")
    
    # Market Overview
    st.subheader("Market Overview")
    
    cols = st.columns(4)
    for idx, symbol in enumerate(["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"]):
        with cols[idx % 4]:
            data = get_market_data(symbol)
            
            delta_color = "normal" if data['change'] >= 0 else "inverse"
            st.metric(
                symbol,
                f"₹{data['price']:,.2f}",
                delta=f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)",
                delta_color=delta_color
            )
    
    st.markdown("---")
    
    # Portfolio Summary
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        metrics = services['pnl'].get_performance_metrics()
        risk_metrics = services['risk'].calculate_portfolio_risk()
        
        with col1:
            st.metric("Total P&L", f"₹{metrics.total_pnl:,.2f}", 
                     delta=f"{metrics.roi:.2f}%")
        
        with col2:
            st.metric("Unrealized P&L", f"₹{metrics.unrealized_pnl:,.2f}")
        
        with col3:
            st.metric("Win Rate", f"{metrics.win_rate:.1f}%")
        
        with col4:
            st.metric("Max Drawdown", f"₹{metrics.max_drawdown:,.2f}")
    
    except Exception as e:
        st.error(f"Error loading portfolio summary: {e}")
    
    st.markdown("---")
    
    # Active Positions
    st.subheader("Active Positions")
    
    try:
        positions = services['trading'].get_active_positions()
        
        if positions:
            pos_data = []
            for pos in positions:
                pos_data.append({
                    'Symbol': pos.symbol,
                    'Type': pos.option_type.value,
                    'Strike': pos.strike_price,
                    'Qty': pos.quantity,
                    'Entry': f"₹{pos.avg_price:.2f}",
                    'Current': f"₹{pos.current_price:.2f}" if pos.current_price else "N/A",
                    'P&L': pos.pnl if pos.pnl else 0.0,
                    'Delta': pos.greeks.delta if pos.greeks else 0.0,
                })
            
            df = pd.DataFrame(pos_data)
            
            # Style the dataframe
            def color_pnl(val):
                color = 'green' if val >= 0 else 'red'
                return f'color: {color}'
            
            if 'P&L' in df.columns:
                styled_df = df.style.applymap(color_pnl, subset=['P&L'])
                st.dataframe(styled_df, use_container_width=True, height=300)
            else:
                st.dataframe(df, use_container_width=True, height=300)
        else:
            st.info("No active positions. Go to Strategy Selector to find opportunities!")
    
    except Exception as e:
        st.error(f"Error loading positions: {e}")
    
    # Risk Alerts
    st.markdown("---")
    st.subheader("⚠️ Risk Alerts")
    
    try:
        alerts = services['risk'].get_risk_alerts()
        
        if alerts:
            for alert in alerts:
                if alert['severity'] == 'HIGH':
                    st.error(alert['message'])
                elif alert['severity'] == 'MEDIUM':
                    st.warning(alert['message'])
                else:
                    st.info(alert['message'])
        else:
            st.success("✅ All risk parameters within limits")
        
        # Hedge suggestion
        hedge = services['risk'].suggest_hedge()
        if hedge:
            st.info(f"💡 **Hedge Suggestion:** {hedge}")
    
    except Exception as e:
        st.error(f"Error loading risk alerts: {e}")

elif page == "🎯 Strategy Selector":
    st.title("🎯 Strategy Selector")
    
    st.markdown("""
    Select a trading strategy based on current market conditions.
    The system will recommend the best strategies with entry/exit levels.
    """)
    
    # Symbol selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_symbol = st.selectbox(
            "Select Symbol",
            ["NIFTY", "BANKNIFTY", "FINNIFTY"],
            index=0
        )
    
    with col2:
        days_to_expiry = st.number_input(
            "Days to Expiry",
            min_value=1,
            max_value=30,
            value=get_days_to_expiry(),
            help="Weekly expiry is typically 7 days"
        )
    
    # Get market data
    market_data = get_market_data(selected_symbol)
    spot_price = market_data['price']
    
    st.metric(f"{selected_symbol} Spot Price", f"₹{spot_price:,.2f}", 
             delta=f"{market_data['change_pct']:+.2f}%")
    
    # Load technical data
    with st.spinner(f"Analyzing {selected_symbol} market conditions..."):
        try:
            # Try to load real chart data
            ticker_symbol = SYMBOLS.get(selected_symbol, f"^NSE{selected_symbol}")
            df = load_data(f"{ticker_symbol}.NS" if not ticker_symbol.startswith("^") else ticker_symbol, 
                          interval="5m", period="5d")
            
            if not df.empty:
                df = calculate_indicators(df)
            else:
                # Create dummy data for demo
                df = pd.DataFrame({
                    'Close': [spot_price] * 50,
                    'RSI': [55] * 50,
                    'ADX': [30] * 50,
                    'EMA20': [spot_price * 0.99] * 50,
                    'EMA50': [spot_price * 0.98] * 50,
                })
        except:
            # Fallback dummy data
            df = pd.DataFrame({
                'Close': [spot_price] * 50,
                'RSI': [55] * 50,
                'ADX': [30] * 50,
                'EMA20': [spot_price * 0.99] * 50,
                'EMA50': [spot_price * 0.98] * 50,
            })
    
    # Get strategy recommendations
    with st.spinner("Getting strategy recommendations..."):
        try:
            recommendations = services['strategy'].get_strategy_recommendations(
                df, selected_symbol, spot_price, days_to_expiry
            )
            
            if recommendations:
                st.success(f"Found {len(recommendations)} suitable strategies")
                
                for idx, signal in enumerate(recommendations):
                    with st.expander(f"**{signal.strategy_type.value}** - Confidence: {signal.confidence:.0%}", expanded=(idx==0)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Entry Price", f"₹{signal.entry_price:.2f}")
                            st.metric("Stop Loss", f"₹{signal.stop_loss:.2f}")
                        
                        with col2:
                            st.metric("Target", f"₹{signal.target:.2f}")
                            st.metric("Risk:Reward", f"1:{signal.risk_reward:.2f}")
                        
                        with col3:
                            st.metric("Max Profit", f"₹{signal.max_profit:,.2f}" if signal.max_profit != float('inf') else "Unlimited")
                            st.metric("Max Loss", f"₹{abs(signal.max_loss):,.2f}")
                        
                        # Option legs
                        st.markdown("**Option Legs:**")
                        for leg in signal.option_legs:
                            st.write(f"- {leg['action']} {leg['type']} @ Strike {leg['strike']} - Premium: ₹{leg['premium']:.2f}")
                        
                        st.info(signal.notes)
                        
                        # Execute button
                        if st.button(f"Execute {signal.strategy_type.value}", key=f"exec_{idx}"):
                            # Check risk limits
                            allowed, msg = services['risk'].check_all_limits(signal.entry_price, signal.position_size)
                            
                            if allowed:
                                trade_id = services['trading'].place_trade(signal)
                                if trade_id:
                                    st.success(f"✅ Trade placed successfully! Trade ID: {trade_id}")
                                    st.balloons()
                                else:
                                    st.error("Failed to place trade")
                            else:
                                st.error(f"❌ Risk limit check failed: {msg}")
            
            else:
                st.warning("No suitable strategies found for current market conditions. Try a different symbol or wait for better setups.")
        
        except Exception as e:
            st.error(f"Error getting recommendations: {e}")
            import traceback
            st.code(traceback.format_exc())

elif page == "📈 Positions":
    st.title("📈 Open Positions")
    
    try:
        positions = services['trading'].get_active_positions()
        
        if positions:
            # Portfolio Greeks
            st.subheader("Portfolio Greeks")
            
            portfolio_greeks = services['trading'].get_portfolio_greeks()
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Delta", f"{portfolio_greeks.delta:.4f}")
            col2.metric("Gamma", f"{portfolio_greeks.gamma:.4f}")
            col3.metric("Theta", f"₹{portfolio_greeks.theta:.2f}")
            col4.metric("Vega", f"₹{portfolio_greeks.vega:.2f}")
            col5.metric("Rho", f"₹{portfolio_greeks.rho:.4f}")
            
            st.markdown("---")
            
            # Position details
            for idx, pos in enumerate(positions):
                with st.expander(f"{pos.symbol} {pos.option_type.value} {pos.strike_price} - P&L: ₹{pos.pnl:.2f}" if pos.pnl else f"{pos.symbol} {pos.option_type.value} {pos.strike_price}",
                                expanded=(idx<3)):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**Entry:** ₹{pos.avg_price:.2f}")
                        st.write(f"**Current:** ₹{pos.current_price:.2f}" if pos.current_price else "**Current:** Updating...")
                    
                    with col2:
                        pnl_html = format_pnl(pos.pnl) if pos.pnl else "₹0.00"
                        st.markdown(f"**P&L:** {pnl_html}", unsafe_allow_html=True)
                        st.write(f"**Quantity:** {pos.quantity}")
                    
                    with col3:
                        if pos.greeks:
                            st.write(f"**Delta:** {pos.greeks.delta:.4f}")
                            st.write(f"**Theta:** ₹{pos.greeks.theta:.2f}")
                    
                    with col4:
                        if pos.max_profit != float('inf'):
                            st.write(f"**Max Profit:** ₹{pos.max_profit:.2f}")
                        st.write(f"**Max Loss:** ₹{abs(pos.max_loss):.2f}" if pos.max_loss else "N/A")
                    
                    # Close button
                    if st.button(f"Close Position", key=f"close_{pos.id}"):
                        if pos.current_price:
                            success = services['trading'].close_position(pos.id, pos.current_price, "Manual Close")
                            if success:
                                st.success("Position closed successfully!")
                                st.rerun()
                        else:
                            st.error("Cannot close: current price not available")
        
        else:
            st.info("No open positions")
    
    except Exception as e:
        st.error(f"Error loading positions: {e}")

elif page == "📜 Trade History":
    st.title("📜 Trade History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol_filter = st.selectbox("Symbol", ["All"] + list(SYMBOLS.keys()))
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "OPEN", "CLOSED", "STOPPED"])
    
    with col3:
        days_back = st.number_input("Days Back", min_value=1, max_value=365, value=30)
    
    try:
        # Get trades
        start_date = datetime.now() - timedelta(days=days_back)
        
        if status_filter == "All":
            trades = services['db'].get_trades(
                symbol=None if symbol_filter == "All" else symbol_filter,
                start_date=start_date,
                limit=200
            )
        else:
            trades = services['db'].get_trades(
                symbol=None if symbol_filter == "All" else symbol_filter,
                status=TradeStatus[status_filter],
                start_date=start_date,
                limit=200
            )
        
        if trades:
            st.write(f"**Total Trades:** {len(trades)}")
            
            # Convert to DataFrame
            trade_data = []
            for t in trades:
                trade_data.append({
                    'ID': t.id,
                    'Date': t.entry_time.strftime('%Y-%m-%d %H:%M'),
                    'Symbol': t.symbol,
                    'Type': t.option_type.value,
                    'Strike': t.strike_price,
                    'Entry': f"₹{t.entry_price:.2f}",
                    'Exit': f"₹{t.exit_price:.2f}" if t.exit_price else "-",
                    'P&L': t.pnl if t.pnl else 0.0,
                    'Status': t.status.value,
                })
            
            df = pd.DataFrame(trade_data)
            
            # Display
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "trade_history.csv",
                "text/csv"
            )
        
        else:
            st.info("No trades found matching the filters")
    
    except Exception as e:
        st.error(f"Error loading trade history: {e}")

elif page == "📉 Analytics":
    st.title("📉 Performance Analytics")
    
    try:
        # Performance metrics
        metrics = services['pnl'].get_performance_metrics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total P&L", f"₹{metrics.total_pnl:,.2f}", delta=f"{metrics.roi:.2f}%")
        
        with col2:
            st.metric("Win Rate", f"{metrics.win_rate:.1f}%", 
                     delta=f"{metrics.win_count}W-{metrics.loss_count}L")
        
        with col3:
            st.metric("Avg Profit", f"₹{metrics.avg_profit:.2f}")
        
        with col4:
            st.metric("Max Drawdown", f"₹{metrics.max_drawdown:.2f}")
        
        st.markdown("---")
        
        # P&L Chart
        st.subheader("Cumulative P&L")
        
        pnl_series = services['pnl'].get_pnl_series(days=30)
        
        if not pnl_series.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pnl_series['Date'],
                y=pnl_series['Cumulative_PnL'],
                mode='lines+markers',
                name='Cumulative P&L',
                line=dict(color='#667eea', width=3),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                height=400,
                hovermode='x unified',
                xaxis_title="Date",
                yaxis_title="P&L (₹)",
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Strategy Performance
        st.subheader("Strategy Performance")
        
        strat_perf = services['pnl'].get_strategy_performance()
        
        if not strat_perf.empty:
            fig = go.Figure(data=[
                go.Bar(x=strat_perf['Strategy'], y=strat_perf['Total_PnL'],
                      marker_color=strat_perf['Total_PnL'].apply(lambda x: 'green' if x >= 0 else 'red'))
            ])
            
            fig.update_layout(
                height=400,
                xaxis_title="Strategy",
                yaxis_title="Total P&L (₹)",
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Best/Worst Trades
        col1, col2 = st.columns(2)
        
        best, worst = services['pnl'].get_best_worst_trades(top_n=5)
        
        with col1:
            st.subheader("🏆 Best Trades")
            for t in best:
                st.success(f"{t.symbol} {t.option_type.value} - ₹{t.pnl:.2f}")
        
        with col2:
            st.subheader("❌ Worst Trades")
            for t in worst:
                st.error(f"{t.symbol} {t.option_type.value} - ₹{t.pnl:.2f}")
    
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.subheader("Trading Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Initial Capital:** ₹{TRADING_CONFIG['initial_capital']:,.0f}")
        st.write(f"**Max Position Size:** {TRADING_CONFIG['max_position_size']*100}%")
        st.write(f"**Max Daily Loss:** {TRADING_CONFIG['max_daily_loss']*100}%")
    
    with col2:
        st.write(f"**Max Positions:** {TRADING_CONFIG['max_positions']}")
        st.write(f"**Brokerage per Lot:** ₹{TRADING_CONFIG['brokerage_per_lot']}")
    
    st.markdown("---")
    st.subheader("Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Database Stats"):
            stats = services['db'].get_trade_statistics()
            st.json(stats)
    
    with col2:
        if st.button("🗑️ Clean Old Data (90+ days)"):
            services['db'].cleanup_old_data(days=90)
            st.success("Old data cleaned!")
    
    with col3:
        if st.button("🔄 Reset Database"):
            if st.checkbox("I understand this will delete ALL data"):
                st.error("Feature disabled for safety")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <strong>F&O Options Trading System v1.0</strong><br>
    Created by MuthuKumar Krishnan | PRIME SKILL DEVELOPMENT<br>
    <em>⚠️ For educational and paper trading purposes only. Not financial advice.</em>
</div>
""", unsafe_allow_html=True)
