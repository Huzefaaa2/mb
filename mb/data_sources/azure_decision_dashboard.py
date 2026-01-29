"""
Enhanced Decision Dashboard Module
Provides actionable insights using local SQLite and Azure Blob Storage datasets
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import sys
from pathlib import Path
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from azure_blob_connector import get_blob_connector
from azure_feature_engineer import AzureFeatureEngineer

logger = logging.getLogger(__name__)


class AzureDecisionDashboard:
    """Analytics engine for decision dashboards using local and Azure data"""
    
    def __init__(self):
        self.connector = get_blob_connector()
        self.feature_engineer = AzureFeatureEngineer()
        self.features_cache = {}
        # SQLite database path for local fallback
        self.db_path = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"
    
    # ========================
    # DATA LOADING HELPERS
    # ========================
    
    def _load_from_sqlite(self, table_name: str) -> pd.DataFrame:
        """Load dataset from SQLite database"""
        try:
            if not self.db_path.exists():
                logger.warning(f"SQLite database not found")
                return pd.DataFrame()
            
            conn = sqlite3.connect(str(self.db_path))
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
            return df
        except Exception as e:
            logger.warning(f"Could not load {table_name} from SQLite: {e}")
            return pd.DataFrame()
    
    def _get_features(self, feature_name: str, force_reload: bool = False) -> pd.DataFrame:
        """Get computed features with caching"""
        if feature_name in self.features_cache and not force_reload:
            return self.features_cache[feature_name]
        
        # Compute features if not cached
        if not self.features_cache:
            all_features = self.feature_engineer.compute_all_features()
            self.features_cache = all_features
        
        return self.features_cache.get(feature_name, pd.DataFrame())
    
    # ========================
    # EXECUTIVE OVERVIEW
    # ========================
    # ========================
    # EXECUTIVE OVERVIEW
    # ========================
    
    def get_executive_overview(self, region: Optional[str] = None) -> Dict:
        """
        Get high-level KPIs from feature tables:
        - Total enrolled students
        - Active learners
        - Completion rate
        - Dropout risk percentage
        - Average quiz performance
        - Engagement score
        """
        logger.info("📊 Generating executive overview...")
        
        try:
            # Load feature tables
            daily_features = self._get_features('student_daily_features')
            dropout_risk = self._get_features('dropout_risk')
            
            # Load user data for total count
            users_df = self._load_from_sqlite('mb_users')
            
            if users_df.empty and daily_features.empty:
                return self._get_default_overview()
            
            # KPI 1: Total enrolled (from mb_users table)
            total_enrolled = len(users_df) if not users_df.empty else 0
            
            # KPI 2: Active learners (from daily features)
            if not daily_features.empty:
                active_learners = len(daily_features[daily_features['modules_assigned'] > 0])
            else:
                active_learners = 0
            
            # KPI 3: Completion rate (from daily features)
            if not daily_features.empty and daily_features['modules_assigned'].sum() > 0:
                completion_rate = round(
                    100.0 * daily_features['modules_completed'].sum() / 
                    daily_features['modules_assigned'].sum(),
                    1
                )
            else:
                completion_rate = 0
            
            # KPI 4: Dropout risk percentage
            if not dropout_risk.empty:
                high_risk_count = len(dropout_risk[dropout_risk['dropout_risk_level'] == 'HIGH'])
                dropout_pct = round(100.0 * high_risk_count / len(dropout_risk), 1) if len(dropout_risk) > 0 else 0
            else:
                dropout_pct = 0
            
            # KPI 5 & 6: Quiz metrics (from learning modules)
            learning_modules = self._load_from_sqlite('learning_modules')
            if not learning_modules.empty:
                # Calculate quiz-like metrics from module completion
                avg_quiz_score = round(
                    learning_modules['progress'].mean() if 'progress' in learning_modules.columns else 0,
                    1
                )
                quiz_pass_rate = round(
                    100.0 * (learning_modules['status'] == 'completed').sum() / len(learning_modules),
                    1
                ) if len(learning_modules) > 0 else 0
            else:
                avg_quiz_score = 0
                quiz_pass_rate = 0
            
            # KPI 7: Engagement score (composite)
            if total_enrolled > 0:
                engagement_score = round(
                    (active_learners / total_enrolled * 100 + completion_rate + quiz_pass_rate) / 3,
                    1
                )
            else:
                engagement_score = 0
            
            # KPI 8: Active percentage
            active_pct = round(100.0 * active_learners / total_enrolled, 1) if total_enrolled > 0 else 0
            
            overview = {
                'total_enrolled': total_enrolled,
                'active_learners': active_learners,
                'active_pct': active_pct,
                'completion_rate': completion_rate,
                'dropout_risk_pct': dropout_pct,
                'avg_quiz_score': avg_quiz_score,
                'quiz_pass_rate': quiz_pass_rate,
                'engagement_score': engagement_score,
                'timestamp': pd.Timestamp.now(),
            }
            
            logger.info(f"✅ Overview KPIs: Enrolled={total_enrolled}, Active={active_learners}, Completion={completion_rate}%")
            return overview
        
        except Exception as e:
            logger.error(f"❌ Error generating overview: {e}")
            return self._get_default_overview()
    
    def _get_default_overview(self) -> Dict:
        """Default overview when data is unavailable"""
        return {
            'total_enrolled': 0,
            'active_learners': 0,
            'active_pct': 0,
            'completion_rate': 0,
            'dropout_risk_pct': 0,
            'avg_quiz_score': 0,
            'quiz_pass_rate': 0,
            'engagement_score': 0,
            'timestamp': pd.Timestamp.now(),
        }
    
    # ========================
    # MOBILISATION FUNNEL
    # ========================
    
    def get_mobilisation_funnel(self) -> pd.DataFrame:
        """Get progression funnel data"""
        try:
            funnel_df = self._get_features('mobilisation_funnel')
            if not funnel_df.empty:
                logger.info(f"✅ Funnel data retrieved: {len(funnel_df)} stages")
                return funnel_df
            else:
                logger.warning("⚠️ No funnel data available")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error getting funnel: {e}")
            return pd.DataFrame()
    
    # ========================
    # SECTOR HEATMAP
    # ========================
    
    def get_sector_heatmap(self) -> pd.DataFrame:
        """
        Get sector × readiness status matrix for heatmap visualization
        Uses sector_interests and readiness_status from sector fit features
        """
        logger.info("🔥 Generating sector heatmap...")
        
        try:
            import json
            
            # Load sector fit features
            sector_fit_df = self._get_features('sector_fit')
            
            if sector_fit_df.empty:
                logger.warning("⚠️ No sector fit data available")
                return pd.DataFrame()
            
            # Parse sector interests (may be JSON)
            def extract_sectors(interests_str):
                """Extract sector names from interests field"""
                if pd.isna(interests_str) or interests_str == '' or interests_str == 'No data':
                    return ['Unspecified']
                
                # Try to parse as JSON
                try:
                    data = json.loads(interests_str) if isinstance(interests_str, str) else interests_str
                    if isinstance(data, dict) and 'interests' in data:
                        interests = data['interests']
                        return interests if isinstance(interests, list) else [str(interests)]
                    elif isinstance(data, list):
                        return data
                    else:
                        return [str(data)]
                except:
                    # If not JSON, treat as string
                    return [str(interests_str)]
            
            # Explode sectors and build heatmap
            heatmap_data = []
            statuses = ['Green', 'Amber', 'Red']
            
            for idx, row in sector_fit_df.iterrows():
                sectors = extract_sectors(row.get('sector_interests'))
                readiness = row.get('readiness_status', 'Amber')
                fit_score = row.get('sector_fit_score', 0)
                
                for sector in sectors:
                    if sector and sector.strip():
                        sector = sector.strip()
                        # Check if this sector-status combo already exists
                        existing = [h for h in heatmap_data if h['sector'] == sector and h['readiness'] == readiness]
                        if existing:
                            existing[0]['count'] += 1
                            existing[0]['avg_fit_score'] = (existing[0]['avg_fit_score'] + fit_score) / 2
                        else:
                            heatmap_data.append({
                                'sector': sector,
                                'readiness': readiness,
                                'count': 1,
                                'avg_fit_score': fit_score
                            })
            
            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                logger.info(f"✅ Heatmap generated: {len(heatmap_df)} data points, {len(heatmap_df['sector'].unique())} sectors")
                return heatmap_df
            else:
                logger.warning("⚠️ No sector heatmap data after parsing")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"❌ Error generating heatmap: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    # ========================
    # AT-RISK YOUTH
    # ========================
    
    def get_at_risk_youth(self, limit: int = 50, risk_level: Optional[str] = None) -> pd.DataFrame:
        """
        Get prioritized list of at-risk students for intervention
        
        Args:
            limit: Number of records to return
            risk_level: Filter by 'HIGH', 'MEDIUM', or None for all
        """
        logger.info("🚨 Retrieving at-risk youth list...")
        
        try:
            dropout_df = self._get_features('dropout_risk')
            
            if dropout_df.empty:
                logger.warning("⚠️ No at-risk data available")
                return pd.DataFrame()
            
            # Filter by risk level if specified
            if risk_level:
                dropout_df = dropout_df[dropout_df['risk_level'] == risk_level]
            
            # Sort by risk score (descending) and take top N
            at_risk = dropout_df.sort_values('risk_score', ascending=False).head(limit)
            
            logger.info(f"✅ Retrieved {len(at_risk)} at-risk students")
            return at_risk
        
        except Exception as e:
            logger.error(f"❌ Error retrieving at-risk youth: {e}")
            return pd.DataFrame()
    
    # ========================
    # MODULE EFFECTIVENESS
    # ========================
    
    def get_module_effectiveness(self, limit: int = 20, sort_by: str = 'completion_rate') -> pd.DataFrame:
        """
        Get module performance rankings
        
        Args:
            limit: Number of modules to return
            sort_by: 'completion_rate', 'learners', or 'total_points_earned'
        """
        logger.info("📚 Retrieving module effectiveness...")
        
        try:
            effectiveness_df = self._get_features('module_effectiveness')
            
            if effectiveness_df.empty:
                logger.warning("⚠️ No module effectiveness data")
                return pd.DataFrame()
            
            # Sort and limit
            if sort_by in effectiveness_df.columns:
                effectiveness_df = effectiveness_df.sort_values(sort_by, ascending=False)
            
            result = effectiveness_df.head(limit)
            
            logger.info(f"✅ Retrieved effectiveness for {len(result)} modules")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error retrieving module effectiveness: {e}")
            return pd.DataFrame()
    
    # ========================
    # GAMIFICATION IMPACT
    # ========================
    
    def get_gamification_impact(self) -> pd.DataFrame:
        """Get gamification (badges/points) impact on learning"""
        logger.info("🏅 Retrieving gamification impact...")
        
        try:
            gamification_df = self._get_features('gamification_impact')
            
            if gamification_df.empty:
                logger.warning("⚠️ No gamification data")
                return pd.DataFrame()
            
            logger.info(f"✅ Retrieved gamification data: {len(gamification_df)} groups")
            return gamification_df
        
        except Exception as e:
            logger.error(f"❌ Error retrieving gamification impact: {e}")
            return pd.DataFrame()
    
    # ========================
    # PROPOSAL GENERATION
    # ========================
    
    def generate_proposal_insights(
        self,
        region: Optional[str] = None,
        sector: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> Dict:
        """
        Generate funding proposal insights based on data
        
        Returns:
            Dictionary with proposal content, metrics, and recommendations
        """
        logger.info("💡 Generating proposal insights...")
        
        try:
            # Get all key metrics
            overview = self.get_executive_overview(region)
            at_risk = self.get_at_risk_youth(limit=10)
            effectiveness = self.get_module_effectiveness(limit=5)
            gamification = self.get_gamification_impact()
            
            # Build proposal content
            proposal = {
                'title': f"Impact Proposal - Magic Bus Compass 360",
                'generated_at': pd.Timestamp.now().strftime("%B %d, %Y"),
                'executive_summary': self._build_executive_summary(overview),
                'key_metrics': overview,
                'impact_highlights': self._build_impact_highlights(overview, at_risk, effectiveness),
                'at_risk_analysis': {
                    'count': len(at_risk),
                    'intervention_strategies': self._get_intervention_strategies(at_risk)
                },
                'module_recommendations': self._get_top_recommendations(effectiveness),
                'gamification_insights': self._get_gamification_insights(gamification),
                'funding_requirements': self._calculate_funding_needs(overview),
                'roi_projection': self._calculate_roi(overview),
            }
            
            logger.info("✅ Proposal insights generated")
            return proposal
        
        except Exception as e:
            logger.error(f"❌ Error generating proposal: {e}")
            return self._get_default_proposal()
    
    def _build_executive_summary(self, overview: Dict) -> str:
        """Build executive summary text"""
        return f"""
