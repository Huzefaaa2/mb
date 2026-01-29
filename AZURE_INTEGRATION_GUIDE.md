# Azure Data Integration Guide

## Overview

The Decision Intelligence Dashboard now connects to Azure Blob Storage to retrieve real-time datasets from the APAC region. This guide explains how to use the Azure-powered reporting system.

## Data Source

**Azure Blob Storage URL:** `https://defaultstoragehackathon.blob.core.windows.net/usethisone/apac`

### Available Datasets

The system integrates with 25+ tables from the APAC region:

#### Core Student Data
- **students** - Student enrollment and basic info
- **student_progress** - Module completion tracking
- **student_skills** - Skill assessments and proficiency
- **student_achievements** - Badges and achievements earned

#### Learning Content
- **learning_modules** - Module definitions and metadata
- **lessons** - Individual lesson content
- **lesson_content** - Lesson media and resources
- **quizzes** - Quiz definitions
- **quiz_questions** - Quiz question bank
- **quiz_attempts** - Student quiz performance
- **quiz_responses** - Individual quiz answers

#### Career & Skills
- **career_interests** - Student career pathway interests
- **career_pathways** - Career path definitions
- **skills** - Skill definitions and levels
- **pathway_skills** - Skill requirements per pathway

#### Engagement & Gamification
- **daily_challenges** - Daily challenge data
- **achievements** - Badge/achievement definitions
- **points_ledger** - Gamification points tracking
- **user_sessions** - User activity sessions
- **notifications** - System notifications sent

#### Infrastructure
- **schools** - School information
- **teachers** - Teacher profiles
- **safety_scenarios** - Safety training scenarios
- **scenario_responses** - Safety response data

---

## Architecture

### Data Flow

```
Azure Blob Storage (APAC)
        ↓
Azure Blob Connector (azure_blob_connector.py)
        ↓
Feature Engineer (azure_feature_engineer.py)
        ↓
6 Enriched Features:
  • student_daily_features
  • dropout_risk
  • sector_fit
  • module_effectiveness
  • gamification_impact
  • mobilisation_funnel
        ↓
Decision Dashboard (azure_decision_dashboard.py)
        ↓
Streamlit UI (4_decision_intelligence_azure.py)
        ↓
7 Interactive Dashboards + Proposal Generator
```

### Key Components

#### 1. **Azure Blob Connector** (`azure_blob_connector.py`)
- Connects to Azure Blob Storage
- Downloads CSV files
- Caches data locally
- Provides health checks

**Usage:**
```python
from azure_blob_connector import get_blob_connector

connector = get_blob_connector()
students_df = connector.get_students()
progress_df = connector.get_student_progress()
```

#### 2. **Feature Engineer** (`azure_feature_engineer.py`)
- Computes 6 enriched feature sets
- Generates dropout risk scores
- Calculates sector fit metrics
- Creates mobilisation funnel

**Usage:**
```python
from azure_feature_engineer import get_azure_feature_engineer

engineer = get_azure_feature_engineer()
features = engineer.compute_all_features()
```

#### 3. **Decision Dashboard** (`azure_decision_dashboard.py`)
- Retrieves and aggregates features
- Generates executive summaries
- Creates at-risk youth lists
- Generates funding proposals

**Usage:**
```python
from azure_decision_dashboard import get_azure_dashboard

dashboard = get_azure_dashboard()
overview = dashboard.get_executive_overview()
at_risk = dashboard.get_at_risk_youth(limit=50)
```

#### 4. **Streamlit UI** (`pages/4_decision_intelligence_azure.py`)
- 7 interactive dashboard tabs
- Real-time data visualization
- Proposal generator
- Export capabilities

---

## Feature Definitions

### 1. **Student Daily Features**
Aggregates engagement metrics per student:
- Modules assigned, started, completed
- Average completion percentage
- Quiz participation and scores
- Session frequency
- Time spent learning

**Key Columns:**
- `student_id`, `display_name`, `email`
- `modules_assigned`, `modules_completed`
- `avg_completion_pct`
- `quizzes_attempted`, `avg_quiz_score`
- `sessions_count`, `total_session_minutes`
- `days_since_enrollment`

### 2. **Dropout Risk Score**
Predicts student dropout probability:
- **HIGH (9)**: <3 modules started + <30% avg completion
- **MEDIUM (5)**: <5 modules started OR <50% avg completion
- **LOW (1)**: Otherwise

**Key Columns:**
- `student_id`, `risk_level`, `risk_score` (1-9)
- `risk_reason` - Explanation of risk factors
- `modules_started`, `avg_completion_pct`

### 3. **Sector Fit Score**
Matches students to career sectors:
- **Green (≥70)**: Ready for sector
- **Amber (50-69)**: Developing skills
- **Red (<50)**: Needs support

**Calculation:**
```
sector_fit_score = (interest_confidence × 0.6 + skill_proficiency × 0.4)
```

### 4. **Module Effectiveness**
Ranks modules by learning outcomes:
- **High Impact (≥80% completion)**: Scale & promote
- **Medium Impact (60-79%)**: Monitor
- **Needs Improvement (<60%)**: Revise

### 5. **Gamification Impact**
Measures badges/points impact:
- Compares badge earners vs control group
- Tracks completion rates
- Engagement score calculation

### 6. **Mobilisation Funnel**
Tracks 4-stage progression:
1. **Registered** - Total enrolled students
2. **Started Learning** - Has progress records
3. **Quiz Participation** - Attempted quizzes
4. **Achievement** - Earned certificates

---

## Dashboard Tabs

