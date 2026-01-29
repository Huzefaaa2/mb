"""
Magic Bus Compass 360 - Youth Dashboard
Personalized learning dashboard for students with integrated learning modules
"""

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
import json

# Import custom modules
from gamification import check_and_award_badges, get_user_badges, get_user_streak, get_motivational_message, update_streak
from job_scraper import fetch_jobs
from resume_matcher import match_resume_to_job, get_quick_match_score
from interview_bot import simulate_interview

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Youth Dashboard | Magic Bus Compass", page_icon="📊", layout="wide")

st.title("📊 Youth Dashboard")

# Initialize session state if not already present
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None

# SQLite database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

def check_survey_completed(user_id):
    """Check if user has completed the career survey"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT survey_id FROM career_surveys WHERE user_id = ? LIMIT 1", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"Error checking survey status: {e}")
        return False

def get_module_statistics(user_id):
    """Get module completion statistics for a user"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                ROUND(AVG(progress), 1) as avg_progress
            FROM learning_modules
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_modules": row[0] or 0,
            "completed_modules": row[1] or 0,
            "in_progress_modules": row[2] or 0,
            "average_progress": row[3] or 0
        }
    
    except Exception as e:
        logger.error(f"Error getting module statistics: {e}")
        return {
            "total_modules": 0,
            "completed_modules": 0,
            "in_progress_modules": 0,
            "average_progress": 0
        }

def get_learning_modules(user_id):
    """Get all learning modules for a user"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT module_assignment_id, module_id, title, description, duration, 
                   skills, prerequisites, difficulty_level, status, progress, 
                   started_date, completed_date, assigned_date
            FROM learning_modules
            WHERE user_id = ?
            ORDER BY assigned_date ASC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        modules = []
        for row in rows:
            modules.append({
                "module_assignment_id": row[0],
                "module_id": row[1],
                "title": row[2],
                "description": row[3],
                "duration": row[4],
                "skills": json.loads(row[5]) if row[5] else [],
                "prerequisites": row[6],
                "difficulty_level": row[7],
                "status": row[8],
                "progress": row[9],
                "started_date": row[10],
                "completed_date": row[11],
                "assigned_date": row[12]
            })
        
        return modules
    
    except Exception as e:
        logger.error(f"Error retrieving learning modules: {e}")
        return []

def update_module_status(module_assignment_id, status, progress=None):
    """
    Update module status and progress
    
    Args:
        module_assignment_id: ID of the module assignment
        status: New status ('not_started', 'in_progress', 'completed')
        progress: Progress percentage (0-100)
    
    Returns:
        Boolean indicating success
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        update_fields = ["status = ?"]
        params = [status]
        
        if progress is not None:
            update_fields.append("progress = ?")
            params.append(progress)
        
        if status == "in_progress":
            update_fields.append("started_date = CASE WHEN started_date IS NULL THEN ? ELSE started_date END")
            params.append(datetime.now().isoformat())
        elif status == "completed":
            update_fields.append("completed_date = ?")
            update_fields.append("progress = 100")
            params.append(datetime.now().isoformat())
        
        params.append(module_assignment_id)
        
        query = f"UPDATE learning_modules SET {', '.join(update_fields)} WHERE module_assignment_id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Error updating module status: {e}")
        return False

