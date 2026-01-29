# User Journey Flows - Detailed Process Diagrams

## 1. Youth Registration Flow - Detailed

### High-Level Process

```mermaid
flowchart TD
    Start["🔗 User Visits Platform"] -->|HTTP Request| A["Streamlit App<br/>Port 8501"]
    A -->|Load| B["Check Session"]
    B -->|No Session| C["Show Login Page"]
    B -->|Has Session| D["Redirect to Dashboard"]
    C -->|Click 'Register'| E["Show Registration Form"]
    E -->|Fill Form| F{Validate Input}
    F -->|Invalid| G["Show Error<br/>- Invalid Email<br/>- Weak Password<br/>- Email Exists"]
    G -->|Retry| E
    F -->|Valid| H["Hash Password"]
    H -->|Create| I["Insert into mb_users<br/>- user_id (auto)<br/>- email<br/>- password_hash<br/>- role = 'student'<br/>- created_at"]
    I -->|Success| J["Create Session<br/>st.session_state"]
    I -->|Failure| K["Show DB Error"]
    J -->|Redirect| L["Youth Dashboard"]
    K -->|Retry| E
    L -->|Load| M["Display Profile<br/>- Student ID<br/>- Email<br/>- Institution"]
    M -->|End| N["✅ Registration Complete"]
```

### Detailed Sequence Diagram

```mermaid
sequenceDiagram
    actor User as Youth User<br/>Browser
    participant UI as Streamlit UI<br/>0_login.py
    participant Auth as Auth Module<br/>Authentication
    participant Hash as Password<br/>Hashing
    participant DB as SQLite DB<br/>mb_compass.db
    participant Session as Session Manager<br/>st.session_state
    
    User->>UI: Click "Register" Button
    UI->>UI: Display Registration Form
    Note over UI: Form Fields:<br/>- Email<br/>- Password (confirm)<br/>- Full Name<br/>- Institution<br/>- Education Level
    
    User->>UI: Fill & Submit Form
    UI->>Auth: validate_input(form_data)
    Auth->>Auth: Check Email Format
    Auth->>Auth: Check Password Strength
    Auth->>DB: SELECT * FROM mb_users WHERE email=?
    
    alt Email Already Exists
        DB-->>Auth: User Record Found
        Auth-->>UI: Error: "Email Already Registered"
        UI-->>User: Show Error Message
        User->>UI: Correct Email & Retry
    else Email is Unique
        DB-->>Auth: No Records Found
        Auth->>Hash: hash_password(password)
        Hash-->>Auth: password_hash
        Auth->>DB: INSERT INTO mb_users
        Note over DB: INSERT VALUES<br/>- null (auto id)<br/>- email<br/>- password_hash<br/>- 'student' (role)<br/>- full_name<br/>- institution<br/>- education_level<br/>- NULL (phone)<br/>- NULL (dob)<br/>- NULL (skills)<br/>- NOW() (created_at)
        
        DB-->>Auth: Success (user_id=X)
        Auth->>Session: Create Session
        Note over Session: st.session_state updates:<br/>- logged_in = True<br/>- user_id = X<br/>- email = user@email.com<br/>- role = 'student'<br/>- full_name = name
        Session-->>Auth: Session Created
        Auth-->>UI: Success
        UI->>UI: Clear Form
        UI->>UI: Redirect Page
        UI-->>User: "Welcome! → Youth Dashboard"
    end
```

### Error Handling Flow

```mermaid
flowchart TD
    Input["User Registration<br/>Input"] -->|Validate| A{Email Valid?}
    A -->|No| E1["❌ Show Error<br/>Invalid Email Format"]
    E1 -->|User Retry| Input
    A -->|Yes| B{Password<br/>Strong?}
    B -->|No| E2["❌ Show Error<br/>Password < 8 chars"]
    E2 -->|User Retry| Input
    B -->|Yes| C{Email Unique<br/>in DB?}
    C -->|No| E3["❌ Show Error<br/>Email Already Registered"]
    E3 -->|User Retry| Input
    C -->|Yes| D["✅ Create User<br/>in Database"]
    D -->|Insert Success| Success["✅ Registration<br/>Complete"]
    D -->|DB Error| E4["❌ Show Error<br/>Database Error"]
    E4 -->|Retry| D
```

