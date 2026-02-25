import streamlit as st

def render_plans(data=None):
    """
    Renders the PLANS & ACCESS workspace
    """
    st.markdown("""
    <div style="text-align:center; padding: 20px 0;">
        <h1 style="color:#00f2ff; text-shadow: 0 0 15px #00f2ff; margin-bottom: 10px;">💎 PRIME SKILL MEMBERSHIP PLANS</h1>
        <p style="color:#ccc; font-size:1.1rem;">Choose your professional trading edge</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid #444; border-radius:15px; padding:25px; height:500px; position:relative;">
            <h2 style="color:white; margin-top:0;">🆓 FREE ACCESS</h2>
            <h3 style="color:#00e676;">₹0 <span style="font-size:0.8rem; color:#888;">/ Lifetime</span></h3>
            <hr style="border-color:#333;">
            <ul style="color:#ccc; font-size:0.9rem; line-height:2;">
                <li>✅ Real-time Nifty 50 Scan</li>
                <li>✅ Basic Momentum Indicators</li>
                <li>✅ Manual Telegram Alerts</li>
                <li>✅ Paper Trading Simulator</li>
                <li>✅ Basic Option Chain</li>
                <li>❌ No Pro Scalp Signals</li>
                <li>❌ No Auto-Execution</li>
            </ul>
            <div style="position:absolute; bottom:25px; left:25px; right:25px;">
                <button style="width:100%; padding:10px; background:#444; color:white; border:none; border-radius:5px; cursor:not-allowed;">CURRENT PLAN</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:linear-gradient(145deg, rgba(0,242,255,0.1), rgba(0,0,0,0)); border:2px solid #00f2ff; border-radius:15px; padding:25px; height:500px; position:relative; transform: scale(1.05);">
            <div style="position:absolute; top:-15px; right:20px; background:#00f2ff; color:black; padding:2px 12px; border-radius:20px; font-weight:bold; font-size:0.8rem;">MOST POPULAR</div>
            <h2 style="color:#00f2ff; margin-top:0;">🔥 PRO TERMINAL</h2>
            <h3 style="color:white;">₹1,999 <span style="font-size:0.8rem; color:#888;">/ Month</span></h3>
            <hr style="border-color:rgba(0,242,255,0.3);">
            <ul style="color:white; font-size:0.9rem; line-height:2;">
                <li>✅ <b>All Free Features</b></li>
                <li>✅ Full F&O Market Scan (180+ Stocks)</li>
                <li>✅ <b>Diamond Jackpot Signals</b></li>
                <li>✅ 24/7 Automated Telegram Bot</li>
                <li>✅ Pro Scalp Engine Access</li>
                <li>✅ Strategy Hub & Greek Analysis</li>
                <li>✅ Advanced Charting Suite</li>
            </ul>
            <div style="position:absolute; bottom:25px; left:25px; right:25px;">
                <button style="width:100%; padding:10px; background:#00f2ff; color:black; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">UPGRADE NOW</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid #ffd740; border-radius:15px; padding:25px; height:500px; position:relative;">
            <h2 style="color:#ffd740; margin-top:0;">👑 ELITE (AI)</h2>
            <h3 style="color:white;">₹4,999 <span style="font-size:0.8rem; color:#888;">/ Month</span></h3>
            <hr style="border-color:rgba(255,215,64,0.3);">
            <ul style="color:#ccc; font-size:0.9rem; line-height:2;">
                <li>✅ <b>Everything in PRO</b></li>
                <li>✅ <b>AI-Powered Trend Prediction</b></li>
                <li>✅ API Bridging (Live Execution)</li>
                <li>✅ Custom Strategy Builder</li>
                <li>✅ 1-on-1 Strategy Consulting</li>
                <li>✅ Multi-Instance Hosting</li>
                <li>✅ Dedicated Support Bot</li>
            </ul>
            <div style="position:absolute; bottom:25px; left:25px; right:25px;">
                <button style="width:100%; padding:10px; background:#ffd740; color:black; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">GET ELITE</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("### 🌐 Your Website Access Information")
    i1, i2 = st.columns(2)
    with i1:
        st.info("""
        **How to access your website for free:**
        1. We use **Streamlit Community Cloud** for free hosting.
        2. Your website is synced with your GitHub repository.
        3. Any changes you make locally can be pushed to the cloud using `PUBLISH_TO_WEBSITE.bat`.
        """)
    with i2:
        st.success("""
        **Benefits of Free Cloud Access:**
        - Check signals from your Mobile Phone.
        - Access from any computer without installing Python.
        - 24/7 Availability (Dashboard stays live).
        - SSL Encryption (Secure access).
        """)

    st.markdown("""
    <div style="background:rgba(0,230,118,0.1); border:1px solid #00e676; padding:15px; border-radius:10px; text-align:center; margin-top:20px;">
        <h4 style="color:#00e676; margin:0;">💡 DID YOU KNOW?</h4>
        <p style="color:#ccc; margin:5px 0 0 0;">You can share your website URL with your clients or friends for free access!</p>
    </div>
    """, unsafe_allow_html=True)
