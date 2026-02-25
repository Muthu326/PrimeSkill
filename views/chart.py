import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_chart(data):
    """
    Renders the CHART workspace
    """
    st.markdown("### 📊 Advanced Interactive Chart")
    main_df = data.get('main_df')
    
    if main_df is not None and not main_df.empty:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2],
                            vertical_spacing=0.03, subplot_titles=("Price Action", "RSI", "Volume"))
        fig.add_trace(go.Candlestick(x=main_df.index, open=main_df['Open'], high=main_df['High'],
                      low=main_df['Low'], close=main_df['Close'], name='Price'), row=1, col=1)
        
        if 'EMA20' in main_df.columns:
            fig.add_trace(go.Scatter(x=main_df.index, y=main_df['EMA20'], line=dict(color='orange', width=1), name='EMA20'), row=1, col=1)
        if 'EMA200' in main_df.columns:
            fig.add_trace(go.Scatter(x=main_df.index, y=main_df['EMA200'], line=dict(color='cyan', width=1), name='EMA200'), row=1, col=1)
        if 'VWAP' in main_df.columns:
            fig.add_trace(go.Scatter(x=main_df.index, y=main_df['VWAP'], line=dict(color='purple', width=1, dash='dot'), name='VWAP'), row=1, col=1)
            
        if 'RSI' in main_df.columns:
            fig.add_trace(go.Scatter(x=main_df.index, y=main_df['RSI'], line=dict(color='#ffd740', width=1), name='RSI'), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
        colors = ['#00e676' if c > o else '#ff1744' for c, o in zip(main_df['Close'], main_df['Open'])]
        fig.add_trace(go.Bar(x=main_df.index, y=main_df['Volume'], marker_color=colors, name='Volume', opacity=0.6), row=3, col=1)
        
        fig.update_layout(template="plotly_dark", height=700, showlegend=False, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select a symbol and fetch data to view chart.")