---

## 2. Youth Dashboard Flow - Complete User Journey

### Youth Dashboard Process

```mermaid
flowchart TD
    A["Youth Logs In"] -->|Authenticated| B["Load Youth Dashboard<br/>2_youth_dashboard.py"]
    B -->|Query| C["Get User Profile<br/>FROM mb_users"]
    B -->|Query| D["Get Learning Modules<br/>FROM learning_modules"]
    B -->|Query| E["Get Progress<br/>FROM student_daily_features"]
    B -->|Query| F["Get Feedback Status<br/>FROM survey_distribution_logs"]
    
    C -->|Display| G["Profile Section<br/>- Student ID<br/>- Email<br/>- Full Name<br/>- Institution<br/>- Education Level"]
    
    D -->|Display| H["Modules Section<br/>- List of Assigned Modules<br/>- Module Title<br/>- Description<br/>- Status"]
    
    E -->|Display| I["Progress Section<br/>- Modules Assigned<br/>- Modules Completed<br/>- Completion %<br/>- Days Since Registration"]
    
    F -->|Display| J["Feedback Section<br/>- Survey Forms<br/>- Response Status<br/>- Submit Button"]
    
    H -->|Click Module| K["View Module Details<br/>- Full Description<br/>- Duration<br/>- Skills Covered<br/>- Current Progress"]
    
    J -->|Click Feedback| L["Open Survey Form<br/>1. Role Match<br/>2. Satisfaction<br/>3. Growth Opportunity<br/>4. Compensation<br/>5. Comments"]
    
    L -->|Submit| M["Validate Survey<br/>- Required Fields<br/>- Rating Ranges<br/>- Comment Length"]
    
    M -->|Valid| N["Store Survey<br/>INSERT INTO<br/>youth_feedback_surveys"]
    M -->|Invalid| O["Show Validation<br/>Errors"]
    
    O -->|Correct| L
    N -->|Success| P["Show Confirmation<br/>✅ Feedback Saved"]
    P -->|Continue| J
```

### Detailed Sequence Diagram - Profile & Progress

```mermaid
sequenceDiagram
    participant Youth as Youth User
    participant Dashboard as Youth Dashboard<br/>Page
    participant YouthService as Youth Service<br/>Data Layer
    participant DB as SQLite Database
    participant Cache as Session Cache
    
    Youth->>Dashboard: Load Page
    Dashboard->>Cache: Check Cached Profile
    
    alt Cache Hit
        Cache-->>Dashboard: Profile Data (TTL Valid)
    else Cache Miss
        Dashboard->>YouthService: get_user_profile(user_id)
        YouthService->>DB: SELECT * FROM mb_users<br/>WHERE user_id = ?
        DB-->>YouthService: User Record
        YouthService->>DB: SELECT * FROM learning_modules<br/>WHERE user_id = ?
        DB-->>YouthService: Module List (2 records)
        YouthService->>DB: SELECT * FROM student_daily_features<br/>WHERE user_id = ?
        DB-->>YouthService: Feature Record
        YouthService->>Cache: Store Profile
        YouthService-->>Dashboard: Profile Object
        Cache-->>Dashboard: Cached Copy
    end
    
    Dashboard->>Dashboard: Render Profile Section
    Note over Dashboard: Display:<br/>- Student ID: MB-APAC-2026-ABC<br/>- Email: youth@magicbus.local<br/>- Name: Student Name<br/>- Institution: School Name
    
    Dashboard->>Dashboard: Render Modules Section
    Note over Dashboard: Module 1: Python Basics<br/>Status: In Progress (60%)<br/>Module 2: Communication<br/>Status: Completed
    
    Dashboard->>Dashboard: Render Progress Card
    Note over Dashboard: Assigned: 2<br/>Completed: 1<br/>Completion: 50%<br/>Days: 15 days
    
    Dashboard-->>Youth: Display Dashboard
```

