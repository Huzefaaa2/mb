"""
Feedback Survey Database Module
Handles creation and management of feedback survey tables
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"


def init_feedback_tables():
    """Initialize all feedback survey tables"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Employer Feedback Survey (for employers who interviewed youths)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employer_interview_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_email TEXT NOT NULL,
            employer_name TEXT,
            company_name TEXT,
            student_id TEXT,
            student_name TEXT,
            position_applied TEXT,
            interview_date TIMESTAMP,
            
            -- Interview Experience (1-5 scale)
            technical_skills_rating INTEGER,
            communication_rating INTEGER,
            problem_solving_rating INTEGER,
            cultural_fit_rating INTEGER,
            overall_impression_rating INTEGER,
            
            -- Feedback
            strengths TEXT,
            areas_for_improvement TEXT,
            would_hire_again TEXT,
            feedback_comments TEXT,
            
            -- Meta
            survey_completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            survey_url TEXT
        )
    ''')
    
    # Employer Placement Feedback (for companies where students are placed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employer_placement_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_email TEXT NOT NULL,
            employer_name TEXT,
            company_name TEXT,
            student_id TEXT,
            student_name TEXT,
            position_title TEXT,
            placement_date TIMESTAMP,
            feedback_date TIMESTAMP,
            
            -- Performance (1-5 scale)
            job_performance_rating INTEGER,
            teamwork_rating INTEGER,
            reliability_rating INTEGER,
            learning_ability_rating INTEGER,
            professional_conduct_rating INTEGER,
            
            -- Outcomes
            retention_likelihood TEXT,
            promotion_potential TEXT,
            
            -- Feedback
            what_went_well TEXT,
            challenges_faced TEXT,
            recommendations TEXT,
            overall_feedback TEXT,
            
            -- Meta
            survey_completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            survey_url TEXT
        )
    ''')
    
    # Youth Post-Placement Survey (for students after placement)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS youth_placement_survey (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            student_id TEXT,
            student_name TEXT,
            email TEXT,
            company_name TEXT,
            position_title TEXT,
            placement_date TIMESTAMP,
            
            -- Job Experience (1-5 scale)
            job_satisfaction_rating INTEGER,
            role_clarity_rating INTEGER,
            work_environment_rating INTEGER,
            manager_support_rating INTEGER,
            growth_opportunity_rating INTEGER,
            
            -- Career Development
            skill_development TEXT,
            achievements TEXT,
            
            -- Support from MagicBus
            magicbus_support_rating INTEGER,
            additional_support_needed TEXT,
            
            -- Feedback
            what_went_well TEXT,
            challenges_faced TEXT,
            suggestions_for_improvement TEXT,
            would_recommend TEXT,
            overall_feedback TEXT,
            
            -- Meta
            survey_completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            survey_url TEXT,
            FOREIGN KEY (user_id) REFERENCES mb_users(user_id)
        )
    ''')
    
    # Survey Distribution Tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_distribution (
            distribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_type TEXT,
            recipient_email TEXT,
            recipient_type TEXT,
            recipient_id TEXT,
            survey_url TEXT,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            opened_date TIMESTAMP,
            completed_date TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Feedback Analytics Cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_analytics_cache (
            cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_value REAL,
            metric_category TEXT,
            data_period TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Feedback tables initialized successfully")


def submit_employer_interview_feedback(feedback_data):
    """Submit employer interview feedback"""
    try:
        init_feedback_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO employer_interview_feedback (
                employer_email, employer_name, company_name, student_id, student_name,
                position_applied, interview_date, technical_skills_rating, communication_rating,
                problem_solving_rating, cultural_fit_rating, overall_impression_rating,
                strengths, areas_for_improvement, would_hire_again, feedback_comments
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data.get('employer_email'),
            feedback_data.get('employer_name'),
            feedback_data.get('company_name'),
            feedback_data.get('student_id'),
            feedback_data.get('student_name'),
            feedback_data.get('position_applied'),
            feedback_data.get('interview_date'),
            feedback_data.get('technical_skills_rating'),
            feedback_data.get('communication_rating'),
            feedback_data.get('problem_solving_rating'),
            feedback_data.get('cultural_fit_rating'),
            feedback_data.get('overall_impression_rating'),
            feedback_data.get('strengths'),
            feedback_data.get('areas_for_improvement'),
            feedback_data.get('would_hire_again'),
            feedback_data.get('feedback_comments')
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Employer interview feedback submitted for {feedback_data.get('student_id')}")
        return True
    except Exception as e:
        logger.error(f"Error submitting employer interview feedback: {e}")
        return False


def submit_employer_placement_feedback(feedback_data):
    """Submit employer placement feedback"""
    try:
        init_feedback_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO employer_placement_feedback (
                employer_email, employer_name, company_name, student_id, student_name,
                position_title, placement_date, feedback_date, job_performance_rating,
                teamwork_rating, reliability_rating, learning_ability_rating,
                professional_conduct_rating, retention_likelihood, promotion_potential,
                what_went_well, challenges_faced, recommendations, overall_feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data.get('employer_email'),
            feedback_data.get('employer_name'),
            feedback_data.get('company_name'),
            feedback_data.get('student_id'),
            feedback_data.get('student_name'),
            feedback_data.get('position_title'),
            feedback_data.get('placement_date'),
            feedback_data.get('feedback_date'),
            feedback_data.get('job_performance_rating'),
            feedback_data.get('teamwork_rating'),
            feedback_data.get('reliability_rating'),
            feedback_data.get('learning_ability_rating'),
            feedback_data.get('professional_conduct_rating'),
            feedback_data.get('retention_likelihood'),
            feedback_data.get('promotion_potential'),
            feedback_data.get('what_went_well'),
            feedback_data.get('challenges_faced'),
            feedback_data.get('recommendations'),
            feedback_data.get('overall_feedback')
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Employer placement feedback submitted for {feedback_data.get('student_id')}")
        return True
    except Exception as e:
        logger.error(f"Error submitting employer placement feedback: {e}")
        return False


def submit_youth_placement_feedback(feedback_data):
    """Submit youth post-placement feedback"""
    try:
        init_feedback_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO youth_placement_survey (
                user_id, student_id, student_name, email, company_name, position_title,
                placement_date, job_satisfaction_rating, role_clarity_rating,
                work_environment_rating, manager_support_rating, growth_opportunity_rating,
                skill_development, achievements, magicbus_support_rating,
                additional_support_needed, what_went_well, challenges_faced,
                suggestions_for_improvement, would_recommend, overall_feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data.get('user_id'),
            feedback_data.get('student_id'),
            feedback_data.get('student_name'),
            feedback_data.get('email'),
            feedback_data.get('company_name'),
            feedback_data.get('position_title'),
            feedback_data.get('placement_date'),
            feedback_data.get('job_satisfaction_rating'),
            feedback_data.get('role_clarity_rating'),
            feedback_data.get('work_environment_rating'),
            feedback_data.get('manager_support_rating'),
            feedback_data.get('growth_opportunity_rating'),
            feedback_data.get('skill_development'),
            feedback_data.get('achievements'),
            feedback_data.get('magicbus_support_rating'),
            feedback_data.get('additional_support_needed'),
            feedback_data.get('what_went_well'),
            feedback_data.get('challenges_faced'),
            feedback_data.get('suggestions_for_improvement'),
            feedback_data.get('would_recommend'),
            feedback_data.get('overall_feedback')
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Youth placement feedback submitted for {feedback_data.get('student_id')}")
        return True
    except Exception as e:
        logger.error(f"Error submitting youth placement feedback: {e}")
        return False


def get_feedback_analytics():
    """Get analytics from all feedback surveys"""
    try:
        init_feedback_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        analytics = {}
        
        # Employer Interview Feedback Average Ratings
        cursor.execute('''
            SELECT 
                AVG(technical_skills_rating) as avg_technical,
                AVG(communication_rating) as avg_communication,
                AVG(problem_solving_rating) as avg_problem_solving,
                AVG(cultural_fit_rating) as avg_cultural_fit,
                AVG(overall_impression_rating) as avg_overall,
                COUNT(*) as total_interviews
            FROM employer_interview_feedback
        ''')
        
        interview_data = cursor.fetchone()
        if interview_data:
            analytics['employer_interview'] = {
                'technical_skills': interview_data[0] or 0,
                'communication': interview_data[1] or 0,
                'problem_solving': interview_data[2] or 0,
                'cultural_fit': interview_data[3] or 0,
                'overall_impression': interview_data[4] or 0,
                'total_feedbacks': interview_data[5] or 0
            }
        
        # Employer Placement Feedback Average Ratings
        cursor.execute('''
            SELECT 
                AVG(job_performance_rating) as avg_performance,
                AVG(teamwork_rating) as avg_teamwork,
                AVG(reliability_rating) as avg_reliability,
                AVG(learning_ability_rating) as avg_learning,
                AVG(professional_conduct_rating) as avg_conduct,
                COUNT(*) as total_placements
            FROM employer_placement_feedback
        ''')
        
        placement_data = cursor.fetchone()
        if placement_data:
            analytics['employer_placement'] = {
                'job_performance': placement_data[0] or 0,
                'teamwork': placement_data[1] or 0,
                'reliability': placement_data[2] or 0,
                'learning_ability': placement_data[3] or 0,
                'professional_conduct': placement_data[4] or 0,
                'total_feedbacks': placement_data[5] or 0
            }
        
        # Youth Placement Feedback Average Ratings
        cursor.execute('''
            SELECT 
                AVG(job_satisfaction_rating) as avg_satisfaction,
                AVG(role_clarity_rating) as avg_clarity,
                AVG(work_environment_rating) as avg_environment,
                AVG(manager_support_rating) as avg_manager,
                AVG(growth_opportunity_rating) as avg_growth,
                AVG(magicbus_support_rating) as avg_magicbus,
                COUNT(*) as total_feedbacks
            FROM youth_placement_survey
        ''')
        
        youth_data = cursor.fetchone()
        if youth_data:
            analytics['youth_placement'] = {
                'job_satisfaction': youth_data[0] or 0,
                'role_clarity': youth_data[1] or 0,
                'work_environment': youth_data[2] or 0,
                'manager_support': youth_data[3] or 0,
                'growth_opportunity': youth_data[4] or 0,
                'magicbus_support': youth_data[5] or 0,
                'total_feedbacks': youth_data[6] or 0
            }
        
        conn.close()
        return analytics
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {e}")
        return {}


def get_all_feedback_surveys():
    """Get all feedback surveys for admin dashboard"""
    try:
        init_feedback_tables()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get employer interview feedbacks
        cursor.execute('SELECT * FROM employer_interview_feedback ORDER BY survey_completed_date DESC')
        interview_feedbacks = cursor.fetchall()
        
        # Get employer placement feedbacks
        cursor.execute('SELECT * FROM employer_placement_feedback ORDER BY survey_completed_date DESC')
        placement_feedbacks = cursor.fetchall()
        
        # Get youth feedbacks
        cursor.execute('SELECT * FROM youth_placement_survey ORDER BY survey_completed_date DESC')
        youth_feedbacks = cursor.fetchall()
        
        conn.close()
        
        return {
            'interview': interview_feedbacks,
            'placement': placement_feedbacks,
            'youth': youth_feedbacks
        }
    except Exception as e:
        logger.error(f"Error getting feedback surveys: {e}")
        return {'interview': [], 'placement': [], 'youth': []}
