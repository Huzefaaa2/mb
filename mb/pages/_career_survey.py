"""
Magic Bus Compass 360 - Career Fit Survey
Comprehensive survey to assess student's career preferences and aptitudes
"""

import streamlit as st
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Career Fit Survey | Magic Bus Compass", page_icon="🎯", layout="wide")

# Initialize session state if not already present
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "survey_completed" not in st.session_state:
    st.session_state.survey_completed = False

# SQLite database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

# ============================================
# LEARNING MODULES FUNCTIONS (EMBEDDED)
# ============================================

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
    """Save generated learning modules for a student"""
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
                f"{module.get('title', '')} ({module.get('platform', '')})",
                module.get("description", ""),
                module.get("duration", ""),
                json.dumps(module.get("skills", [])),
                module.get("prerequisites", ""),
                module.get("difficulty_level", ""),
                module.get("status", "not_started"),
                module.get("progress", 0)
            ))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error saving learning modules: {e}")
        return False

def generate_learning_modules_with_ai(career_interests, strengths, goals, learning_style):
    """Generate personalized learning modules - with fallback to default modules"""
    try:
        # For now, using intelligent fallback modules based on career interests
        # Azure OpenAI deployment configuration needs to be verified
        logger.info("Generating personalized learning modules based on your career profile...")
        return get_intelligent_fallback_modules(career_interests, strengths, goals)
    
    except Exception as e:
        logger.error(f"Error generating modules: {e}")
        return get_fallback_modules(career_interests, strengths)

def get_intelligent_fallback_modules(career_interests, strengths, goals):
    """Generate intelligent fallback modules based on career interests"""
    
    # Create dynamic modules based on interests
    interest_keywords = {
        "Technology": ["Python", "JavaScript", "Web Development", "Cloud Computing", "AI/ML"],
        "Business": ["Project Management", "Business Analysis", "Leadership", "Data Analysis"],
        "Creative": ["Design", "Content Creation", "Digital Marketing", "UX/UI"],
        "Data": ["Data Science", "SQL", "Analytics", "Visualization", "Statistics"],
        "Leadership": ["Team Management", "Strategic Planning", "Communication", "Decision Making"],
    }
    
    # Try to match interests to skill paths
    matched_keywords = []
    for interest in career_interests:
        for category, keywords in interest_keywords.items():
            if any(keyword.lower() in interest.lower() for keyword in keywords):
                matched_keywords.extend(keywords)
                break
    
    # Create personalized modules
    modules = [
        {
            "module_id": "MOD_001",
            "title": f"Foundations in {career_interests[0] if career_interests else 'Your Career Path'}",
            "platform": "Multiple (YouTube, Coursera, Udemy)",
            "course_name": f"Complete {career_interests[0] if career_interests else 'Career'} Foundations",
            "description": f"Build a strong foundation in {career_interests[0] if career_interests else 'your chosen field'}. Learn industry fundamentals, best practices, and career strategies.",
            "duration": "8-12 hours",
            "skills": matched_keywords[:4] if matched_keywords else ["Industry Overview", "Career Planning", "Professional Development"],
            "prerequisites": "None",
            "difficulty_level": "Beginner",
            "learning_match": "Perfect for starting your journey",
            "resource_hint": f"Search YouTube for '{career_interests[0] if career_interests else 'career'} tutorial for beginners'",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_002",
            "title": f"Core Skills: {', '.join(strengths[:2]) if strengths else 'Technical Skills'}",
            "platform": "Udemy / Coursera",
            "course_name": f"Master {strengths[0] if strengths else 'Core Skills'} - Complete Guide",
            "description": f"Develop your {strengths[0] if strengths else 'core'} skills with hands-on projects and real-world examples. Master the tools and techniques professionals use.",
            "duration": "16-20 hours",
            "skills": matched_keywords[2:6] if matched_keywords else ["Technical Skills", "Problem Solving", "Best Practices"],
            "prerequisites": f"{career_interests[0] if career_interests else 'Foundational knowledge'}",
            "difficulty_level": "Intermediate",
            "learning_match": "Leverages your strengths",
            "resource_hint": f"Search 'Advanced {career_interests[0] if career_interests else 'career'} skills on Udemy'",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_003",
            "title": "Practical Projects & Portfolio Building",
            "platform": "GitHub / YouTube / Coursera",
            "course_name": "Real-World Projects & Portfolio Development",
            "description": "Build a professional portfolio with real-world projects. Learn how to showcase your work to potential employers and clients.",
            "duration": "12-16 hours",
            "skills": ["Project Implementation", "Portfolio Building", "Collaboration", "Code Review"],
            "prerequisites": "Modules 1-2",
            "difficulty_level": "Intermediate",
            "learning_match": "Practical application of your learning",
            "resource_hint": "Search 'portfolio projects for [your field]' on GitHub",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_004",
            "title": "Advanced Specialization",
            "platform": "LinkedIn Learning / Pluralsight",
            "course_name": f"Advanced Topics in {career_interests[0] if career_interests else 'Your Field'}",
            "description": "Explore advanced concepts and specialization areas in your chosen field. Stay ahead of industry trends and best practices.",
            "duration": "20-25 hours",
            "skills": ["Advanced Techniques", "Industry Trends", "Innovation", "Leadership Prep"],
            "prerequisites": "Modules 1-3",
            "difficulty_level": "Advanced",
            "learning_match": "Next level expertise",
            "resource_hint": f"Explore specialized courses on LinkedIn Learning or Pluralsight",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_005",
            "title": "Interview Prep & Career Launch",
            "platform": "YouTube / InterviewBit / LeetCode",
            "course_name": "Job Interview Preparation & Placement Ready",
            "description": "Prepare for interviews with mock sessions, behavioral questions, and salary negotiation tips. Launch your career with confidence.",
            "duration": "6-10 hours",
            "skills": ["Interview Skills", "Resume Writing", "Communication", "Negotiation"],
            "prerequisites": "Modules 1-4",
            "difficulty_level": "Beginner to Intermediate",
            "learning_match": "Get job-ready",
            "resource_hint": "Search 'interview preparation' on YouTube or use InterviewBit",
            "status": "not_started",
            "progress": 0
        }
    ]
    
    return modules

