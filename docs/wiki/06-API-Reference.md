# API Reference & Integration Guide

## REST API Endpoints

### Authentication

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
    "login_id": "student@magicbus.com",
    "password": "password123"
}

Response (200):
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user_id": 1,
    "role": "student",
    "student_id": "MB-APAC-2026-ABC01"
}

Error (401):
{
    "error": "Invalid credentials"
}
```

#### Register
```
POST /api/auth/register
Content-Type: application/json

{
    "email": "student@magicbus.com",
    "password": "password123",
    "full_name": "John Doe",
    "institution": "XYZ University"
}

Response (201):
{
    "user_id": 1,
    "student_id": "MB-APAC-2026-ABC01",
    "message": "Registration successful"
}
```

---

### User Management

#### Get User Profile
```
GET /api/users/{user_id}
Authorization: Bearer <token>

Response (200):
{
    "user_id": 1,
    "login_id": "student@magicbus.com",
    "full_name": "John Doe",
    "student_id": "MB-APAC-2026-ABC01",
    "email": "student@magicbus.com",
    "role": "student",
    "institution": "XYZ University",
    "education_level": "Undergraduate",
    "created_at": "2026-01-15T10:00:00Z"
}
```

#### Update User Profile
```
PUT /api/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "full_name": "John Doe Updated",
    "phone": "+1-555-0123",
    "skills": "Python, JavaScript, SQL"
}

Response (200):
{
    "message": "Profile updated successfully"
}
```

#### List Users (Admin Only)
```
GET /api/users?role=student&limit=50&offset=0
Authorization: Bearer <admin_token>

Response (200):
{
    "total": 50,
    "limit": 50,
    "offset": 0,
    "users": [...]
}
```

---

### Learning Modules

#### Get Module Assignments
```
GET /api/modules/assignments/{user_id}
Authorization: Bearer <token>

Response (200):
{
    "assignments": [
        {
            "module_assignment_id": 1,
            "module_id": "py101",
            "title": "Python Basics",
            "description": "Introduction to Python",
            "duration": 4,
            "difficulty_level": "Beginner",
            "status": "active",
            "progress": 45,
            "started_date": "2026-01-15",
            "skills": "Python, Programming Fundamentals"
        }
    ]
}
```

#### Update Module Progress
```
PUT /api/modules/progress/{module_assignment_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "progress": 75,
    "status": "in_progress"
}

Response (200):
{
    "message": "Progress updated",
    "progress": 75,
    "updated_at": "2026-01-29T10:00:00Z"
}
```

#### Complete Module
```
POST /api/modules/complete/{module_assignment_id}
Authorization: Bearer <token>

Response (200):
{
    "message": "Module completed successfully",
    "points_earned": 100,
    "badges_earned": ["Learner", "Completed Module"]
}
```

---

### Surveys

#### Get Survey Templates
```
GET /api/surveys/templates?type=youth_feedback
Authorization: Bearer <token>

Response (200):
{
    "templates": [
        {
            "template_id": 1,
            "template_type": "youth_feedback",
            "template_name": "Post-Placement Feedback",
            "version": 1,
            "questions": [...]
        }
    ]
}
```

#### Submit Survey Response
```
POST /api/surveys/submit
Authorization: Bearer <token>
Content-Type: application/json

{
    "survey_id": 1,
    "responses": {
        "q1_overall_performance": 4,
        "q2_technical_skills": 4,
        "q3_strengths": "Great problem solver",
        "q4_improvements": "Improve presentation skills"
    }
}

Response (200):
{
    "message": "Survey submitted successfully",
    "submission_id": "survey_123"
}
```

---

### Analytics

#### Get User Analytics
```
GET /api/analytics/user/{user_id}
Authorization: Bearer <token>

Response (200):
{
    "user_id": 1,
    "total_modules": 5,
    "completed_modules": 3,
    "avg_completion_pct": 65,
    "current_streak": 5,
    "total_points": 450,
    "badges": ["Learner", "Completed Module", "Week Warrior"],
    "sector_fit": {
        "sector": "Design & UI/UX",
        "fit_score": 75,
        "status": "Green"
    }
}
```

#### Get Dashboard Summary
```
GET /api/analytics/dashboard
Authorization: Bearer <admin_token>

Response (200):
{
    "total_users": 50,
    "active_users_today": 28,
    "modules_assigned": 100,
    "modules_completed": 60,
    "avg_completion_rate": 65,
    "at_risk_users": 5,
    "top_modules": [...]
}
```

---

## Databricks Integration

### SQL Queries

#### Get Sector Fit Analysis

```sql
SELECT 
    user_id,
    sector_interests,
    interest_confidence,
    skill_readiness_score,
    sector_fit_score,
    readiness_status
FROM gold.student_sector_fit
WHERE sector_fit_score >= 70
ORDER BY sector_fit_score DESC;
```

#### Get Dropout Risk Analysis

```sql
SELECT 
    user_id,
    student_id,
    modules_assigned,
    modules_completed,
    avg_completion_pct,
    dropout_risk_level,
    risk_score,
    risk_reason
