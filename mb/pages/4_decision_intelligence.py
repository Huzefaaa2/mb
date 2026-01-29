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
with dashboard_tabs[6]:
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
