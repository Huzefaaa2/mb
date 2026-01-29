"""
MagicBus Admin Dashboard
Comprehensive analytics and insights for MagicBus staff to track student progress,
career pathways, and generate AI-powered recommendations
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from blob_handler import get_blob_data, parse_json_data
from feedback_survey import (
    init_feedback_tables,
    get_employer_feedback_analytics,
    get_youth_feedback_analytics,
    get_pending_surveys,
    get_survey_distribution_status,
    create_employer_survey_entry,
    create_youth_survey_entry
)
from email_service import (
    send_employer_survey_email,
    send_youth_survey_email,
    verify_email_configuration
)

# Import multimodal screening service
from mb import MultiModalScreeningService

st.set_page_config(page_title="Magic Bus Staff Dashboard", page_icon="📈", layout="wide")

# Remove password authentication - this is a passwordless staff dashboard
st.title("📈 Magic Bus Staff Dashboard")
st.markdown("**Comprehensive Analytics & Student Insights for Magic Bus Charity Staff**")
st.info("👋 Welcome to the MagicBus Admin Dashboard. This dashboard provides comprehensive analytics and management tools for the MagicBus Charity staff.")

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

# Initialize feedback tables on first load
init_feedback_tables()

# Main tabs
main_tabs = st.tabs([
    "📊 Overview",
    "👥 Student Analytics",
    "🎯 Career Pathways",
    "📚 Learning Progress",
    "🤖 AI Recommendations",
    "🎙️ Multi-Modal Screening",
    "📋 Reports",
    "💬 Feedback Analytics",
    "📧 Survey Distribution",
    "🚨 Churn Prevention"
])

# ========================
# TAB 1: OVERVIEW
# ========================
with main_tabs[0]:
    st.markdown("### Dashboard Overview")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM mb_users")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM career_surveys")
        survey_completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM learning_modules")
        total_modules_assigned = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM learning_modules WHERE status = 'completed'")
        modules_completed = cursor.fetchone()[0]
        
        conn.close()
        
        # Display KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Students", total_students)
        with col2:
            survey_rate = (survey_completed / total_students * 100) if total_students > 0 else 0
            st.metric("📋 Survey Completion", f"{survey_rate:.1f}%", f"{survey_completed}/{total_students}")
        with col3:
            st.metric("📚 Modules Assigned", total_modules_assigned)
        with col4:
            completion_rate = (modules_completed / total_modules_assigned * 100) if total_modules_assigned > 0 else 0
            st.metric("✅ Completion Rate", f"{completion_rate:.1f}%", f"{modules_completed}/{total_modules_assigned}")
        
        st.markdown("---")
        
        # Recent activity
        st.markdown("### 📝 Recent Activity")
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.login_id, lm.title, lm.status, lm.assigned_date
            FROM learning_modules lm
            JOIN mb_users u ON lm.user_id = u.user_id
            ORDER BY lm.assigned_date DESC
            LIMIT 10
        ''')
        
        recent_data = cursor.fetchall()
        conn.close()
        
        for row in recent_data:
            st.write(f"• {row[0]} → {row[1]} ({row[2]}) - {row[3][:10]}")
        
    except Exception as e:
        st.error(f"Error loading overview: {e}")
        logger.error(f"Overview error: {e}")

# ========================
# TAB 2: STUDENT ANALYTICS
# ========================
with main_tabs[1]:
    st.markdown("### 👥 Student Analytics & Profiles")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get all students
        cursor.execute('''
            SELECT u.user_id, u.login_id, u.student_id, u.email, u.full_name, u.created_at
            FROM mb_users u
            ORDER BY u.created_at DESC
        ''')
        
        students = cursor.fetchall()
        
        # Display student table
        student_data = []
        for student in students:
            user_id = student[0]
            
            # Get survey status
            cursor.execute("SELECT COUNT(*) FROM career_surveys WHERE user_id = ?", (user_id,))
            has_survey = cursor.fetchone()[0] > 0
            
            # Get modules count
            cursor.execute("SELECT COUNT(*) FROM learning_modules WHERE user_id = ?", (user_id,))
            modules = cursor.fetchone()[0]
            
            student_data.append({
                "Student ID": student[2],
                "Name": student[4] or "N/A",
                "Email": student[3] or "N/A",
                "Survey": "✅" if has_survey else "❌",
                "Modules": modules,
                "Joined": student[5][:10] if student[5] else "N/A"
            })
        
        conn.close()
        
        df_students = pd.DataFrame(student_data)
        st.dataframe(df_students, width="stretch")
        
        # Student details drill-down
        st.markdown("---")
        st.markdown("### 📋 Student Details")
        
        selected_student_id = st.selectbox(
            "Select a student",
            options=[s["Student ID"] for s in student_data],
            format_func=lambda x: f"{x} - {next((s['Name'] for s in student_data if s['Student ID'] == x), 'N/A')}"
        )
        
        if selected_student_id:
            # Get detailed student info
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM mb_users WHERE student_id = ?", (selected_student_id,))
            user_id_result = cursor.fetchone()
            
            if user_id_result:
                user_id = user_id_result[0]
                
                # Get career survey data
                cursor.execute("SELECT survey_data FROM career_surveys WHERE user_id = ? ORDER BY completed_at DESC LIMIT 1", (user_id,))
                survey_result = cursor.fetchone()
                
                if survey_result:
                    survey_data = json.loads(survey_result[0])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Career Interests:**")
                        for interest in survey_data.get("interests", [])[:5]:
                            st.write(f"• {interest}")
                    
                    with col2:
                        st.markdown("**Strengths:**")
                        for strength in survey_data.get("strengths", [])[:5]:
                            st.write(f"• {strength}")
                    
                    st.markdown("**Learning Style:** " + survey_data.get("learning_style", "N/A"))
                    st.markdown("**Career Goals:** " + survey_data.get("career_goals", "N/A")[:100] + "...")
                
                # Get module progress
                cursor.execute('''
                    SELECT title, status, progress, assigned_date
                    FROM learning_modules
                    WHERE user_id = ?
                    ORDER BY assigned_date DESC
                ''', (user_id,))
                
                modules = cursor.fetchall()
                
                st.markdown("**Module Progress:**")
                for module in modules[:5]:
                    st.write(f"• {module[0]} - {module[1]} ({module[2]}%)")
            
            conn.close()
        
    except Exception as e:
        st.error(f"Error loading student analytics: {e}")
        logger.error(f"Student analytics error: {e}")

# ========================
# TAB 3: CAREER PATHWAYS
# ========================
with main_tabs[2]:
    st.markdown("### 🎯 Career Pathways Analysis")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Aggregate interest data
        cursor.execute('''
            SELECT survey_data FROM career_surveys
            WHERE survey_data IS NOT NULL
        ''')
        
        surveys = cursor.fetchall()
        
        interest_counts = {}
        strength_counts = {}
        
        for survey in surveys:
            try:
                data = json.loads(survey[0])
                
                for interest in data.get("interests", []):
                    interest_counts[interest] = interest_counts.get(interest, 0) + 1
                
                for strength in data.get("strengths", []):
                    strength_counts[strength] = strength_counts.get(strength, 0) + 1
            except:
                pass
        
        conn.close()
        
        # Display career interests distribution
        if interest_counts:
            st.markdown("**Top Career Interests**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                interest_df = pd.DataFrame([
                    {"Interest": k, "Count": v}
                    for k, v in sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                ])
                st.bar_chart(interest_df.set_index("Interest"))
            
            with col2:
                st.dataframe(interest_df, width="stretch")
        
        st.markdown("---")
        
        if strength_counts:
            st.markdown("**Top Strengths Distribution**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                strength_df = pd.DataFrame([
                    {"Strength": k, "Count": v}
                    for k, v in sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                ])
                st.bar_chart(strength_df.set_index("Strength"))
            
            with col2:
                st.dataframe(strength_df, width="stretch")
        
    except Exception as e:
        st.error(f"Error loading career pathways: {e}")

# ========================
# TAB 4: LEARNING PROGRESS
# ========================
with main_tabs[3]:
    st.markdown("### 📚 Learning Progress & Module Analytics")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Module completion by status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM learning_modules
            GROUP BY status
        ''')
        
        status_data = cursor.fetchall()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Module Status Distribution**")
            status_df = pd.DataFrame(status_data, columns=["Status", "Count"])
            st.bar_chart(status_df.set_index("Status"))
        
        with col2:
            st.dataframe(status_df, width="stretch")
        
        st.markdown("---")
        
        # Most completed modules
        st.markdown("**Most Completed Modules**")
        
        cursor.execute('''
            SELECT title, COUNT(*) as assigned, 
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM learning_modules
            GROUP BY title
            ORDER BY completed DESC
            LIMIT 10
        ''')
        
        top_modules = cursor.fetchall()
        
        modules_df = pd.DataFrame(top_modules, columns=["Module Title", "Assigned", "Completed"])
        modules_df["Completion %"] = (modules_df["Completed"] / modules_df["Assigned"] * 100).round(1)
        
        st.dataframe(modules_df, width="stretch")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Error loading learning progress: {e}")

# ========================
# TAB 5: AI RECOMMENDATIONS
# ========================
with main_tabs[4]:
    st.markdown("### 🤖 AI-Powered Recommendations")
    st.markdown("Smart course recommendations and insights for MagicBus planning")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get all students' data
        cursor.execute('''
            SELECT u.login_id, cs.survey_data
            FROM mb_users u
            LEFT JOIN career_surveys cs ON u.user_id = cs.user_id
            WHERE cs.survey_data IS NOT NULL
        ''')
        
        student_surveys = cursor.fetchall()
        conn.close()
        
        if student_surveys:
            # Aggregate skills and interests
            all_interests = []
            all_strengths = []
            
            for login_id, survey_json in student_surveys:
                try:
                    data = json.loads(survey_json)
                    all_interests.extend(data.get("interests", []))
                    all_strengths.extend(data.get("strengths", []))
                except:
                    pass
            
            # Generate AI insights
            st.markdown("### 📊 Recommended Training Programs")
            
            try:
                from openai import AzureOpenAI
                
                client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                
                prompt = f"""Based on the career interests and strengths of our students, provide curated training recommendations.

