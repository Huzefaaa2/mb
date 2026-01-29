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


def predict_churn_risk(student_id, days_ahead=7):
    """
    Predict churn risk for a student over next N days
    Returns risk score 0-100 and intervention recommendations
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get user_id from student_id
        cursor.execute("SELECT user_id FROM mb_users WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        if not row:
            return {"error": "Student not found"}
        user_id = row[0]
        
        # Get recent activity (last 7 days)
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT module_id) as recent_modules,
                MAX(updated_at) as last_activity,
                AVG(progress) as avg_progress,
                COUNT(*) as total_interactions
            FROM learning_modules
            WHERE user_id = ? AND datetime(updated_at) > datetime('now', '-7 days')
        """, (user_id,))
        
        activity_row = cursor.fetchone()
        recent_modules = activity_row[0] or 0
        last_activity = activity_row[1]
        avg_progress = activity_row[2] or 0
        total_interactions = activity_row[3] or 0
        
        # Get dropout risk
        cursor.execute("""
            SELECT risk_score FROM student_dropout_risk WHERE student_id = ?
        """, (student_id,))
        
        dropout_row = cursor.fetchone()
        dropout_risk_score = (dropout_row[0] or 5) if dropout_row else 5
        
        # Calculate churn risk
        # Factors: recent activity (40%), dropout risk (40%), interaction consistency (20%)
        activity_score = min(100, recent_modules * 20)  # 0-5 modules = 0-100
        dropout_factor = (dropout_risk_score / 9) * 100  # Convert 1-9 to 0-100
        consistency_score = min(100, total_interactions * 15)  # 0-6+ interactions = 0-100
        
        churn_risk = (activity_score * 0.15) + (dropout_factor * 0.55) + (consistency_score * 0.30)
        churn_risk = max(0, min(100, churn_risk))
        
        # Determine risk level and interventions
        if churn_risk >= 75:
            risk_level = "Critical"
            interventions = [
                "🚨 Send urgent engagement push notification",
                "📞 Schedule intervention call with mentor",
                "🎁 Offer bonus badge or challenge to re-engage",
                "💬 Send personalized message from peer mentor"
            ]
        elif churn_risk >= 60:
            risk_level = "High"
            interventions = [
                "⚠️ Send reminder notification",
                "🎯 Suggest milestone-based goal setting",
                "👥 Connect with peer mentor for support",
                "📊 Share progress visualization"
            ]
        elif churn_risk >= 40:
            risk_level = "Medium"
            interventions = [
                "💡 Suggest new learning module",
                "🌟 Highlight earned badges",
                "📈 Share learning path progress",
                "🤝 Encourage peer interaction"
            ]
        else:
            risk_level = "Low"
            interventions = [
                "✨ Celebrate engagement streak",
                "🎓 Suggest advanced modules",
                "🏆 Recognize as role model"
            ]
        
        conn.close()
        
        return {
            "student_id": student_id,
            "churn_risk_score": round(churn_risk, 2),
            "risk_level": risk_level,
            "prediction_window_days": days_ahead,
            "risk_factors": {
                "recent_activity_score": round(activity_score, 2),
                "dropout_risk_factor": round(dropout_factor, 2),
                "interaction_consistency": round(consistency_score, 2)
            },
            "last_activity": last_activity,
            "recommended_interventions": interventions,
            "predicted_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error predicting churn risk: {e}")
        return {"error": str(e)}


