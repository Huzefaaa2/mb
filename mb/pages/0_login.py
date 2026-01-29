"""
Magic Bus Compass 360 - Login Page
"""

import streamlit as st
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Login | Magic Bus Compass", page_icon="🔐")

st.title("🔐 Login to Magic Bus Compass 360")

# SQLite database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

def init_db():
    """Initialize SQLite database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mb_users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            student_id TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            email TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def authenticate_user(login_id, password):
    """Authenticate user against database"""
    try:
        init_db()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, student_id, role FROM mb_users WHERE login_id = ? AND password = ?",
            (login_id, password)
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
    
    submitted = st.form_submit_button("Login", width="stretch")
    
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

if st.button("📝 Register Now", width="stretch"):
    st.switch_page("pages/1_register.py")