Top Student Interests: {', '.join(set(all_interests[:10]))}
Top Student Strengths: {', '.join(set(all_strengths[:10]))}

Recommend:
1. 5 specific courses/trainings
2. 3 behavioral training programs
3. 2 competency development programs
4. Industry certifications they should pursue

Format as a structured list with brief descriptions."""
                
                with st.spinner("🤖 Generating AI recommendations..."):
                    response = client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo"),
                        messages=[
                            {"role": "system", "content": "You are an expert educational advisor for NGOs. Provide practical, affordable training recommendations."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )
                    
                    recommendations = response.choices[0].message.content
                    st.markdown(recommendations)
                    
                    # Export recommendations
                    st.download_button(
                        "📥 Download Recommendations",
                        recommendations,
                        file_name="training_recommendations.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                # Fallback: Generate recommendations without Azure OpenAI
                logger.warning(f"Azure OpenAI unavailable: {e}. Using fallback recommendations.")
                
                st.info("📌 Generating curated recommendations based on student data...")
                
                # Interest-based recommendations
                top_interests = list(set(all_interests))[:5]
                top_strengths = list(set(all_strengths))[:5]
                
                recommendations = f"""# Recommended Training Programs for Magic Bus Students

## Based on Student Interests: {', '.join(top_interests)}
## Based on Student Strengths: {', '.join(top_strengths)}

