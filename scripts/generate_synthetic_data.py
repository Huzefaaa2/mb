"""
Generate synthetic data for local testing using approved packages.
Uses: faker, sdv (Synthetic Data Vault), numpy, pandas
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import json
import os

fake = Faker('en_IN')
np.random.seed(42)

SYNTHETIC_DATA_DIR = "data/synthetic"
os.makedirs(SYNTHETIC_DATA_DIR, exist_ok=True)

def generate_students(count=100):
    """Generate synthetic student records."""
    students = []
    for i in range(1, count + 1):
        dob = fake.date_of_birth(minimum_age=16, maximum_age=25)
        enrollment_date = fake.date_between(start_date='-1y')
        
        students.append({
            'student_id': f'STU{i:06d}',
            'student_code': f'SC{i:05d}',
            'display_name': fake.first_name() + ' ' + fake.last_name(),
            'email': f'student{i}@magicbus.org',
            'phone': fake.numerify(text='9#########'),
            'date_of_birth': dob.isoformat(),
            'age': (datetime.now().date() - dob).days // 365,
            'grade': np.random.randint(10, 13),
            'school_id': f'SCH{np.random.randint(1, 11):03d}',
            'section': np.random.choice(['A', 'B', 'C', 'D']),
            'device_access': np.random.choice(['mobile', 'tablet', 'desktop']),
            'preferred_language': np.random.choice(['English', 'Hindi', 'Marathi', 'Tamil']),
            'enrollment_date': enrollment_date.isoformat(),
            'last_login': (datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat(),
            'login_streak': np.random.randint(0, 30),
            'total_points': np.random.randint(0, 5000),
            'current_level': np.random.randint(1, 10),
            'onboarding_completed': np.random.choice([True, False]),
            'is_active': True,
            'created_at': enrollment_date.isoformat(),
        })
    
    return pd.DataFrame(students)

def generate_career_interests(students_df, count_per_student=2):
    """Generate synthetic career interest records."""
    career_interests = []
    interest_id = 1
    
    pathways = [1, 2, 3, 11, 15, 17, 24]
    sources = ['Module Completion', 'Self Discovery', 'Quiz Result']
    interest_levels = ['Very Interested', 'Somewhat Interested', 'Neutral']
    
    for _, student in students_df.iterrows():
        for _ in range(count_per_student):
            created_at = fake.date_between(start_date=student['created_at'])
            last_explored = fake.date_between(start_date=created_at)
            
            career_interests.append({
                'interest_id': interest_id,
                'student_id': student['student_id'],
                'pathway_id': np.random.choice(pathways),
                'interest_level': np.random.choice(interest_levels),
                'source': np.random.choice(sources),
                'confidence_score': round(np.random.uniform(0.4, 1.0), 2),
                'times_explored': np.random.randint(1, 15),
                'last_explored_at': last_explored.isoformat(),
                'is_primary_interest': np.random.choice([True, False]),
                'notes': None,
                'created_at': created_at.isoformat(),
            })
            interest_id += 1
    
    return pd.DataFrame(career_interests)

def generate_quiz_attempts(students_df, count_per_student=3):
    """Generate synthetic quiz attempt records."""
    quiz_attempts = []
    attempt_id = 1
    
    for _, student in students_df.iterrows():
        for _ in range(count_per_student):
            started_at = fake.date_time_between(start_date=student['created_at'])
            duration_seconds = np.random.randint(300, 3600)
            completed_at = started_at + timedelta(seconds=duration_seconds)
            
            questions_correct = np.random.randint(0, 21)
            score = int((questions_correct / 20) * 100)
            passed = score >= 60
            
            quiz_attempts.append({
                'attempt_id': attempt_id,
                'student_id': student['student_id'],
                'quiz_id': np.random.randint(1, 50),
                'attempt_number': np.random.randint(1, 4),
                'started_at': started_at.isoformat(),
                'completed_at': completed_at.isoformat(),
                'status': 'completed',
                'questions_attempted': 20,
                'questions_correct': questions_correct,
                'score': score,
                'passed': passed,
                'points_earned': int(questions_correct * 10) if passed else 0,
                'time_taken_seconds': duration_seconds,
                'hints_used': np.random.randint(0, 5),
                'feedback_viewed': np.random.choice([True, False]),
                'device_used': np.random.choice(['mobile', 'tablet', 'desktop']),
                'created_at': started_at.isoformat(),
            })
            attempt_id += 1
    
    return pd.DataFrame(quiz_attempts)

def generate_student_progress(students_df, count_per_student=5):
    """Generate synthetic student progress records."""
    student_progress = []
    progress_id = 1
    
    for _, student in students_df.iterrows():
        for _ in range(count_per_student):
            started_at = fake.date_time_between(start_date=student['created_at'])
            completion_percentage = np.random.choice([0, 25, 50, 75, 100])
            completed_at = started_at + timedelta(days=np.random.randint(1, 30)) if completion_percentage == 100 else None
            time_spent = np.random.randint(10, 300)
            
            student_progress.append({
                'progress_id': progress_id,
                'student_id': student['student_id'],
                'module_id': np.random.randint(1, 30),
                'lesson_id': np.random.randint(1, 100),
                'started_at': started_at.isoformat(),
                'completed_at': completed_at.isoformat() if completed_at else None,
                'completion_percentage': completion_percentage,
                'time_spent_minutes': time_spent,
                'points_earned': completion_percentage * 10,
                'status': 'completed' if completion_percentage == 100 else 'in_progress',
                'attempts_count': np.random.randint(1, 5),
                'bookmarked': np.random.choice([True, False]),
                'last_position_seconds': np.random.randint(0, 3600),
                'device_used': np.random.choice(['mobile', 'tablet', 'desktop']),
                'created_at': started_at.isoformat(),
                'updated_at': (started_at + timedelta(days=np.random.randint(0, 30))).isoformat(),
            })
            progress_id += 1
    
    return pd.DataFrame(student_progress)

def generate_student_skills(students_df, count_per_student=3):
    """Generate synthetic student skills records."""
    student_skills = []
    record_id = 1
    
    for _, student in students_df.iterrows():
        for _ in range(count_per_student):
            proficiency_level = np.random.randint(1, 6)
            proficiency_label = ['Beginner', 'Elementary', 'Intermediate', 'Advanced', 'Expert'][proficiency_level - 1]
            
            student_skills.append({
                'record_id': record_id,
                'student_id': student['student_id'],
                'skill_id': np.random.randint(1, 100),
                'proficiency_level': proficiency_level,
                'proficiency_label': proficiency_label,
                'practice_hours': np.random.randint(0, 100),
                'last_assessment_score': round(np.random.uniform(40, 100), 1),
                'assessments_completed': np.random.randint(0, 5),
                'certified': np.random.choice([True, False]),
                'improvement_trend': np.random.choice(['improving', 'stable', 'declining']),
                'xp_earned': np.random.randint(0, 1000),
                'source_module_id': np.random.randint(1, 30),
                'first_acquired_at': fake.date_between(start_date=student['created_at']).isoformat(),
                'last_practiced_at': fake.date_time_this_month().isoformat(),
                'created_at': fake.date_between(start_date=student['created_at']).isoformat(),
                'updated_at': datetime.now().isoformat(),
            })
            record_id += 1
    
    return pd.DataFrame(student_skills)

def generate_all_synthetic_data():
    """Generate all synthetic datasets."""
    print("🚀 Generating synthetic data for Magic Bus Compass 360...\n")
    
    print("  → Generating students...")
    students_df = generate_students(count=100)
    students_df.to_csv(f"{SYNTHETIC_DATA_DIR}/students.csv", index=False)
    print(f"    ✓ Generated {len(students_df)} students")
    
    print("  → Generating career interests...")
    interests_df = generate_career_interests(students_df, count_per_student=2)
    interests_df.to_csv(f"{SYNTHETIC_DATA_DIR}/career_interests.csv", index=False)
    print(f"    ✓ Generated {len(interests_df)} career interests")
    
    print("  → Generating quiz attempts...")
    quiz_df = generate_quiz_attempts(students_df, count_per_student=3)
    quiz_df.to_csv(f"{SYNTHETIC_DATA_DIR}/quiz_attempts.csv", index=False)
    print(f"    ✓ Generated {len(quiz_df)} quiz attempts")
    
    print("  → Generating student progress...")
    progress_df = generate_student_progress(students_df, count_per_student=5)
    progress_df.to_csv(f"{SYNTHETIC_DATA_DIR}/student_progress.csv", index=False)
    print(f"    ✓ Generated {len(progress_df)} progress records")
    
    print("  → Generating student skills...")
    skills_df = generate_student_skills(students_df, count_per_student=3)
    skills_df.to_csv(f"{SYNTHETIC_DATA_DIR}/student_skills.csv", index=False)
    print(f"    ✓ Generated {len(skills_df)} student skills")
    
    print(f"\n✅ Synthetic data generated in {SYNTHETIC_DATA_DIR}/")

if __name__ == "__main__":
    generate_all_synthetic_data()
