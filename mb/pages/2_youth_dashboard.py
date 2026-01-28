"""
Magic Bus Compass 360 - Youth Dashboard
Personalized learning dashboard for students
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Youth Dashboard | Magic Bus Compass", page_icon="📊", layout="wide")

st.title("📊 Youth Dashboard")

# Check if user is logged in
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("⚠️ Please log in to access your dashboard")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/0_login.py")
else:
    # Display dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Modules Completed", "0", "in progress")
    
    with col2:
        st.metric("🏆 Total Points", "0", "pending")
    
    with col3:
        st.metric("🎯 Current Streak", "0 days", "Start a module")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Career Fit Survey")
    st.info("Complete the career fit survey to discover your ideal career path.")
    
    if st.button("📋 Take Career Fit Survey"):
        st.info("Survey coming soon!")
    
    st.markdown("### 📚 Learning Modules")
    st.write("Your personalized learning path will appear here once you complete the career fit survey.")
    
    st.markdown("### 📈 Progress")
    st.write("Track your progress and achievements as you complete modules and earn badges.")