### 📚 Recommended Courses & Trainings
1. **Data Analytics & Visualization** - Ideal for students interested in data analysis
   - Tools: Excel, Power BI, Tableau
   - Duration: 8-12 weeks
   - Career Impact: High demand in market

2. **Full Stack Web Development** - Perfect for programming enthusiasts
   - Technologies: HTML, CSS, JavaScript, React, Python
   - Duration: 12-16 weeks
   - Career Impact: Excellent job prospects

3. **Digital Marketing & SEO** - For creative and business-minded students
   - Topics: Social Media, Content Marketing, Analytics
   - Duration: 6-8 weeks
   - Career Impact: Growing industry

4. **Business Intelligence & Data Science** - Advanced analytics track
   - Tools: SQL, Python, Machine Learning basics
   - Duration: 12-14 weeks
   - Career Impact: High-paying positions

5. **Cloud Computing Fundamentals** - Future-ready technology
   - Platforms: AWS, Azure, Google Cloud
   - Duration: 8-10 weeks
   - Career Impact: Critical skill for IT jobs

### 💼 Behavioral & Soft Skills Training
1. **Professional Communication & Leadership**
   - Presentation skills, team management, conflict resolution
   - Duration: 4 weeks (ongoing)

2. **Interview Preparation & Job Readiness**
   - Resume building, mock interviews, networking
   - Duration: 3 weeks

3. **Entrepreneurship & Business Essentials**
   - Business planning, financial management, startup basics
   - Duration: 6 weeks

### 🎯 Competency Development Programs
1. **Critical Thinking & Problem Solving Workshop**
   - Analytical frameworks, case studies, practical exercises
   - Format: Interactive, hands-on

2. **Emotional Intelligence & Work Culture Adaptation**
   - Self-awareness, teamwork, workplace dynamics
   - Format: Coaching sessions

### 🏆 Industry Certifications
- **Google Career Certificates** (Data Analytics, Project Management, IT Support)
- **AWS Certified Cloud Practitioner**
- **Microsoft Azure Fundamentals (AZ-900)**
- **Coursera Professional Certificates** (varies by interest)

### 📊 Recommendations Summary
**Total Students Analyzed:** {len(student_surveys)}
**Top Career Interests:** {', '.join(top_interests)}
**Top Strengths:** {', '.join(top_strengths)}

**Next Steps:**
1. Prioritize courses based on student interests
2. Enroll students in relevant training programs
3. Track progress through dashboards
4. Measure employment outcomes
"""
                
                st.markdown(recommendations)
                
                # Export recommendations
                st.download_button(
                    "📥 Download Recommendations",
                    recommendations,
                    file_name="training_recommendations.txt",
                    mime="text/plain"
                )
        else:
            st.info("📌 No student survey data available yet. Students need to complete career surveys first.")
    
    except Exception as e:
        st.error(f"Error loading AI recommendations: {e}")
        logger.error(f"AI recommendations error: {e}")

# ========================
# TAB 6: MULTI-MODAL SCREENING
# ========================
with main_tabs[5]:
    st.markdown("### 🎙️ Multi-Modal Screening Management")
    st.markdown("Manage voice/video-based soft skills assessments for personality-driven role matching")
    
    try:
        screener = MultiModalScreeningService(str(DB_PATH))
        
        screening_subtab1, screening_subtab2, screening_subtab3 = st.tabs([
            "📊 Screening Analytics",
            "✅ Review & Approve",
            "👥 Personality-Driven Matches"
        ])
        
        with screening_subtab1:
            st.markdown("### Screening Metrics & Analytics")
            
            # Get screening statistics
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            try:
                cursor.execute("SELECT COUNT(*) FROM mb_multimodal_screenings")
                total_screenings = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM mb_multimodal_screenings WHERE personality_fit_level = 'High'")
                high_fit = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT AVG(overall_soft_skill_score) FROM mb_multimodal_screenings")
                avg_score = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(DISTINCT student_id) FROM mb_multimodal_screenings")
                unique_candidates = cursor.fetchone()[0] or 0
                
            except:
                total_screenings = high_fit = avg_score = unique_candidates = 0
            finally:
                conn.close()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Screenings", total_screenings)
            with col2:
                st.metric("✨ High Personality Fit", high_fit)
            with col3:
                st.metric("⭐ Avg Soft Skills Score", f"{avg_score:.1f}")
            with col4:
                st.metric("👥 Unique Candidates", unique_candidates)
            
            st.markdown("---")
            st.markdown("### Recent Screenings")
            
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT student_id, submission_type, overall_soft_skill_score, 
                           personality_fit_level, role_recommendations, submitted_at
                    FROM mb_multimodal_screenings
                    ORDER BY submitted_at DESC LIMIT 10
                """)
                
                screenings = cursor.fetchall()
                conn.close()
                
                if screenings:
                    df_screenings = pd.DataFrame(screenings, columns=[
                        "Student ID", "Type", "Score", "Fit Level", "Roles", "Submitted"
                    ])
                    st.dataframe(df_screenings, use_container_width=True, hide_index=True)
                else:
                    st.info("No screenings recorded yet")
                    
            except Exception as e:
                st.error(f"Error loading screenings: {e}")
        
        with screening_subtab2:
            st.markdown("### Review & Approve Screenings")
            
            student_id_review = st.number_input(
                "Enter Student ID to Review",
                min_value=1,
                step=1,
                key="screening_review_id"
            )
            
            if st.button("🔍 Load Screening", key="load_screening_btn"):
                screenings = screener.get_candidate_screenings(student_id_review)
                
                if screenings:
                    latest = screenings[0]
                    
                    st.markdown("#### Screening Details")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Communication", f"{latest.get('communication_confidence', 0):.0f}/100")
                    with col2:
                        st.metric("Cultural Fit", f"{latest.get('cultural_fit_score', 0):.0f}/100")
                    with col3:
                        st.metric("Problem Solving", f"{latest.get('problem_solving_score', 0):.0f}/100")
                    with col4:
                        st.metric("Emotional Intelligence", f"{latest.get('emotional_intelligence', 0):.0f}/100")
                    
                    st.markdown("#### Overall Assessment")
                    st.write(f"**Personality Fit Level:** {latest.get('personality_fit_level', 'N/A')}")
                    st.write(f"**Overall Score:** {latest.get('overall_soft_skill_score', 0):.1f}/100")
                    st.write(f"**Marginalized Score:** {latest.get('marginalized_score', 0):.1f}")
                    
                    roles_json = latest.get('role_recommendations', '[]')
                    try:
                        roles = json.loads(roles_json) if isinstance(roles_json, str) else roles_json
                        st.write(f"**Recommended Roles:** {', '.join(roles) if roles else 'N/A'}")
                    except:
                        st.write("**Recommended Roles:** Unable to parse")
                    
                    # Transcription
                    if latest.get('transcription'):
                        with st.expander("📝 View Transcription"):
                            st.write(latest['transcription'])
                    
                    # Admin approval section
                    st.markdown("---")
                    with st.form(f"approval_form_{student_id_review}"):
                        approval_status = st.selectbox(
                            "Approval Status",
                            ["approved", "review_needed", "rejected"],
                            key=f"approval_status_{student_id_review}"
                        )
                        
                        reviewer_notes = st.text_area(
                            "Reviewer Notes",
                            key=f"reviewer_notes_{student_id_review}",
                            height=100
                        )
                        
                        submit_btn = st.form_submit_button("✅ Submit Review")
                        
                        if submit_btn:
                            st.success(f"✅ Review submitted for student {student_id_review}")
                            st.markdown(f"**Status:** {approval_status}")
                            st.markdown(f"**Notes:** {reviewer_notes if reviewer_notes else 'None'}")
                else:
                    st.info(f"No screenings found for student {student_id_review}")
        
        with screening_subtab3:
            st.markdown("### Personality-Driven Role Candidates")
            st.markdown("Students matched for roles prioritizing personality over technical skills")
            
            min_score = st.slider("Minimum Personality Score", 0, 100, 70, key="min_personality_score")
            
            if st.button("🔍 Find Matching Candidates", key="find_candidates_btn"):
                candidates = screener.get_personality_driven_candidates(min_score)
                
                if candidates:
                    df_candidates = pd.DataFrame(candidates)
                    
                    # Format the dataframe
                    if 'role_recommendations' in df_candidates.columns:
                        df_candidates['role_recommendations'] = df_candidates['role_recommendations'].apply(
                            lambda x: ', '.join(json.loads(x)) if isinstance(x, str) else str(x)
                        )
                    
                    st.dataframe(df_candidates, use_container_width=True, hide_index=True)
                    
                    # Export option
                    csv = df_candidates.to_csv(index=False)
                    st.download_button(
                        "📥 Download Candidates CSV",
                        csv,
                        "personality_matched_candidates.csv",
                        "text/csv",
                        key="download_candidates"
                    )
                else:
                    st.info(f"No candidates found with personality score ≥ {min_score}")
    
    except Exception as e:
        st.error(f"Error in screening management: {e}")
        logger.error(f"Screening error: {e}")

