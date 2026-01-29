# Analytics & Metrics Framework

## Key Performance Indicators (KPIs)

### User Engagement KPIs

| KPI | Target | Current | Status | Threshold |
|-----|--------|---------|--------|-----------|
| Daily Active Users (DAU) | 30 | TBD | Pending | >20 |
| Weekly Active Users (WAU) | 40 | TBD | Pending | >35 |
| Monthly Active Users (MAU) | 50 | 50 | ✓ On Target | >40 |
| Session Duration (avg) | 15 min | 12 min | 80% | >10 min |
| Session Frequency (weekly) | 3.5 | TBD | Pending | >3 |
| Feature Usage Rate | 80% | TBD | Pending | >70% |

### Learning Outcomes KPIs

| KPI | Target | Current | Status | Threshold |
|-----|--------|---------|--------|-----------|
| Module Completion Rate | 80% | 60% | ⚠ Below Target | >70% |
| Quiz Pass Rate | 75% | 65% | ⚠ Below Target | >60% |
| Avg Time to Complete | 3 hours | 4 hours | ⚠ Below Target | <5 hours |
| Badge Earn Rate | 70% | 55% | ⚠ Below Target | >50% |
| Skill Certification Rate | 60% | 40% | ⚠ Below Target | >35% |
| Retention Rate (Week 4) | 70% | 60% | ⚠ Below Target | >50% |

### Business Impact KPIs

| KPI | Target | Current | Status | Threshold |
|-----|--------|---------|--------|-----------|
| Employment Placement Rate | 85% | TBD | Pending | >75% |
| Average Starting Salary | $45,000 | TBD | Pending | >$40,000 |
| Employer Satisfaction | 4.0/5 | TBD | Pending | >3.5/5 |
| Student Satisfaction | 4.2/5 | TBD | Pending | >3.8/5 |
| Sector Fit Success Rate | 75% | TBD | Pending | >65% |
| Feedback Completion Rate | 80% | TBD | Pending | >70% |

---

## Analytics Dashboards

### 1. Mobilisation Funnel

**Purpose**: Track user journey through key stages

```
Registered
    ├─ 50 users (100%)
    │
    ├──> Started Learning
    │     └─ 40 users (80%)
    │
    ├──> Attempted Quiz
    │     └─ 30 users (60%)
    │
    └──> Achievement Earned
          └─ 25 users (50%)
```

**Metrics Tracked:**
- Conversion rate between stages
- Drop-off reasons
- Time to next stage
- User segment analysis

---

### 2. Learning Progress Dashboard

**Purpose**: Monitor student learning journey

```python
# Dashboard Components
st.metric("Total Learners", 50)
st.metric("Modules Assigned", 100)
st.metric("Modules Completed", 60)
st.metric("Avg Completion %", 65)

# Charts
progress_by_module = get_progress_by_module()
st.bar_chart(progress_by_module)

difficulty_impact = get_completion_by_difficulty()
st.line_chart(difficulty_impact)

completion_timeline = get_completion_timeline()
st.area_chart(completion_timeline)
```

**Key Insights:**
- Module completion rate trend
- Difficulty level impact
- Student segment performance
- Time-to-completion analysis

---

### 3. Dropout Risk Dashboard

**Purpose**: Identify and track at-risk students

**Risk Scoring Model:**

```python
def calculate_dropout_risk(user_data):
    """
    Composite risk score (1-10):
    - No activity (7 days): +3 points
    - Low completion rate (<30%): +2 points
    - Modules started but not completed: +2 points
    - No quiz attempts: +1 point
    - Long inactive period: +2 points
    """
    risk_score = 0
    
    # Activity score
    days_inactive = (datetime.now() - user_data['last_activity']).days
    if days_inactive > 7:
        risk_score += 3
    elif days_inactive > 3:
        risk_score += 1
    
    # Completion score
    completion_rate = user_data['avg_completion_pct']
    if completion_rate < 30:
        risk_score += 2
    elif completion_rate < 50:
        risk_score += 1
    
    # Module engagement
    if user_data['modules_started'] > 0 and user_data['modules_completed'] == 0:
        risk_score += 2
    
    # Quiz engagement
    if user_data['quiz_attempts'] == 0:
        risk_score += 1
    
    return min(risk_score, 10)  # Cap at 10
```

**Risk Levels:**
- **High Risk (7-10)**: Immediate intervention needed
- **Medium Risk (4-6)**: Monitor closely
- **Low Risk (1-3)**: On track

**Dashboard Elements:**
- Risk distribution pie chart
- At-risk student list with actions
- Risk trend over time
- Intervention effectiveness

---

### 4. Sector Fit Analysis

**Purpose**: Align students with career sectors

```
Student Sector Interests:
├─ Design & UI/UX (Interest: 85%, Skill: 65%, Fit: 75%) - GREEN
├─ Full Stack Development (Interest: 70%, Skill: 50%, Fit: 60%) - AMBER  
└─ Data Science (Interest: 40%, Skill: 30%, Fit: 35%) - RED

Readiness Status:
├─ Green (Ready): 25 students (50%)
├─ Amber (Developing): 18 students (36%)
└─ Red (Needs Support): 7 students (14%)
```

**Fit Scoring:**
$$\text{Fit Score} = (I \times 0.3) + (S \times 0.5) + (A \times 0.2)$$

Where:
- $I$ = Interest Confidence (0-100)
- $S$ = Skill Readiness (0-100)
- $A$ = Alignment Score (0-100)

