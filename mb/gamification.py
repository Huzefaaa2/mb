"""
Gamification - Badges, Streaks, and Motivational Elements
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

def init_gamification_tables():
    """Initialize gamification tables"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # User achievements/badges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_name TEXT NOT NULL,
            badge_description TEXT,
            badge_icon TEXT,
            earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES mb_users(user_id),
            UNIQUE(user_id, badge_name)
        )
    ''')
    
    # Learning streaks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_streaks (
            streak_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES mb_users(user_id),
            UNIQUE(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()


def check_and_award_badges(user_id, student_id):
    """Check user progress and award badges"""
    try:
        init_gamification_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        badges_earned = []
        
        # Get user's module statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                AVG(progress) as avg_progress
            FROM learning_modules
            WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        total, completed, in_progress = stats[0] or 0, stats[1] or 0, stats[2] or 0
        
        # Badge criteria
        badge_criteria = [
            {
                "name": "First Step",
                "description": "Started your first learning module",
                "icon": "🎯",
                "condition": lambda: in_progress > 0 or completed > 0
            },
            {
                "name": "Module Completer",
                "description": "Completed your first learning module",
                "icon": "✅",
                "condition": lambda: completed >= 1
            },
            {
                "name": "Dedicated Learner",
                "description": "Completed 5 learning modules",
                "icon": "🌟",
                "condition": lambda: completed >= 5
            },
            {
                "name": "Knowledge Master",
                "description": "Completed 10 learning modules",
                "icon": "🏆",
                "condition": lambda: completed >= 10
            },
            {
                "name": "Multi-Tasker",
                "description": "Have 3 or more modules in progress",
                "icon": "⚡",
                "condition": lambda: in_progress >= 3
            },
            {
                "name": "Focused Learner",
                "description": "Completed all modules in a learning path",
                "icon": "🎓",
                "condition": lambda: total > 0 and completed == total
            }
        ]
        
        for badge in badge_criteria:
            if badge["condition"]():
                # Check if badge already earned
                cursor.execute(
                    "SELECT badge_id FROM user_badges WHERE user_id = ? AND badge_name = ?",
                    (user_id, badge["name"])
                )
                
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO user_badges (user_id, badge_name, badge_description, badge_icon)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, badge["name"], badge["description"], badge["icon"]))
                    badges_earned.append(badge)
        
        conn.commit()
        conn.close()
        
        return badges_earned
        
    except Exception as e:
        logger.error(f"Error awarding badges: {e}")
        return []


def get_user_badges(user_id):
    """Get all badges earned by user"""
    try:
        init_gamification_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT badge_name, badge_description, badge_icon, earned_date
            FROM user_badges
            WHERE user_id = ?
            ORDER BY earned_date DESC
        ''', (user_id,))
        
        badges = []
        for row in cursor.fetchall():
            badges.append({
                "name": row[0],
                "description": row[1],
                "icon": row[2],
                "earned_date": row[3]
            })
        
        conn.close()
        return badges
        
    except Exception as e:
        logger.error(f"Error retrieving badges: {e}")
        return []


def update_streak(user_id):
    """Update learning streak for user"""
    try:
        init_gamification_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        # Get current streak info
        cursor.execute(
            "SELECT current_streak, longest_streak, last_activity_date FROM learning_streaks WHERE user_id = ?",
            (user_id,)
        )
        
        result = cursor.fetchone()
        
        if result:
            current_streak, longest_streak, last_activity = result
            last_activity_date = datetime.fromisoformat(last_activity).date() if last_activity else None
            
            # Check if activity was today
            if last_activity_date == today:
                # Already counted today
                pass
            elif last_activity_date == today - timedelta(days=1):
                # Streak continues
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
            else:
                # Streak broken
                current_streak = 1
            
            cursor.execute('''
                UPDATE learning_streaks
                SET current_streak = ?, longest_streak = ?, last_activity_date = ?
                WHERE user_id = ?
            ''', (current_streak, longest_streak, datetime.now().isoformat(), user_id))
        else:
            # First time
            cursor.execute('''
                INSERT INTO learning_streaks (user_id, current_streak, longest_streak, last_activity_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 1, 1, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return get_user_streak(user_id)
        
    except Exception as e:
        logger.error(f"Error updating streak: {e}")
        return None


def get_user_streak(user_id):
    """Get user's current learning streak"""
    try:
        init_gamification_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT current_streak, longest_streak FROM learning_streaks WHERE user_id = ?",
            (user_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"current": result[0], "longest": result[1]}
        else:
            return {"current": 0, "longest": 0}
        
    except Exception as e:
        logger.error(f"Error getting streak: {e}")
        return {"current": 0, "longest": 0}


def get_motivational_message(completed_modules):
    """Get motivational message based on progress"""
    messages = {
        0: "🚀 Start your learning journey today!",
        1: "🌱 Great start! Keep the momentum going!",
        3: "💪 You're doing awesome! Keep it up!",
        5: "🌟 Amazing progress! You're a dedicated learner!",
        10: "🏆 Incredible! You're a learning champion!",
        15: "👑 You're unstoppable! Inspiring others!",
        20: "🎯 Master level achieved! Exceptional dedication!"
    }
    
    for threshold in sorted(messages.keys(), reverse=True):
        if completed_modules >= threshold:
            return messages[threshold]
    
    return "📚 Every step counts. Keep learning!"