### Feedback Survey Submission Flow

```mermaid
sequenceDiagram
    participant Youth as Youth User
    participant SurveyUI as Feedback Form<br/>Streamlit UI
    participant Validator as Form Validator
    participant DB as SQLite DB
    
    Youth->>SurveyUI: Click "Submit Feedback"
    SurveyUI->>Youth: Show Survey Questions
    
    Note over SurveyUI: Survey Questions:<br/>1. Role Match (1-5)<br/>2. Environment (1-5)<br/>3. Growth (1-5)<br/>4. Compensation (1-5)<br/>5. Comments (text)
    
    Youth->>SurveyUI: Fill All Answers
    Youth->>SurveyUI: Click "Submit"
    
    SurveyUI->>Validator: validate_survey(form_data)
    Validator->>Validator: Check All Fields Filled
    Validator->>Validator: Check Ratings in Range
    Validator->>Validator: Check Comments < 500 chars
    
    alt Validation Fails
        Validator-->>SurveyUI: Error Messages
        SurveyUI-->>Youth: Show Errors & Highlights
        Youth->>SurveyUI: Correct Errors
        SurveyUI->>Validator: validate_survey(form_data)
    else Validation Passes
        Validator-->>SurveyUI: OK
        SurveyUI->>DB: INSERT INTO youth_feedback_surveys
        Note over DB: INSERT VALUES<br/>- survey_id (auto)<br/>- user_id<br/>- email<br/>- placement_company<br/>- job_title<br/>- rating_1, rating_2, ...<br/>- comments<br/>- NOW() (created_at)
        
        DB-->>SurveyUI: Inserted (survey_id=X)
        SurveyUI->>SurveyUI: Refresh Page
        SurveyUI-->>Youth: "✅ Feedback Saved Successfully"
    end
```

---

## 3. Admin Control Flow - Complete

### Admin Dashboard Process

```mermaid
flowchart TD
    A["Admin Logs In"] -->|Role Check| B{Is Admin?}
    B -->|No| C["❌ Access Denied"]
    B -->|Yes| D["Load Admin Portal<br/>3_magicbus_admin.py"]
    
    D -->|Query| E["Load Dashboard Data<br/>- Total Users<br/>- Module Count<br/>- Survey Status"]
    
    D -->|Display| F["Admin Menu"]
    
    F -->|Option 1| G["👥 User Management"]
    F -->|Option 2| H["📚 Module Management"]
    F -->|Option 3| I["📋 Survey Distribution"]
    F -->|Option 4| J["📊 System Reports"]
    
    G -->|Action| G1["List All Users<br/>- User ID<br/>- Email<br/>- Role<br/>- Created Date"]
    G1 -->|Search| G2["Filter Users<br/>- By Email<br/>- By Role<br/>- By Date"]
    
    H -->|Action| H1["View Modules<br/>- Module List<br/>- Completion Stats<br/>- Learner Count"]
    H1 -->|Edit| H2["Create/Edit Module<br/>- Title<br/>- Description<br/>- Duration<br/>- Skills"]
    H2 -->|Save| H3["Store in DB<br/>INSERT/UPDATE<br/>learning_modules"]
    
    I -->|Action| I1["Create Survey<br/>- Select Template<br/>- Choose Recipients<br/>- Set Deadline"]
    I1 -->|Send| I2["Distribute Survey<br/>- Send Emails<br/>- Create Log Records<br/>- Track Opens"]
    I2 -->|Store| I3["Log Distribution<br/>INSERT<br/>survey_distribution_logs"]
    
    J -->|Action| J1["View Reports<br/>- Completion Rate<br/>- Dropout Risk<br/>- Engagement Stats"]
```

