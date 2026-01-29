"""
Magic Bus Compass 360 - Confirmation Page after Registration
Shows registration details and downloadable ID card
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Registration Confirmed", page_icon="✅", layout="wide")

st.title("✅ Registration Confirmed!")

if "registration_data" not in st.session_state:
    st.error("No registration data found. Please complete registration first.")
    if st.button("← Back to Registration"):
        st.switch_page("pages/1_register.py")
else:
    reg_data = st.session_state.registration_data
    student_data = reg_data["student_data"]
    
    # Registration Details
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("Your registration is complete!")
        st.write(f"**Name:** {student_data['first_name']} {student_data['last_name']}")
        st.write(f"**Email:** {student_data['email']}")
        st.write(f"**Phone:** {student_data['phone']}")
        st.write(f"**Institution:** {student_data['institution']}")
    
    with col2:
        st.info("📌 Save your credentials:")
        st.code(f"Login ID: {reg_data['login_id']}\nPassword: {reg_data['password_hint']}")
        st.write(f"**Student ID:** `{reg_data['student_id']}`")
    
    st.markdown("---")
    
    # ID Card Section
    st.markdown("### 📛 Your Student ID Card")
    
    tab1, tab2 = st.tabs(["📸 Preview", "📥 Download"])
    
    with tab1:
        if reg_data.get('id_card_png'):
            st.image(reg_data['id_card_png'], caption="Your Student ID Card")
        else:
            st.warning("ID card could not be generated")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if reg_data.get('id_card_png'):
                st.download_button(
                    label="📥 Download as PNG",
                    data=reg_data['id_card_png'],
                    file_name=f"{reg_data['student_id']}_ID_Card.png",
                    mime="image/png",
                    width="stretch"
                )
        
        with col2:
            if reg_data.get('id_card_pdf'):
                st.download_button(
                    label="📥 Download as PDF",
                    data=reg_data['id_card_pdf'],
                    file_name=f"{reg_data['student_id']}_ID_Card.pdf",
                    mime="application/pdf",
                    width="stretch"
                )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Start Career Fit Survey", width="stretch"):
            st.switch_page("pages/2_youth_dashboard.py")
    
    with col2:
        if st.button("🔐 Go to Login", width="stretch"):
            st.switch_page("pages/0_login.py")