---

### 5. Gamification Impact Analysis

**Purpose**: Measure engagement through gamification

```
Comparison Groups:
┌──────────────────────────────┐
│ Badge Earners (n=30)         │
│ - Avg Engagement: 85%        │
│ - Completion Rate: 90%       │
│ - Session Duration: 18 min   │
│ - Weekly Sessions: 4.2       │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Non-Gamification (n=20)      │
│ - Avg Engagement: 60%        │
│ - Completion Rate: 65%       │
│ - Session Duration: 10 min   │
│ - Weekly Sessions: 2.5       │
└──────────────────────────────┘

Impact: +42% engagement with gamification
```

---

### 6. Employer Feedback Analysis

**Purpose**: Track employment outcomes and satisfaction

**Feedback Metrics:**
```
Overall Performance Ratings:
├─ Excellent (5/5): 35% of students
├─ Good (4/5): 45% of students
├─ Satisfactory (3/5): 18% of students
├─ Needs Improvement (2/5): 2% of students
└─ Poor (1/5): 0% of students

Skill Ratings (Average):
├─ Technical Skills: 4.2/5
├─ Communication: 4.1/5
├─ Teamwork: 4.3/5
├─ Work Ethic: 4.4/5
├─ Problem Solving: 4.0/5
└─ Punctuality: 4.5/5

Would Rehire: 92%
Recommendation Score (avg): 8.5/10
```

---

## Retention & Churn Analysis

### Retention Cohort Analysis

```
Cohort Retention by Week:
                Week 1  Week 2  Week 3  Week 4  Week 5  Week 6  Week 7  Week 8
Jan Cohort      100%    85%     72%     60%     50%     42%     35%     30%
Dec Cohort      100%    82%     68%     55%     45%     38%     32%     28%

Key Insight: Drop-off highest in Week 1-2 (retention dip to 85%)
```

### Churn Prediction Model

```python
def predict_churn_probability(user_data):
    """
    Features used:
    1. Days since last activity
    2. Completion rate trend
    3. Module consistency score
    4. Engagement velocity
    """
    features = {
        'days_inactive': user_data['days_inactive'],
        'completion_trend': user_data['completion_trend'],
        'consistency': user_data['module_consistency'],
        'engagement_velocity': user_data['engagement_velocity']
    }
    
    # Simple threshold-based model
    risk_probability = predict_from_features(features)
    
    return {
        'churn_probability': risk_probability,
        'recommended_action': get_intervention(risk_probability)
    }
```

---

## Custom Analytics Queries

### Query 1: Module Effectiveness

```sql
SELECT 
    module_id,
    COUNT(DISTINCT user_id) as learners,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / 
          COUNT(DISTINCT user_id), 1) as completion_rate,
    AVG(progress) as avg_progress,
    difficulty_level
FROM learning_modules
GROUP BY module_id, difficulty_level
ORDER BY completion_rate DESC;
```

### Query 2: User Segment Analysis

```sql
SELECT 
    CASE 
        WHEN avg_completion_pct >= 80 THEN 'High Performers'
        WHEN avg_completion_pct >= 50 THEN 'On Track'
        WHEN avg_completion_pct > 0 THEN 'At Risk'
        ELSE 'No Activity'
    END as segment,
    COUNT(*) as user_count,
    ROUND(100.0 * COUNT(*) / 
          (SELECT COUNT(*) FROM mb_users), 1) as percentage
FROM student_daily_features
GROUP BY segment
ORDER BY user_count DESC;
```

### Query 3: Feedback Response Rate

```sql
SELECT 
    s.student_id,
    s.full_name,
    COUNT(f.survey_id) as surveys_sent,
    SUM(CASE WHEN f.completed_date IS NOT NULL THEN 1 ELSE 0 END) as surveys_completed,
    ROUND(100.0 * SUM(CASE WHEN f.completed_date IS NOT NULL THEN 1 ELSE 0 END) / 
          COUNT(f.survey_id), 1) as response_rate
FROM mb_users s
LEFT JOIN youth_feedback_surveys f ON s.user_id = f.user_id
GROUP BY s.user_id, s.student_id, s.full_name
HAVING surveys_sent > 0;
```

---

## Reporting Schedule

| Report | Frequency | Recipient | Format |
|--------|-----------|-----------|--------|
| Daily Summary | Daily | Team Lead | Email |
| Weekly Performance | Weekly (Monday) | Management | Dashboard |
| Monthly Analytics | Monthly (1st) | Executive Team | PDF + Presentation |
| Quarterly Review | Quarterly | Board | Full Report |
| Annual Impact | Annually | Stakeholders | Comprehensive Report |

---

## Data Quality Metrics

### Data Completeness

| Field | Completeness | Target | Status |
|-------|-------------|--------|--------|
| User Email | 100% | 100% | ✓ |
| Student ID | 100% | 100% | ✓ |
| Module Assignment | 100% | 100% | ✓ |
| Feedback Submission | 75% | >80% | ⚠ |
| Survey Completion | 65% | >75% | ⚠ |

### Data Accuracy

```python
# Validation checks
accuracy_metrics = {
    'user_count_match': validate_user_count(),
    'module_assignments_valid': validate_module_data(),
    'completion_percentages_valid': validate_completion_ranges(),
    'date_consistency': validate_date_ranges(),
    'referential_integrity': validate_foreign_keys()
}
```

---

**Last Updated**: January 29, 2026
**Next Review**: February 29, 2026