### Admin Workflow - Detailed Sequence

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant Portal as Admin Portal<br/>3_magicbus_admin.py
    participant AdminSvc as Admin Service
    participant DB as SQLite DB
    participant Email as Email Service<br/>Background Job
    
    Admin->>Portal: Navigate to Admin Portal
    Portal->>AdminSvc: load_dashboard()
    AdminSvc->>DB: SELECT COUNT(*) FROM mb_users
    DB-->>AdminSvc: 50
    AdminSvc->>DB: SELECT COUNT(*) FROM learning_modules
    DB-->>AdminSvc: 16
    AdminSvc-->>Portal: Dashboard Data
    Portal-->>Admin: Show Admin Dashboard
    
    Note over Portal: Admin Options:<br/>- User Management<br/>- Module Management<br/>- Survey Distribution<br/>- System Health
    
    Admin->>Portal: Click "Create New Module"
    Portal-->>Admin: Show Module Form
    
    Admin->>Portal: Fill Module Details
    Note over Admin: - Title: "Leadership Skills"<br/>- Duration: 4 weeks<br/>- Skills: Leadership, Communication<br/>- Description: Learn to lead
    
    Admin->>Portal: Submit Form
    Portal->>AdminSvc: create_module(module_data)
    AdminSvc->>AdminSvc: Validate Module
    AdminSvc->>DB: INSERT INTO learning_modules
    Note over DB: INSERT VALUES<br/>- module_id (auto)<br/>- title<br/>- description<br/>- duration<br/>- skills<br/>- status = 'active'
    DB-->>AdminSvc: Inserted (module_id=17)
    AdminSvc-->>Portal: Success
    Portal-->>Admin: "✅ Module Created"
    
    Admin->>Portal: Click "Send Survey"
    Portal-->>Admin: Show Survey Distribution Form
    
    Admin->>Portal: Select Recipients & Template
    Admin->>Portal: Submit
    Portal->>AdminSvc: send_survey(recipients, template)
    AdminSvc->>DB: SELECT * FROM mb_users WHERE role='student'
    DB-->>AdminSvc: 50 Users
    AdminSvc->>Email: Send Emails (async)
    AdminSvc->>DB: INSERT INTO survey_distribution_logs (x50 records)
    Note over DB: Log each send:<br/>- recipient_email<br/>- survey_type<br/>- sent_date<br/>- opened = False
    DB-->>AdminSvc: Inserted
    AdminSvc-->>Portal: Success
    Portal-->>Admin: "✅ Surveys Sent to 50 Recipients"
    Email->>Email: Send 50 Emails
```

### Module Creation & Management

```mermaid
flowchart TD
    A["Admin: Create Module"] -->|Form| B["Enter Module Details<br/>- Title<br/>- Description<br/>- Duration<br/>- Skills<br/>- Prerequisites<br/>- Difficulty"]
    B -->|Validate| C{Valid Input?}
    C -->|No| D["Show Validation<br/>Errors"]
    D -->|Correct| B
    C -->|Yes| E["Store in DB"]
    E -->|Query| F["INSERT INTO<br/>learning_modules"]
    F -->|Success| G["✅ Module Created<br/>module_id=X"]
    F -->|Failure| H["❌ Database Error"]
    
    G -->|Next| I["Assign to Youth<br/>- Select Module<br/>- Select Students"]
    I -->|Assign| J["UPDATE learning_modules<br/>SET user_id = Y"]
    J -->|Success| K["✅ Assigned to<br/>N Students"]
    
    K -->|Track| L["View Completion<br/>- Modules Assigned<br/>- Modules Completed<br/>- Completion %"]
    
    L -->|Report| M["Generate Report<br/>- Per Module Stats<br/>- Overall Stats<br/>- Effectiveness"]
