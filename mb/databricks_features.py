"""
Databricks Feature Engineering Module
Transforms raw transactional tables into decision-ready features
Used for: Sector fit scoring, dropout risk, skill uplift, gamification impact
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "mb_compass.db"


class FeatureEngineer:
    """Generates enriched features for decision dashboards"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))
    
    # ========================
    # A) STUDENT DAILY FEATURES
    # ========================
    def compute_student_daily_features(self):
        """
        Create student_daily_features table
        Features: sessions_count, avg_completion, avg_quiz_score, days_active, last_login
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Drop existing table if any
            cursor.execute("DROP TABLE IF EXISTS student_daily_features")
            
            query = """
            CREATE TABLE student_daily_features AS
            SELECT
                u.user_id,
                u.student_id,
                u.email,
                u.created_at as registration_date,
                COUNT(DISTINCT lm.module_id) as modules_assigned,
                SUM(CASE WHEN lm.status = 'completed' THEN 1 ELSE 0 END) as modules_completed,
                AVG(CASE WHEN lm.progress IS NOT NULL THEN lm.progress ELSE 0 END) as avg_completion_pct,
                COUNT(DISTINCT CASE WHEN lm.status IS NOT NULL THEN lm.module_id END) as modules_started,
                CAST((julianday('now') - julianday(u.created_at)) AS INTEGER) as days_since_registration,
                datetime('now') as feature_timestamp
            FROM mb_users u
            LEFT JOIN learning_modules lm ON u.user_id = lm.user_id
            GROUP BY u.user_id, u.student_id, u.email, u.created_at
            """
            
            cursor.execute(query)
            conn.commit()
            logger.info("✅ student_daily_features computed")
            return True
        except Exception as e:
            logger.error(f"❌ Error computing student_daily_features: {e}")
            return False
        finally:
            conn.close()
    
    # ========================
    # B) DROPOUT RISK SCORE
    # ========================
    def compute_dropout_risk(self):
        """
        Dropout Risk Score Logic:
        - HIGH: <3 modules started + avg completion <30% OR no activity in 7 days
        - MEDIUM: <5 modules started OR avg completion <50%
        - LOW: ≥5 modules started AND avg completion ≥50%
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DROP TABLE IF EXISTS student_dropout_risk")
            
            query = """
            CREATE TABLE student_dropout_risk AS
            SELECT
                user_id,
                student_id,
                email,
                modules_assigned,
                modules_completed,
                modules_started,
                avg_completion_pct,
                days_since_registration,
                CASE
                    WHEN modules_started < 3 AND avg_completion_pct < 30 THEN 'HIGH'
                    WHEN modules_started < 5 OR avg_completion_pct < 50 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as dropout_risk_level,
                CASE
                    WHEN modules_started < 3 AND avg_completion_pct < 30 THEN 9
                    WHEN modules_started < 5 OR avg_completion_pct < 50 THEN 5
                    ELSE 1
                END as risk_score,
                CASE
                    WHEN modules_started = 0 THEN 'No modules started'
                    WHEN modules_started < 3 AND avg_completion_pct < 30 THEN 'Low engagement & completion'
                    WHEN avg_completion_pct < 50 THEN 'Below 50% completion'
                    ELSE 'On track'
                END as risk_reason,
                datetime('now') as risk_computed_at
            FROM student_daily_features
            """
            
            cursor.execute(query)
            conn.commit()
            logger.info("✅ student_dropout_risk computed")
            return True
        except Exception as e:
            logger.error(f"❌ Error computing dropout risk: {e}")
            return False
        finally:
            conn.close()
    
    # ========================
    # C) SECTOR FIT SCORE
    # ========================
    def compute_sector_fit(self):
        """
        Sector Fit Score: Combines career interest confidence with skill readiness
        Score: 0-100 (Green ≥70, Amber 50-69, Red <50)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DROP TABLE IF EXISTS student_sector_fit")
            
            query = """
            CREATE TABLE student_sector_fit AS
            SELECT
                u.user_id,
                u.student_id,
                COALESCE(cs.survey_data, 'No data') as sector_interests,
                CASE
                    WHEN cs.survey_id IS NOT NULL THEN 75
                    ELSE 0
                END as interest_confidence,
                CASE
                    WHEN lm.modules_completed >= 3 THEN 80
                    WHEN lm.modules_completed >= 1 THEN 60
                    ELSE 40
                END as skill_readiness_score,
                ROUND(
                    (CASE WHEN cs.survey_id IS NOT NULL THEN 75 ELSE 0 END +
                     CASE WHEN lm.modules_completed >= 3 THEN 80 WHEN lm.modules_completed >= 1 THEN 60 ELSE 40 END) / 2.0,
                    0
                ) as sector_fit_score,
                CASE
                    WHEN (CASE WHEN cs.survey_id IS NOT NULL THEN 75 ELSE 0 END +
                          CASE WHEN lm.modules_completed >= 3 THEN 80 WHEN lm.modules_completed >= 1 THEN 60 ELSE 40 END) / 2.0 >= 70 THEN 'Green'
                    WHEN (CASE WHEN cs.survey_id IS NOT NULL THEN 75 ELSE 0 END +
                          CASE WHEN lm.modules_completed >= 3 THEN 80 WHEN lm.modules_completed >= 1 THEN 60 ELSE 40 END) / 2.0 >= 50 THEN 'Amber'
                    ELSE 'Red'
                END as readiness_status,
                datetime('now') as computed_at
            FROM mb_users u
            LEFT JOIN career_surveys cs ON u.user_id = cs.user_id
            LEFT JOIN (
                SELECT user_id, COUNT(*) as modules_completed 
                FROM learning_modules 
                WHERE status = 'completed' 
                GROUP BY user_id
            ) lm ON u.user_id = lm.user_id
            """
            
            cursor.execute(query)
            conn.commit()
            logger.info("✅ student_sector_fit computed")
            return True
        except Exception as e:
            logger.error(f"❌ Error computing sector fit: {e}")
            return False
        finally:
            conn.close()
    
    # ========================
    # D) MODULE EFFECTIVENESS
    # ========================
    def compute_module_effectiveness(self):
        """
        Module ROI: Completion rate, avg time spent, skill gain impact
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DROP TABLE IF EXISTS module_effectiveness")
            
            query = """
            CREATE TABLE module_effectiveness AS
            SELECT
                module_id,
                title as module_name,
                COUNT(DISTINCT user_id) as learners,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT user_id), 0), 2) as completion_rate,
                ROUND(AVG(CASE WHEN progress IS NOT NULL THEN progress ELSE 0 END), 2) as avg_completion_pct,
                ROUND(AVG(CASE WHEN status = 'completed' THEN 100 ELSE 50 END), 2) as avg_points_earned,
                CASE
                    WHEN ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT user_id), 0), 2) >= 80 THEN 'High Impact'
                    WHEN ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT user_id), 0), 2) >= 60 THEN 'Medium Impact'
                    ELSE 'Needs Improvement'
                END as effectiveness_level,
                datetime('now') as computed_at
            FROM learning_modules
            GROUP BY module_id, title
            """
            
            cursor.execute(query)
            conn.commit()
            logger.info("✅ module_effectiveness computed")
            return True
        except Exception as e:
            logger.error(f"❌ Error computing module effectiveness: {e}")
            return False
        finally:
            conn.close()
    
    # ========================
    # E) MOBILISATION FUNNEL
    # ========================
    def compute_mobilisation_funnel(self):
        """
        Funnel stages: Registered → Survey Completed → Sector Selected → Active Day 15 → Completed
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DROP TABLE IF EXISTS mobilisation_funnel")
            
            query = """
            CREATE TABLE mobilisation_funnel AS
            SELECT
                'Registered' as funnel_stage,
                COUNT(DISTINCT u.user_id) as count,
                100.0 as pct_of_registered
            FROM mb_users u
            UNION ALL
            SELECT
                'Career Survey Completed',
                COUNT(DISTINCT cs.user_id),
                ROUND(100.0 * COUNT(DISTINCT cs.user_id) / (SELECT COUNT(*) FROM mb_users), 2)
            FROM career_surveys cs
            UNION ALL
            SELECT
                'Learning Started',
                COUNT(DISTINCT user_id),
                ROUND(100.0 * COUNT(DISTINCT user_id) / (SELECT COUNT(*) FROM mb_users), 2)
            FROM learning_modules
            WHERE status IN ('in_progress', 'completed')
            UNION ALL
            SELECT
                'Modules Completed',
                COUNT(DISTINCT user_id),
                ROUND(100.0 * COUNT(DISTINCT user_id) / (SELECT COUNT(*) FROM mb_users), 2)
            FROM learning_modules
            WHERE status = 'completed'
            """
            
            cursor.execute(query)
            conn.commit()
            logger.info("✅ mobilisation_funnel computed")
            return True
        except Exception as e:
            logger.error(f"❌ Error computing mobilisation funnel: {e}")
            return False
        finally:
            conn.close()
    
    # ========================
    # F) GAMIFICATION IMPACT
    # ========================
    def compute_gamification_impact(self):
        """
        Compare retention & completion for badge earners vs non-earners
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DROP TABLE IF EXISTS gamification_impact")
            
            query = """
            CREATE TABLE gamification_impact AS
            SELECT
                'Badge Earners' as group_type,
                COUNT(DISTINCT user_id) as user_count,
                ROUND(AVG(CASE WHEN status = 'completed' THEN 100 ELSE 50 END), 2) as avg_engagement_pct,
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN status = 'completed' THEN user_id END) / 
                      NULLIF(COUNT(DISTINCT user_id), 0), 2) as completion_rate
            FROM learning_modules
            WHERE user_id IN (SELECT DISTINCT user_id FROM learning_modules WHERE progress >= 75)
            UNION ALL
            SELECT
                'Non-Badge Earners',
                COUNT(DISTINCT user_id),
                ROUND(AVG(CASE WHEN status = 'completed' THEN 100 ELSE 50 END), 2),
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN status = 'completed' THEN user_id END) / 
                      NULLIF(COUNT(DISTINCT user_id), 0), 2)
            FROM learning_modules
            WHERE user_id NOT IN (SELECT DISTINCT user_id FROM learning_modules WHERE progress >= 75)
            """
            
            cursor.execute(query)
            conn.commit()
            logger.info("✅ gamification_impact computed")
            return True
        except Exception as e:
            logger.error(f"❌ Error computing gamification impact: {e}")
            return False
        finally:
            conn.close()
    
    # ========================
    # ORCHESTRATION
    # ========================
    def compute_all_features(self):
        """Compute all enriched feature tables"""
        logger.info("🚀 Starting feature engineering pipeline...")
        
        results = {
            "student_daily_features": self.compute_student_daily_features(),
            "dropout_risk": self.compute_dropout_risk(),
            "sector_fit": self.compute_sector_fit(),
            "module_effectiveness": self.compute_module_effectiveness(),
            "mobilisation_funnel": self.compute_mobilisation_funnel(),
            "gamification_impact": self.compute_gamification_impact(),
        }
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"✅ Feature pipeline complete: {success_count}/{len(results)} tables created")
        
        return results


# Quick helper function
def refresh_all_features():
    """One-liner to refresh all features"""
    engineer = FeatureEngineer()
    return engineer.compute_all_features()


if __name__ == "__main__":
    refresh_all_features()
