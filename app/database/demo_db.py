"""
Local Demo Database - For testing without Azure connection
Uses SQLite for local development and testing
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "demo.db"

def init_demo_db():
    """Initialize SQLite demo database"""
    db_path = DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            program_name TEXT,
            skills TEXT,
            experience TEXT,
            resume_url TEXT,
            qr_id_card BLOB,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            assessment_type TEXT,
            score REAL,
            answers TEXT,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Demo database initialized at {db_path}")

def get_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))

def verify_credentials(username, password):
    """Verify user credentials"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, full_name FROM users WHERE username = ? AND password = ?',
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        return user is not None, user
    except Exception as e:
        print(f"Error verifying credentials: {e}")
        return False, None

def create_user(username, password, email, full_name):
    """Create new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, email, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, password, email, full_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        print(f"✓ User created: {username} (ID: {user_id})")
        return True, user_id
    except sqlite3.IntegrityError:
        print(f"✗ User already exists: {username}")
        return False, None
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return False, None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, full_name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def save_registration(user_id, program_name, skills, experience):
    """Save registration data"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registrations (user_id, program_name, skills, experience, status)
            VALUES (?, ?, ?, ?, 'active')
        ''', (user_id, program_name, skills, experience))
        conn.commit()
        registration_id = cursor.lastrowid
        conn.close()
        print(f"✓ Registration saved (ID: {registration_id})")
        return True, registration_id
    except Exception as e:
        print(f"✗ Error saving registration: {e}")
        return False, None

def get_user_registration(user_id):
    """Get user registration"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM registrations WHERE user_id = ? LIMIT 1', (user_id,))
        registration = cursor.fetchone()
        conn.close()
        return registration
    except Exception as e:
        print(f"Error getting registration: {e}")
        return None

# Initialize on import
if not DB_PATH.exists():
    init_demo_db()