```

---

## 4. Decision Intelligence Flow - Complete

### Decision Intelligence Dashboard Process

```mermaid
flowchart TD
    A["Admin: Access DI<br/>Decision Intelligence<br/>4_decision_intelligence_azure.py"] -->|Load| B["Initialize Components"]
    
    B -->|Create| B1["AzureBlobConnector"]
    B -->|Create| B2["AzureFeatureEngineer"]
    B -->|Create| B3["AzureDecisionDashboard"]
    
    C["Sidebar: Refresh Features<br/>Click 🔄 Button"] -->|Trigger| D["Feature Engineering<br/>Pipeline"]
    
    D -->|Load| D1["Load Raw Data<br/>- From SQLite<br/>- From Azure Blob"]
    D1 -->|Query| E["mb_users (50)"]
    D1 -->|Query| F["learning_modules (16)"]
    D1 -->|Query| G["student_daily_features"]
    
    D -->|Compute| H["Compute 6 Features"]
    H -->|Feature 1| H1["student_daily_features<br/>- modules_assigned<br/>- modules_completed<br/>- avg_completion_pct"]
    H -->|Feature 2| H2["dropout_risk<br/>- risk_level: HIGH/MED/LOW<br/>- risk_score: 1-9<br/>- risk_reason"]
    H -->|Feature 3| H3["sector_fit<br/>- sector: Design, Programming...<br/>- sector_fit_score: 0-100<br/>- readiness_status: Green/Amber/Red"]
    H -->|Feature 4| H4["module_effectiveness<br/>- completion_rate<br/>- effectiveness_level"]
    H -->|Feature 5| H5["gamification_impact<br/>- Badge earners vs non-earners<br/>- Engagement comparison"]
    H -->|Feature 6| H6["mobilisation_funnel<br/>- 4 stages<br/>- Progression %"]
    
    D -->|Store| I["Cache Features<br/>In Memory<br/>TTL: 1 hour"]
    
    I -->|Return| J["Feature Data Ready<br/>✅ All 6 Computed"]
    
    J -->|Display| TAB1["Tab 1: Executive Overview<br/>- KPIs: 50 enrolled<br/>- 70.9% completion<br/>- 40% dropout"]
    J -->|Display| TAB2["Tab 2: Mobilisation Funnel<br/>- Funnel Chart<br/>- Progression Stats"]
    J -->|Display| TAB3["Tab 3: Sector Heatmap<br/>- Sector vs Readiness<br/>- Interactive Heatmap"]
    J -->|Display| TAB4["Tab 4: At-Risk Youth<br/>- Student List<br/>- Risk Scores<br/>- Interventions"]
    J -->|Display| TAB5["Tab 5: Module Effectiveness<br/>- Module Rankings<br/>- Completion Rates"]
    J -->|Display| TAB6["Tab 6: Gamification<br/>- Comparison Metrics<br/>- Impact Analysis"]
    J -->|Display| TAB7["Tab 7: Proposals<br/>- AI-Generated<br/>- Download PDF"]
