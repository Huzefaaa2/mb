"""
Feedback Survey Page
UI for submitting feedback surveys
"""

import streamlit as st
from pathlib import Path
import logging
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from feedback_survey import (
    init_feedback_tables,
    submit_employer_feedback,
    submit_youth_feedback,
    get_employer_feedback_analytics,
    get_youth_feedback_analytics
)

st.set_page_config(page_title="Feedback Survey", page_icon="📋", layout="wide")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize feedback tables
init_feedback_tables()

st.title("📋 Feedback Survey Portal")
st.markdown("Your feedback helps us improve and support better placement outcomes")

# Survey type selection
survey_type = st.radio(
    "What feedback would you like to provide?",
    ["👤 Youth Post-Placement Feedback", "🏢 Employer Feedback"],
    horizontal=True
)

if survey_type == "👤 Youth Post-Placement Feedback":
    st.markdown("---")
    st.subheader("📝 Your Post-Placement Experience")
    st.markdown("Help us understand your placement journey and how we can better support future students")
    
    with st.form("youth_feedback_form", clear_on_submit=True):
        # Basic Information
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("Your Student ID (e.g., mb_8045f0)", placeholder="mb_xxxxx")
            user_id = st.number_input("Your User ID", min_value=1)
        with col2:
            placement_company = st.text_input("Company Name", placeholder="e.g., Google, Microsoft")
            job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
        
        st.markdown("#### ⭐ Your Satisfaction Levels (Rate 1-10)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            role_match = st.slider("Role matched expectations", 1, 10, 7)
            work_env = st.slider("Work environment satisfaction", 1, 10, 7)
            team_collab = st.slider("Team collaboration", 1, 10, 7)
        with col2:
            career_growth = st.slider("Career growth opportunity", 1, 10, 7)
            compensation = st.slider("Compensation satisfaction", 1, 10, 7)
            manager_support = st.slider("Manager support", 1, 10, 7)
        with col3:
            skill_app = st.slider("Skill application", 1, 10, 7)
            magicbus_prep = st.slider("MagicBus preparation", 1, 10, 7)
            overall_sat = st.slider("Overall satisfaction", 1, 10, 7)
        
        st.markdown("#### 💬 Your Feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            what_went_well = st.text_area(
                "What went well during your placement?",
                placeholder="Share what you felt was positive about the experience...",
                height=100
            )
        with col2:
            what_improve = st.text_area(
                "What could have been better?",
                placeholder="Areas you felt needed improvement...",
                height=100
            )
        
        col1, col2 = st.columns(2)
        with col1:
            challenges = st.text_area(
                "What challenges did you face?",
                placeholder="Any difficulties you encountered...",
                height=80
            )
        with col2:
            training_needed = st.text_area(
                "Additional training or skills you needed",
                placeholder="What would have helped you succeed better...",
                height=80
            )
        
        suggestions = st.text_area(
            "Suggestions for MagicBus improvement",
            placeholder="How can we improve our program for future students...",
            height=80
        )
        
        col1, col2 = st.columns(2)
        with col1:
            recommend = st.checkbox("✅ I would recommend MagicBus to others", value=True)
        with col2:
            st.info(f"Your recommendation: {'Yes ✅' if recommend else 'No ❌'}")
        
        st.markdown("---")
        
        submitted = st.form_submit_button("📤 Submit Feedback", width="stretch")
        
        if submitted:
            if not student_id or not placement_company or not job_title:
                st.error("❌ Please fill in all required fields (Student ID, Company, Job Title)")
            else:
                success, message = submit_youth_feedback(
                    student_id=student_id,
                    user_id=user_id,
                    placement_company=placement_company,
                    job_title=job_title,
                    role_expectation_match=role_match,
                    work_environment_satisfaction=work_env,
                    team_collaboration_satisfaction=team_collab,
                    career_growth_opportunity=career_growth,
                    compensation_satisfaction=compensation,
                    overall_satisfaction=overall_sat,
                    what_went_well=what_went_well,
                    what_could_improve=what_improve,
                    manager_support_rating=manager_support,
                    skill_application_rating=skill_app,
                    magicbus_preparation_rating=magicbus_prep,
                    would_recommend_magicbus=recommend,
                    suggestions_for_improvement=suggestions,
                    challenges_faced=challenges,
                    additional_training_needed=training_needed
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

else:  # Employer Feedback
    st.markdown("---")
    st.subheader("🏢 Employer Feedback Form")
    st.markdown("Your insights help us improve our student preparation and curriculum")
    
    with st.form("employer_feedback_form", clear_on_submit=True):
        # Basic Information
        col1, col2 = st.columns(2)
        with col1:
            employer_name = st.text_input("Your Name", placeholder="Full name")
            employer_email = st.text_input("Your Email", placeholder="email@company.com")
        with col2:
            student_id = st.text_input("Student ID (if known)", placeholder="mb_xxxxx or leave blank")
            job_title = st.text_input("Position Title", placeholder="Job title offered")
        
        company_name = st.text_input("Company Name", placeholder="Organization name")
        
        st.markdown("#### ⭐ Student Performance Evaluation (Rate 1-10)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            overall_perf = st.slider("Overall Performance", 1, 10, 7)
            technical = st.slider("Technical Skills", 1, 10, 7)
            communication = st.slider("Communication Skills", 1, 10, 7)
        with col2:
            teamwork = st.slider("Teamwork", 1, 10, 7)
            work_ethic = st.slider("Work Ethic", 1, 10, 7)
            punctuality = st.slider("Punctuality", 1, 10, 7)
        with col3:
            reliability = st.slider("Reliability", 1, 10, 7)
            problem_solving = st.slider("Problem Solving", 1, 10, 7)
            recommendation = st.slider("Recommendation Score", 1, 10, 7)
        
        st.markdown("#### 💬 Detailed Feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            strengths = st.text_area(
                "Key Strengths",
                placeholder="Areas where the student excelled...",
                height=100
            )
        with col2:
            areas_improve = st.text_area(
                "Areas for Improvement",
                placeholder="Specific skills or behaviors to work on...",
                height=100
            )
        
        feedback_comments = st.text_area(
            "Overall Comments & Feedback",
            placeholder="Any additional observations or suggestions...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            would_rehire = st.checkbox("✅ Would you hire this student again?", value=True)
        with col2:
            if would_rehire:
                st.success("Great! You'd consider them for future opportunities")
            else:
                st.warning("You'd prefer not to rehire for future positions")
        
        st.markdown("---")
        
        submitted = st.form_submit_button("📤 Submit Feedback", width="stretch")
        
        if submitted:
            if not employer_name or not employer_email or not company_name:
                st.error("❌ Please fill in all required fields (Name, Email, Company)")
            else:
                success, message = submit_employer_feedback(
                    student_id=student_id if student_id else "UNKNOWN",
                    employer_name=employer_name,
                    employer_email=employer_email,
                    job_title=job_title,
                    overall_performance=overall_perf,
                    technical_skills=technical,
                    communication_skills=communication,
                    teamwork=teamwork,
                    work_ethic=work_ethic,
                    punctuality=punctuality,
                    reliability=reliability,
                    problem_solving=problem_solving,
                    strengths=strengths,
                    areas_for_improvement=areas_improve,
                    would_rehire=would_rehire,
                    feedback_comments=feedback_comments,
                    recommendation_score=recommendation
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

# Show analytics summary (read-only)
st.markdown("---")
st.markdown("### 📊 Feedback Analytics Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏢 Employer Feedback Analytics")
    employer_analytics = get_employer_feedback_analytics()
    
    if employer_analytics:
        st.metric("Total Surveys", employer_analytics.get('total_surveys', 0))
        st.metric("Completed", employer_analytics.get('completed_surveys', 0))
        st.metric("Pending", employer_analytics.get('pending_surveys', 0))
        st.metric("Avg Performance", f"{employer_analytics.get('avg_overall_performance', 0)}/10")
        st.metric("Would Rehire", employer_analytics.get('rehire_count', 0))

with col2:
    st.markdown("#### 👤 Youth Feedback Analytics")
    youth_analytics = get_youth_feedback_analytics()
    
    if youth_analytics:
        st.metric("Total Surveys", youth_analytics.get('total_surveys', 0))
        st.metric("Completed", youth_analytics.get('completed_surveys', 0))
        st.metric("Pending", youth_analytics.get('pending_surveys', 0))
        st.metric("Avg Satisfaction", f"{youth_analytics.get('avg_satisfaction', 0)}/10")
        st.metric("Recommend MagicBus", youth_analytics.get('recommend_count', 0))
