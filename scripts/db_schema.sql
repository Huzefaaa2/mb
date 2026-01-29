-- Magic Bus Compass 360 Database Schema

-- Users table (login credentials)
CREATE TABLE IF NOT EXISTS mb_users (
    user_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    login_id VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'student',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mb_users_student_id ON mb_users(student_id);
CREATE INDEX IF NOT EXISTS idx_mb_users_email ON mb_users(email);
CREATE INDEX IF NOT EXISTS idx_mb_users_role ON mb_users(role);

-- Onboarding profiles (resume, uploads, preferences)
CREATE TABLE IF NOT EXISTS mb_onboarding_profiles (
    profile_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    mb_unique_id VARCHAR(50) UNIQUE NOT NULL,
    resume_text TEXT,
    resume_file_path VARCHAR(500),
    marksheet_file_path VARCHAR(500),
    id_proof_file_path VARCHAR(500),
    extracted_skills TEXT,
    extracted_education TEXT,
    device_access VARCHAR(100),
    preferred_language VARCHAR(20),
    location VARCHAR(255),
    consent_given BOOLEAN DEFAULT false,
    communication_preference VARCHAR(50),
    qr_code_path VARCHAR(500),
    id_card_pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_onboarding_mb_unique_id ON mb_onboarding_profiles(mb_unique_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_created ON mb_onboarding_profiles(created_at);

-- Student-Dataset mapping
CREATE TABLE IF NOT EXISTS mb_student_map (
    map_id SERIAL PRIMARY KEY,
    mb_user_id VARCHAR(50) UNIQUE NOT NULL,
    dataset_student_id VARCHAR(50),
    match_confidence FLOAT DEFAULT 0.0,
    match_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_map_mb_user ON mb_student_map(mb_user_id);

-- Sector surveys (Day 0-2 career fit)
CREATE TABLE IF NOT EXISTS mb_sector_surveys (
    survey_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    survey_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interests TEXT,
    voice_note_path VARCHAR(500),
    voice_transcription TEXT,
    soft_skill_score FLOAT,
    top_3_sectors TEXT,
    selected_pathway_id INTEGER,
    confirmation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sector_surveys_student ON mb_sector_surveys(student_id);
CREATE INDEX IF NOT EXISTS idx_sector_surveys_date ON mb_sector_surveys(survey_date);
CREATE INDEX IF NOT EXISTS idx_sector_surveys_pathway ON mb_sector_surveys(selected_pathway_id);

-- Teacher assignments
CREATE TABLE IF NOT EXISTS mb_teacher_assignments (
    assignment_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    assignment_reason VARCHAR(100),
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_teacher_assignments_student ON mb_teacher_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_assignments_teacher ON mb_teacher_assignments(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_assignments_status ON mb_teacher_assignments(status);

-- Counselling sessions (post-placement feedback)
CREATE TABLE IF NOT EXISTS mb_counselling_sessions (
    session_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_type VARCHAR(50),
    stress_level INTEGER,
    workload_level INTEGER,
    manager_relationship_score INTEGER,
    challenges TEXT,
    issue_classification VARCHAR(100),
    ai_recommendation TEXT,
    escalated_to_counsellor BOOLEAN DEFAULT false,
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_counselling_student ON mb_counselling_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_counselling_date ON mb_counselling_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_counselling_issues ON mb_counselling_sessions(issue_classification);

-- Recommendations log (AI-generated recommendations)
CREATE TABLE IF NOT EXISTS mb_recommendations_log (
    rec_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    recommendation_type VARCHAR(100),
    content TEXT,
    ai_model_used VARCHAR(50),
    confidence_score FLOAT,
    user_feedback VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recommendations_student ON mb_recommendations_log(student_id);

-- Dropout risk scores
CREATE TABLE IF NOT EXISTS mb_dropout_risk (
    risk_id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    risk_score FLOAT,
    risk_level VARCHAR(20),
    risk_factors TEXT,
    last_computed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dropout_risk_student ON mb_dropout_risk(student_id);
CREATE INDEX IF NOT EXISTS idx_dropout_risk_score ON mb_dropout_risk(risk_score);
CREATE INDEX IF NOT EXISTS idx_dropout_risk_level ON mb_dropout_risk(risk_level);

-- Batch formations
CREATE TABLE IF NOT EXISTS mb_batch_formations (
    batch_id SERIAL PRIMARY KEY,
    batch_code VARCHAR(50) UNIQUE NOT NULL,
    sector_id INTEGER,
    region VARCHAR(100),
    teacher_id VARCHAR(50),
    max_students INTEGER,
    current_students INTEGER DEFAULT 0,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_batch_sector ON mb_batch_formations(sector_id);

-- Multi-Modal Screening Results (Voice/Video interviews for soft skills assessment)
CREATE TABLE IF NOT EXISTS mb_multimodal_screenings (
    screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) NOT NULL,
    submission_type VARCHAR(20) NOT NULL,
    media_path VARCHAR(500),
    transcription TEXT,
    communication_confidence REAL,
    cultural_fit_score REAL,
    problem_solving_score REAL,
    emotional_intelligence REAL,
    leadership_potential REAL,
    overall_soft_skill_score REAL,
    extraction_confidence REAL,
    top_role_match VARCHAR(100),
    role_match_confidence REAL,
    role_recommendations TEXT,
    personality_fit_level VARCHAR(20),
    marginalized_score REAL,
    neet_score REAL,
    screening_status VARCHAR(20) DEFAULT 'completed',
    reviewer_notes TEXT,
    manual_override_score REAL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extracted_at TIMESTAMP,
    scored_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_screening_student ON mb_multimodal_screenings(student_id);
CREATE INDEX IF NOT EXISTS idx_screening_submitted ON mb_multimodal_screenings(submitted_at);
CREATE INDEX IF NOT EXISTS idx_screening_status ON mb_multimodal_screenings(screening_status);
CREATE INDEX IF NOT EXISTS idx_screening_personality_fit ON mb_multimodal_screenings(personality_fit_level);