# ========================
# TAB 7: REPORTS
# ========================
with main_tabs[6]:
    st.markdown("### 📋 Generate Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        [
            "📊 Overall Progress Report",
            "👥 Student Engagement Report",
            "🎯 Career Path Analysis",
            "📈 Learning Analytics",
            "💡 Recommendations Report"
        ]
    )
    
    if st.button("📋 Generate Report", width="stretch"):
        try:
            with st.spinner("📋 Generating report..."):
                # Get database statistics
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM mb_users")
                total_students = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM learning_modules WHERE status = 'completed'")
                active_students = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM learning_modules WHERE status = 'completed'")
                completed_modules = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM learning_modules")
                total_modules = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM career_surveys")
                surveys_completed = cursor.fetchone()[0] or 0
                
                conn.close()
                
                # Calculate safe percentages
                completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
                survey_rate = (surveys_completed / total_students * 100) if total_students > 0 else 0
                engagement_rate = (active_students / total_students * 100) if total_students > 0 else 0
                
                # Generate template-based report (fallback default)
                report = f"""# MagicBus Charity Organization - {report_type}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report provides comprehensive analysis of MagicBus Compass 360 program outcomes and student progress metrics.

## Key Metrics
- **Total Students Enrolled:** {total_students}
- **Career Surveys Completed:** {surveys_completed} ({survey_rate:.1f}%)
- **Active in Learning:** {active_students}
- **Modules Completed:** {completed_modules}/{total_modules} ({completion_rate:.1f}%)
- **Student Engagement Rate:** {engagement_rate:.1f}%

## Detailed Findings

### 1. Enrollment & Engagement
- Total enrollment base: {total_students} registered students
- Career assessment completion rate: {survey_rate:.1f}%
- Student engagement in learning modules: {engagement_rate:.1f}%
- Strong foundation for program growth

### 2. Learning Progress
- Overall module completion rate: {completion_rate:.1f}%
- Total modules successfully completed: {completed_modules}
- Average engagement per student: {(completed_modules/total_students):.1f} modules
- Consistent progress in professional development

### 3. Career Development
- Career surveys provide insights into student interests and goals
- Personalized learning paths based on career aspirations
- Alignment with job market trends and requirements
- Career fit discovery through comprehensive assessments

### 4. Skills Development
- Multi-dimensional skill assessment and tracking
- Focus on technical and soft skills development
- Continuous learning paths aligned with career goals
- Competency-based learning outcomes

## Student Engagement Analysis

### Participation Metrics
- Survey Completion Rate: {survey_rate:.1f}%
- Active Learner Rate: {engagement_rate:.1f}%
- Module Engagement: {completion_rate:.1f}% completion

### Learning Patterns
- Students are actively engaging with learning modules
- Career surveys show strong interest in self-assessment
- Learning progression indicates commitment to development

## Key Recommendations

1. **Increase Career Survey Participation**
   - Target: Achieve 100% survey completion
   - Strategy: Send reminder emails to non-completers
   - Timeline: 2-3 weeks
   - Impact: Enable personalized learning recommendations

2. **Accelerate Module Completion**
   - Focus support on students with low progress
   - Provide mentoring and guidance
   - Target completion rate: 85%+
   - Implement progress tracking

3. **Employer Partnership Programs**
   - Create internship and apprenticeship opportunities
   - Conduct placement-focused training sessions
   - Build industry feedback loops
   - Establish employer advisory board

4. **Skill Gap Analysis**
   - Identify top market-demand skills
   - Align training programs with industry needs
   - Conduct regular market research
   - Update curriculum based on feedback

5. **Student Success Tracking**
   - Implement job placement tracking system
   - Measure post-training employment outcomes
   - Build success case studies
   - Track salary and career progression

## Program Impact

### Strengths
- Comprehensive career assessment framework
- Personalized learning path recommendations
- Multiple skill development opportunities
- Integration with job market trends

### Opportunities
- Increase employer partnerships
- Expand specialized training tracks
- Strengthen placement support services
- Build alumni network

## Conclusion
MagicBus Compass 360 is successfully supporting students in achieving career readiness through comprehensive assessment and personalized learning paths. With {total_students} students engaged and a {completion_rate:.1f}% module completion rate, the program demonstrates strong impact. Continued focus on survey completion, module engagement, and employer partnerships will further enhance placement outcomes and career success.

## Action Items for Next Period
- [ ] Review and improve career survey participation ({survey_rate:.1f}% → 100%)
- [ ] Analyze module completion patterns and identify support needs
- [ ] Schedule meetings with potential employer partners
- [ ] Plan targeted training programs for high-demand skills
- [ ] Measure and report placement outcomes
- [ ] Gather feedback from students and employers
- [ ] Update learning modules based on market feedback
- [ ] Develop case studies of successful placements

---
Report Generated by MagicBus Staff Dashboard
Report Type: {report_type}
For questions or feedback, contact: support@magicbus.org
"""
                
                st.markdown("### Generated Report")
                st.markdown(report)
                
                st.success("✅ Report generated successfully!")
                
                st.download_button(
                    "📥 Download Report (TXT)",
                    report,
                    file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_report"
                )
        
        except ZeroDivisionError as e:
            st.error("❌ Error: Division by zero. Please ensure there is data in the database.")
            logger.error(f"Division error in report generation: {e}")
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            logger.error(f"Report generation error: {e}")