# Check if user is logged in
logger.info(f"Dashboard - Session state keys: {list(st.session_state.keys())}")
logger.info(f"Dashboard - User ID from session: {st.session_state.get('user_id', 'NOT SET')}")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("⚠️ Please log in to access your dashboard")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/0_login.py")
else:
    # Check if survey is completed
    survey_completed = check_survey_completed(st.session_state.user_id)
    
    if not survey_completed:
        st.warning("🎯 Welcome! Please complete the Career Fit Survey to get started.")
        st.info("This survey will help us personalize your learning path based on your career interests and strengths.")
        
        if st.button("📋 Complete Career Fit Survey Now", width="stretch"):
            st.switch_page("pages/career_survey.py")
        
        st.stop()
    
    # Get module statistics
    stats = get_module_statistics(st.session_state.user_id)
    
    # Display dashboard with module stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Modules Completed", stats['completed_modules'], f"of {stats['total_modules']}")
    
    with col2:
        st.metric("⏳ In Progress", stats['in_progress_modules'], "modules")
    
    with col3:
        st.metric("📊 Overall Progress", f"{int(stats['average_progress'])}%", "average")
    
    st.markdown("---")
    
    # GAMIFICATION SECTION
    st.markdown("### 🎮 Your Achievements & Streaks")
    
    # Check for new badges
    new_badges = check_and_award_badges(st.session_state.user_id, st.session_state.student_id)
    if new_badges:
        st.balloons()
        with st.expander("🎉 New Badges Unlocked!", expanded=True):
            for badge in new_badges:
                st.success(f"{badge['icon']} **{badge['name']}** - {badge['description']}")
    
    # Display all badges
    badges = get_user_badges(st.session_state.user_id)
    streak = get_user_streak(st.session_state.user_id)
    
    gamif_col1, gamif_col2, gamif_col3 = st.columns(3)
    
    with gamif_col1:
        if badges:
            st.metric("🏅 Badges Earned", len(badges))
        else:
            st.info("No badges yet. Start completing modules!")
    
    with gamif_col2:
        st.metric("🔥 Current Streak", f"{streak['current']} days")
    
    with gamif_col3:
        st.metric("⭐ Best Streak", f"{streak['longest']} days")
    
    # Show motivational message
    motivational = get_motivational_message(stats['completed_modules'])
    st.info(f"💡 {motivational}")
    
    # Display badges in expander
    if badges:
        with st.expander(f"🏆 View All {len(badges)} Badges"):
            badge_cols = st.columns(min(4, len(badges)))
            for idx, badge in enumerate(badges):
                with badge_cols[idx % 4]:
                    st.markdown(f"<div style='text-align: center; padding: 10px; background: #f0f0f0; border-radius: 10px;'>"
                              f"<h3>{badge['icon']}</h3>"
                              f"<b>{badge['name']}</b><br/>"
                              f"<small>{badge['description']}</small>"
                              f"</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Your Career Path")
    
    # Get user's career recommendations
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT survey_data FROM career_surveys WHERE user_id = ? ORDER BY completed_at DESC LIMIT 1", (st.session_state.user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            survey_data = json.loads(result[0])
            
            # Display career recommendations
            interests = survey_data.get("interests", [])
            strengths = survey_data.get("strengths", [])
            goals = survey_data.get("career_goals", "")
            learning_style = survey_data.get("learning_style", "")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📌 Your Interests:**")
                if interests:
                    for interest in interests[:5]:
                        st.write(f"• {interest}")
                else:
                    st.write("Not specified")
            
            with col2:
                st.markdown("**💪 Your Strengths:**")
                if strengths:
                    for strength in strengths:
                        st.write(f"• {strength}")
                else:
                    st.write("Not specified")
            
            if goals:
                st.markdown("**🌍 Career Goals:**")
                st.write(goals)
            
            if learning_style:
                st.markdown("**📚 Learning Style:**")
                st.write(learning_style)
    except Exception as e:
        logger.error(f"Error loading survey data: {e}")
        st.warning("Could not load survey data")
    
    st.markdown("---")
    
    # Learning Modules Section
    st.markdown("### 📚 Your Learning Modules")
    
    logger.info(f"Fetching modules for user_id: {st.session_state.user_id}")
    modules = get_learning_modules(st.session_state.user_id)
    logger.info(f"Found {len(modules)} modules for user")
    
    if not modules:
        st.warning("🎯 **Please complete the Career Fit Survey first**")
        st.info("Your personalized learning path will be generated based on your career interests, strengths, and learning style.")
        if st.button("📋 Complete Career Fit Survey", width="stretch", key="btn_career_survey_modules"):
            st.switch_page("pages/career_survey.py")
    else:
        st.info("💡 **If your interests have changed**, go back and complete the Career Fit Survey again to get updated recommendations.")
        
        # Create tabs for filtering
        tab1, tab2, tab3, tab4 = st.tabs(["All Modules", "Not Started", "In Progress", "Completed"])
        
        # TAB 1: All Modules
        with tab1:
            display_modules = modules
            if not display_modules:
                st.write("No modules in this category")
            else:
                for module in display_modules:
                    with st.expander(
                        f"{'✅' if module['status'] == 'completed' else '⏳' if module['status'] == 'in_progress' else '📋'} {module['title']} ({module['difficulty_level']})"
                    ):
                        # Module details
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Duration:** {module['duration']}")
                            st.write(f"**Status:** {module['status'].replace('_', ' ').title()}")
                        
                        with col2:
                            st.write(f"**Difficulty:** {module['difficulty_level']}")
                            st.write(f"**Progress:** {module['progress']}%")
                        
                        st.write(f"**Description:** {module['description']}")
                        
                        if module['skills']:
                            st.write("**Key Skills:**")
                            skills_display = ", ".join(module['skills'])
                            st.write(skills_display)
                        
                        if module['prerequisites']:
                            st.write(f"**Prerequisites:** {module['prerequisites']}")
                    
                    # Progress bar
                    st.progress(module['progress'] / 100 if module['progress'] > 0 else 0)
                    
                    # Status management buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if module['status'] == 'not_started':
                            if st.button(f"▶️ Start", key=f"start_{module['module_assignment_id']}"):
                                update_module_status(module['module_assignment_id'], 'in_progress', 0)
                                st.rerun()
                    
                    with col2:
                        if module['status'] == 'in_progress':
                            progress_val = st.slider(
                                f"Progress for {module['title']}",
                                min_value=0,
                                max_value=100,
                                value=module['progress'],
                                key=f"progress_{module['module_assignment_id']}"
                            )
                            if progress_val != module['progress']:
                                update_module_status(module['module_assignment_id'], 'in_progress', progress_val)
                                st.rerun()
                    
                    with col3:
                        if module['status'] == 'in_progress':
                            if st.button(f"✅ Complete", key=f"complete_{module['module_assignment_id']}"):
                                update_module_status(module['module_assignment_id'], 'completed', 100)
                                st.rerun()
                        elif module['status'] == 'completed':
                            if st.button(f"🔄 Restart", key=f"restart_{module['module_assignment_id']}"):
                                update_module_status(module['module_assignment_id'], 'not_started', 0)
                                st.rerun()
                    
                    # Show dates
                    if module['started_date']:
                        st.caption(f"Started: {module['started_date'][:10]}")
                        if module['completed_date']:
                            st.caption(f"Completed: {module['completed_date'][:10]}")
        
        # TAB 2: Not Started
        with tab2:
            display_modules = [m for m in modules if m['status'] == 'not_started']
            if not display_modules:
                st.write("All modules started! Great progress! 🎉")
            else:
                for module in display_modules:
                    with st.expander(
                        f"📋 {module['title']} ({module['difficulty_level']})"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Duration:** {module['duration']}")
                            st.write(f"**Difficulty:** {module['difficulty_level']}")
                        
                        with col2:
                            st.write(f"**Description:** {module['description']}")
                        
                        if st.button(f"▶️ Start", key=f"start_ns_{module['module_assignment_id']}"):
                            update_module_status(module['module_assignment_id'], 'in_progress', 0)
                            st.rerun()
        
        # TAB 3: In Progress
        with tab3:
            display_modules = [m for m in modules if m['status'] == 'in_progress']
            if not display_modules:
                st.write("No modules in progress. Start one to begin! 🚀")
            else:
                for module in display_modules:
                    with st.expander(
                        f"⏳ {module['title']} ({module['progress']}%)",
                        expanded=True
                    ):
                        st.write(f"**Description:** {module['description']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Duration:** {module['duration']}")
                        with col2:
                            st.write(f"**Difficulty:** {module['difficulty_level']}")
                        
                        progress_val = st.slider(
                            "Update Progress",
                            min_value=0,
                            max_value=100,
                            value=module['progress'],
                            key=f"progress_{module['module_assignment_id']}"
                        )
                        if progress_val != module['progress']:
                            update_module_status(module['module_assignment_id'], 'in_progress', progress_val)
                            st.rerun()
                        
                        if st.button(f"✅ Complete", key=f"complete_{module['module_assignment_id']}"):
                            update_module_status(module['module_assignment_id'], 'completed', 100)
                            st.rerun()
        
        # TAB 4: Completed
        with tab4:
            display_modules = [m for m in modules if m['status'] == 'completed']
            if not display_modules:
                st.write("No completed modules yet. Keep learning! 📚")
            else:
                st.success(f"🎉 You've completed {len(display_modules)} module(s)!")
                for module in display_modules:
                    with st.expander(
                        f"✅ {module['title']}"
                    ):
                        st.write(f"**Description:** {module['description']}")
                        st.caption(f"Completed: {module['completed_date'][:10] if module['completed_date'] else 'N/A'}")
                        
                        if st.button(f"🔄 Restart", key=f"restart_{module['module_assignment_id']}"):
                            update_module_status(module['module_assignment_id'], 'not_started', 0)
                            st.rerun()
    
    st.markdown("---")
    
    # JOBGPT SECTION
    st.markdown("### 🤖 JobGPT - AI-Powered Job Hunting Assistant")
    st.markdown("Find relevant jobs, match your resume, generate cover letters, and practice interviews!")
    
    jobgpt_tabs = st.tabs(["🔍 Find Jobs", "📊 Resume Match", "✍️ Cover Letter", "🎤 Interview Prep"])
    
    with jobgpt_tabs[0]:
        st.subheader("🔍 Job Search")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job_title = st.text_input("Job Title", "Software Engineer", key="job_title_input")
        with col2:
            job_location = st.text_input("Location", "Remote", key="job_location_input")
        with col3:
            num_jobs = st.selectbox("Number of Jobs", [5, 10, 15, 20], index=1, key="num_jobs")
        
        if st.button("🔍 Search Jobs", width="stretch", key="search_jobs_btn"):
            with st.spinner("Searching for jobs..."):
                jobs = fetch_jobs(job_title, job_location, num_jobs)
                st.session_state['jobgpt_jobs'] = jobs
                st.success(f"Found {len(jobs)} jobs!")
        
        if 'jobgpt_jobs' in st.session_state and st.session_state['jobgpt_jobs']:
            for idx, job in enumerate(st.session_state['jobgpt_jobs'], 1):
                with st.expander(f"**{idx}. {job.get('title', 'Job')}** at {job.get('company_name', 'Company')}"):
                    st.write(f"**Location:** {job.get('location', 'N/A')}")
                    st.write(f"**Description:**\n{job.get('description', 'No description available')[:300]}...")
                    
                    if job.get('url') or job.get('via'):
                        apply_link = job.get('url') or job.get('via')
                        st.markdown(f"[👉 Apply Here]({apply_link})", unsafe_allow_html=True)
                    
                    st.session_state[f'selected_job_{idx}'] = job
    
    with jobgpt_tabs[1]:
        st.subheader("📊 Resume-Job Match Analysis")
        
        resume_input = st.text_area("Paste Your Resume Here", height=200, key="resume_for_match")
        
        if 'jobgpt_jobs' in st.session_state and st.session_state['jobgpt_jobs']:
            selected_job_idx = st.selectbox(
                "Select a job to match against",
                range(len(st.session_state['jobgpt_jobs'])),
                format_func=lambda i: f"{st.session_state['jobgpt_jobs'][i].get('title')} at {st.session_state['jobgpt_jobs'][i].get('company_name')}"
            )
            
            if st.button("📊 Analyze Match", key="analyze_match_btn"):
                if resume_input:
                    with st.spinner("Analyzing resume match..."):
                        job_desc = st.session_state['jobgpt_jobs'][selected_job_idx].get('description', '')
                        analysis = match_resume_to_job(resume_input, job_desc)
                        st.markdown(analysis)
                else:
                    st.warning("Please paste your resume first")
        else:
            st.info("Search for jobs first in the 'Find Jobs' tab")
    
    with jobgpt_tabs[2]:
        st.subheader("✍️ Personalized Cover Letter Generator")
        
        company_name = st.text_input("Company Name", key="cover_letter_company")
        job_role = st.text_input("Job Role", key="cover_letter_role")
        your_name = st.text_input("Your Name", key="cover_letter_name")
        
        if st.button("✍️ Generate Cover Letter", key="gen_cover_letter_btn"):
            if company_name and job_role and your_name:
                with st.spinner("Generating cover letter..."):
                    try:
                        from openai import AzureOpenAI
                        import os
                        
                        client = AzureOpenAI(
                            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                        )
                        
                        prompt = f"""Write a professional cover letter for {your_name} applying for a {job_role} position at {company_name}.
                        
Make it compelling, personalized, and highlight relevant skills. Format it as a proper cover letter with greeting, body paragraphs, and closing."""
                        
                        response = client.chat.completions.create(
                            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo"),
                            messages=[
                                {"role": "system", "content": "You are an expert career coach. Write compelling cover letters."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=600
                        )
                        
                        cover_letter = response.choices[0].message.content
                        st.markdown("### Generated Cover Letter:")
                        st.markdown(cover_letter)
                        st.download_button(
                            "📥 Download Cover Letter",
                            cover_letter,
                            file_name=f"cover_letter_{company_name}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Error generating cover letter: {e}")
            else:
                st.warning("Please fill in all fields")
    
    with jobgpt_tabs[3]:
        st.subheader("🎤 Interview Preparation")
        
        interview_job = st.text_input("Job Position to Practice For", "Software Engineer", key="interview_job")
        experience = st.select_slider("Your Experience Level", ["Beginner", "Intermediate", "Advanced"], value="Intermediate", key="experience_level")
        
        if st.button("🎤 Generate Interview Questions", key="gen_interview_btn"):
            with st.spinner("Generating interview questions..."):
                questions = simulate_interview(interview_job, experience.lower())
                st.markdown("### Interview Questions:")
                st.markdown(questions)
                
                st.markdown("---")
                st.tip("💡 **Tip:** Practice answering these questions out loud. Record yourself and review for improvements!")
    
    st.markdown("---")
    
    # CAREER SURVEY SECTION
    st.markdown("### 🎯 Career Fit Survey")
    st.markdown("Discover your ideal career path through a comprehensive career assessment.")
    
    career_col1, career_col2 = st.columns([3, 1])
    with career_col1:
        st.markdown("""
        This survey will help you:
        - Identify careers that match your interests
        - Discover suitable learning paths
        - Get AI-powered personalized recommendations
        - Plan your training and development
        """)
    with career_col2:
        if st.button("📋 Take Career Survey", key="btn_career_survey"):
            st.switch_page("pages/career_survey.py")
    
    st.markdown("---")
