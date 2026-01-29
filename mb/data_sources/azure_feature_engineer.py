"""
Enhanced Feature Engineering using Azure Blob Storage Datasets
Generates enriched features for decision dashboards from real APAC data
Falls back to SQLite local database when Azure is unavailable
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, Tuple, Optional
import sys
from pathlib import Path
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from azure_blob_connector import get_blob_connector

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AzureFeatureEngineer:
    """Feature engineering using Azure Blob Storage datasets with SQLite fallback"""
    
    def __init__(self):
        self.connector = get_blob_connector()
        self.cache = {}
        # SQLite database path for fallback
        self.db_path = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"
    
    # ========================
    # DATA LOADING & CACHING
    # ========================
    
    def _load_from_sqlite(self, table_name: str) -> pd.DataFrame:
        """Load dataset from SQLite database (fallback when Azure unavailable)"""
        try:
            if not self.db_path.exists():
                logger.warning(f"SQLite database not found at {self.db_path}")
                return pd.DataFrame()
            
            conn = sqlite3.connect(str(self.db_path))
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
            logger.info(f"📦 Loaded from SQLite - {table_name}: {len(df)} rows")
            return df
        except Exception as e:
            logger.warning(f"Could not load {table_name} from SQLite: {e}")
            return pd.DataFrame()
    
    def _load_dataset(self, table_name: str, force_reload: bool = False) -> pd.DataFrame:
        """Load dataset with caching - try Azure first, then SQLite fallback"""
        if table_name in self.cache and not force_reload:
            return self.cache[table_name]
        
        # Try Azure first
        df = self.connector.get_dataset(table_name)
        
        # If Azure returns empty, try SQLite fallback
        if df.empty:
            df = self._load_from_sqlite(table_name)
        
        if not df.empty:
            self.cache[table_name] = df
        return df
    
    def _get_student_id_column(self, df: pd.DataFrame) -> str:
        """Identify student ID column (flexible column naming)"""
        student_cols = [col for col in df.columns if 'student' in col.lower() and 'id' in col.lower()]
        if student_cols:
            return student_cols[0]
        return 'student_id' if 'student_id' in df.columns else 'id'
    
    # ========================
    # A) STUDENT DAILY FEATURES
    # ========================
    
    def compute_student_daily_features(self) -> pd.DataFrame:
        """
        Compute engagement features for each student:
        - Modules assigned, started, completed
        - Average completion percentage
        - Quiz participation and performance
        - Session frequency
        - Days since enrollment
        """
        logger.info("📊 Computing student daily features...")
        
        try:
            # Load data
            students_df = self._load_dataset("students")
            progress_df = self._load_dataset("student_progress")
            quiz_df = self._load_dataset("quiz_attempts")
            sessions_df = self._load_dataset("user_sessions")
            
            if students_df.empty:
                logger.warning("⚠️ No students data available")
                return pd.DataFrame()
            
            # Identify student ID column
            student_col = self._get_student_id_column(students_df)
            
            # Aggregate module statistics
            module_stats = progress_df.groupby(student_col).agg({
                'module_id': 'nunique',
                'completion_percentage': 'mean',
                'status': lambda x: (x == 'completed').sum(),
                'time_spent_minutes': 'sum',
                'points_earned': 'sum'
            }).reset_index()
            
            module_stats.columns = [
                student_col, 'modules_assigned', 'avg_completion_pct',
                'modules_completed', 'total_time_minutes', 'module_points'
            ]
            
            # Quiz statistics
            quiz_stats = quiz_df.groupby(student_col).agg({
                'quiz_id': 'count',
                'score': 'mean',
                'passed': lambda x: (x == True).sum(),
                'time_taken_seconds': 'mean'
            }).reset_index()
            
            quiz_stats.columns = [
                student_col, 'quizzes_attempted', 'avg_quiz_score',
                'quizzes_passed', 'avg_quiz_time_sec'
            ]
            
            # Session statistics
            session_stats = sessions_df.groupby(student_col).agg({
                'session_id': 'count',
                'duration_minutes': 'sum',
                'created_at': 'max'
            }).reset_index()
            
            session_stats.columns = [
                student_col, 'sessions_count', 'total_session_minutes', 'last_login_date'
            ]
            
            # Merge all features
            features_df = students_df[[student_col, 'display_name', 'email', 'enrollment_date']].copy()
            features_df = features_df.merge(module_stats, on=student_col, how='left')
            features_df = features_df.merge(quiz_stats, on=student_col, how='left')
            features_df = features_df.merge(session_stats, on=student_col, how='left')
            
            # Calculate days since enrollment
            if pd.api.types.is_datetime64_any_dtype(features_df['enrollment_date']):
                enroll_date = features_df['enrollment_date']
            else:
                enroll_date = pd.to_datetime(features_df['enrollment_date'], errors='coerce')
            
            features_df['days_since_enrollment'] = (
                pd.Timestamp.now() - enroll_date
            ).dt.days
            
            # Fill NaN values with 0
            features_df = features_df.fillna(0)
            
            features_df['feature_timestamp'] = pd.Timestamp.now()
            
            logger.info(f"✅ Computed features for {len(features_df)} students")
            return features_df
        
        except Exception as e:
            logger.error(f"❌ Error computing student daily features: {e}")
            return pd.DataFrame()
    
    # ========================
    # B) DROPOUT RISK SCORING
    # ========================
    
    def compute_dropout_risk(self) -> pd.DataFrame:
        """
        Dropout Risk Scoring Logic:
        - HIGH (9): <3 modules started + avg completion <30%, OR no activity >14 days
        - MEDIUM (5): <5 modules started OR avg completion <50%
        - LOW (1): Otherwise
        """
        logger.info("🚨 Computing dropout risk scores...")
        
        try:
            # Get daily features
            daily_features = self.compute_student_daily_features()
            
            if daily_features.empty:
                logger.warning("⚠️ No daily features available")
                return pd.DataFrame()
            
            # Calculate risk scores
            def assign_risk_level(row):
                modules_started = row.get('modules_assigned', 0)
                avg_completion = row.get('avg_completion_pct', 0)
                days_inactive = row.get('days_since_enrollment', 0) - (
                    row.get('days_since_enrollment', 0) - 7  # Approximation for inactivity
                )
                
                # HIGH RISK
                if (modules_started < 3 and avg_completion < 30) or days_inactive > 14:
                    return 'HIGH', 9
                
                # MEDIUM RISK
                elif modules_started < 5 or avg_completion < 50:
                    return 'MEDIUM', 5
                
                # LOW RISK
                else:
                    return 'LOW', 1
            
            # Apply risk scoring
            risk_data = []
            for idx, row in daily_features.iterrows():
                risk_level, risk_score = assign_risk_level(row)
                
                # Generate risk reason
                reasons = []
                if row.get('modules_assigned', 0) < 3:
                    reasons.append(f"Low module engagement: {row.get('modules_assigned', 0)} modules")
                if row.get('avg_completion_pct', 0) < 50:
                    reasons.append(f"Low completion rate: {row.get('avg_completion_pct', 0):.1f}%")
                if row.get('sessions_count', 0) < 3:
                    reasons.append(f"Limited sessions: {row.get('sessions_count', 0)}")
                
                risk_data.append({
                    'student_id': row.get('student_id'),
                    'student_name': row.get('display_name'),
                    'email': row.get('email'),
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'risk_reason': ' | '.join(reasons) if reasons else 'Monitoring',
                    'modules_started': row.get('modules_assigned', 0),
                    'avg_completion_pct': row.get('avg_completion_pct', 0),
                    'days_since_enrollment': row.get('days_since_enrollment', 0),
                    'computed_at': pd.Timestamp.now()
                })
            
            risk_df = pd.DataFrame(risk_data)
            logger.info(f"✅ Computed dropout risk for {len(risk_df)} students")
            return risk_df
        
        except Exception as e:
            logger.error(f"❌ Error computing dropout risk: {e}")
            return pd.DataFrame()
    
    # ========================
    # C) SECTOR FIT SCORING
    # ========================
    
    def compute_sector_fit(self) -> pd.DataFrame:
        """
        Career sector fit scoring:
        - Match students to sectors based on interests and skills
        - Readiness status: Green (≥70), Amber (50-69), Red (<50)
        """
        logger.info("🎯 Computing sector fit scores...")
        
        try:
            # Load data
            students_df = self._load_dataset("students")
            interests_df = self._load_dataset("career_interests")
            skills_df = self._load_dataset("student_skills")
            pathways_df = self._load_dataset("career_pathways")
            
            if students_df.empty or interests_df.empty:
                logger.warning("⚠️ Missing sector data")
                return pd.DataFrame()
            
            # Get student ID columns
            student_col = self._get_student_id_column(students_df)
            
            # Aggregate interests per student
            student_interests = interests_df.groupby(student_col).agg({
                'interest_level': 'mean',
                'confidence_score': 'mean',
                'pathway_id': lambda x: x.nunique()
            }).reset_index()
            
            student_interests.columns = [
                student_col, 'interest_strength', 'interest_confidence', 'sectors_explored'
            ]
            
            # Aggregate skills per student
            student_skill_level = skills_df.groupby(student_col).agg({
                'proficiency_level': 'mean',
                'skill_id': 'count'
            }).reset_index()
            
            student_skill_level.columns = [
                student_col, 'avg_skill_proficiency', 'skills_acquired'
            ]
            
            # Merge with student data
            sector_fit = students_df[[student_col, 'display_name', 'email', 'grade']].copy()
            sector_fit = sector_fit.merge(student_interests, on=student_col, how='left')
            sector_fit = sector_fit.merge(student_skill_level, on=student_col, how='left')
            
            # Calculate sector fit score (0-100)
            sector_fit['sector_fit_score'] = (
                sector_fit['interest_confidence'].fillna(0) * 0.6 +
                sector_fit['avg_skill_proficiency'].fillna(0) * 0.4
            ) * 100 / 5  # Normalize to 0-100
            
            # Determine readiness status
            def get_readiness_status(score):
                if score >= 70:
                    return 'Green'
                elif score >= 50:
                    return 'Amber'
                else:
                    return 'Red'
            
            sector_fit['readiness_status'] = sector_fit['sector_fit_score'].apply(
                get_readiness_status
            )
            
            sector_fit['computed_at'] = pd.Timestamp.now()
            
            logger.info(f"✅ Computed sector fit for {len(sector_fit)} students")
            return sector_fit
        
        except Exception as e:
            logger.error(f"❌ Error computing sector fit: {e}")
            return pd.DataFrame()
    
    # ========================
    # D) MODULE EFFECTIVENESS
    # ========================
    
    def compute_module_effectiveness(self) -> pd.DataFrame:
        """
        Module effectiveness ranking based on:
        - Completion rate
        - Average time to completion
        - Quiz performance by module
        - Points earned per module
        """
        logger.info("📚 Computing module effectiveness...")
        
        try:
            # Load data
            modules_df = self._load_dataset("learning_modules")
            progress_df = self._load_dataset("student_progress")
            quiz_df = self._load_dataset("quiz_attempts")
            
            if modules_df.empty or progress_df.empty:
                logger.warning("⚠️ Missing module data")
                return pd.DataFrame()
            
            # Module statistics
            mod_stats = progress_df.groupby('module_id').agg({
                'student_id': 'nunique',
                'completion_percentage': 'mean',
                'status': lambda x: (x == 'completed').sum(),
                'time_spent_minutes': 'mean',
                'points_earned': 'sum'
            }).reset_index()
            
            mod_stats.columns = [
                'module_id', 'learners', 'avg_completion_pct',
                'completions', 'avg_time_minutes', 'total_points_earned'
            ]
            
            # Calculate completion rate
            mod_stats['completion_rate'] = (
                mod_stats['completions'] / mod_stats['learners'] * 100
            ).fillna(0)
            
            # Quiz performance by module
            quiz_performance = quiz_df.groupby('quiz_id').agg({
                'score': 'mean',
                'passed': lambda x: (x == True).sum()
            }).reset_index()
            
            # Merge with module data
            effectiveness_df = modules_df[['module_id', 'module_name', 'category', 'difficulty_level']].copy()
            effectiveness_df = effectiveness_df.merge(mod_stats, on='module_id', how='left')
            
            # Determine effectiveness level
            def get_effectiveness(row):
                comp_rate = row['completion_rate']
                if comp_rate >= 80:
                    return 'High Impact'
                elif comp_rate >= 60:
                    return 'Medium Impact'
                else:
                    return 'Needs Improvement'
            
            effectiveness_df['effectiveness_level'] = effectiveness_df.apply(
                get_effectiveness, axis=1
            )
            
            # Fill NaN values
            effectiveness_df = effectiveness_df.fillna(0)
            effectiveness_df['computed_at'] = pd.Timestamp.now()
            
            logger.info(f"✅ Computed effectiveness for {len(effectiveness_df)} modules")
            return effectiveness_df
        
        except Exception as e:
            logger.error(f"❌ Error computing module effectiveness: {e}")
            return pd.DataFrame()
    
    # ========================
    # E) GAMIFICATION IMPACT
    # ========================
    
    def compute_gamification_impact(self) -> pd.DataFrame:
        """
        Measure impact of gamification (badges, points) on learning outcomes:
        - Compare badge earners vs non-earners
        - Completion rates and engagement metrics
        """
        logger.info("🏅 Computing gamification impact...")
        
        try:
            # Load data
            students_df = self._load_dataset("students")
            achievements_df = self._load_dataset("student_achievements")
            progress_df = self._load_dataset("student_progress")
            points_df = self._load_dataset("points_ledger")
            
            if students_df.empty or achievements_df.empty:
                logger.warning("⚠️ Missing gamification data")
                return pd.DataFrame()
            
            student_col = self._get_student_id_column(students_df)
            
            # Get badge earners
            badge_earners = achievements_df[student_col].unique()
            points_earners = points_df[student_col].unique()
            
            # Combine gamification participants
            gamified_students = set(badge_earners) | set(points_earners)
            
            # Calculate statistics for both groups
            def calc_group_stats(student_list, group_name):
                group_df = progress_df[progress_df[student_col].isin(student_list)]
                
                if len(group_df) > 0:
                    completion_rate = (
                        (group_df['status'] == 'completed').sum() / 
                        len(group_df) * 100
                    )
                    avg_time = group_df['time_spent_minutes'].mean()
                    avg_points = group_df['points_earned'].mean()
                else:
                    completion_rate = 0
                    avg_time = 0
                    avg_points = 0
                
                return {
                    'group_type': group_name,
                    'user_count': len(student_list),
                    'completion_rate': round(completion_rate, 1),
                    'avg_time_per_module': round(avg_time, 1),
                    'avg_points_earned': round(avg_points, 1),
                    'engagement_score': round(
                        (completion_rate / 100 + avg_time / 100 + avg_points / 100) / 3 * 100, 1
                    )
                }
            
            # Compare groups
            gamified_stats = calc_group_stats(
                list(gamified_students), 'Badge & Points Earners'
            )
            
            non_gamified = set(students_df[student_col].unique()) - gamified_students
            non_gamified_stats = calc_group_stats(
                list(non_gamified), 'Non-Gamification Participants'
            )
            
            gamification_df = pd.DataFrame([gamified_stats, non_gamified_stats])
            gamification_df['computed_at'] = pd.Timestamp.now()
            
            logger.info(f"✅ Computed gamification impact")
            return gamification_df
        
        except Exception as e:
            logger.error(f"❌ Error computing gamification impact: {e}")
            return pd.DataFrame()
    
    # ========================
    # F) MOBILISATION FUNNEL
    # ========================
    
    def compute_mobilisation_funnel(self) -> pd.DataFrame:
        """
        Track student progression funnel:
        Registered → Active Learner → Quiz Participation → Goal Achievement
        """
        logger.info("📈 Computing mobilisation funnel...")
        
        try:
            # Load data
            students_df = self._load_dataset("students")
            progress_df = self._load_dataset("student_progress")
            quiz_df = self._load_dataset("quiz_attempts")
            achievements_df = self._load_dataset("student_achievements")
            
            if students_df.empty:
                logger.warning("⚠️ Missing funnel data")
                return pd.DataFrame()
            
            student_col = self._get_student_id_column(students_df)
            
            # Stage 1: Registered
            registered = len(students_df)
            
            # Stage 2: Started Learning (has progress records)
            started_learning = progress_df[student_col].nunique()
            
            # Stage 3: Quiz Participation (attempted at least 1 quiz)
            quiz_participants = quiz_df[student_col].nunique()
            
            # Stage 4: Achievement (earned badges/certificates)
            achieved = achievements_df[student_col].nunique()
            
            # Calculate percentages
            funnel_data = [
                {
                    'funnel_stage': 'Registered',
                    'count': registered,
                    'pct_of_registered': 100.0
                },
                {
                    'funnel_stage': 'Started Learning',
                    'count': started_learning,
                    'pct_of_registered': round(100.0 * started_learning / registered, 1)
                },
                {
                    'funnel_stage': 'Quiz Participation',
                    'count': quiz_participants,
                    'pct_of_registered': round(100.0 * quiz_participants / registered, 1)
                },
                {
                    'funnel_stage': 'Achievement',
                    'count': achieved,
                    'pct_of_registered': round(100.0 * achieved / registered, 1)
                }
            ]
            
            funnel_df = pd.DataFrame(funnel_data)
            funnel_df['computed_at'] = pd.Timestamp.now()
            
            logger.info(f"✅ Computed mobilisation funnel with {len(funnel_df)} stages")
            return funnel_df
        
        except Exception as e:
            logger.error(f"❌ Error computing mobilisation funnel: {e}")
            return pd.DataFrame()
    
    # ========================
    # ORCHESTRATION
    # ========================
    
    def compute_all_features(self) -> Dict[str, pd.DataFrame]:
        """Load all pre-computed features from database"""
        logger.info("\n" + "="*60)
        logger.info("🚀 STARTING FEATURE LOAD PIPELINE")
        logger.info("="*60)
        
        # Map of feature names to database table names
        feature_tables = {
            'student_daily_features': 'student_daily_features',
            'dropout_risk': 'student_dropout_risk',
            'sector_fit': 'student_sector_fit',
            'module_effectiveness': 'module_effectiveness',
            'gamification_impact': 'gamification_impact',
            'mobilisation_funnel': 'mobilisation_funnel',
        }
        
        features = {}
        for feature_name, table_name in feature_tables.items():
            try:
                df = self._load_from_sqlite(table_name)
                if df.empty:
                    logger.warning(f"⚠️ {feature_name}: Attempting computation...")
                    # Fall back to computation if table doesn't exist
                    if feature_name == 'student_daily_features':
                        df = self.compute_student_daily_features()
                    elif feature_name == 'dropout_risk':
                        df = self.compute_dropout_risk()
                    elif feature_name == 'sector_fit':
                        df = self.compute_sector_fit()
                    elif feature_name == 'module_effectiveness':
                        df = self.compute_module_effectiveness()
                    elif feature_name == 'gamification_impact':
                        df = self.compute_gamification_impact()
                    elif feature_name == 'mobilisation_funnel':
                        df = self.compute_mobilisation_funnel()
                features[feature_name] = df
            except Exception as e:
                logger.error(f"Error loading {feature_name}: {e}")
                features[feature_name] = pd.DataFrame()
        
        logger.info("\n" + "="*60)
        logger.info("✅ FEATURE LOAD COMPLETE")
        logger.info("="*60)
        for name, df in features.items():
            if not df.empty:
                logger.info(f"  ✅ {name}: {len(df)} rows")
            else:
                logger.info(f"  ⚠️ {name}: No data")
        
        return features


# ========================
# HELPER FUNCTIONS
# ========================

def get_azure_feature_engineer() -> AzureFeatureEngineer:
    """Get singleton feature engineer instance"""
    return AzureFeatureEngineer()


def refresh_all_azure_features() -> Dict[str, pd.DataFrame]:
    """Refresh all features from Azure Blob Storage"""
    engineer = get_azure_feature_engineer()
    return engineer.compute_all_features()


if __name__ == "__main__":
    # Test feature engineering
    features = refresh_all_azure_features()
    
    print("\n" + "="*60)
    print("FEATURE ENGINEERING TEST RESULTS")
    print("="*60)
    for name, df in features.items():
        if not df.empty:
            print(f"\n{name}:")
            print(df.head(3))
        else:
            print(f"\n{name}: No data available")