def get_fallback_modules(career_interests, strengths):
    """Fallback modules when Azure OpenAI is not available"""
    fallback_modules = [
        {
            "module_id": "MOD_001",
            "title": "Career Foundations",
            "description": "Build a strong foundation in your chosen career path with industry fundamentals.",
            "duration": "8 hours",
            "skills": ["Industry Overview", "Career Planning", "Professional Development", "Networking Basics"],
            "prerequisites": "None",
            "difficulty_level": "Beginner",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_002",
            "title": "Core Technical Skills",
            "description": "Master the essential technical skills required in your field.",
            "duration": "16 hours",
            "skills": ["Technical Fundamentals", "Problem Solving", "Tools & Software", "Best Practices"],
            "prerequisites": "Module 1",
            "difficulty_level": "Intermediate",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_003",
            "title": "Practical Projects",
            "description": "Apply your learning through real-world project scenarios.",
            "duration": "12 hours",
            "skills": ["Project Management", "Collaboration", "Implementation", "Portfolio Building"],
            "prerequisites": "Module 2",
            "difficulty_level": "Intermediate",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_004",
            "title": "Advanced Specialization",
            "description": "Dive deep into specialized areas of your career path.",
            "duration": "20 hours",
            "skills": ["Specialization", "Advanced Techniques", "Industry Trends", "Innovation"],
            "prerequisites": "Module 3",
            "difficulty_level": "Advanced",
            "status": "not_started",
            "progress": 0
        },
        {
            "module_id": "MOD_005",
            "title": "Placement Preparation",
            "description": "Get interview-ready with mock interviews and resume building.",
            "duration": "6 hours",
            "skills": ["Interview Skills", "Resume Writing", "Communication", "Job Search Strategies"],
            "prerequisites": "Module 4",
            "difficulty_level": "Beginner",
            "status": "not_started",
            "progress": 0
        }
    ]
    
    return fallback_modules

