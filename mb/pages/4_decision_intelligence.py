"""
Decision Intelligence Dashboard - Complete Implementation
Transforms raw data into actionable insights for Magic Bus Staff
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import logging

# Import custom modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from databricks_features import FeatureEngineer, refresh_all_features
from decision_dashboard import DecisionDashboard, init_decision_dashboard

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Decision Intelligence Dashboard", page_icon="🧠", layout="wide")

st.title("🧠 Decision Intelligence Dashboard")
st.markdown("**Transform Data into Strategic Decisions for Youth Development**")

# Initialize modules
dashboard = init_decision_dashboard()
engineer = FeatureEngineer()

# ========================
# SIDEBAR: FEATURE REFRESH
# ========================
st.sidebar.markdown("### 🔄 Data Refresh")
if st.sidebar.button("🔄 Refresh All Features"):
    with st.spinner("Computing enriched features..."):
        results = refresh_all_features()
        st.sidebar.success("✅ All features refreshed!")

st.sidebar.markdown("---")

# ========================
# MAIN DASHBOARD TABS
# ========================
dashboard_tabs = st.tabs([
    "📊 Executive Overview",
    "📈 Mobilisation Funnel",
    "🔥 Sector Heatmap",
    "🚨 At-Risk Youth",
    "📚 Module Effectiveness",
    "🏅 Gamification Impact",
    "🎙️ Screening Analytics",
    "⭐ Youth Potential Score™",
    "📉 Retention Analytics",
    "🎓 Skill Development",
    "💡 Proposal Generator"
])

# ========================
# TAB 1: EXECUTIVE OVERVIEW
# ========================
with dashboard_tabs[0]:
    st.markdown("### Executive Dashboard Overview")
    st.markdown("*High-level KPIs at a glance*")
    
    # Get overview data
    overview = dashboard.get_executive_overview()
    
    if overview:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "👥 Youth Enrolled",
                overview.get('total_enrolled', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "🎯 Active Learners",
                overview.get('active_count', 0),
                delta=f"{round(100*overview.get('active_count', 0)/max(overview.get('total_enrolled', 1), 1), 1)}% enrollment"
            )
        
        with col3:
            st.metric(
                "📚 Completion Rate",
                f"{overview.get('completion_rate', 0)}%",
                delta="Target: 80%"
            )
        
        with col4:
            st.metric(
                "⚠️ Dropout Risk",
                f"{overview.get('dropout_risk_pct', 0)}%",
                delta="High Risk Students"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Career Pathway Adoption")
            st.metric("Surveys Completed", overview.get('surveys_completed', 0), 
                     f"{overview.get('survey_completion_rate', 0)}% of enrolled")
        
        with col2:
            st.markdown("#### Quick Recommendations")
            if overview.get('dropout_risk_pct', 0) > 20:
                st.warning(f"🚨 High dropout risk ({overview.get('dropout_risk_pct', 0)}%). Consider interventions in Tab 4.")
            if overview.get('completion_rate', 0) < 50:
                st.info(f"📍 Completion rate ({overview.get('completion_rate', 0)}%) below target. Review modules in Tab 5.")

# ========================
# TAB 2: MOBILISATION FUNNEL
# ========================
with dashboard_tabs[1]:
    st.markdown("### 📈 Mobilisation Funnel Analysis")
    st.markdown("*Track youth journey: Registered → Survey → Learning → Completion*")
    
    funnel_data = dashboard.get_mobilisation_funnel()
    
    if not funnel_data.empty:
        # Funnel chart
        fig = go.Figure(data=[go.Funnel(
            y=funnel_data['funnel_stage'],
            x=funnel_data['count'],
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(
                color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )
        )])
        
        fig.update_layout(
            title="Youth Journey Through Magic Bus",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Funnel data table
        st.markdown("#### Funnel Metrics")
        st.dataframe(
            funnel_data[['funnel_stage', 'count', 'pct_of_registered']],
            column_config={
                "funnel_stage": "Stage",
                "count": "Count",
                "pct_of_registered": "% of Registered"
            },
            width="stretch",
            hide_index=True
        )
        
        # Dropoff analysis
        st.markdown("---")
        st.markdown("#### Dropoff Analysis")
        
        if len(funnel_data) >= 2:
            for i in range(len(funnel_data) - 1):
                stage1 = funnel_data.iloc[i]
                stage2 = funnel_data.iloc[i + 1]
                dropoff = stage1['count'] - stage2['count']
                dropoff_pct = (dropoff / stage1['count'] * 100) if stage1['count'] > 0 else 0
                
                if dropoff > 0:
                    st.warning(f"**{stage1['funnel_stage']} → {stage2['funnel_stage']}**: {dropoff} students dropped ({dropoff_pct:.1f}%)")
    else:
        st.info("No funnel data available. Run feature refresh first.")

# ========================
# TAB 3: SECTOR HEATMAP
# ========================
with dashboard_tabs[2]:
    st.markdown("### 🔥 Sector Interest & Readiness Heatmap")
    st.markdown("*Where are youth interests and skill readiness aligned?*")
    
    heatmap_data = dashboard.get_sector_heatmap()
    
    if not heatmap_data.empty:
        # Pivot for heatmap
        heatmap_pivot = heatmap_data.pivot_table(
            index='sector', 
            columns='readiness_status', 
            values='count', 
            fill_value=0
        )
        
        fig = px.imshow(
            heatmap_pivot,
            labels=dict(x="Readiness Status", y="Sector", color="Count"),
            title="Sector Interest × Readiness Matrix",
            color_continuous_scale="RdYlGn",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Sector insights
        st.markdown("#### Sector-wise Insights")
        
        for sector in heatmap_data['sector'].unique():
            sector_data = heatmap_data[heatmap_data['sector'] == sector]
            total = sector_data['count'].sum()
            
            green_count = sector_data[sector_data['readiness_status'] == 'Green']['count'].sum()
            green_pct = (green_count / total * 100) if total > 0 else 0
            
            red_count = sector_data[sector_data['readiness_status'] == 'Red']['count'].sum()
            red_pct = (red_count / total * 100) if total > 0 else 0
            
            if red_pct > 30:
                st.warning(f"**{sector}**: {total} youth, but {red_pct:.0f}% need skill bridging")
            else:
                st.success(f"**{sector}**: {total} youth, {green_pct:.0f}% ready to proceed")
    else:
        st.info("No sector data available. Run feature refresh first.")

# ========================
# TAB 4: AT-RISK YOUTH INTERVENTION
# ========================
with dashboard_tabs[3]:
    st.markdown("### 🚨 At-Risk Youth & Intervention Board")
    st.markdown("*Identify and support students before they drop out*")
    
    at_risk_data = dashboard.get_at_risk_youth(limit=50)
    
    if not at_risk_data.empty:
        # Risk summary
        high_risk = (at_risk_data['risk'] == 'HIGH').sum()
        medium_risk = (at_risk_data['risk'] == 'MEDIUM').sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 HIGH Risk", high_risk)
        with col2:
            st.metric("🟡 MEDIUM Risk", medium_risk)
        with col3:
            st.metric("Total At Risk", len(at_risk_data))
        
        st.markdown("---")
        
        # Intervention priority table
        st.markdown("#### Intervention Priority List")
        
        display_cols = ['student_id', 'email', 'modules_started', 'avg_completion_pct', 'risk', 'reason', 'days_since_registration']
        st.dataframe(
            at_risk_data[display_cols],
            column_config={
                "student_id": "Student ID",
                "email": "Email",
                "modules_started": "Modules Started",
                "avg_completion_pct": "Avg %",
                "risk": "Risk Level",
                "reason": "Reason",
                "days_since_registration": "Days Enrolled"
            },
            width="stretch",
            hide_index=True
        )
        
        st.markdown("---")
        
        # Risk factors breakdown
        st.markdown("#### Risk Factor Breakdown")
        
        reason_counts = at_risk_data['reason'].value_counts()
        fig = px.bar(
            x=reason_counts.index,
            y=reason_counts.values,
            labels={'x': 'Risk Reason', 'y': 'Student Count'},
            title="Top Dropout Risk Reasons"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommended actions
        st.markdown("---")
        st.markdown("#### Recommended Actions")
        st.info("""
        🎯 **Intervention Strategy**
        1. **Immediate (24h)**: Call HIGH risk students to check engagement
        2. **3-day**: Assign teacher mentor for MEDIUM risk students
        3. **7-day**: Send sector-specific micro-learning modules
        4. **14-day**: Follow up with career counselling session
        """)
    else:
        st.success("✅ No students at risk. Keep monitoring!")

# ========================
# TAB 5: MODULE EFFECTIVENESS & ROI
# ========================
with dashboard_tabs[4]:
    st.markdown("### 📚 Module Effectiveness & Training ROI")
    st.markdown("*Which modules drive the highest impact?*")
    
    effectiveness_data = dashboard.get_module_effectiveness()
    
    if not effectiveness_data.empty:
        # Top modules by completion
        fig = px.bar(
            effectiveness_data,
            x='module_name',
            y='completion_rate',
            color='effectiveness_level',
            title="Module Completion Rates",
            labels={'completion_rate': 'Completion Rate (%)', 'module_name': 'Module'},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Effectiveness table
        st.markdown("#### Module Performance Metrics")
        
        display_cols = ['module_name', 'learners', 'completed_count', 'completion_rate', 'avg_points_earned', 'effectiveness_level']
        st.dataframe(
            effectiveness_data[display_cols],
            column_config={
                "module_name": "Module",
                "learners": "Total Learners",
                "completed_count": "Completed",
                "completion_rate": "Completion %",
                "avg_points_earned": "Avg Points",
                "effectiveness_level": "Impact Level"
            },
            width="stretch",
            hide_index=True
        )
        
        st.markdown("---")
        
        # High-impact modules highlight
        high_impact = effectiveness_data[effectiveness_data['effectiveness_level'] == 'High Impact']
        
        if not high_impact.empty:
            st.markdown("#### 🏆 High-Impact Modules (Scale These)")
            for _, module in high_impact.iterrows():
                st.success(f"**{module['module_name']}**: {module['completion_rate']:.0f}% completion, {module['learners']} learners")
        
        # Low-impact modules needing improvement
        low_impact = effectiveness_data[effectiveness_data['effectiveness_level'] == 'Needs Improvement']
        
        if not low_impact.empty:
            st.markdown("#### 📍 Modules Needing Improvement")
            for _, module in low_impact.iterrows():
                st.warning(f"**{module['module_name']}**: Only {module['completion_rate']:.0f}% completion. Consider redesign.")
    else:
        st.info("No module effectiveness data available. Run feature refresh first.")

# ========================
# TAB 6: GAMIFICATION IMPACT
# ========================
with dashboard_tabs[5]:
    st.markdown("### 🏅 Gamification Impact on Retention")
    st.markdown("*Do badges and streaks drive better outcomes?*")
    
    gamification_data = dashboard.get_gamification_impact()
    
    if not gamification_data.empty:
        # Comparison metrics
        col1, col2, col3 = st.columns(3)
        
        badge_earners = gamification_data[gamification_data['group_type'] == 'Badge Earners']
        non_earners = gamification_data[gamification_data['group_type'] == 'Non-Badge Earners']
        
        if not badge_earners.empty:
            badge_completion = badge_earners['completion_rate'].iloc[0]
        else:
            badge_completion = 0
        
        if not non_earners.empty:
            non_completion = non_earners['completion_rate'].iloc[0]
        else:
            non_completion = 0
        
        with col1:
            st.metric("🏅 Badge Earners Completion", f"{badge_completion:.0f}%")
        
        with col2:
            st.metric("⚪ Non-Badge Earners Completion", f"{non_completion:.0f}%")
        
        with col3:
            improvement = badge_completion - non_completion
            st.metric("📈 Improvement", f"+{improvement:.0f}%")
        
        st.markdown("---")
        
        # Comparison chart
        fig = go.Figure(data=[
            go.Bar(name='Badge Earners', x=gamification_data['group_type'], y=gamification_data['completion_rate']),
        ])
        
        fig.update_layout(
            title="Completion Rate Comparison",
            height=400,
            yaxis_title="Completion Rate (%)",
            xaxis_title="Group"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Gamification effectiveness
        st.markdown("#### Gamification Effectiveness Summary")
        
        st.info(f"""
        ✨ **Key Finding**: Badge earners show {improvement:.0f}% higher completion rate.
        
        💡 **Recommendation**: 
        - Scale gamification features to all learners
        - Set achievement milestones to encourage early engagement
        - Use streaks to maintain momentum
        - Celebrate wins publicly in community
        """)
    else:
        st.info("No gamification data available. Run feature refresh first.")

# ========================
# TAB 7: PROPOSAL INSIGHTS GENERATOR
# ========================
# TAB 7: SCREENING ANALYTICS
# ========================
with dashboard_tabs[6]:
    st.markdown("### 🎙️ Multi-Modal Screening Analytics")
    st.markdown("*Voice-based soft skills assessment and role-personality matching metrics*")
    
    try:
        # Get screening data
        screening_analytics = dashboard.get_screening_analytics()
        screening_funnel = dashboard.get_screening_funnel()
        
        if screening_analytics['total_screenings'] > 0:
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Screenings", screening_analytics['total_screenings'])
            
            with col2:
                st.metric("👥 Unique Students", screening_analytics['unique_students'])
            
            with col3:
                high_fit = screening_analytics['fit_distribution'].get('High', 0)
                st.metric("✨ High Personality Fit", high_fit)
            
            with col4:
                marginalized = screening_analytics['marginalized_count']
                st.metric("🎯 Marginalized Youth", marginalized)
            
            st.markdown("---")
            
            # Soft skills distribution
            st.markdown("### Soft Skills Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                avg_scores = screening_analytics['avg_scores']
                
                skills_names = [
                    'Communication',
                    'Cultural Fit',
                    'Problem Solving',
                    'Emotional Intelligence',
                    'Leadership'
                ]
                skills_scores = [
                    avg_scores.get('communication', 0),
                    avg_scores.get('cultural_fit', 0),
                    avg_scores.get('problem_solving', 0),
                    avg_scores.get('emotional_intelligence', 0),
                    avg_scores.get('leadership', 0)
                ]
                
                fig_skills = go.Figure(data=[
                    go.Bar(x=skills_names, y=skills_scores, marker_color='lightblue')
                ])
                fig_skills.update_layout(
                    title="Average Soft Skills Scores",
                    xaxis_title="Skill",
                    yaxis_title="Average Score",
                    height=350
                )
                st.plotly_chart(fig_skills, use_container_width=True)
            
            with col2:
                # Personality fit distribution
                fit_data = screening_analytics['fit_distribution']
                
                fig_fit = go.Figure(data=[
                    go.Pie(
                        labels=list(fit_data.keys()),
                        values=list(fit_data.values()),
                        marker=dict(colors=['green', 'orange', 'red'])
                    )
                ])
                fig_fit.update_layout(
                    title="Personality Fit Distribution",
                    height=350
                )
                st.plotly_chart(fig_fit, use_container_width=True)
            
            st.markdown("---")
            
            # Screening funnel
            st.markdown("### Screening Submission Funnel")
            
            funnel_data = screening_funnel
            funnel_stages = ['Submitted', 'High Fit', 'Medium Fit']
            funnel_values = [
                funnel_data['submitted'],
                funnel_data['high_fit'],
                funnel_data['medium_fit']
            ]
            
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_stages,
                x=funnel_values,
                marker=dict(color=['blue', 'green', 'orange'])
            ))
            fig_funnel.update_layout(
                title="Screening Submission & Personality Fit Funnel",
                height=350
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Conversion insights
            st.markdown("### Conversion Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "High Fit Rate",
                    f"{funnel_data['high_fit_rate']}%",
                    delta="Of screenings submitted"
                )
            
            with col2:
                st.metric(
                    "Matchable Rate",
                    f"{funnel_data['matchable_rate']}%",
                    delta="High + Medium fit"
                )
            
            with col3:
                if funnel_data['submitted'] > 0:
                    low_fit_pct = round(100.0 * funnel_data['low_fit'] / funnel_data['submitted'], 1)
                    st.metric("Low Fit Rate", f"{low_fit_pct}%")
            
            st.markdown("---")
            
            # Top recommended roles
            st.markdown("### Top Personality-Driven Roles")
            
            top_roles = screening_analytics['top_roles']
            
            if top_roles:
                role_names = [role[0] for role in top_roles]
                role_counts = [role[1] for role in top_roles]
                
                fig_roles = go.Figure(data=[
                    go.Bar(y=role_names, x=role_counts, orientation='h', marker_color='teal')
                ])
                fig_roles.update_layout(
                    title="Top 5 Personality-Matched Roles",
                    xaxis_title="Number of Matches",
                    yaxis_title="Role",
                    height=300
                )
                st.plotly_chart(fig_roles, use_container_width=True)
            else:
                st.info("No role recommendations yet")
            
            # Marginalized youth insights
            st.markdown("---")
            st.markdown("### Marginalized Youth Screening Impact")
            
            total_screened = screening_analytics['unique_students']
            marginalized_screened = screening_analytics['marginalized_count']
            
            if total_screened > 0:
                marginalized_pct = round(100.0 * marginalized_screened / total_screened, 1)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Marginalized Youth Screened",
                        marginalized_screened,
                        delta=f"{marginalized_pct}% of total"
                    )
                
                with col2:
                    avg_marginalized_boost = screening_analytics['avg_scores'].get('marginalized', 0)
                    st.metric(
                        "Avg Marginalized Score",
                        f"{avg_marginalized_boost:.1f}",
                        delta="1.15x boost applied"
                    )
        else:
            st.info("📊 No screening data available yet. Voice screenings will appear here once students submit assessments.")
    
    except Exception as e:
        st.error(f"Error loading screening analytics: {e}")
        logger.error(f"Screening analytics error: {e}")

# ========================
# TAB 8: YOUTH POTENTIAL SCORE™
# ========================
with dashboard_tabs[8]:
    st.markdown("### ⭐ Youth Potential Score™ Dashboard")
    st.markdown("*AI-Powered Composite Score for Personalized Development*")
    
    try:
        # Get distribution
        distribution = dashboard.get_potential_distribution()
        top_students = dashboard.get_top_potential_students(limit=20)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            exceptional = distribution.get("Exceptional", 0)
            st.metric("🚀 Exceptional", exceptional, delta=f"{round(100*exceptional/max(sum(distribution.values()), 1), 1)}%")
        
        with col2:
            high = distribution.get("High", 0)
            st.metric("📈 High", high, delta=f"{round(100*high/max(sum(distribution.values()), 1), 1)}%")
        
        with col3:
            medium = distribution.get("Medium", 0)
            st.metric("📊 Medium", medium, delta=f"{round(100*medium/max(sum(distribution.values()), 1), 1)}%")
        
        with col4:
            development = distribution.get("Development", 0)
            st.metric("🌱 Development", development, delta=f"{round(100*development/max(sum(distribution.values()), 1), 1)}%")
        
        st.markdown("---")
        
        # Tier distribution pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig_dist = px.pie(
                values=distribution.values(),
                names=distribution.keys(),
                title="Distribution by Tier",
                color_discrete_map={
                    "Exceptional": "#1f77b4",
                    "High": "#2ca02c",
                    "Medium": "#ff7f0e",
                    "Development": "#d62728"
                }
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Score statistics
            if top_students:
                scores = [s['overall_score'] for s in top_students]
                fig_hist = px.histogram(
                    x=scores,
                    nbins=10,
                    title="Potential Score Distribution",
                    labels={"x": "Score", "y": "Count"}
                )
                fig_hist.add_vline(x=80, line_dash="dash", line_color="blue", annotation_text="Exceptional (80)")
                fig_hist.add_vline(x=65, line_dash="dash", line_color="green", annotation_text="High (65)")
                fig_hist.add_vline(x=50, line_dash="dash", line_color="orange", annotation_text="Medium (50)")
                st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("---")
        
        # Top students leaderboard
        st.subheader("🏆 Top 20 Students by Potential")
        
        if top_students:
            leaderboard_data = []
            for i, student in enumerate(top_students, 1):
                leaderboard_data.append({
                    "Rank": i,
                    "Student ID": student['student_id'],
                    "Overall Score": round(student['overall_score'], 2),
                    "Tier": student['tier'],
                    "Engagement": round(student['engagement_probability'], 1),
                    "Retention": round(student['retention_likelihood'], 1),
                    "Skills": round(student['skill_readiness'], 1),
                    "Placement": round(student['placement_fit'], 1)
                })
            
            df_leaderboard = pd.DataFrame(leaderboard_data)
            
            # Color-code by tier
            def tier_color(tier):
                if tier == "Exceptional": return "background-color: #d4edda"
                elif tier == "High": return "background-color: #cce5ff"
                elif tier == "Medium": return "background-color: #fff3cd"
                else: return "background-color: #f8d7da"
            
            st.dataframe(
                df_leaderboard.style.applymap(tier_color, subset=['Tier']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No student data available yet.")
    
    except Exception as e:
        st.error(f"Error loading Youth Potential Score: {e}")
        logger.error(f"Youth Potential error: {e}")

# ========================
# TAB 9: RETENTION ANALYTICS
# ========================
with dashboard_tabs[9]:
    st.markdown("### 📉 Retention Analytics & Churn Prevention")
    st.markdown("*Monitor and manage student retention toward 85% goal*")
    
    try:
        from mb.pages.gamification import predict_churn_risk, calculate_retention_impact
        
        # Retention metrics
        impact = calculate_retention_impact()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Retention",
                f"{impact.get('current_retention_rate', 0):.1f}%",
                delta=f"Goal: {impact.get('target_retention', 85)}%"
            )
        
        with col2:
            progress = impact.get('progress_toward_target_pct', 0)
            st.metric(
                "Progress to Target",
                f"{progress:.1f}%",
                delta="From 65% baseline"
            )
        
        with col3:
            at_risk = impact.get('at_risk_students', 0)
            st.metric(
                "At-Risk Students",
                at_risk,
                delta=f"Total: {impact.get('total_students', 0)}"
            )
        
        st.markdown("---")
        
        # Retention progress meter
        col1, col2 = st.columns([3, 1])
        
        with col1:
            baseline = impact.get('baseline_retention', 65)
            current = impact.get('current_retention_rate', 65)
            target = impact.get('target_retention', 85)
            
            fig_meter = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=current,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Retention Rate (%)"},
                delta={'reference': baseline},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 65], 'color': "#d62728"},
                        {'range': [65, 85], 'color': "#ff7f0e"},
                        {'range': [85, 100], 'color': "#2ca02c"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': target
                    }
                }
            ))
            st.plotly_chart(fig_meter, use_container_width=True)
        
        st.markdown("---")
        
        # Intervention effectiveness
        st.subheader("🎯 Intervention Effectiveness")
        
        interv_metrics = impact.get('intervention_metrics', {})
        gam_metrics = impact.get('gamification_metrics', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Interventions (30d)",
                interv_metrics.get('total_interventions_30d', 0),
                delta=f"Success: {interv_metrics.get('success_rate_pct', 0):.0f}%"
            )
        
        with col2:
            st.metric(
                "Badge Earners",
                gam_metrics.get('badge_earners_30d', 0),
                delta=f"Total: {gam_metrics.get('total_badges_earned_30d', 0)} badges"
            )
        
        with col3:
            avg_badges = gam_metrics.get('avg_badges_per_earner', 0)
            st.metric(
                "Avg Badges/Earner",
                f"{avg_badges:.2f}",
                delta="Engagement indicator"
            )
        
        st.markdown("---")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        for rec in impact.get('recommendations', []):
            st.write(f"• {rec}")
    
    except Exception as e:
        st.error(f"Error loading retention analytics: {e}")
        logger.error(f"Retention analytics error: {e}")

# ========================
# TAB 10: SKILL DEVELOPMENT
# ========================
with dashboard_tabs[10]:
    st.markdown("### 🎓 Skill Development & Learning Paths")
    st.markdown("*Track skill gaps and personalized learning recommendations*")
    
    try:
        from mb.services.skill_gap_bridger import SkillGapBridger
        
        bridger = SkillGapBridger()
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.selectbox(
                "Select Student",
                ["STU001", "STU002", "STU003", "STU004", "STU005"],
                key="skill_student"
            )
        
        with col2:
            role = st.selectbox(
                "Target Role",
                ["Software Developer", "Data Analyst", "Business Analyst", "Project Manager", "UX Designer"],
                key="skill_role"
            )
        
        if st.button("🔍 Analyze Skill Gaps", use_container_width=True):
            with st.spinner("Analyzing skills and generating learning path..."):
                gaps = bridger.analyze_skill_gaps(student_id, role)
                
                if "error" not in gaps:
                    # Gap summary
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Current Skills", gaps.get('current_skills_count', 0))
                    
                    with col2:
                        st.metric("Required Skills", gaps.get('required_skills_count', 0))
                    
                    with col3:
                        st.metric("Skill Gaps", gaps.get('total_gaps', 0))
                    
                    st.markdown("---")
                    
                    # Generate learning path
                    path = bridger.generate_learning_path(gaps)
                    
                    st.subheader("📚 Personalized Learning Path")
                    
                    if path.get('learning_path'):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Total Hours", f"{path.get('total_estimated_hours', 0)}")
                            st.metric("Estimated Days", f"{path.get('total_estimated_days', 0):.0f}")
                        
                        with col2:
                            st.info(path.get('recommendation', 'Complete learning path to develop skills'))
                        
                        st.markdown("---")
                        
                        # Detailed learning path
                        for i, item in enumerate(path['learning_path'], 1):
                            with st.expander(f"📖 {item['skill']} - {item['priority']} Priority"):
                                for resource in item['resources']:
                                    st.write(f"**{resource['resource']}**")
                                    st.write(f"Platform: {resource['platform']} | Duration: {resource['duration_hours']}h")
                                    st.write(f"[📎 View Resource]({resource.get('url', '#')})")
                                    st.divider()
                    else:
                        st.info("✅ All skills aligned with role requirements!")
                else:
                    st.error(f"Error: {gaps['error']}")
        
        st.markdown("---")
        
        # Supported roles info
        st.subheader("📋 Supported Roles & Skills")
        
        roles_info = {
            "Software Developer": ["Python", "SQL", "Problem Solving", "Version Control", "APIs", "Testing"],
            "Data Analyst": ["SQL", "Excel", "Data Visualization", "Statistics", "Python", "Tableau"],
            "Business Analyst": ["Communication", "Business Acumen", "Documentation", "Excel", "SQL", "Stakeholder Management"],
            "Project Manager": ["Leadership", "Communication", "Planning", "Risk Management", "Budgeting", "Team Management"],
            "UX Designer": ["Design Thinking", "Figma", "User Research", "Wireframing", "Communication", "Prototyping"]
        }
        
        selected_role = st.selectbox("View role requirements:", list(roles_info.keys()), key="view_role")
        
        col1, col2, col3 = st.columns(3)
        for i, skill in enumerate(roles_info[selected_role]):
            if i % 3 == 0:
                st.write(f"✓ {skill}")
            elif i % 3 == 1:
                st.write(f"✓ {skill}")
            else:
                st.write(f"✓ {skill}")
    
    except Exception as e:
        st.error(f"Error loading skill development: {e}")
        logger.error(f"Skill development error: {e}")

# ========================
# TAB 11: PROPOSAL GENERATOR
# ========================
with dashboard_tabs[11]:
    st.markdown("### 💡 AI-Powered Funding Proposal Generator")
    st.markdown("*Generate evidence-backed proposals for donors and CSR partners*")
    
    st.markdown("---")
    
    # Proposal parameters
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox(
            "Select Region",
            ["AP", "TG", "KA", "MH", "All India"],
            key="proposal_region"
        )
    
    with col2:
        sector = st.selectbox(
            "Focus Sector",
            ["IT", "Hospitality", "Retail", "Healthcare", "Manufacturing", "All Sectors"],
            key="proposal_sector"
        )
    
    st.markdown("---")
    
    if st.button("🚀 Generate Proposal Insights", use_container_width=True):
        with st.spinner("Generating proposal with AI insights..."):
            proposal = dashboard.generate_proposal_insights(region=region, sector=sector)
            
            st.markdown("### 📄 Generated Proposal")
            st.markdown(proposal)
            
            st.markdown("---")
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download as Text",
                    data=proposal,
                    file_name=f"magic_bus_proposal_{region}_{sector}.txt",
                    mime="text/plain"
                )
            
            with col2:
                st.info("💡 **Tip**: Copy this proposal and customize with specific donor interests and program details.")

st.markdown("---")
st.markdown("*Decision Intelligence Dashboard | Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")
