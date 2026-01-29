"""
Azure-Powered Decision Intelligence Dashboard
Generates reports from APAC region datasets
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "data_sources"))

from azure_decision_dashboard import get_azure_dashboard
from azure_feature_engineer import get_azure_feature_engineer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Decision Intelligence Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Decision Intelligence Dashboard")
st.markdown("**Transform Azure Data into Strategic Decisions for Youth Development**")

# Initialize Azure modules
dashboard = get_azure_dashboard()
engineer = get_azure_feature_engineer()

# ========================
# SIDEBAR: DATA SOURCE & REFRESH
# ========================
st.sidebar.markdown("### 📊 Data Source")
st.sidebar.info("""
**Source:** Azure Blob Storage
**Region:** APAC
**URL:** https://defaultstoragehackathon.blob.core.windows.net/usethisone/apac
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Refresh Features")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔄 Compute Features", key="refresh_btn"):
        with st.spinner("Computing features from Azure data..."):
            try:
                features = engineer.compute_all_features()
                st.sidebar.success("✅ Features computed!")
                for name, df in features.items():
                    if not df.empty:
                        st.sidebar.caption(f"  ✅ {name}: {len(df)} rows")
                    else:
                        st.sidebar.warning(f"  ⚠️ {name}: No data")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

with col2:
    if st.button("🔗 Test Connection", key="test_conn"):
        with st.spinner("Testing Azure connection..."):
            try:
                health = dashboard.connector.get_health_report()
                if health['connection_status'] == 'connected':
                    st.sidebar.success("✅ Connected to Azure")
                    st.sidebar.caption(f"Datasets: {len(health['available_datasets'])}")
                else:
                    st.sidebar.warning("⚠️ Connection issues")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

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
    st.markdown("*Real-time KPIs from Azure data sources*")
    
    try:
        overview = dashboard.get_executive_overview()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "👥 Youth Enrolled",
                f"{overview.get('total_enrolled', 0):,}",
                delta=None
            )
        
        with col2:
            st.metric(
                "🎯 Active Learners",
                f"{overview.get('active_learners', 0):,}",
                delta=f"{overview.get('active_pct', 0)}% engagement"
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
                delta="High Risk"
            )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📋 Avg Quiz Score", f"{overview.get('avg_quiz_score', 0):.1f}/100")
        
        with col2:
            st.metric("✅ Quiz Pass Rate", f"{overview.get('quiz_pass_rate', 0)}%")
        
        with col3:
            st.metric("💪 Engagement Score", f"{overview.get('engagement_score', 0):.1f}%")
        
        st.markdown("---")
        st.markdown("#### 📌 Quick Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if overview.get('dropout_risk_pct', 0) > 20:
                st.warning(
                    f"🚨 **High Dropout Risk** ({overview.get('dropout_risk_pct', 0)}%)\n\n"
                    "Consider interventions:\n"
                    "- Target at-risk students (Tab 4)\n"
                    "- Increase engagement (gamification boost)\n"
                    "- Personalized learning paths"
                )
            else:
                st.success(f"✅ Dropout risk under control ({overview.get('dropout_risk_pct', 0)}%)")
        
        with col2:
            if overview.get('completion_rate', 0) < 50:
                st.info(
                    f"📍 **Low Completion Rate** ({overview.get('completion_rate', 0)}%)\n\n"
                    "Recommendations:\n"
                    "- Review module difficulty (Tab 5)\n"
                    "- Identify bottleneck modules\n"
                    "- Provide additional support"
                )
            else:
                st.success(f"✅ Strong completion ({overview.get('completion_rate', 0)}%)")
    
    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")

# ========================
# TAB 2: MOBILISATION FUNNEL
# ========================
with dashboard_tabs[1]:
    st.markdown("### 📈 Mobilisation Funnel Analysis")
    st.markdown("*Track youth progression: Registered → Learning → Quiz → Achievement*")
    
    try:
        funnel_data = dashboard.get_mobilisation_funnel()
        
        if not funnel_data.empty:
            # Funnel chart
            fig = go.Figure(data=[go.Funnel(
                y=funnel_data['funnel_stage'],
                x=funnel_data['count'],
                textposition="inside",
                textinfo="value+percent initial",
                marker=dict(
                    color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                    line=dict(color='white', width=2)
                )
            )])
            
            fig.update_layout(
                title="Youth Progression Funnel",
                height=500,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Funnel data table
            st.markdown("#### Funnel Metrics")
            display_df = funnel_data[['funnel_stage', 'count', 'pct_of_registered']].copy()
            display_df.columns = ['Stage', 'Count', '% of Registered']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Dropoff analysis
            st.markdown("---")
            st.markdown("#### Dropoff Analysis & Insights")
            
            if len(funnel_data) >= 2:
                for i in range(len(funnel_data) - 1):
                    stage1 = funnel_data.iloc[i]
                    stage2 = funnel_data.iloc[i + 1]
                    dropoff = stage1['count'] - stage2['count']
                    dropoff_pct = (dropoff / stage1['count'] * 100) if stage1['count'] > 0 else 0
                    
                    if dropoff > 0:
                        st.warning(
                            f"**{stage1['funnel_stage']} → {stage2['funnel_stage']}**: "
                            f"{dropoff:,} students dropped ({dropoff_pct:.1f}%)"
                        )
        else:
            st.info("No funnel data available. Run feature refresh to populate.")
    
    except Exception as e:
        st.error(f"Error loading funnel: {str(e)}")

# ========================
# TAB 3: SECTOR HEATMAP
# ========================
with dashboard_tabs[2]:
    st.markdown("### 🔥 Sector Interest & Readiness Heatmap")
    st.markdown("*Where are youth interests and skill readiness aligned?*")
    
    try:
        heatmap_data = dashboard.get_sector_heatmap()
        
        if not heatmap_data.empty:
            # Create pivot table for heatmap
            if 'sector' in heatmap_data.columns:
                heatmap_pivot = heatmap_data.pivot_table(
                    index='sector',
                    columns='readiness',
                    values='count',
                    fill_value=0
                )
            else:
                st.info("Heatmap data format requires recalibration.")
                heatmap_pivot = pd.DataFrame()
            
            if not heatmap_pivot.empty:
                fig = px.imshow(
                    heatmap_pivot,
                    labels=dict(x="Readiness Status", y="Sector", color="Count"),
                    title="Sector × Readiness Matrix",
                    color_continuous_scale="RdYlGn",
                    height=500
                )
                
                fig.update_xaxes(side="bottom")
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.markdown("#### Sector Distribution")
                st.dataframe(heatmap_pivot, use_container_width=True)
        else:
            st.info("No sector heatmap data available.")
    
    except Exception as e:
        st.error(f"Error loading heatmap: {str(e)}")

# ========================
# TAB 4: AT-RISK YOUTH
# ========================
with dashboard_tabs[3]:
    st.markdown("### 🚨 At-Risk Youth Identification")
    st.markdown("*Prioritized list for intervention*")
    
    try:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_filter = st.selectbox(
                "Risk Level",
                ["All", "HIGH", "MEDIUM", "LOW"],
                key="risk_filter"
            )
        
        with col2:
            limit = st.slider("Show top N students", 10, 100, 50, step=10)
        
        with col3:
            st.write("")  # Spacer
        
        # Get at-risk students
        if risk_filter == "All":
            at_risk = dashboard.get_at_risk_youth(limit=limit)
        else:
            at_risk = dashboard.get_at_risk_youth(limit=limit, risk_level=risk_filter)
        
        if not at_risk.empty:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_risk = len(at_risk[at_risk['risk_level'] == 'HIGH'])
                st.metric("🔴 High Risk", high_risk)
            
            with col2:
                medium_risk = len(at_risk[at_risk['risk_level'] == 'MEDIUM'])
                st.metric("🟡 Medium Risk", medium_risk)
            
            with col3:
                low_risk = len(at_risk[at_risk['risk_level'] == 'LOW'])
                st.metric("🟢 Low Risk", low_risk)
            
            st.markdown("---")
            
            # Detailed list
            st.markdown("#### At-Risk Student List")
            display_cols = ['student_name', 'risk_level', 'risk_score', 'risk_reason', 'modules_started']
            available_cols = [col for col in display_cols if col in at_risk.columns]
            
            st.dataframe(
                at_risk[available_cols],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            st.markdown("#### Risk Distribution")
            
            risk_counts = at_risk['risk_level'].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Risk Level Distribution",
                color_discrete_map={'HIGH': '#ff4444', 'MEDIUM': '#ffaa00', 'LOW': '#44aa44'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No at-risk students found.")
    
    except Exception as e:
        st.error(f"Error loading at-risk data: {str(e)}")

# ========================
# TAB 5: MODULE EFFECTIVENESS
# ========================
with dashboard_tabs[4]:
    st.markdown("### 📚 Module Effectiveness Analysis")
    st.markdown("*Identify high-impact and underperforming modules*")
    
    try:
        effectiveness = dashboard.get_module_effectiveness(limit=20)
        
        if not effectiveness.empty:
            # Sort option
            sort_col = st.selectbox(
                "Sort by",
                ["completion_rate", "learners", "total_points_earned"],
                key="sort_module"
            )
            
            if sort_col in effectiveness.columns:
                effectiveness = effectiveness.sort_values(sort_col, ascending=False)
            
            # Completion rate chart
            if 'completion_rate' in effectiveness.columns and 'module_name' in effectiveness.columns:
                fig = px.bar(
                    effectiveness.head(15),
                    x='completion_rate',
                    y='module_name',
                    orientation='h',
                    title="Module Completion Rates (Top 15)",
                    color='completion_rate',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed table
            st.markdown("#### Module Performance Details")
            display_cols = ['module_name', 'learners', 'completions', 'completion_rate', 'effectiveness_level']
            available_cols = [col for col in display_cols if col in effectiveness.columns]
            
            st.dataframe(
                effectiveness[available_cols],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            st.markdown("#### Effectiveness Distribution")
            
            if 'effectiveness_level' in effectiveness.columns:
                effect_counts = effectiveness['effectiveness_level'].value_counts()
                fig = px.pie(
                    values=effect_counts.values,
                    names=effect_counts.index,
                    title="Modules by Effectiveness",
                    color_discrete_map={
                        'High Impact': '#44aa44',
                        'Medium Impact': '#ffaa00',
                        'Needs Improvement': '#ff4444'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No module effectiveness data available.")
    
    except Exception as e:
        st.error(f"Error loading module data: {str(e)}")

# ========================
# TAB 6: GAMIFICATION IMPACT
# ========================
with dashboard_tabs[5]:
    st.markdown("### 🏅 Gamification Impact Analysis")
    st.markdown("*Does gamification (badges, points) drive better learning outcomes?*")
    
    try:
        gamification = dashboard.get_gamification_impact()
        
        if not gamification.empty and len(gamification) >= 1:
            # Create comparison metrics
            if len(gamification) >= 2:
                col1, col2 = st.columns(2)
                
                gamified = gamification.iloc[0]
                non_gamified = gamification.iloc[1] if len(gamification) > 1 else None
                
                with col1:
                    st.markdown("#### 🎯 Badge & Points Earners")
                    st.metric("Users", gamified.get('user_count', 0))
                    st.metric("Completion Rate", f"{gamified.get('completion_rate', 0)}%")
                    st.metric("Engagement", f"{gamified.get('engagement_score', 0):.1f}%")
                
                with col2:
                    if non_gamified is not None:
                        st.markdown("#### 📊 Control Group")
                        st.metric("Users", non_gamified.get('user_count', 0))
                        st.metric("Completion Rate", f"{non_gamified.get('completion_rate', 0)}%")
                        st.metric("Engagement", f"{non_gamified.get('engagement_score', 0):.1f}%")
                
                st.markdown("---")
                
                # Comparison chart
                if non_gamified is not None:
                    comparison_data = pd.DataFrame([
                        {
                            'Group': gamified.get('group_type', 'Gamified'),
                            'Completion Rate': gamified.get('completion_rate', 0)
                        },
                        {
                            'Group': non_gamified.get('group_type', 'Control'),
                            'Completion Rate': non_gamified.get('completion_rate', 0)
                        }
                    ])
                    
                    fig = px.bar(
                        comparison_data,
                        x='Group',
                        y='Completion Rate',
                        title="Gamification Impact on Completion",
                        color='Completion Rate',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed metrics
                st.markdown("---")
                st.markdown("#### Detailed Metrics")
                st.dataframe(gamification, use_container_width=True, hide_index=True)
        
        else:
            st.info("Gamification data coming soon...")
    
    except Exception as e:
        st.error(f"Error loading gamification data: {str(e)}")

# ========================
# TAB 7: PROPOSAL GENERATOR
# ========================
with dashboard_tabs[6]:
    st.markdown("### 💡 Funding Proposal Generator")
    st.markdown("*Generate data-driven proposals for stakeholders*")
    
    try:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            sector = st.text_input("Sector (optional)", "")
        
        with col2:
            grade = st.text_input("Grade Level (optional)", "")
        
        # Generate button
        if st.button("📄 Generate Proposal", key="gen_proposal"):
            with st.spinner("Generating proposal from Azure data..."):
                try:
                    proposal = dashboard.generate_proposal_insights(
                        sector=sector if sector else None,
                        grade_level=grade if grade else None
                    )
                    
                    if proposal and 'title' in proposal:
                        st.markdown(f"## {proposal['title']}")
                        st.markdown(f"*Generated: {proposal.get('generated_at', 'N/A')}*")
                        
                        st.markdown("---")
                        st.markdown("### Executive Summary")
                        st.markdown(proposal.get('executive_summary', ''))
                        
                        st.markdown("---")
                        st.markdown("### Key Metrics")
                        
                        key_metrics = proposal.get('key_metrics', {})
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Enrolled", f"{key_metrics.get('total_enrolled', 0):,}")
                        with col2:
                            st.metric("Active", f"{key_metrics.get('active_learners', 0):,}")
                        with col3:
                            st.metric("Completion", f"{key_metrics.get('completion_rate', 0)}%")
                        with col4:
                            st.metric("At-Risk", f"{key_metrics.get('dropout_risk_pct', 0)}%")
                        
                        st.markdown("---")
                        st.markdown("### Impact Highlights")
                        for highlight in proposal.get('impact_highlights', []):
                            st.success(f"✅ {highlight}")
                        
                        st.markdown("---")
                        st.markdown("### At-Risk Analysis")
                        at_risk_info = proposal.get('at_risk_analysis', {})
                        st.metric("High-Risk Students", at_risk_info.get('count', 0))
                        
                        st.markdown("#### Intervention Strategies")
                        for strategy in at_risk_info.get('intervention_strategies', []):
                            st.write(f"• {strategy}")
                        
                        st.markdown("---")
                        st.markdown("### Module Recommendations")
                        for rec in proposal.get('module_recommendations', []):
                            status_color = "✅" if rec.get('status') == 'Scale & Promote' else "🔧"
                            st.info(
                                f"{status_color} **{rec.get('module', 'N/A')}** ({rec.get('completion_rate', 'N/A')})\n\n"
                                f"{rec.get('action', 'N/A')}"
                            )
                        
                        st.markdown("---")
                        st.markdown("### Funding Requirements")
                        funding = proposal.get('funding_requirements', {})
                        st.metric(
                            "Annual Cost",
                            f"${funding.get('annual_cost', 0):,.0f}",
                            f"@ ${funding.get('cost_per_student', 0)}/student"
                        )
                        
                        st.markdown("---")
                        st.markdown("### ROI Projection")
                        roi = proposal.get('roi_projection', {})
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Est. Value", f"${roi.get('estimated_value', 0):,.0f}")
                        with col2:
                            st.metric("Est. Cost", f"${roi.get('estimated_cost', 0):,.0f}")
                        with col3:
                            st.metric("ROI", f"{roi.get('estimated_roi_pct', 0):.1f}%")
                        
                        st.markdown("---")
                        st.download_button(
                            label="📥 Download Proposal as Text",
                            data=str(proposal),
                            file_name=f"proposal_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                except Exception as e:
                    st.error(f"Error generating proposal: {str(e)}")
    
    except Exception as e:
        st.error(f"Error in proposal generator: {str(e)}")

# ========================
# FOOTER
# ========================
st.markdown("---")
st.markdown("""
### 📚 Documentation
- **Data Source:** Azure Blob Storage (APAC Region)
- **Last Updated:** Real-time from Azure datasets
- **Report Generator:** Magic Bus Compass 360

For support, contact the data team.
""")