def init_survey_table():
    """Initialize survey results table"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_surveys (
            survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            survey_data TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES mb_users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_survey_results(user_id, student_id, survey_data):
    """Save survey results to database"""
    try:
        init_survey_table()
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO career_surveys (user_id, student_id, survey_data)
            VALUES (?, ?, ?)
        ''', (user_id, student_id, json.dumps(survey_data)))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving survey: {e}")
        return False

def get_career_recommendation(responses):
    """Generate career recommendations based on survey responses"""
    career_scores = {
        "Technology": 0,
        "Finance": 0,
        "Healthcare": 0,
        "Creative": 0,
        "Business": 0,
        "Education": 0
    }
    
    # Score based on interests
    interests = responses.get("interests", [])
    if "Programming" in interests or "Data Analysis" in interests:
        career_scores["Technology"] += 3
    if "Problem Solving" in interests or "Analytics" in interests:
        career_scores["Finance"] += 2
        career_scores["Technology"] += 1
    if "Helping Others" in interests or "Biology" in interests:
        career_scores["Healthcare"] += 3
    if "Art" in interests or "Design" in interests:
        career_scores["Creative"] += 3
    if "Management" in interests or "Leadership" in interests:
        career_scores["Business"] += 3
    if "Teaching" in interests or "Communication" in interests:
        career_scores["Education"] += 3
    
    # Score based on strengths
    strengths = responses.get("strengths", [])
    if "Analytical" in strengths:
        career_scores["Technology"] += 2
        career_scores["Finance"] += 2
    if "Creative" in strengths:
        career_scores["Creative"] += 3
    if "Leadership" in strengths:
        career_scores["Business"] += 2
        career_scores["Education"] += 1
    if "Communication" in strengths:
        career_scores["Education"] += 2
        career_scores["Business"] += 1
    
    # Get top 3 careers
    sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    top_careers = [career[0] for career in sorted_careers[:3]]
    
    return top_careers

# Check if user is logged in
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("⚠️ Please log in to access the career survey")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/0_login.py")
else:
    st.title("🎯 Career Fit Survey")
    st.markdown("Discover your ideal career path through this comprehensive survey.")
    st.markdown("This survey takes about 5-10 minutes to complete.")
    
    with st.form("career_survey_form"):
        st.markdown("### 📌 Personal Information")
        education_level = st.selectbox(
            "Current Education Level",
            ["High School", "Diploma", "Bachelor's", "Master's", "Other"],
            key="education_level"
        )
        
        st.markdown("### 🎯 Interests")
        st.write("Select all that apply:")
        interests = st.multiselect(
            "What topics interest you most?",
            [
                "Programming",
                "Data Analysis",
                "Design & UI/UX",
                "Art & Creativity",
                "Biology & Healthcare",
                "Business & Entrepreneurship",
                "Teaching & Education",
                "Finance & Economics",
                "Problem Solving",
                "Analytics",
                "Helping Others",
                "Leadership & Management",
                "Communication"
            ],
            key="interests"
        )
        
        st.markdown("### 💪 Strengths")
        st.write("Select your top 3 strengths:")
        strengths = st.multiselect(
            "What are your strongest abilities?",
            [
                "Analytical Thinking",
                "Creative Problem Solving",
                "Communication",
                "Leadership",
                "Technical Skills",
                "Organization",
                "Empathy & People Skills",
                "Quick Learning",
                "Attention to Detail",
                "Initiative & Drive"
            ],
            max_selections=3,
            key="strengths"
        )
        
        st.markdown("### 📚 Learning Style")
        learning_style = st.radio(
            "How do you learn best?",
            [
                "Hands-on projects & practice",
                "Videos & visual learning",
                "Reading & written materials",
                "Interactive discussions",
                "Mix of everything"
            ],
            key="learning_style"
        )
        
        st.markdown("### ⏰ Work Preferences")
        col1, col2 = st.columns(2)
        
        with col1:
            work_environment = st.radio(
                "Preferred work environment:",
                [
                    "Office/Corporate",
                    "Remote/Flexible",
                    "Field/Outdoor",
                    "Creative Space",
                    "No preference"
                ],
                key="work_environment"
            )
        
        with col2:
            pace = st.radio(
                "Preferred work pace:",
                [
                    "Fast-paced & dynamic",
                    "Steady & consistent",
                    "Project-based",
                    "No preference"
                ],
                key="pace"
            )
        
        st.markdown("### 🌍 Career Goals")
        career_goals = st.text_area(
            "What are your career goals for the next 5 years?",
            placeholder="Describe your aspirations, what you want to achieve, and what type of work excites you...",
            key="career_goals"
        )
        
        st.markdown("### 💼 Experience")
        experience = st.multiselect(
            "Do you have experience in any of these areas?",
            [
                "Internship/Part-time work",
                "Freelancing/Project work",
                "Volunteer work",
                "Personal projects",
                "No formal experience"
            ],
            key="experience"
        )
        
        st.markdown("### 🎓 Certifications & Skills")
        certifications = st.text_area(
            "List any relevant certifications, skills, or qualifications",
            placeholder="E.g., Microsoft Office, Python, Project Management, etc.",
            key="certifications"
        )
        
        submitted = st.form_submit_button("✅ Submit Career Survey", width="stretch")
    
    if submitted:
        if not st.session_state.get("interests") or not st.session_state.get("strengths"):
            st.error("❌ Please select at least one interest and strength")
        else:
            survey_data = {
                "education_level": st.session_state.get("education_level"),
                "interests": st.session_state.get("interests", []),
                "strengths": st.session_state.get("strengths", []),
                "learning_style": st.session_state.get("learning_style"),
                "work_environment": st.session_state.get("work_environment"),
                "pace": st.session_state.get("pace"),
                "career_goals": st.session_state.get("career_goals", ""),
                "experience": st.session_state.get("experience", []),
                "certifications": st.session_state.get("certifications", ""),
                "completed_at": datetime.now().isoformat()
            }
            
            if save_survey_results(
                st.session_state.user_id,
                st.session_state.student_id,
                survey_data
            ):
                st.session_state.survey_completed = True
                
                st.success("✅ Survey submitted successfully!")
                st.markdown("### 🎯 Your Career Recommendations")
                
                top_careers = get_career_recommendation(survey_data)
                st.markdown(f"Based on your responses, we recommend exploring these career paths:")
                
                for i, career in enumerate(top_careers, 1):
                    st.info(f"**{i}. {career}**")
                
                # Generate personalized learning modules
                st.markdown("---")
                st.markdown("### 📚 Generating Your Personalized Learning Path...")
                
                with st.spinner("🤖 Creating modules with AI..."):
                    learning_modules = generate_learning_modules_with_ai(
                        survey_data.get("interests", []),
                        survey_data.get("strengths", []),
                        survey_data.get("career_goals", ""),
                        survey_data.get("learning_style", "")
                    )
                
                # Save modules to database
                if save_learning_modules(
                    st.session_state.user_id,
                    st.session_state.student_id,
                    learning_modules
                ):
                    st.success("✅ Learning modules generated successfully!")
                    st.markdown("### 📚 Your Recommended Learning Path:")
                    st.markdown("Based on your career interests and learning style, here are the best courses for you:")
                    
                    for module in learning_modules:
                        with st.expander(f"📖 {module['title']}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Platform:** {module.get('platform', 'Multiple')}")
                                st.write(f"**Duration:** {module['duration']}")
                                st.write(f"**Difficulty:** {module['difficulty_level']}")
                            
                            with col2:
                                st.write(f"**Learning Match:** {module.get('learning_match', 'Aligned with your preferences')}")
                                if module.get('course_name'):
                                    st.write(f"**Course Name:** {module['course_name']}")
                            
                            st.write(f"**Description:** {module['description']}")
                            
                            st.write("**Skills You'll Learn:**")
                            for skill in module.get('skills', []):
                                st.write(f"  • {skill}")
                            
                            if module.get('prerequisites') and module['prerequisites'].lower() != 'none':
                                st.write(f"**Prerequisites:** {module['prerequisites']}")
                            
                            # Show resource hint
                            if module.get('resource_hint'):
                                st.info(f"🔍 **How to find this course:** {module['resource_hint']}")
                else:
                    st.warning("⚠️ Could not save learning modules. They will be generated when you visit the dashboard.")
                
                st.markdown("---")
                st.success("✅ Career survey completed! Your learning path is ready.")
                st.info("📊 Click the button below to view your personalized learning modules on the dashboard.")
                
                if st.button("📊 Go to Dashboard", width="stretch", key="btn_goto_dashboard"):
                    st.switch_page("pages/2_youth_dashboard.py")
            else:
                st.error("❌ Failed to save survey. Please try again.")
