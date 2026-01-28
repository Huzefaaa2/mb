"""
Magic Bus Compass 360 - Main Streamlit App Entry Point
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Magic Bus Compass 360",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1> Magic Bus Compass 360</h1>
        <p style="font-size: 18px; color: #666;">Career Fit Discovery  Training  Placement Success</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

st.sidebar.markdown("---")

if st.session_state.user_id is None:
    st.sidebar.info(" User Not Logged In")
    st.sidebar.markdown("### Quick Links")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button(" Login", key="btn_sidebar_login"):
            st.switch_page("pages/0_login.py")
    with col2:
        if st.button(" Register", key="btn_sidebar_register"):
            st.switch_page("pages/1_register.py")
else:
    st.sidebar.success(f" {st.session_state.get('username', 'User')}")
    if st.sidebar.button(" Logout", key="btn_sidebar_logout"):
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Pages")
st.sidebar.page_link("pages/0_login.py", label=" Login")
st.sidebar.page_link("pages/1_register.py", label=" Register")
if st.session_state.user_id:
    st.sidebar.page_link("pages/2_youth_dashboard.py", label=" Dashboard")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Students", "1,234", "+12%")

with col2:
    st.metric("Placement Rate", "89%", "+5%")

with col3:
    st.metric("Avg Salary", "$65K", "+8%")

st.markdown("""
##  Features

### Career Fit Discovery
Comprehensive assessments to identify the best career paths for each student based on skills, interests, and market demand.

### Personalized Training
Customized learning paths with industry-relevant content delivered through our platform.

### Placement Success
Direct connections with employers and job placement support to ensure career transition success.

### Analytics Dashboard
Real-time insights into student progress, skills development, and placement outcomes.

##  Integrated Azure Services

- **PostgreSQL Database**: Student data and program information
- **Blob Storage**: Resume and document storage with read-only and writable separation
- **Speech-to-Text**: Audio transcription and accessibility features
- **Databricks**: Advanced analytics and SQL processing
- **OpenAI**: AI-powered recommendations and content generation

##  Demo Mode

This application is running in **demo mode** with a local SQLite database for testing.
- Use demo credentials to login
- Create new accounts to test registration
- All data is stored locally for development
""")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'><small> 2026 Magic Bus Compass 360 - All Rights Reserved</small></div>", unsafe_allow_html=True)