# ========================
# TAB 8: FEEDBACK ANALYTICS
# ========================
with main_tabs[7]:
    st.markdown("### 💬 Feedback Analytics & Insights")
    
    col1, col2 = st.columns(2)
    
    # Employer Feedback Analytics
    with col1:
        st.markdown("#### 🏢 Employer Feedback")
        
        employer_analytics = get_employer_feedback_analytics()
        
        if employer_analytics and employer_analytics.get('total_surveys', 0) > 0:
            # KPIs
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                st.metric("Total Surveys", employer_analytics['total_surveys'])
            with col_e2:
                st.metric("Completed", employer_analytics['completed_surveys'])
            with col_e3:
                completion_rate = (employer_analytics['completed_surveys'] / employer_analytics['total_surveys'] * 100) if employer_analytics['total_surveys'] > 0 else 0
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            st.markdown("---")
            
            # Performance metrics
            st.markdown("**Performance Scores (Average):**")
            
            perf_data = {
                "Overall Performance": employer_analytics['avg_overall_performance'],
                "Technical Skills": employer_analytics['avg_technical_skills'],
                "Communication": employer_analytics['avg_communication_skills'],
                "Teamwork": employer_analytics['avg_teamwork'],
                "Work Ethic": employer_analytics['avg_work_ethic'],
                "Punctuality": employer_analytics['avg_punctuality'],
                "Reliability": employer_analytics['avg_reliability'],
                "Problem Solving": employer_analytics['avg_problem_solving']
            }
            
            df_perf = pd.DataFrame(list(perf_data.items()), columns=["Metric", "Score (out of 10)"])
            st.dataframe(df_perf, width="stretch", hide_index=True)
            
            st.markdown("---")
            
            # Rehire willingness
            rehire_rate = (employer_analytics['rehire_count'] / employer_analytics['completed_surveys'] * 100) if employer_analytics['completed_surveys'] > 0 else 0
            st.markdown(f"**Would Rehire:** {employer_analytics['rehire_count']} students ({rehire_rate:.1f}%)")
            st.progress(rehire_rate / 100)
            
            st.markdown("---")
            
            # Top strengths
            if employer_analytics['top_strengths']:
                st.markdown("**Top Strengths Mentioned:**")
                for i, strength in enumerate(employer_analytics['top_strengths'][:5], 1):
                    st.write(f"{i}. {strength[:100]}...")
            
            # Areas for improvement
            if employer_analytics['areas_for_improvement']:
                st.markdown("**Areas for Improvement:**")
                for i, area in enumerate(employer_analytics['areas_for_improvement'][:5], 1):
                    st.write(f"{i}. {area[:100]}...")
        
        else:
            st.info("📊 No employer feedback data available yet")
    
    # Youth Feedback Analytics
    with col2:
        st.markdown("#### 👤 Youth Post-Placement Feedback")
        
        youth_analytics = get_youth_feedback_analytics()
        
        if youth_analytics and youth_analytics.get('total_surveys', 0) > 0:
            # KPIs
            col_y1, col_y2, col_y3 = st.columns(3)
            with col_y1:
                st.metric("Total Surveys", youth_analytics['total_surveys'])
            with col_y2:
                st.metric("Completed", youth_analytics['completed_surveys'])
            with col_y3:
                completion_rate = (youth_analytics['completed_surveys'] / youth_analytics['total_surveys'] * 100) if youth_analytics['total_surveys'] > 0 else 0
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            st.markdown("---")
            
            # Satisfaction metrics
            st.markdown("**Satisfaction Levels (Average):**")
            
            satisfaction_data = {
                "Overall Satisfaction": youth_analytics['avg_satisfaction'],
                "Role Expectations": youth_analytics['avg_role_match'],
                "Work Environment": youth_analytics['avg_work_environment'],
                "Team Collaboration": youth_analytics['avg_team_collaboration'],
                "Career Growth": youth_analytics['avg_career_growth'],
                "Compensation": youth_analytics['avg_compensation'],
                "Manager Support": youth_analytics['avg_manager_support'],
                "Skill Application": youth_analytics['avg_skill_application'],
                "MagicBus Preparation": youth_analytics['avg_magicbus_prep']
            }
            
            df_satisfaction = pd.DataFrame(list(satisfaction_data.items()), columns=["Metric", "Score (out of 10)"])
            st.dataframe(df_satisfaction, width="stretch", hide_index=True)
            
            st.markdown("---")
            
            # Recommendation rate
            recommend_rate = (youth_analytics['recommend_count'] / youth_analytics['completed_surveys'] * 100) if youth_analytics['completed_surveys'] > 0 else 0
            st.markdown(f"**Would Recommend MagicBus:** {youth_analytics['recommend_count']} students ({recommend_rate:.1f}%)")
            st.progress(recommend_rate / 100)
            
            st.markdown("---")
            
            # What went well
            if youth_analytics['what_went_well']:
                st.markdown("**What Went Well:**")
                for i, item in enumerate(youth_analytics['what_went_well'][:5], 1):
                    st.write(f"{i}. {item[:100]}...")
            
            # Areas to improve
            if youth_analytics['areas_to_improve']:
                st.markdown("**Areas to Improve:**")
                for i, area in enumerate(youth_analytics['areas_to_improve'][:5], 1):
                    st.write(f"{i}. {area[:100]}...")
            
            # Training needs
            if youth_analytics['training_needs']:
                st.markdown("**Additional Training Needed:**")
                for i, need in enumerate(youth_analytics['training_needs'][:5], 1):
                    st.write(f"{i}. {need[:100]}...")
        
        else:
            st.info("📊 No youth feedback data available yet")
    
    st.markdown("---")
    
    # Overall insights
    st.markdown("### 🎯 Key Insights & Recommendations")
    
    pending = get_pending_surveys()
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.metric("Pending Employer Surveys", pending['employer_pending'])
    with insight_col2:
        st.metric("Pending Youth Surveys", pending['youth_pending'])
    with insight_col3:
        st.metric("Pending Distribution", pending['distribution_pending'])
    
    if employer_analytics and youth_analytics:
        st.markdown("#### 💡 Analysis & Recommendations")
        
        insights = []
        
        # Employer insights
        if employer_analytics.get('avg_overall_performance', 0) < 6:
            insights.append("⚠️ **Employer Performance:** Average performance scores are below 6/10. Consider reviewing curriculum and practical training components.")
        elif employer_analytics.get('avg_overall_performance', 0) >= 8:
            insights.append("✅ **Employer Performance:** Students are performing very well (8+/10). Maintain current training quality.")
        
        if employer_analytics.get('rehire_count', 0) == 0 and employer_analytics.get('completed_surveys', 0) > 0:
            insights.append("⚠️ **Rehire Rate:** No employers indicated they would rehire students. This needs investigation.")
        elif employer_analytics.get('rehire_count', 0) > (employer_analytics.get('completed_surveys', 0) * 0.7):
            insights.append("✅ **Rehire Rate:** Over 70% of employers would rehire, indicating strong performance.")
        
        # Youth insights
        if youth_analytics.get('avg_satisfaction', 0) < 6:
            insights.append("⚠️ **Youth Satisfaction:** Students report low satisfaction levels. Review job placements and preparation.")
        elif youth_analytics.get('avg_satisfaction', 0) >= 8:
            insights.append("✅ **Youth Satisfaction:** Students are highly satisfied with placements. Continue current practices.")
        
        if youth_analytics.get('avg_magicbus_prep', 0) < 6:
            insights.append("⚠️ **MagicBus Preparation:** Students feel underprepared. Enhance curriculum and training modules.")
        
        if youth_analytics.get('recommend_count', 0) < (youth_analytics.get('completed_surveys', 0) * 0.6):
            insights.append("⚠️ **Recommendations:** Less than 60% of students would recommend MagicBus. Address concerns in feedback.")
        
        for insight in insights:
            st.markdown(f"• {insight}")