Magic Bus Compass 360 has engaged {overview['total_enrolled']:,} youth across the APAC region.
Our data-driven decision intelligence platform has identified key intervention opportunities:
- {overview['active_pct']}% active engagement rate
- {overview['completion_rate']}% module completion
- {overview['quiz_pass_rate']}% quiz pass rate
- {overview['dropout_risk_pct']}% at-risk population requiring intervention
        """
    
    def _build_impact_highlights(self, overview: Dict, at_risk: pd.DataFrame, effectiveness: pd.DataFrame) -> List[str]:
        """Build impact highlight bullets"""
        highlights = [
            f"Engaged {overview['active_learners']:,} active learners",
            f"Achieved {overview['completion_rate']}% completion rate",
            f"Identified {len(at_risk)} students for targeted intervention",
        ]
        
        if not effectiveness.empty:
            top_module = effectiveness.iloc[0]
            highlights.append(
                f"Top-performing module: {top_module.get('module_name', 'N/A')} "
                f"({top_module.get('completion_rate', 0)}% completion)"
            )
        
        return highlights
    
    def _get_intervention_strategies(self, at_risk: pd.DataFrame) -> List[str]:
        """Generate intervention strategies for at-risk students"""
        strategies = [
            "📱 SMS reminder campaigns for module completion",
            "👥 Peer mentoring assignment based on sector interests",
            "🎯 Personalized learning paths based on skill gaps",
            "🏆 Gamification boost (extra badges/points for milestones)",
            "📞 Teacher outreach for high-risk students",
        ]
        
        if len(at_risk) > 20:
            strategies.append("⚡ Escalated support for top 20 highest-risk students")
        
        return strategies
    
    def _get_top_recommendations(self, effectiveness: pd.DataFrame) -> List[Dict]:
        """Get top module recommendations"""
        recommendations = []
        
        if not effectiveness.empty:
            # High impact modules
            high_impact = effectiveness[effectiveness['effectiveness_level'] == 'High Impact'].head(3)
            for _, module in high_impact.iterrows():
                recommendations.append({
                    'module': module.get('module_name', 'Unknown'),
                    'status': 'Scale & Promote',
                    'completion_rate': f"{module.get('completion_rate', 0):.1f}%",
                    'action': 'Increase capacity & expand to new schools'
                })
            
            # Needs improvement modules
            needs_improve = effectiveness[effectiveness['effectiveness_level'] == 'Needs Improvement'].head(2)
            for _, module in needs_improve.iterrows():
                recommendations.append({
                    'module': module.get('module_name', 'Unknown'),
                    'status': 'Revise Content',
                    'completion_rate': f"{module.get('completion_rate', 0):.1f}%",
                    'action': 'Review and update curriculum'
                })
        
        return recommendations
    
    def _get_gamification_insights(self, gamification: pd.DataFrame) -> Dict:
        """Extract gamification insights"""
        if gamification.empty:
            return {}
        
        if len(gamification) >= 2:
            badge_earners = gamification.iloc[0]
            non_badge = gamification.iloc[1]
            
            return {
                'badge_earners': badge_earners.to_dict(),
                'non_badge': non_badge.to_dict(),
                'impact': f"Badge earners have {badge_earners.get('completion_rate', 0):.1f}% "
                         f"vs {non_badge.get('completion_rate', 0):.1f}% for non-participants"
            }
        
        return {}
    
    def _calculate_funding_needs(self, overview: Dict) -> Dict:
        """Calculate funding requirements"""
        cost_per_student = 150  # Assumed cost per student per year (USD)
        
        return {
            'annual_cost': overview['total_enrolled'] * cost_per_student,
            'cost_per_student': cost_per_student,
            'student_count': overview['total_enrolled'],
            'currency': 'USD'
        }
    
    def _calculate_roi(self, overview: Dict) -> Dict:
        """Calculate ROI projections"""
        # Assume $100 value per successfully completed module
        value_per_completion = 100
        completed_students = overview['active_learners']
        completion_rate = overview['completion_rate']
        
        total_value = completed_students * (completion_rate / 100) * value_per_completion
        cost = overview['total_enrolled'] * 150
        
        roi = ((total_value - cost) / cost * 100) if cost > 0 else 0
        
        return {
            'estimated_value': round(total_value, 2),
            'estimated_cost': round(cost, 2),
            'estimated_roi_pct': round(roi, 1),
            'payback_period_months': 12  # Assumed annual program
        }
    
    def _get_default_proposal(self) -> Dict:
        """Default proposal when data unavailable"""
        return {
            'title': 'Impact Proposal - Magic Bus Compass 360',
            'status': 'Data loading...',
            'message': 'Proposal will be generated once data sources are connected.'
        }


# ========================
# HELPER FUNCTIONS
# ========================

def get_azure_dashboard() -> AzureDecisionDashboard:
    """Get singleton dashboard instance"""
    return AzureDecisionDashboard()


if __name__ == "__main__":
    # Test dashboard
    dashboard = get_azure_dashboard()
    
    print("\n" + "="*60)
    print("DECISION DASHBOARD TEST")
    print("="*60)
    
    overview = dashboard.get_executive_overview()
    print("\n📊 EXECUTIVE OVERVIEW:")
    for key, value in overview.items():
        print(f"  {key}: {value}")
    
    at_risk = dashboard.get_at_risk_youth()
    print(f"\n🚨 AT-RISK YOUTH: {len(at_risk)} students")
    
    effectiveness = dashboard.get_module_effectiveness()
    print(f"\n📚 MODULE EFFECTIVENESS: {len(effectiveness)} modules")
    
    proposal = dashboard.generate_proposal_insights()
    print(f"\n💡 PROPOSAL: {proposal.get('title')}")
