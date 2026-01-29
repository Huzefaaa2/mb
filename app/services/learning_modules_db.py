"""
Learning Modules Database Service
Manages storage and retrieval of learning modules and their progress
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

def init_learning_modules_table():
    """Initialize learning modules table"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_modules (
            module_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            module_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            skills TEXT,
            prerequisites TEXT,
            difficulty_level TEXT,
            status TEXT DEFAULT 'not_started',
            progress INTEGER DEFAULT 0,
            started_date TIMESTAMP,
            completed_date TIMESTAMP,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES mb_users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_learning_modules(user_id, student_id, modules):
    """
    Save generated learning modules for a student
    
    Args:
        user_id: User ID
        student_id: Student ID
        modules: List of module dictionaries
    
    Returns:
        Boolean indicating success
    """
    try:
        init_learning_modules_table()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        for module in modules:
            cursor.execute('''
                INSERT INTO learning_modules 
                (user_id, student_id, module_id, title, description, duration, 
                 skills, prerequisites, difficulty_level, status, progress)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                student_id,
                module.get("module_id"),
                module.get("title"),
                module.get("description"),
                module.get("duration"),
                json.dumps(module.get("skills", [])),
                module.get("prerequisites"),
                module.get("difficulty_level"),
                module.get("status", "not_started"),
                module.get("progress", 0)
            ))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error saving learning modules: {e}")
        return False

def get_learning_modules(user_id):
    """Get all learning modules for a user"""
    try:
        init_learning_modules_table()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT module_assignment_id, module_id, title, description, duration, 
                   skills, prerequisites, difficulty_level, status, progress, 
                   started_date, completed_date, assigned_date
            FROM learning_modules
            WHERE user_id = ?
            ORDER BY assigned_date ASC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        modules = []
        for row in rows:
            modules.append({
                "module_assignment_id": row[0],
                "module_id": row[1],
                "title": row[2],
                "description": row[3],
                "duration": row[4],
                "skills": json.loads(row[5]) if row[5] else [],
                "prerequisites": row[6],
                "difficulty_level": row[7],
                "status": row[8],
                "progress": row[9],
                "started_date": row[10],
                "completed_date": row[11],
                "assigned_date": row[12]
            })
        
        return modules
    
    except Exception as e:
        logger.error(f"Error retrieving learning modules: {e}")
        return []

def update_module_status(module_assignment_id, status, progress=None):
    """
    Update module status and progress
    
    Args:
        module_assignment_id: ID of the module assignment
        status: New status ('not_started', 'in_progress', 'completed')
        progress: Progress percentage (0-100)
    
    Returns:
        Boolean indicating success
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        update_fields = ["status = ?"]
        params = [status]
        
        if progress is not None:
            update_fields.append("progress = ?")
            params.append(progress)
        
        if status == "in_progress":
            update_fields.append("started_date = CASE WHEN started_date IS NULL THEN ? ELSE started_date END")
            params.append(datetime.now().isoformat())
        elif status == "completed":
            update_fields.append("completed_date = ?")
            update_fields.append("progress = 100")
            params.append(datetime.now().isoformat())
        
        params.append(module_assignment_id)
        
        query = f"UPDATE learning_modules SET {', '.join(update_fields)} WHERE module_assignment_id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error updating module status: {e}")
        return False

def get_module_statistics(user_id):
    """Get module completion statistics for a user"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                ROUND(AVG(progress), 1) as avg_progress
            FROM learning_modules
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_modules": row[0] or 0,
            "completed_modules": row[1] or 0,
            "in_progress_modules": row[2] or 0,
            "average_progress": row[3] or 0
        }
    
    except Exception as e:
        logger.error(f"Error getting module statistics: {e}")
        return {
            "total_modules": 0,
            "completed_modules": 0,
            "in_progress_modules": 0,
            "average_progress": 0
        }