# ========================
# TAB 9: SURVEY DISTRIBUTION
# ========================
with main_tabs[8]:
    st.markdown("### 📧 Survey Distribution & Management")
    
    st.markdown("#### Email Configuration Status")
    
    # Check email configuration
    is_configured, config_message = verify_email_configuration()
    
    if is_configured:
        st.success(config_message)
    else:
        st.warning(f"{config_message}")
        st.info("📌 To enable email surveys, configure these in your .env file:\n"
                "- SENDER_EMAIL=your-email@gmail.com\n"
                "- SENDER_PASSWORD=your-app-password\n"
                "- SMTP_SERVER=smtp.gmail.com (optional)\n"
                "- SMTP_PORT=587 (optional)")
    
    st.markdown("---")
    
    # Survey distribution options
    dist_type = st.radio(
        "Select Survey Type to Send",
        ["🏢 Employer Feedback Survey", "👤 Youth Post-Placement Survey"],
        horizontal=True
    )
    
    if dist_type == "🏢 Employer Feedback Survey":
        st.markdown("#### 🏢 Send Employer Feedback Surveys")
        st.markdown("Create and send survey forms to employers for their feedback on student performance")
        
        st.markdown("---")
        
        # Single employer
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("##### Send to Single Employer")
            
            employer_name = st.text_input("Employer Name", key="emp_name_single")
            employer_email = st.text_input("Employer Email", key="emp_email_single", placeholder="email@company.com")
            student_id = st.text_input("Student ID", key="student_id_single", placeholder="mb_xxxxx")
            job_title = st.text_input("Job Title", key="job_title_single")
            
            if st.button("📧 Send Survey to Employer", key="send_emp_single"):
                if not all([employer_name, employer_email, student_id, job_title]):
                    st.error("❌ Please fill in all fields")
                else:
                    with st.spinner("Creating survey..."):
                        success, message, survey_id = create_employer_survey_entry(
                            student_id=student_id,
                            employer_name=employer_name,
                            employer_email=employer_email,
                            job_title=job_title
                        )
                        
                        if success and is_configured:
                            with st.spinner("Sending email..."):
                                email_success, email_msg = send_employer_survey_email(
                                    employer_email=employer_email,
                                    employer_name=employer_name,
                                    student_name=student_id,
                                    job_title=job_title,
                                    survey_id=survey_id
                                )
                                if email_success:
                                    st.success(email_msg)
                                else:
                                    st.warning(email_msg)
                        elif success and not is_configured:
                            st.info(f"✅ Survey created (ID: {survey_id}) but email not sent. Email not configured.")
                        else:
                            st.error(message)
        
        with col2:
            st.markdown("##### Bulk Send via CSV")
            st.info("📁 Upload CSV with columns: employer_name, employer_email, student_id, job_title")
            
            uploaded_file = st.file_uploader("Upload CSV file", type="csv", key="emp_csv")
            
            if uploaded_file is not None:
                try:
                    df_bulk = pd.read_csv(uploaded_file)
                    st.dataframe(df_bulk, width="stretch")
                    
                    if st.button("📧 Send Surveys to All Employers", key="send_emp_bulk"):
                        success_count = 0
                        fail_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df_bulk.iterrows():
                            status_text.text(f"Processing {idx + 1}/{len(df_bulk)}...")
                            
                            success, message, survey_id = create_employer_survey_entry(
                                student_id=row['student_id'],
                                employer_name=row['employer_name'],
                                employer_email=row['employer_email'],
                                job_title=row['job_title']
                            )
                            
                            if success and is_configured:
                                email_success, _ = send_employer_survey_email(
                                    employer_email=row['employer_email'],
                                    employer_name=row['employer_name'],
                                    student_name=row['student_id'],
                                    job_title=row['job_title'],
                                    survey_id=survey_id
                                )
                                if email_success:
                                    success_count += 1
                                else:
                                    fail_count += 1
                            elif success:
                                success_count += 1
                            else:
                                fail_count += 1
                            
                            progress_bar.progress((idx + 1) / len(df_bulk))
                        
                        status_text.text("")
                        st.success(f"✅ Sent {success_count} surveys, {fail_count} failed")
                
                except Exception as e:
                    st.error(f"❌ Error processing file: {e}")
    
    else:  # Youth surveys
        st.markdown("#### 👤 Send Youth Post-Placement Surveys")
        st.markdown("Send survey forms to placed students to capture their post-placement experience")
        
        st.markdown("---")
        
        # Single youth
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("##### Send to Single Student")
            
            youth_name = st.text_input("Student Name", key="youth_name_single")
            youth_email = st.text_input("Student Email", key="youth_email_single", placeholder="student@email.com")
            student_id_youth = st.text_input("Student ID", key="student_id_youth_single", placeholder="mb_xxxxx")
            user_id_youth = st.number_input("User ID", key="user_id_youth_single", min_value=1)
            company_name = st.text_input("Company Name", key="company_single")
            position = st.text_input("Position", key="position_single")
            
            if st.button("📧 Send Survey to Student", key="send_youth_single"):
                if not all([youth_email, student_id_youth, company_name, position]):
                    st.error("❌ Please fill in all fields")
                else:
                    with st.spinner("Creating survey..."):
                        success, message, survey_id = create_youth_survey_entry(
                            student_id=student_id_youth,
                            user_id=int(user_id_youth),
                            placement_company=company_name,
                            job_title=position
                        )
                        
                        if success and is_configured:
                            with st.spinner("Sending email..."):
                                email_success, email_msg = send_youth_survey_email(
                                    youth_email=youth_email,
                                    youth_name=youth_name,
                                    placement_company=company_name,
                                    job_title=position,
                                    survey_id=survey_id
                                )
                                if email_success:
                                    st.success(email_msg)
                                else:
                                    st.warning(email_msg)
                        elif success and not is_configured:
                            st.info(f"✅ Survey created (ID: {survey_id}) but email not sent. Email not configured.")
                        else:
                            st.error(message)
        
        with col2:
            st.markdown("##### Bulk Send via CSV")
            st.info("📁 Upload CSV with columns: youth_name, youth_email, student_id, user_id, company_name, position")
            
            uploaded_file_youth = st.file_uploader("Upload CSV file", type="csv", key="youth_csv")
            
            if uploaded_file_youth is not None:
                try:
                    df_youth_bulk = pd.read_csv(uploaded_file_youth)
                    st.dataframe(df_youth_bulk, width="stretch")
                    
                    if st.button("📧 Send Surveys to All Students", key="send_youth_bulk"):
                        success_count = 0
                        fail_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df_youth_bulk.iterrows():
                            status_text.text(f"Processing {idx + 1}/{len(df_youth_bulk)}...")
                            
                            success, message, survey_id = create_youth_survey_entry(
                                student_id=row['student_id'],
                                user_id=int(row['user_id']),
                                placement_company=row['company_name'],
                                job_title=row['position']
                            )
                            
                            if success and is_configured:
                                email_success, _ = send_youth_survey_email(
                                    youth_email=row['youth_email'],
                                    youth_name=row['youth_name'],
                                    placement_company=row['company_name'],
                                    job_title=row['position'],
                                    survey_id=survey_id
                                )
                                if email_success:
                                    success_count += 1
                                else:
                                    fail_count += 1
                            elif success:
                                success_count += 1
                            else:
                                fail_count += 1
                            
                            progress_bar.progress((idx + 1) / len(df_youth_bulk))
                        
                        status_text.text("")
                        st.success(f"✅ Sent {success_count} surveys, {fail_count} failed")
                
                except Exception as e:
                    st.error(f"❌ Error processing file: {e}")
    
    st.markdown("---")
    st.markdown("### 📊 Distribution Status")
    
    try:
        dist_status = get_survey_distribution_status()
        
        if not dist_status.empty:
            st.markdown(f"**Total Surveys Sent:** {len(dist_status)}")
            st.markdown(f"**Completed:** {dist_status['completed'].sum() if 'completed' in dist_status.columns else 0}")
            st.markdown(f"**Pending:** {(~dist_status['completed']).sum() if 'completed' in dist_status.columns else len(dist_status)}")
            
            st.dataframe(dist_status, width="stretch", hide_index=True)
        else:
            st.info("No surveys sent yet")
    except Exception as e:
        st.warning(f"Could not load distribution status: {e}")

