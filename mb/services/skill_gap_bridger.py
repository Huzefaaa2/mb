"""
Skill Gap Bridger Service
Identifies skill gaps between current abilities and role requirements
Recommends personalized learning paths with micro-learning resources
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

# Mock role requirements database
ROLE_REQUIREMENTS = {
    "Software Developer": {
        "required_skills": ["Python", "SQL", "Problem Solving", "Version Control", "APIs", "Testing"],
        "priority": ["Python", "Problem Solving", "Testing"],
        "proficiency_level": "Intermediate"
    },
    "Data Analyst": {
        "required_skills": ["SQL", "Excel", "Data Visualization", "Statistics", "Python", "Tableau"],
        "priority": ["SQL", "Data Visualization", "Statistics"],
        "proficiency_level": "Intermediate"
    },
    "Business Analyst": {
        "required_skills": ["Communication", "Business Acumen", "Documentation", "Excel", "SQL", "Stakeholder Management"],
        "priority": ["Communication", "Business Acumen", "Documentation"],
        "proficiency_level": "Intermediate"
    },
    "Project Manager": {
        "required_skills": ["Leadership", "Communication", "Planning", "Risk Management", "Budgeting", "Team Management"],
        "priority": ["Leadership", "Communication", "Planning"],
        "proficiency_level": "Intermediate"
    },
    "UX Designer": {
        "required_skills": ["Design Thinking", "Figma", "User Research", "Wireframing", "Communication", "Prototyping"],
        "priority": ["Design Thinking", "User Research", "Figma"],
        "proficiency_level": "Intermediate"
    }
}

# Mock learning resources (YouTube/Udemy style)
LEARNING_RESOURCES = {
    "Python": [
        {"resource": "Python Basics", "platform": "YouTube", "duration_hours": 10, "url": "https://youtube.com/python-basics"},
        {"resource": "Python Advanced", "platform": "Udemy", "duration_hours": 20, "url": "https://udemy.com/python-advanced"},
    ],
    "SQL": [
        {"resource": "SQL Fundamentals", "platform": "YouTube", "duration_hours": 8, "url": "https://youtube.com/sql-intro"},
        {"resource": "Advanced SQL", "platform": "Udemy", "duration_hours": 15, "url": "https://udemy.com/sql-advanced"},
    ],
    "Problem Solving": [
        {"resource": "Problem Solving Techniques", "platform": "Udemy", "duration_hours": 12, "url": "https://udemy.com/problem-solving"},
        {"resource": "Coding Challenges", "platform": "YouTube", "duration_hours": 20, "url": "https://youtube.com/coding-challenges"},
    ],
    "Communication": [
        {"resource": "Professional Communication", "platform": "Udemy", "duration_hours": 6, "url": "https://udemy.com/communication"},
        {"resource": "Presentation Skills", "platform": "YouTube", "duration_hours": 8, "url": "https://youtube.com/presentations"},
    ],
    "Leadership": [
        {"resource": "Leadership Fundamentals", "platform": "Udemy", "duration_hours": 15, "url": "https://udemy.com/leadership"},
        {"resource": "Team Management", "platform": "YouTube", "duration_hours": 12, "url": "https://youtube.com/team-management"},
    ],
    "Data Visualization": [
        {"resource": "Tableau Basics", "platform": "Udemy", "duration_hours": 10, "url": "https://udemy.com/tableau"},
        {"resource": "Power BI Essentials", "platform": "YouTube", "duration_hours": 12, "url": "https://youtube.com/powerbi"},
    ],
    "Design Thinking": [
        {"resource": "Design Thinking Workshop", "platform": "Udemy", "duration_hours": 8, "url": "https://udemy.com/design-thinking"},
        {"resource": "User-Centered Design", "platform": "YouTube", "duration_hours": 10, "url": "https://youtube.com/user-design"},
    ],
    "Figma": [
        {"resource": "Figma Masterclass", "platform": "Udemy", "duration_hours": 12, "url": "https://udemy.com/figma"},
        {"resource": "Prototyping with Figma", "platform": "YouTube", "duration_hours": 10, "url": "https://youtube.com/figma-prototyping"},
    ],
}


class SkillGapBridger:
    """Service for identifying skill gaps and recommending learning paths"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.role_requirements = ROLE_REQUIREMENTS
        self.learning_resources = LEARNING_RESOURCES
    
    def get_connection(self):
        return sqlite3.connect(str(self.db_path))
    
    def analyze_skill_gaps(self, student_id, role_id):
        """
        Analyze skill gaps between current skills and role requirements
        Returns gap list with priority scores
        """
        conn = self.get_connection()
        try:
            # Get student's current skills
            df_skills = pd.read_sql_query(
                """SELECT extracted_skills FROM mb_onboarding_profiles WHERE student_id = ?""",
                conn,
                params=(student_id,)
            )
            
            current_skills = set()
            if not df_skills.empty:
                skills_str = df_skills.iloc[0]['extracted_skills'] or ""
                current_skills = set(skill.strip().lower() for skill in skills_str.split(",") if skill.strip())
            
            # Get role requirements
            if role_id not in self.role_requirements:
                return {"error": f"Role '{role_id}' not found in requirements database"}
            
            role_reqs = self.role_requirements[role_id]
            required_skills = set(skill.lower() for skill in role_reqs["required_skills"])
            
            # Calculate gaps
            gaps = []
            for skill in required_skills:
                if skill not in current_skills:
                    # Determine priority
                    is_priority = skill in [s.lower() for s in role_reqs.get("priority", [])]
                    priority_score = 10 if is_priority else 5
                    
                    gaps.append({
                        "skill": skill,
                        "priority": "High" if is_priority else "Medium",
                        "priority_score": priority_score,
                        "status": "Gap",
                        "resources_available": skill in self.learning_resources
                    })
            
            # Calculate proficiency gaps (existing skills to improve)
            for skill in current_skills:
                if skill in required_skills:
                    gaps.append({
                        "skill": skill,
                        "priority": "Low",
                        "priority_score": 3,
                        "status": "Improve",
                        "resources_available": skill in self.learning_resources
                    })
            
            # Sort by priority score
            gaps.sort(key=lambda x: x["priority_score"], reverse=True)
            
            return {
                "student_id": student_id,
                "role_id": role_id,
                "current_skills_count": len(current_skills),
                "required_skills_count": len(required_skills),
                "gaps": gaps,
                "total_gaps": len([g for g in gaps if g["status"] == "Gap"]),
                "improvement_areas": len([g for g in gaps if g["status"] == "Improve"]),
                "proficiency_level_target": role_reqs.get("proficiency_level", "Intermediate"),
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {e}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def generate_learning_path(self, gaps_data, max_resources_per_skill=2):
        """
        Generate personalized learning path from gap analysis
        Returns micro-learning playlists with Udemy/YouTube links
        """
        try:
            gaps = gaps_data.get("gaps", [])
            
            if not gaps:
                return {
                    "message": "No skill gaps identified",
                    "learning_path": [],
                    "total_estimated_hours": 0
                }
            
            learning_path = []
            total_hours = 0
            
            for gap in gaps:
                skill = gap["skill"].lower()
                
                if skill not in self.learning_resources:
                    continue
                
                resources = self.learning_resources[skill][:max_resources_per_skill]
                
                path_item = {
                    "skill": gap["skill"],
                    "priority": gap["priority"],
                    "status": gap["status"],
                    "resources": resources,
                    "total_duration_hours": sum(r.get("duration_hours", 0) for r in resources),
                    "estimated_completion_days": max(7, sum(r.get("duration_hours", 0) for r in resources) / 2)  # Assume 2 hrs/day
                }
                
                learning_path.append(path_item)
                total_hours += path_item["total_duration_hours"]
            
            return {
                "student_id": gaps_data.get("student_id"),
                "role_id": gaps_data.get("role_id"),
                "learning_path": learning_path,
                "total_estimated_hours": total_hours,
                "total_estimated_days": max(30, total_hours / 2),
                "path_created_at": datetime.now().isoformat(),
                "recommendation": f"Complete {len(learning_path)} skill areas over approximately {max(30, total_hours / 2):.0f} days"
            }
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return {"error": str(e)}
    
    def track_learning_completion(self, student_id, skill, quiz_score):
        """
        Track learning resource completion
        Updates student's skill proficiency
        """
        conn = self.get_connection()
        try:
            # Check if tracking table exists, create if needed
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skill_learning_tracking (
                    tracking_id INTEGER PRIMARY KEY,
                    student_id VARCHAR(50),
                    skill VARCHAR(100),
                    quiz_score INTEGER,
                    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    proficiency_level VARCHAR(50)
                )
            """)
            
            # Determine proficiency from quiz score
            if quiz_score >= 85:
                proficiency = "Expert"
            elif quiz_score >= 70:
                proficiency = "Proficient"
            elif quiz_score >= 55:
                proficiency = "Basic"
            else:
                proficiency = "Beginner"
            
            cursor.execute(
                """INSERT INTO skill_learning_tracking (student_id, skill, quiz_score, proficiency_level)
                   VALUES (?, ?, ?, ?)""",
                (student_id, skill, quiz_score, proficiency)
            )
            
            conn.commit()
            
            return {
                "student_id": student_id,
                "skill": skill,
                "quiz_score": quiz_score,
                "proficiency_level": proficiency,
                "tracked_at": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error tracking learning completion: {e}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_learning_progress(self, student_id):
        """
        Get student's learning progress across skills
        Returns tracked skills and proficiency levels
        """
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(
                """SELECT skill, AVG(quiz_score) as avg_score, 
                          MAX(proficiency_level) as current_proficiency,
                          COUNT(*) as completions,
                          MAX(completion_date) as last_completion
                   FROM skill_learning_tracking
                   WHERE student_id = ?
                   GROUP BY skill
                   ORDER BY last_completion DESC""",
                conn,
                params=(student_id,)
            )
            
            if df.empty:
                return {"student_id": student_id, "progress": []}
            
            return {
                "student_id": student_id,
                "progress": df.to_dict('records'),
                "total_skills_tracked": len(df),
                "retrieved_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting learning progress: {e}")
            return {"error": str(e)}
        finally:
            conn.close()


def init_skill_gap_bridger():
    """Initialize skill gap bridger service"""
    return SkillGapBridger()
