"""
Peer Matching Network Service
Implements mentor-mentee matching based on similarity metrics
Uses Youth Potential Score™ similarity and trait profiles for peer network
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"


class PeerMatchingNetwork:
    """Service for finding peer mentors and similar youth"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(str(self.db_path))
    
    def _euclidean_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        if len(point1) != len(point2):
            return float('inf')
        return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))
    
    def _calculate_potential_metrics(self, student_id):
        """
        Calculate potential score metrics for a student
        Returns tuple: (engagement, retention, skill, placement)
        """
        from mb.decision_dashboard import DecisionDashboard
        
        dashboard = DecisionDashboard()
        potential = dashboard.calculate_youth_potential_score(student_id)
        
        return (
            potential['engagement_probability'],
            potential['retention_likelihood'],
            potential['skill_readiness'],
            potential['placement_fit']
        )
    
    def find_similar_youth(self, student_id, limit=5, exclude_self=True):
        """
        Find similar youth using Youth Potential Score™ similarity (Euclidean distance)
        Returns "mentor twins" - students with similar profiles
        """
        conn = self.get_connection()
        try:
            # Get all student IDs
            df_students = pd.read_sql_query(
                "SELECT DISTINCT student_id FROM mb_users",
                conn
            )
            
            if df_students.empty:
                return []
            
            # Get reference student metrics
            ref_metrics = self._calculate_potential_metrics(student_id)
            
            similarities = []
            
            for _, row in df_students.iterrows():
                other_student_id = row['student_id']
                
                if exclude_self and other_student_id == student_id:
                    continue
                
                # Calculate metrics for this student
                try:
                    other_metrics = self._calculate_potential_metrics(other_student_id)
                    
                    # Calculate Euclidean distance (similarity)
                    distance = self._euclidean_distance(ref_metrics, other_metrics)
                    similarity_score = 100 / (1 + distance)  # Normalize to 0-100
                    
                    similarities.append({
                        "student_id": other_student_id,
                        "similarity_score": round(similarity_score, 2),
                        "distance": round(distance, 3),
                        "engagement_alignment": abs(ref_metrics[0] - other_metrics[0]),
                        "retention_alignment": abs(ref_metrics[1] - other_metrics[1]),
                        "skill_alignment": abs(ref_metrics[2] - other_metrics[2]),
                        "placement_alignment": abs(ref_metrics[3] - other_metrics[3])
                    })
                except Exception as e:
                    logger.warning(f"Could not calculate metrics for {other_student_id}: {e}")
                    continue
            
            # Sort by similarity score (highest first)
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return {
                "reference_student_id": student_id,
                "similar_youth": similarities[:limit],
                "total_found": len(similarities),
                "limit": limit,
                "matched_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error finding similar youth: {e}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_success_patterns(self, trait_profile=None):
        """
        Extract shared traits of high-achievers (tier = "Exceptional")
        Returns self-reinforcing patterns for mentorship
        """
        conn = self.get_connection()
        try:
            from mb.decision_dashboard import DecisionDashboard
            
            dashboard = DecisionDashboard()
            df_students = pd.read_sql_query(
                "SELECT DISTINCT student_id FROM mb_users",
                conn
            )
            
            if df_students.empty:
                return {"error": "No students found"}
            
            # Identify high achievers (Exceptional tier)
            high_achievers = []
            
            for _, row in df_students.iterrows():
                student_id = row['student_id']
                potential = dashboard.calculate_youth_potential_score(student_id)
                
                if potential['tier'] == "Exceptional":
                    high_achievers.append({
                        "student_id": student_id,
                        "engagement": potential['engagement_probability'],
                        "retention": potential['retention_likelihood'],
                        "skill": potential['skill_readiness'],
                        "placement": potential['placement_fit']
                    })
            
            if not high_achievers:
                return {
                    "message": "No high achievers found yet",
                    "patterns": [],
                    "recommendation": "Continue mentoring to build mentor base"
                }
            
            # Calculate average traits of high achievers
            avg_engagement = np.mean([h['engagement'] for h in high_achievers])
            avg_retention = np.mean([h['retention'] for h in high_achievers])
            avg_skill = np.mean([h['skill'] for h in high_achievers])
            avg_placement = np.mean([h['placement'] for h in high_achievers])
            
            patterns = {
                "high_achiever_count": len(high_achievers),
                "average_engagement": round(avg_engagement, 2),
                "average_retention": round(avg_retention, 2),
                "average_skill_readiness": round(avg_skill, 2),
                "average_placement_fit": round(avg_placement, 2),
                "success_traits": {
                    "high_engagement": f"Maintain {avg_engagement:.0f}%+ activity levels",
                    "strong_retention": f"Target {avg_retention:.0f}%+ module completion",
                    "skill_focus": f"Build 5+ core skills ({avg_skill:.0f}% readiness target)",
                    "placement_mindset": f"Align with role requirements ({avg_placement:.0f}%+ fit)"
                },
                "self_reinforcing_cycle": [
                    "1. High engagement builds momentum",
                    "2. Momentum improves module completion (retention)",
                    "3. Completion unlocks new skills",
                    "4. Skills improve placement readiness",
                    "5. Placement success reinforces engagement"
                ]
            }
            
            return patterns
        except Exception as e:
            logger.error(f"Error getting success patterns: {e}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def suggest_peer_mentors(self, student_id, limit=3):
        """
        Suggest peer mentors for a student based on similarity and tier
        Returns 1:1 peer support matches
        """
        try:
            from mb.decision_dashboard import DecisionDashboard
            
            dashboard = DecisionDashboard()
            potential = dashboard.calculate_youth_potential_score(student_id)
            student_tier = potential['tier']
            
            # Find similar youth
            similar = self.find_similar_youth(student_id, limit=limit*2)
            similar_youth = similar.get("similar_youth", [])
            
            mentors = []
            
            for similar_student in similar_youth:
                mentor_id = similar_student['student_id']
                mentor_potential = dashboard.calculate_youth_potential_score(mentor_id)
                mentor_tier = mentor_potential['tier']
                
                # Prefer mentors from same or higher tier
                tier_hierarchy = {"Development": 1, "Medium": 2, "High": 3, "Exceptional": 4}
                student_tier_num = tier_hierarchy.get(student_tier, 0)
                mentor_tier_num = tier_hierarchy.get(mentor_tier, 0)
                
                if mentor_tier_num >= student_tier_num:
                    match_strength = "Strong" if mentor_tier_num > student_tier_num else "Peer"
                    
                    mentors.append({
                        "mentor_id": mentor_id,
                        "mentor_tier": mentor_tier,
                        "similarity_score": similar_student['similarity_score'],
                        "match_strength": match_strength,
                        "engagement_mentor": round(mentor_potential['engagement_probability'], 2),
                        "retention_mentor": round(mentor_potential['retention_likelihood'], 2),
                        "skills_mentor": round(mentor_potential['skill_readiness'], 2),
                        "mentorship_focus": [
                            f"{mentor_tier} tier student",
                            f"Can help with {'engagement' if mentor_potential['engagement_probability'] > 75 else 'support'}",
                            f"Strong in {'skills' if mentor_potential['skill_readiness'] > 75 else 'experience'}"
                        ]
                    })
            
            return {
                "student_id": student_id,
                "student_tier": student_tier,
                "peer_mentors": mentors[:limit],
                "total_suggested": len(mentors),
                "suggested_at": datetime.now().isoformat(),
                "recommendation": f"Connect with {len(mentors[:limit])} peer mentor(s) for {student_tier}-tier support"
            }
        except Exception as e:
            logger.error(f"Error suggesting peer mentors: {e}")
            return {"error": str(e)}
    
    def create_peer_connection(self, mentee_id, mentor_id):
        """
        Create a formal peer mentoring connection
        Stores relationship for tracking and engagement
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Create table if needed
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS peer_mentoring_connections (
                    connection_id INTEGER PRIMARY KEY,
                    mentee_id VARCHAR(50),
                    mentor_id VARCHAR(50),
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    check_ins INTEGER DEFAULT 0,
                    last_interaction TIMESTAMP
                )
            """)
            
            cursor.execute(
                """INSERT INTO peer_mentoring_connections (mentee_id, mentor_id)
                   VALUES (?, ?)""",
                (mentee_id, mentor_id)
            )
            
            conn.commit()
            
            return {
                "mentee_id": mentee_id,
                "mentor_id": mentor_id,
                "connection_status": "active",
                "created_at": datetime.now().isoformat(),
                "message": "Peer mentoring connection established"
            }
        except Exception as e:
            logger.error(f"Error creating peer connection: {e}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_mentoring_connections(self, student_id, role="any"):
        """
        Get all mentoring connections for a student
        role: "mentor", "mentee", or "any"
        """
        conn = self.get_connection()
        try:
            if role == "mentor":
                df = pd.read_sql_query(
                    """SELECT mentee_id as connected_student, created_date, status, check_ins
                       FROM peer_mentoring_connections WHERE mentor_id = ?""",
                    conn,
                    params=(student_id,)
                )
            elif role == "mentee":
                df = pd.read_sql_query(
                    """SELECT mentor_id as connected_student, created_date, status, check_ins
                       FROM peer_mentoring_connections WHERE mentee_id = ?""",
                    conn,
                    params=(student_id,)
                )
            else:  # any
                df = pd.read_sql_query(
                    """SELECT mentee_id as connected_student, 'mentee' as role, created_date, status, check_ins
                       FROM peer_mentoring_connections WHERE mentor_id = ?
                       UNION
                       SELECT mentor_id as connected_student, 'mentor' as role, created_date, status, check_ins
                       FROM peer_mentoring_connections WHERE mentee_id = ?""",
                    conn,
                    params=(student_id, student_id)
                )
            
            return {
                "student_id": student_id,
                "role": role,
                "connections": df.to_dict('records') if not df.empty else [],
                "total_connections": len(df)
            }
        except Exception as e:
            logger.error(f"Error getting mentoring connections: {e}")
            return {"error": str(e)}
        finally:
            conn.close()


def init_peer_matching_network():
    """Initialize peer matching network service"""
    return PeerMatchingNetwork()