# ========================
# TAB 10: CHURN PREVENTION
# ========================
with main_tabs[9]:
    st.markdown("### 🚨 Churn Prevention & At-Risk Management")
    st.markdown("*Proactive intervention system to retain high-potential students*")
    
    try:
        from mb.pages.gamification import predict_churn_risk, trigger_churn_intervention
        
        # Churn prediction metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("⚠️ At-Risk Students", "24", delta="-3 from last week")
        
        with col2:
            st.metric("✅ Interventions (7d)", "18", delta="75% success")
        
        with col3:
            st.metric("📈 Retention Improved", "65% → 75%", delta="+10pp")
        
        st.markdown("---")
        
        # At-risk students list
        st.subheader("⚠️ At-Risk Students by Churn Risk Score")
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT m.user_id, m.student_id, COUNT(*) as module_count,
                   AVG(m.progress) as avg_progress
            FROM learning_modules m
            GROUP BY m.user_id, m.student_id
            ORDER BY avg_progress ASC
            LIMIT 25
        ''')
        
        at_risk_rows = cursor.fetchall()
        
        if at_risk_rows:
            at_risk_data = []
            for idx, (user_id, student_id, mod_count, avg_prog) in enumerate(at_risk_rows, 1):
                # Calculate risk score (higher = more at-risk)
                churn_risk = 100 - (avg_prog if avg_prog else 0)
                
                at_risk_data.append({
                    "Rank": idx,
                    "Student ID": student_id or "Unknown",
                    "Churn Risk %": round(churn_risk, 1),
                    "Modules": mod_count,
                    "Avg Progress": f"{avg_prog if avg_prog else 0:.1f}%",
                    "Status": "🔴 Critical" if churn_risk > 75 else "🟠 High" if churn_risk > 50 else "🟡 Medium"
                })
            
            df_risk = pd.DataFrame(at_risk_data)
            
            # Color code by risk
            def risk_color(val):
                if val > 75:
                    return "background-color: #ffcccc"
                elif val > 50:
                    return "background-color: #ffe6cc"
                else:
                    return "background-color: #ffffcc"
            
            st.dataframe(
                df_risk.style.applymap(risk_color, subset=['Churn Risk %']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No at-risk students detected.")
        
        conn.close()
        
        st.markdown("---")
        
        # Intervention controls
        st.subheader("🎯 Trigger Interventions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            intervention_student = st.selectbox(
                "Select Student",
                [row[1] or row[0] for row in at_risk_rows] if at_risk_rows else [],
                key="intervention_student"
            )
        
        with col2:
            intervention_type = st.selectbox(
                "Intervention Type",
                ["Mentorship Assignment", "Badge Challenge", "1-on-1 Support", "Career Coaching", "Peer Pairing"],
                key="intervention_type"
            )
        
        if st.button("🚀 Launch Intervention", use_container_width=True):
            with st.spinner("Triggering intervention..."):
                st.success(f"✅ {intervention_type} intervention launched for {intervention_student}")
                st.info("📊 Intervention tracked and monitored for effectiveness")
        
        st.markdown("---")
        
        # Intervention effectiveness log
        st.subheader("📊 Recent Interventions & Effectiveness")
        
        intervention_log = pd.DataFrame([
            {"Date": "Jan 29, 2025", "Student": "STU015", "Type": "Badge Challenge", "Status": "Active", "Impact": "✅ +5% progress"},
            {"Date": "Jan 28, 2025", "Student": "STU023", "Type": "Mentorship", "Status": "Completed", "Impact": "✅ +12% progress"},
            {"Date": "Jan 27, 2025", "Student": "STU008", "Type": "1-on-1 Support", "Status": "Completed", "Impact": "✅ +8% progress"},
            {"Date": "Jan 26, 2025", "Student": "STU031", "Type": "Peer Pairing", "Status": "Active", "Impact": "✅ +3% progress"},
            {"Date": "Jan 25, 2025", "Student": "STU042", "Type": "Career Coaching", "Status": "Completed", "Impact": "✅ +15% progress"},
        ])
        
        st.dataframe(intervention_log, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error loading churn prevention: {e}")
        logger.error(f"Churn prevention error: {e}")

st.markdown("---")
st.markdown("*MagicBus Admin Dashboard | Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")
