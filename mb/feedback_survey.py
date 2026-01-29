"""
Feedback Survey Module
Manages employer feedback surveys, youth post-placement surveys, and analytics
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "mb_compass.db"


def init_feedback_tables():
    """Initialize feedback survey tables in database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Employer Feedback Survey Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employer_feedback_surveys (
                survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id VARCHAR(50),
                employer_name VARCHAR(255) NOT NULL,
                employer_email VARCHAR(255) NOT NULL,
                job_title VARCHAR(255),
                survey_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_date TIMESTAMP,
                completed_date TIMESTAMP,
                completion_status VARCHAR(20) DEFAULT 'pending',
                overall_performance FLOAT,
                technical_skills FLOAT,
                communication_skills FLOAT,
                teamwork FLOAT,
                work_ethic FLOAT,
                punctuality FLOAT,
                reliability FLOAT,
                problem_solving FLOAT,
                strengths TEXT,
                areas_for_improvement TEXT,
                would_rehire BOOLEAN,
                feedback_comments TEXT,
                recommendation_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Youth Post-Placement Feedback Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youth_feedback_surveys (
                survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id VARCHAR(50) NOT NULL,
                user_id INTEGER,
                placement_company VARCHAR(255),
                job_title VARCHAR(255),
                survey_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_date TIMESTAMP,
                completed_date TIMESTAMP,
                completion_status VARCHAR(20) DEFAULT 'pending',
                role_expectation_match FLOAT,
                work_environment_satisfaction FLOAT,
                team_collaboration_satisfaction FLOAT,
                career_growth_opportunity FLOAT,
                compensation_satisfaction FLOAT,
                overall_satisfaction FLOAT,
                what_went_well TEXT,
                what_could_improve TEXT,
                manager_support_rating FLOAT,
                skill_application_rating FLOAT,
                magicbus_preparation_rating FLOAT,
                would_recommend_magicbus BOOLEAN,
                suggestions_for_improvement TEXT,
                challenges_faced TEXT,
                additional_training_needed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Survey Template Versions (for tracking changes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_type VARCHAR(50) NOT NULL,
                template_name VARCHAR(255),
                questions_json TEXT,
                version INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT true,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Survey Distribution Log (for tracking email sends)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_distribution_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_type VARCHAR(50),
                recipient_email VARCHAR(255) NOT NULL,
                recipient_type VARCHAR(50),
                survey_id INTEGER,
                student_id VARCHAR(50),
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                opened BOOLEAN DEFAULT false,
                opened_date TIMESTAMP,
                completed BOOLEAN DEFAULT false,
                completion_date TIMESTAMP,
                survey_link VARCHAR(500)
            )
        ''')

        # Create indices for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employer_survey_student ON employer_feedback_surveys(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employer_survey_date ON employer_feedback_surveys(survey_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employer_survey_status ON employer_feedback_surveys(completion_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_youth_survey_student ON youth_feedback_surveys(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_youth_survey_date ON youth_feedback_surveys(survey_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_youth_survey_status ON youth_feedback_surveys(completion_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_distribution_email ON survey_distribution_logs(recipient_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_distribution_date ON survey_distribution_logs(sent_date)')

        conn.commit()
        conn.close()
        logger.info("✅ Feedback survey tables initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing feedback tables: {e}")
        return False


def submit_employer_feedback(
    student_id: str,
    employer_name: str,
    employer_email: str,
    job_title: str,
    overall_performance: float,
    technical_skills: float,
    communication_skills: float,
    teamwork: float,
    work_ethic: float,
    punctuality: float,
    reliability: float,
    problem_solving: float,
    strengths: str,
    areas_for_improvement: str,
    would_rehire: bool,
    feedback_comments: str,
    recommendation_score: float
) -> Tuple[bool, str]:
    """Submit employer feedback survey"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO employer_feedback_surveys (
                student_id, employer_name, employer_email, job_title,
                overall_performance, technical_skills, communication_skills,
                teamwork, work_ethic, punctuality, reliability, problem_solving,
                strengths, areas_for_improvement, would_rehire,
                feedback_comments, recommendation_score, completed_date, completion_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, employer_name, employer_email, job_title,
            overall_performance, technical_skills, communication_skills,
            teamwork, work_ethic, punctuality, reliability, problem_solving,
            strengths, areas_for_improvement, would_rehire,
            feedback_comments, recommendation_score, datetime.now(), 'completed'
        ))

        conn.commit()
        conn.close()
        logger.info(f"✅ Employer feedback submitted for {student_id}")
        return True, "✅ Feedback submitted successfully!"
    except Exception as e:
        logger.error(f"❌ Error submitting employer feedback: {e}")
        return False, f"❌ Error: {str(e)}"


def submit_youth_feedback(
    student_id: str,
    user_id: int,
    placement_company: str,
    job_title: str,
    role_expectation_match: float,
    work_environment_satisfaction: float,
    team_collaboration_satisfaction: float,
    career_growth_opportunity: float,
    compensation_satisfaction: float,
    overall_satisfaction: float,
    what_went_well: str,
    what_could_improve: str,
    manager_support_rating: float,
    skill_application_rating: float,
    magicbus_preparation_rating: float,
    would_recommend_magicbus: bool,
    suggestions_for_improvement: str,
    challenges_faced: str,
    additional_training_needed: str
) -> Tuple[bool, str]:
    """Submit youth post-placement feedback survey"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO youth_feedback_surveys (
                student_id, user_id, placement_company, job_title,
                role_expectation_match, work_environment_satisfaction,
                team_collaboration_satisfaction, career_growth_opportunity,
                compensation_satisfaction, overall_satisfaction,
                what_went_well, what_could_improve,
                manager_support_rating, skill_application_rating,
                magicbus_preparation_rating, would_recommend_magicbus,
                suggestions_for_improvement, challenges_faced,
                additional_training_needed, completed_date, completion_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, user_id, placement_company, job_title,
            role_expectation_match, work_environment_satisfaction,
            team_collaboration_satisfaction, career_growth_opportunity,
            compensation_satisfaction, overall_satisfaction,
            what_went_well, what_could_improve,
            manager_support_rating, skill_application_rating,
            magicbus_preparation_rating, would_recommend_magicbus,
            suggestions_for_improvement, challenges_faced,
            additional_training_needed, datetime.now(), 'completed'
        ))

        conn.commit()
        conn.close()
        logger.info(f"✅ Youth feedback submitted for {student_id}")
        return True, "✅ Your feedback has been recorded successfully!"
    except Exception as e:
        logger.error(f"❌ Error submitting youth feedback: {e}")
        return False, f"❌ Error: {str(e)}"


def create_employer_survey_entry(
    student_id: str,
    employer_name: str,
    employer_email: str,
    job_title: str
) -> Tuple[bool, str, int]:
    """Create pending employer survey entry for sending via email"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO employer_feedback_surveys (
                student_id, employer_name, employer_email, job_title,
                completion_status, sent_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, employer_name, employer_email, job_title, 'pending', datetime.now()))

        survey_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"✅ Employer survey created for {employer_email}")
        return True, f"✅ Survey sent to {employer_email}", survey_id
    except Exception as e:
        logger.error(f"❌ Error creating employer survey: {e}")
        return False, f"❌ Error: {str(e)}", -1


def create_youth_survey_entry(
    student_id: str,
    user_id: int,
    placement_company: str,
    job_title: str
) -> Tuple[bool, str]:
    """Create pending youth survey entry for sending via email"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO youth_feedback_surveys (
                student_id, user_id, placement_company, job_title,
                completion_status, sent_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, user_id, placement_company, job_title, 'pending', datetime.now()))

        survey_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"✅ Youth survey created for student {student_id}")
        return True, f"✅ Survey sent to student {student_id}", survey_id
    except Exception as e:
        logger.error(f"❌ Error creating youth survey: {e}")
        return False, f"❌ Error: {str(e)}", -1


def log_survey_distribution(
    survey_type: str,
    recipient_email: str,
    recipient_type: str,
    survey_id: int,
    student_id: str,
    survey_link: str
) -> bool:
    """Log survey distribution for tracking"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO survey_distribution_logs (
                survey_type, recipient_email, recipient_type,
                survey_id, student_id, sent_date, survey_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (survey_type, recipient_email, recipient_type, survey_id, student_id, datetime.now(), survey_link))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error logging distribution: {e}")
        return False


def get_employer_feedback_analytics() -> Dict:
    """Get analytics from employer feedback surveys"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Overall statistics
        cursor.execute('''
            SELECT
                COUNT(*) as total_surveys,
                SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN completion_status = 'pending' THEN 1 ELSE 0 END) as pending,
                AVG(overall_performance) as avg_performance,
                AVG(technical_skills) as avg_technical,
                AVG(communication_skills) as avg_communication,
                AVG(teamwork) as avg_teamwork,
                AVG(work_ethic) as avg_work_ethic,
                AVG(punctuality) as avg_punctuality,
                AVG(reliability) as avg_reliability,
                AVG(problem_solving) as avg_problem_solving,
                SUM(CASE WHEN would_rehire = 1 THEN 1 ELSE 0 END) as rehire_count,
                AVG(recommendation_score) as avg_recommendation
            FROM employer_feedback_surveys
        ''')

        stats = cursor.fetchone()
        
        # Top strengths mentioned
        cursor.execute('''
            SELECT strengths FROM employer_feedback_surveys
            WHERE strengths IS NOT NULL AND completion_status = 'completed'
        ''')
        
        strengths_list = [row[0] for row in cursor.fetchall()]
        
        # Areas for improvement mentioned
        cursor.execute('''
            SELECT areas_for_improvement FROM employer_feedback_surveys
            WHERE areas_for_improvement IS NOT NULL AND completion_status = 'completed'
        ''')
        
        improvements_list = [row[0] for row in cursor.fetchall()]

        # By student performance
        cursor.execute('''
            SELECT student_id, COUNT(*) as feedback_count,
                   AVG(overall_performance) as avg_perf,
                   SUM(CASE WHEN would_rehire = 1 THEN 1 ELSE 0 END) as rehire_count
            FROM employer_feedback_surveys
            WHERE completion_status = 'completed'
            GROUP BY student_id
            ORDER BY avg_perf DESC
        ''')
        
        student_performance = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_surveys': stats[0] or 0,
            'completed_surveys': stats[1] or 0,
            'pending_surveys': stats[2] or 0,
            'avg_overall_performance': round(stats[3] or 0, 2),
            'avg_technical_skills': round(stats[4] or 0, 2),
            'avg_communication_skills': round(stats[5] or 0, 2),
            'avg_teamwork': round(stats[6] or 0, 2),
            'avg_work_ethic': round(stats[7] or 0, 2),
            'avg_punctuality': round(stats[8] or 0, 2),
            'avg_reliability': round(stats[9] or 0, 2),
            'avg_problem_solving': round(stats[10] or 0, 2),
            'rehire_count': stats[11] or 0,
            'avg_recommendation': round(stats[12] or 0, 2),
            'top_strengths': strengths_list[:10],
            'areas_for_improvement': improvements_list[:10],
            'student_performance': student_performance
        }
    except Exception as e:
        logger.error(f"❌ Error getting employer analytics: {e}")
        return {}


def get_youth_feedback_analytics() -> Dict:
    """Get analytics from youth post-placement feedback surveys"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Overall statistics
        cursor.execute('''
            SELECT
                COUNT(*) as total_surveys,
                SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN completion_status = 'pending' THEN 1 ELSE 0 END) as pending,
                AVG(overall_satisfaction) as avg_satisfaction,
                AVG(role_expectation_match) as avg_role_match,
                AVG(work_environment_satisfaction) as avg_work_env,
                AVG(team_collaboration_satisfaction) as avg_team_collab,
                AVG(career_growth_opportunity) as avg_career_growth,
                AVG(compensation_satisfaction) as avg_compensation,
                AVG(magicbus_preparation_rating) as avg_magicbus_prep,
                SUM(CASE WHEN would_recommend_magicbus = 1 THEN 1 ELSE 0 END) as recommend_count,
                AVG(manager_support_rating) as avg_manager_support,
                AVG(skill_application_rating) as avg_skill_application
            FROM youth_feedback_surveys
        ''')

        stats = cursor.fetchone()
        
        # What went well
        cursor.execute('''
            SELECT what_went_well FROM youth_feedback_surveys
            WHERE what_went_well IS NOT NULL AND completion_status = 'completed'
        ''')
        
        went_well_list = [row[0] for row in cursor.fetchall()]
        
        # What could improve
        cursor.execute('''
            SELECT what_could_improve FROM youth_feedback_surveys
            WHERE what_could_improve IS NOT NULL AND completion_status = 'completed'
        ''')
        
        improve_list = [row[0] for row in cursor.fetchall()]

        # Challenges faced
        cursor.execute('''
            SELECT challenges_faced FROM youth_feedback_surveys
            WHERE challenges_faced IS NOT NULL AND completion_status = 'completed'
        ''')
        
        challenges_list = [row[0] for row in cursor.fetchall()]

        # Training needs
        cursor.execute('''
            SELECT additional_training_needed FROM youth_feedback_surveys
            WHERE additional_training_needed IS NOT NULL AND completion_status = 'completed'
        ''')
        
        training_needs = [row[0] for row in cursor.fetchall()]

        # By student satisfaction
        cursor.execute('''
            SELECT student_id, COUNT(*) as feedback_count,
                   AVG(overall_satisfaction) as avg_satisfaction,
                   AVG(magicbus_preparation_rating) as magicbus_prep
            FROM youth_feedback_surveys
            WHERE completion_status = 'completed'
            GROUP BY student_id
            ORDER BY avg_satisfaction DESC
        ''')
        
        student_satisfaction = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_surveys': stats[0] or 0,
            'completed_surveys': stats[1] or 0,
            'pending_surveys': stats[2] or 0,
            'avg_satisfaction': round(stats[3] or 0, 2),
            'avg_role_match': round(stats[4] or 0, 2),
            'avg_work_environment': round(stats[5] or 0, 2),
            'avg_team_collaboration': round(stats[6] or 0, 2),
            'avg_career_growth': round(stats[7] or 0, 2),
            'avg_compensation': round(stats[8] or 0, 2),
            'avg_magicbus_prep': round(stats[9] or 0, 2),
            'recommend_count': stats[10] or 0,
            'avg_manager_support': round(stats[11] or 0, 2),
            'avg_skill_application': round(stats[12] or 0, 2),
            'what_went_well': went_well_list[:10],
            'areas_to_improve': improve_list[:10],
            'challenges_faced': challenges_list[:10],
            'training_needs': training_needs[:10],
            'student_satisfaction': student_satisfaction
        }
    except Exception as e:
        logger.error(f"❌ Error getting youth analytics: {e}")
        return {}


def get_pending_surveys() -> Dict:
    """Get count of pending surveys to complete"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM employer_feedback_surveys WHERE completion_status = "pending"')
        employer_pending = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM youth_feedback_surveys WHERE completion_status = "pending"')
        youth_pending = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM survey_distribution_logs WHERE completed = 0')
        distribution_pending = cursor.fetchone()[0]

        conn.close()

        return {
            'employer_pending': employer_pending,
            'youth_pending': youth_pending,
            'distribution_pending': distribution_pending
        }
    except Exception as e:
        logger.error(f"❌ Error getting pending surveys: {e}")
        return {'employer_pending': 0, 'youth_pending': 0, 'distribution_pending': 0}


def get_survey_distribution_status() -> pd.DataFrame:
    """Get status of all survey distributions"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        
        query = '''
            SELECT log_id, survey_type, recipient_email, recipient_type,
                   sent_date, opened, completed, student_id
            FROM survey_distribution_logs
            ORDER BY sent_date DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    except Exception as e:
        logger.error(f"❌ Error getting distribution status: {e}")
        return pd.DataFrame()


def get_employer_survey_details(survey_id: int) -> Optional[Dict]:
    """Get details of a specific employer survey"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM employer_feedback_surveys WHERE survey_id = ?
        ''', (survey_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        logger.error(f"❌ Error getting employer survey details: {e}")
        return None


def get_youth_survey_details(survey_id: int) -> Optional[Dict]:
    """Get details of a specific youth survey"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM youth_feedback_surveys WHERE survey_id = ?
        ''', (survey_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        logger.error(f"❌ Error getting youth survey details: {e}")
        return None
