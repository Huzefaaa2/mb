"""
Magic Bus Compass 360 - Login Page
"""

import streamlit as st
import psycopg2
import hashlib
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Login | Magic Bus Compass", page_icon="🔐")

st.title("🔐 Login to Magic Bus Compass 360")

def hash_password(password):
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(login_id, password):
    """Authenticate user against database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=os.getenv("POSTGRES_DB", "mb_compass"),
            user=os.getenv("POSTGRES_USER", "mb_user"),
            password=os.getenv("POSTGRES_PASSWORD", "")
        )
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, student_id, role FROM mb_users WHERE login_id = %s",
            (login_id,)
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result[0], result[1], result[2]
        return None
    
    except Exception as e:
        logger.error(f"Database error: {e}")
        st.error(f"Database connection error: {e}")
        return None

with st.form("login_form"):
    login_id = st.text_input("Login ID", placeholder="mb_abc1234")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    
    submitted = st.form_submit_button("Login", use_container_width=True)
    
    if submitted:
        if not login_id or not password:
            st.error("❌ Please enter login ID and password")
        else:
            result = authenticate_user(login_id, password)
            
            if result:
                user_id, student_id, role = result
                st.session_state.user_id = user_id
                st.session_state.student_id = student_id
                st.session_state.user_role = role
                
                st.success("✅ Login successful!")
                st.switch_page("pages/2_youth_dashboard.py")
            else:
                st.error("❌ Invalid login ID or password")

st.markdown("---")
st.markdown("**Don't have an account?**")

if st.button("📝 Register Now", use_container_width=True):
    st.switch_page("pages/1_register.py")
