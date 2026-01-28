"""
Magic Bus Compass 360 - Confirmation Page after Registration
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Registration Confirmed", page_icon="✅")

st.title("✅ Registration Confirmed!")

if "registration_data" not in st.session_state:
    st.error("No registration data found. Please complete registration first.")
    if st.button("← Back to Registration"):
        st.switch_page("pages/1_register.py")
else:
    reg_data = st.session_state.registration_data
    student_data = reg_data["student_data"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("Your registration is complete!")
        st.write(f"**Name:** {student_data['first_name']} {student_data['last_name']}")
        st.write(f"**Email:** {student_data['email']}")
        st.write(f"**Student ID:** `{reg_data['student_id']}`")
    
    with col2:
        st.info("📌 Save your credentials:")
        st.code(f"Login ID: {reg_data['login_id']}\nPassword: {reg_data['password_hint']}")
    
    st.markdown("---")
    
    if st.button("🎯 Start Career Fit Survey", use_container_width=True):
        st.switch_page("pages/2_youth_dashboard.py")