### Tab 1: Executive Overview
**KPIs Displayed:**
- Youth Enrolled (count)
- Active Learners (count + %)
- Completion Rate (%)
- Dropout Risk (%)
- Average Quiz Score (0-100)
- Quiz Pass Rate (%)
- Engagement Score (composite)

**Recommendations:**
- High dropout risk alert & intervention suggestions
- Low completion rate alert & module review suggestions

### Tab 2: Mobilisation Funnel
**Visualization:**
- Funnel chart showing stage progression
- Dropoff analysis between stages
- Metrics table with counts & percentages

**Use Case:** Monitor enrollment → achievement conversion

### Tab 3: Sector Heatmap
**Visualization:**
- Heatmap: Sectors × Readiness Status
- Distribution of students across sectors
- Green/Amber/Red alignment

**Use Case:** Identify sector opportunities & skills gaps

### Tab 4: At-Risk Youth
**Features:**
- Prioritized list of 10-100 students
- Filterable by risk level (HIGH/MEDIUM/LOW)
- Risk score & reason columns
- Risk distribution pie chart

**Use Case:** Target interventions & support

### Tab 5: Module Effectiveness
**Visualizations:**
- Bar chart: Completion rates by module
- Detailed metrics table
- Effectiveness distribution pie chart

**Use Case:** Curriculum optimization & resource allocation

### Tab 6: Gamification Impact
**Metrics:**
- Badge earners vs control group comparison
- Completion rate lift (%)
- Engagement score impact

**Use Case:** Justify gamification budget & ROI

### Tab 7: Proposal Generator
**Inputs:**
- Sector filter (optional)
- Grade level filter (optional)

**Outputs:**
- Executive summary
- Key metrics (enrolled, active, completion, at-risk)
- Impact highlights
- At-risk analysis with intervention strategies
- Module recommendations (scale vs revise)
- Gamification insights
- Funding requirements calculation
- ROI projection
- Downloadable proposal text

---

## How to Use

### Starting the Dashboard

```bash
cd c:\Users\HHusain\mb
streamlit run mb/app.py
```

Then navigate to: **Admin & Intelligence** → **🧠 Decision Intelligence** → **Tab with 📊 icon**

### Refreshing Features

1. Click **🔄 Compute Features** button in sidebar
2. Wait for confirmation (typically 10-30 seconds)
3. Refresh dashboard page
4. New data appears in all tabs

### Testing Connection

1. Click **🔗 Test Connection** button in sidebar
2. See connection status and available datasets
3. If connected, proceed with feature refresh

### Generating a Proposal

1. Navigate to **Tab 7: Proposal Generator**
2. (Optional) Filter by sector or grade level
3. Click **📄 Generate Proposal**
4. Review generated proposal
5. Click **📥 Download Proposal as Text** to save

---

## Configuration

### Azure Blob Storage Connection

**Connection String:**
```
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=defaultstoragehackathon;...
```

Set as environment variable or edit in `azure_blob_connector.py`:

```python
self.connection_string = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "YOUR_CONNECTION_STRING_HERE"
)
```

### Data Refresh Intervals

**Default:** On-demand via button click

**To Schedule Automatic Refresh:**
Create a cron job (Linux/Mac) or scheduled task (Windows):

```bash
# Every hour
0 * * * * python -c "from azure_feature_engineer import refresh_all_azure_features; refresh_all_azure_features()"
```

---

## Data Quality & Validation

### Health Check

```python
from azure_blob_connector import get_blob_connector

connector = get_blob_connector()
health = connector.get_health_report()

print(health['connection_status'])
print(health['available_datasets'])
print(health['tables_checked'])
```

### Expected Data Volumes (APAC)

- **Students**: 10,000+
- **Progress Records**: 100,000+
- **Quiz Attempts**: 50,000+
- **Career Surveys**: 5,000+
- **Achievements**: 20,000+

---

## Performance & Optimization

### Feature Computation Time

- **Initial Run**: 15-30 seconds (depending on dataset size)
- **Subsequent Runs**: 10-20 seconds (with caching)
- **Dashboard Load**: <1 second (from cache)

### Optimization Tips

1. **Cache Management**: Features are cached in memory after first refresh
2. **Limit Row Retrieval**: Specify limits for large tables
3. **Parallel Processing**: Feature engineer processes tables concurrently

---

## Troubleshooting

### Issue: "No Azure connection"
**Solution:** 
- Check internet connectivity
- Verify Azure storage URL is accessible
- Check connection string in environment variables

### Issue: "No data available"
**Solution:**
- Click "🔄 Compute Features" to generate features
- Wait for confirmation message
- Check Azure datasets are populated

### Issue: "Slow dashboard load"
**Solution:**
- Reduce row limits in queries
- Increase cache refresh interval
- Check Azure network latency

### Issue: "Missing columns in output"
**Solution:**
- Verify dataset structure matches expected schema
- Check column naming conventions match
- Update feature engineer queries if needed

---

## Roadmap

### Phase 1 (Current)
✅ Azure Blob connector
✅ 6 feature tables
✅ 7 dashboard tabs
✅ Proposal generator

### Phase 2 (Planned)
- 🔄 Automated daily feature refresh
- 📊 Dashboard scheduling & email reports
- 🤖 ML-based predictions (placement likelihood)
- 📈 Cohort analysis & benchmarking

### Phase 3 (Future)
- 🌐 Databricks Delta Lake integration
- 📱 Mobile app for teachers
- 🚀 Production Kubernetes deployment
- 💬 Real-time chat insights

---

## Support

For issues or questions:
- Check Azure connectivity first
- Review logs in console
- Verify dataset schema matches expected columns
- Contact data team for support

---

**Last Updated:** January 29, 2026
**Version:** 2.0 (Azure Integration)
