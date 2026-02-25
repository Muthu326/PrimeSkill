import streamlit as st
import plotly.graph_objects as go

def render_conviction(data):
    """
    Renders the CONVICTION workspace
    """
    st.markdown("### 💎 Trade Conviction Analyzer")
    
    rsi_val = data.get('rsi_val', 50.0)
    adx_val = data.get('adx_val', 20.0)
    v_ratio = data.get('v_ratio', 1.0)
    
    # Calculate score
    score = 0
    if 40 < rsi_val < 60: score += 10
    elif 30 < rsi_val < 70: score += 20
    else: score += 30
    
    score += min(30, adx_val)
    score += min(40, v_ratio * 10)
    
    score = min(100, score)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': "Confidence Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00e676" if score > 70 else "#ffd740" if score > 40 else "#ff1744"}
        }
    ))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### 🔬 Factor Breakdown")
    st.write(f"- RSI Contribution: {min(30, abs(rsi_val-50))}")
    st.write(f"- ADX Strength: {min(30, adx_val)}")
    st.write(f"- Volume Participation: {min(40, v_ratio * 10)}")