FROM gold.student_dropout_risk
WHERE dropout_risk_level IN ('HIGH', 'MEDIUM')
ORDER BY risk_score DESC;
```

#### Get Module Performance

```sql
SELECT 
    module_id,
    COUNT(DISTINCT user_id) as learners,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / 
          COUNT(DISTINCT user_id), 1) as completion_rate,
    AVG(progress) as avg_progress,
    MIN(avg_completion_pct) as min_progress,
    MAX(avg_completion_pct) as max_progress
FROM gold.module_performance
GROUP BY module_id
ORDER BY completion_rate DESC;
```

### Python SDK

```python
from app.integrations.databricks_connector import DatabricksConnector

# Initialize connection
db_connector = DatabricksConnector()

# Query sector fit
sector_data = db_connector.query("""
    SELECT * FROM gold.student_sector_fit 
    WHERE user_id = ?
""", (user_id,))

# Query dropout risk
risk_data = db_connector.query("""
    SELECT * FROM gold.student_dropout_risk
    WHERE dropout_risk_level = 'HIGH'
""")

# Get module effectiveness
effectiveness = db_connector.query("""
    SELECT * FROM gold.module_effectiveness
    ORDER BY completion_rate DESC LIMIT 10
""")
```

---

## Azure Blob Storage Integration

### Upload File
```python
from app.data.blob_storage import BlobStorageManager

storage_manager = BlobStorageManager()

# Upload document
blob_url = storage_manager.upload_file(
    file_path='path/to/document.pdf',
    container='documents',
    blob_name='student_certificates/student_1.pdf'
)
```

### Download File
```python
# Download file
content = storage_manager.download_file(
    container='documents',
    blob_name='student_certificates/student_1.pdf'
)
```

### List Files
```python
# List all files in container
files = storage_manager.list_files(container='documents')

for file in files:
    print(f"File: {file.name}, Size: {file.size} bytes")
```

---

## Error Handling

### Standard Error Response Format

```json
{
    "error": "error_code",
    "message": "Human-readable error message",
    "timestamp": "2026-01-29T10:00:00Z",
    "request_id": "req_12345"
}
```

### Common Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| INVALID_CREDENTIALS | 401 | Login failed |
| UNAUTHORIZED | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource doesn't exist |
| CONFLICT | 409 | Resource already exists |
| VALIDATION_ERROR | 422 | Invalid input data |
| INTERNAL_ERROR | 500 | Server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily down |

---

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1643452800
```

### Limits by Endpoint Type

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Read (GET) | 1000 | 1 hour |
| Write (POST/PUT) | 100 | 1 hour |
| Admin (DELETE) | 50 | 1 hour |
| Survey | 10 | 1 day |

---

## Webhook Events

### Event Types

#### user.registered
```json
{
    "event": "user.registered",
    "timestamp": "2026-01-29T10:00:00Z",
    "data": {
        "user_id": 1,
        "email": "student@magicbus.com",
        "student_id": "MB-APAC-2026-ABC01"
    }
}
```

#### module.completed
```json
{
    "event": "module.completed",
    "timestamp": "2026-01-29T10:00:00Z",
    "data": {
        "user_id": 1,
        "module_id": "py101",
        "points_earned": 100
    }
}
```

#### survey.submitted
```json
{
    "event": "survey.submitted",
    "timestamp": "2026-01-29T10:00:00Z",
    "data": {
        "survey_id": 1,
        "survey_type": "youth_feedback",
        "user_id": 1
    }
}
```

---

## Authentication & Security

### Bearer Token Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...
```

### Token Expiration

- Default: 24 hours
- Refresh token: 30 days
- Admin token: 8 hours

### OAuth 2.0 Support (Planned)

```python
# Future OAuth2 integration
oauth_config = {
    'client_id': 'xxx',
    'client_secret': 'xxx',
    'scope': 'user profile surveys'
}
```

---

## Code Examples

### Python Example
```python
import requests
import json

BASE_URL = "http://localhost:8501/api"
TOKEN = "your_bearer_token"

# Headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get user profile
response = requests.get(
    f"{BASE_URL}/users/1",
    headers=headers
)

user_data = response.json()
print(f"User: {user_data['full_name']}")

# Update progress
progress_update = {
    "progress": 75,
    "status": "in_progress"
}

response = requests.put(
    f"{BASE_URL}/modules/progress/1",
    headers=headers,
    json=progress_update
)

print(response.json())
```

### JavaScript/TypeScript Example
```typescript
const BASE_URL = "http://localhost:8501/api";
const token = "your_bearer_token";

const headers = {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
};

// Get user analytics
async function getUserAnalytics(userId: number) {
    const response = await fetch(
        `${BASE_URL}/analytics/user/${userId}`,
        { headers }
    );
    
    const data = await response.json();
    return data;
}

// Submit survey
async function submitSurvey(surveyId: number, responses: object) {
    const response = await fetch(
        `${BASE_URL}/surveys/submit`,
        {
            method: "POST",
            headers,
            body: JSON.stringify({
                survey_id: surveyId,
                responses
            })
        }
    );
    
    return await response.json();
}
```

---

**Last Updated**: January 29, 2026
**API Version**: 1.0.0