def trigger_churn_intervention(student_id, intervention_type="auto"):
    """
    Trigger intervention for at-risk student
    intervention_type: "auto" (system recommended), "urgent", "reminder", "motivational"
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Create intervention tracking table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS churn_interventions (
                intervention_id INTEGER PRIMARY KEY,
                student_id VARCHAR(50),
                intervention_type VARCHAR(50),
                triggered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'pending',
                response_date TIMESTAMP,
                effectiveness_score INTEGER
            )
        """)
        
        # Get churn risk
        churn_data = predict_churn_risk(student_id)
        
        if "error" in churn_data:
            return churn_data
        
        # Map intervention types
        intervention_messages = {
            "urgent": "🚨 Don't give up! Your mentor believes in you. Let's get back on track!",
            "reminder": "💭 Missing you! Let's continue your learning journey. What's your next step?",
            "motivational": "🌟 You're doing great! One more module completed and you'll earn a new badge!",
            "mentor": "👥 Your peer mentor wants to check in and help you succeed!",
            "reward": "🎁 You're close to unlocking a new achievement. Just a little more!"
        }
        
        # Determine message based on risk level if auto
        if intervention_type == "auto":
            risk_level = churn_data.get("risk_level", "Medium")
            if risk_level == "Critical":
                intervention_type = "urgent"
            elif risk_level == "High":
                intervention_type = "mentor"
            elif risk_level == "Medium":
                intervention_type = "motivational"
            else:
                intervention_type = "reward"
        
        message = intervention_messages.get(intervention_type, "Keep up the great work!")
        
        # Log intervention
        cursor.execute("""
            INSERT INTO churn_interventions (student_id, intervention_type, status)
            VALUES (?, ?, 'triggered')
        """, (student_id, intervention_type))
        
        conn.commit()
        conn.close()
        
        return {
            "student_id": student_id,
            "intervention_type": intervention_type,
            "message": message,
            "churn_risk": churn_data.get("churn_risk_score"),
            "risk_level": churn_data.get("risk_level"),
            "status": "triggered",
            "triggered_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering intervention: {e}")
        return {"error": str(e)}


def calculate_retention_impact(start_date=None, end_date=None):
    """
    Calculate retention impact over time
    Track progress toward 65%→85% retention target
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get target and current retention
        cursor.execute("""
            SELECT 
                COUNT(*) as total_students,
                COUNT(DISTINCT CASE WHEN dropout_risk_level != 'HIGH' THEN student_id END) as retained_students
            FROM student_dropout_risk
        """)
        
        row = cursor.fetchone()
        total_students = row[0] or 1
        retained_students = row[1] or 0
        current_retention_rate = (retained_students / total_students * 100) if total_students > 0 else 0
        
        # Get intervention effectiveness
        cursor.execute("""
            SELECT 
                COUNT(*) as total_interventions,
                SUM(CASE WHEN status = 'successful' THEN 1 ELSE 0 END) as successful_interventions
            FROM churn_interventions
            WHERE triggered_date > datetime('now', '-30 days')
        """)
        
        interv_row = cursor.fetchone()
        total_interventions = interv_row[0] or 0
        successful_interventions = interv_row[1] or 0
        intervention_success_rate = (successful_interventions / total_interventions * 100) if total_interventions > 0 else 0
        
        # Get badge earning rate
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as badge_earners,
                COUNT(*) as total_badges_earned
            FROM user_badges
            WHERE earned_date > datetime('now', '-30 days')
        """)
        
        badge_row = cursor.fetchone()
        badge_earners = badge_row[0] or 0
        total_badges = badge_row[1] or 0
        
        conn.close()
        
        # Calculate trajectory
        baseline_retention = 65.0  # Starting point
        target_retention = 85.0    # Goal
        progress_pct = ((current_retention_rate - baseline_retention) / (target_retention - baseline_retention)) * 100 if target_retention > baseline_retention else 0
        progress_pct = max(0, min(100, progress_pct))
        
        return {
            "current_retention_rate": round(current_retention_rate, 2),
            "baseline_retention": baseline_retention,
            "target_retention": target_retention,
            "progress_toward_target_pct": round(progress_pct, 2),
            "total_students": total_students,
            "retained_students": retained_students,
            "at_risk_students": total_students - retained_students,
            "intervention_metrics": {
                "total_interventions_30d": total_interventions,
                "successful_interventions": successful_interventions,
                "success_rate_pct": round(intervention_success_rate, 2)
            },
            "gamification_metrics": {
                "badge_earners_30d": badge_earners,
                "total_badges_earned_30d": total_badges,
                "avg_badges_per_earner": round(total_badges / max(1, badge_earners), 2)
            },
            "recommendations": [
                f"Current retention: {current_retention_rate:.1f}% (Need {target_retention - current_retention_rate:.1f}% more)" if current_retention_rate < target_retention else "✅ Target retention achieved!",
                f"Intervention effectiveness: {intervention_success_rate:.0f}%" if total_interventions > 0 else "Deploy interventions to increase retention",
                f"Engagement momentum: {badge_earners} students earning badges in past 30 days"
            ],
            "calculated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating retention impact: {e}")
        return {"error": str(e)}