```

### Detailed Feature Computation Flow

```mermaid
sequenceDiagram
    participant Admin as Admin/Stakeholder
    participant UI as DI Dashboard UI
    participant Engineer as Feature Engineer
    participant Connector as Azure Connector
    participant DB as SQLite DB
    participant Azure as Azure Blob
    participant Cache as Feature Cache
    
    Admin->>UI: Click "Compute Features" Button
    UI->>Engineer: compute_all_features()
    
    Note over Engineer: Load Feature 1<br/>student_daily_features
    Engineer->>Connector: load_dataset("student_daily_features")
    Connector->>Cache: Check Cache
    alt Cache Hit
        Cache-->>Connector: Return Cached
    else Cache Miss
        Connector->>DB: SELECT from student_daily_features
        DB-->>Connector: 50 Records
        Connector->>Cache: Store in Cache
    end
    Connector-->>Engineer: DataFrame (50 rows)
    
    Note over Engineer: Load Feature 2<br/>dropout_risk
    Engineer->>Connector: load_dataset("student_dropout_risk")
    Connector->>DB: SELECT from student_dropout_risk
    DB-->>Connector: 50 Records
    Connector-->>Engineer: DataFrame
    
    Note over Engineer: Load Feature 3-6...<br/>Similar pattern
    
    Engineer->>Engineer: Aggregate Metrics
    Note over Engineer: For Executive Overview:<br/>- total_enrolled: COUNT(*) = 50<br/>- completion_rate: AVG(completion%) = 70.9%<br/>- dropout_risk_pct: COUNT(HIGH) / 50 = 40%<br/>- engagement_score: (active/50)*100 = 57%
    
    Engineer->>Engineer: Build Sector Heatmap
    Note over Engineer: Cross-tab:<br/>Sector x Readiness<br/>6 sectors × 3 statuses<br/>= 18 data points
    
    Engineer->>Engineer: Extract At-Risk Youth
    Note over Engineer: WHERE dropout_risk = 'HIGH'<br/>ORDER BY risk_score DESC<br/>LIMIT 10
    
    Engineer-->>UI: All Features Ready
    
    UI->>UI: Render 7 Tabs
    UI->>UI: Tab 1: Display KPIs
    Note over UI: Show Cards:<br/>- 👥 50 Enrolled<br/>- 📚 70.9% Completion<br/>- ⚠️ 40% Dropout
    
    UI->>UI: Tab 3: Render Heatmap
    Note over UI: Plotly Heatmap<br/>X: Sector<br/>Y: Readiness<br/>Z: Count
    
    UI->>UI: Tab 4: Display Youth Table
    Note over UI: Top 10 At-Risk<br/>- Student Name<br/>- Risk Score<br/>- Risk Level
    
    UI-->>Admin: Display Complete Dashboard
```

### Proposal Generation Flow

```mermaid
flowchart TD
    A["Admin: Proposal Tab"] -->|Form| B["Enter Proposal Params<br/>- Region: APAC<br/>- Sector: Design<br/>- Grade Level: High School"]
    B -->|Submit| C["Generate Insights<br/>generate_proposal_insights()"]
    
    C -->|Query| C1["Get Sector Data<br/>- Youth in sector<br/>- Completion rate<br/>- Readiness status"]
    C -->|Query| C2["Get Effectiveness<br/>- Module performance<br/>- Skills coverage<br/>- Time investment"]
    
    C -->|Analyze| C3["Calculate Metrics<br/>- ROI potential<br/>- Funding needs<br/>- Timeline"]
    
    C -->|Generate| C4["Create Proposal Text<br/>- Executive Summary<br/>- Youth Profile<br/>- Sector Analysis<br/>- Resource Needs<br/>- Expected Outcomes"]
    
    C4 -->|Format| C5["Build Proposal<br/>- Header<br/>- Sections<br/>- Metrics<br/>- Recommendations"]
    
    C5 -->|Display| D["Show Proposal<br/>in Streamlit"]
    
    D -->|User Action| E{User Action}
    E -->|Download| F["Generate PDF<br/>Proposal Document"]
    E -->|Copy| G["Copy to Clipboard"]
    E -->|Share| H["Send via Email"]
    
    F -->|Download| I["Download:<br/>proposal_<br/>YYYY_MM_DD.pdf"]
```

---

## Data State Transitions

### User State Machine

```mermaid
stateDiagram-v2
    [*] --> NotRegistered
    NotRegistered -->|Register| Registered
    Registered -->|Submit Profile| ProfileComplete
    ProfileComplete -->|Start Learning| Learning
    Learning -->|Complete Module| ModuleComplete
    Learning -->|Submit Feedback| FeedbackSubmitted
    FeedbackSubmitted -->|[Optional] Continue| Learning
    ModuleComplete -->|All Done| Graduated
    
    note right of NotRegistered
        - New visitor
        - No account
    end note
    
    note right of Registered
        - Account created
        - Initial profile
    end note
    
    note right of ProfileComplete
        - Full details entered
        - Ready to learn
    end note
    
    note right of Learning
        - Active participation
        - Module assignments
    end note
    
    note right of ModuleComplete
        - Finished module
        - Progress updated
    end note
    
    note right of FeedbackSubmitted
        - Feedback recorded
        - Data analyzed
    end note
```

---

**Last Updated**: January 29, 2026
