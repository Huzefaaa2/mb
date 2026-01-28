"""
Magic Bus Compass 360 - Main Streamlit App Entry Point
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Magic Bus Compass 360",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🧭 Magic Bus Compass 360</h1>
        <p style="font-size: 18px; color: #666;">Career Fit Discovery → Training → Placement Success</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

st.sidebar.markdown("---")

if st.session_state.user_id is None:
    st.sidebar.info("👤 Not logged in")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔓 Login", use_container_width=True):
            st.switch_page("pages/0_login.py")
    with col2:
        if st.button("📝 Register", use_container_width=True):
            st.switch_page("pages/1_register.py")
else:
    st.sidebar.success(f"✓ Logged in")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.rerun()

st.sidebar.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🎯 Youth Registered", "Pending", "")

with col2:
    st.metric("📚 Training Active", "Pending", "")

with col3:
    st.metric("💼 Placements", "Pending", "")

st.markdown("---")

st.markdown("""
### 🎯 What is Magic Bus Compass 360?

A **mobile-first platform** that reduces dropout by discovering career fit in the first 5 days,
then guiding youth through 60-day training with personalized skill plans and post-placement counselling.

**Key Features:**
- 🎯 Smart career fit discovery (Day 0-5)
- 📈 Adaptive learning paths & gamification
- 👨‍🏫 Teacher attention routing for at-risk youth
- 🎤 Voice screening for soft skills
- 💬 Post-placement counselling loop

**For Youth:** Get started by registering or logging in  
**For Charity Staff:** Access the dashboard for heatmaps and interventions
""")

st.markdown("---")
st.markdown("**Magic Bus Compass 360** v1.0 | Built with ❤️ for education & careers")
