"""
Magic Bus Compass 360 - Student Registration Page
Handles smart registration with resume parsing and ID card generation
"""

import streamlit as st
import pandas as pd
import re
import json
import uuid
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Student Registration | Magic Bus Compass 360",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Smart Student Registration")
st.markdown("Complete registration in 5 minutes. Resume parsing auto-fills your details.")

# ============================================
# HELPER FUNCTIONS
# ============================================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number"""
    pattern = r'^[\d\s\-\+\(\)]{10,}$'
    return re.match(pattern, phone) is not None

def extract_name_from_text(text):
    """Extract likely name from text"""
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) >= 2:
            words = line.split()[:2]
            if all(word.isalpha() for word in words):
                return words[0], words[1] if len(words) > 1 else ""
    return "", ""

def extract_email_from_text(text):
    """Extract email from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else ""

def extract_phone_from_text(text):
    """Extract phone from text"""
    pattern = r'(?:\+91|0)?[\s\-]?[6-9]\d{9}|(?:\+\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
    matches = re.findall(pattern, text)
    if matches:
        if isinstance(matches[0], tuple):
            return f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
        return matches[0]
    return ""

def extract_skills_from_text(text):
    """Extract technical skills from text"""
    all_skills = [
        "Python", "Java", "JavaScript", "C++", "C#", "SQL", "R",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Machine Learning", "Data Analysis", "Data Science",
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Communication", "Leadership", "Teamwork", "Problem Solving"
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in all_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_education_from_text(text):
    """Extract education information from text"""
    education = []
    
    degree_patterns = {
        "Bachelor": r"(?:B\.?A|B\.?S|BA|BS)(?:\s+in\s+([^,\n]+))?",
        "Master": r"(?:M\.?A|M\.?S|MA|MS)(?:\s+in\s+([^,\n]+))?",
        "PhD": r"(?:Ph\.?D|PhD)(?:\s+in\s+([^,\n]+))?"
    }
    
    for degree_type, pattern in degree_patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            field = match.group(1) if match.group(1) else "Not specified"
            education.append({
                "degree": degree_type,
                "field": field.strip()
            })
    
    return education

def parse_resume(uploaded_file):
    """Parse resume and extract information"""
    try:
        if uploaded_file is None:
            return None
        
        file_type = uploaded_file.name.split('.')[-1].lower()
        text = ""
        
        if file_type == "pdf":
            try:
                import pdfplumber
                with pdfplumber.open(BytesIO(uploaded_file.getvalue())) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            except Exception as e:
                logger.error(f"PDF parsing error: {e}")
                return None
        
        elif file_type in ["docx", "doc"]:
            try:
                from docx import Document
                doc = Document(BytesIO(uploaded_file.getvalue()))
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except Exception as e:
                logger.error(f"DOCX parsing error: {e}")
                return None
        else:
            return None
        
        if not text:
            return None
        
        first_name, last_name = extract_name_from_text(text)
        email = extract_email_from_text(text)
        phone = extract_phone_from_text(text)
        skills = extract_skills_from_text(text)
        education = extract_education_from_text(text)
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "raw_text": text
        }
    
    except Exception as e:
        logger.error(f"Resume parsing error: {e}")
        return None

def generate_student_id():
    """Generate unique student ID"""
    timestamp = datetime.now().strftime("%Y")
    unique_num = str(uuid.uuid4().hex[:6]).upper()
    return f"MB-APAC-{timestamp}-{unique_num}"

def generate_login_credentials(student_id):
    """Generate login ID and password"""
    login_id = f"mb_{student_id.split('-')[-1].lower()}"
    password_hint = "DOB(DDMMYYYY) + last4 of login ID"
    return login_id, password_hint

def generate_id_card(student_data, student_id):
    """Generate PNG ID card with QR code"""
    try:
        card = Image.new('RGB', (1000, 600), color='white')
        draw = ImageDraw.Draw(card)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 28)
            name_font = ImageFont.truetype("arial.ttf", 24)
            label_font = ImageFont.truetype("arial.ttf", 14)
        except:
            title_font = name_font = label_font = ImageFont.load_default()
        
        margin = 40
        y_position = 50
        
        draw.text((margin, y_position), "Magic Bus Compass 360", font=title_font, fill='#003366')
        draw.text((margin, y_position + 35), "Student ID Card", font=label_font, fill='#666666')
        y_position += 80
        
        full_name = f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}"
        draw.text((margin, y_position), full_name, font=name_font, fill='black')
        y_position += 50
        
        info_fields = [
            ("ID:", student_id),
            ("Email:", student_data.get('email', 'N/A')),
            ("Phone:", student_data.get('phone', 'N/A')),
            ("Institution:", student_data.get('institution', 'N/A')),
            ("Education:", student_data.get('education_level', 'N/A'))
        ]
        
        for label, value in info_fields:
            draw.text((margin, y_position), label, font=label_font, fill='#666666')
            draw.text((margin + 100, y_position), str(value)[:30], font=label_font, fill='black')
            y_position += 30
        
        qr_data = {
            "student_id": student_id,
            "name": full_name,
            "email": student_data.get('email'),
            "institution": student_data.get('institution')
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((200, 200))
        
        qr_position = (700, 150)
        card.paste(qr_img, qr_position)
        
        border_color = '#003366'
        draw.rectangle([(0, 0), (999, 599)], outline=border_color, width=3)
        
        footer_text = f"Issued: {datetime.now().strftime('%Y-%m-%d')}"
        draw.text((margin, 550), footer_text, font=label_font, fill='#999999')
        
        img_bytes = BytesIO()
        card.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    except Exception as e:
        logger.error(f"ID card generation error: {e}")
        return None

def connect_database():
    """Connect to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            database=os.getenv("POSTGRES_DB", "mb_compass"),
            user=os.getenv("POSTGRES_USER", "mb_user"),
            password=os.getenv("POSTGRES_PASSWORD", "")
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def check_existing_student(email, conn):
    """Check if student already exists"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mb_users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Exception as e:
        logger.error(f"Database query error: {e}")
        return False

def insert_student_registration(student_data, student_id, login_id, conn):
    """Insert student registration into database"""
    try:
        cursor = conn.cursor()
        
        insert_user = sql.SQL("""
            INSERT INTO mb_users 
            (student_id, email, phone, login_id, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """)
        
        cursor.execute(insert_user, (
            student_id,
            student_data.get('email'),
            student_data.get('phone'),
            login_id,
            "temp_hash",
            'student',
            True
        ))
        
        user_id = cursor.fetchone()[0]
        
        insert_profile = sql.SQL("""
            INSERT INTO mb_onboarding_profiles
            (student_id, mb_unique_id, device_access, preferred_language, 
             consent_given, communication_preference)
            VALUES (%s, %s, %s, %s, %s, %s)
        """)
        
        cursor.execute(insert_profile, (
            student_id,
            student_id,
            student_data.get('device_access', 'mobile'),
            student_data.get('preferred_language', 'English'),
            True,
            student_data.get('communication_preference', 'whatsapp')
        ))
        
        conn.commit()
        cursor.close()
        
        return user_id
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Database insert error: {e}")
        raise

# ============================================
# PAGE LAYOUT
# ============================================

tab1, tab2, tab3 = st.tabs(["📄 Upload Resume", "📝 Complete Form", "✅ Confirmation"])

# ============================================
# TAB 1: RESUME UPLOAD
# ============================================

with tab1:
    st.subheader("Step 1: Upload Your Resume")
    st.write("Upload a PDF or Word document to auto-fill your details.")
    
    uploaded_file = st.file_uploader(
        "Choose resume file",
        type=["pdf", "docx", "doc"],
        help="Maximum 5MB"
    )
    
    parsed_resume = None
    
    if uploaded_file is not None:
        st.info(f"📄 File uploaded: {uploaded_file.name}")
        
        with st.spinner("🔍 Parsing resume..."):
            parsed_resume = parse_resume(uploaded_file)
        
        if parsed_resume:
            st.success("✓ Resume parsed successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if parsed_resume.get('first_name'):
                    st.write(f"**Name:** {parsed_resume['first_name']} {parsed_resume['last_name']}")
                if parsed_resume.get('email'):
                    st.write(f"**Email:** {parsed_resume['email']}")
            
            with col2:
                if parsed_resume.get('phone'):
                    st.write(f"**Phone:** {parsed_resume['phone']}")
                if parsed_resume.get('education'):
                    st.write(f"**Education:** {', '.join([e['degree'] for e in parsed_resume['education']])}")
            
            if parsed_resume.get('skills'):
                st.write(f"**Skills Found:** {', '.join(parsed_resume['skills'][:5])}")
        else:
            st.warning("⚠️ Could not parse resume. Please fill in details manually.")

# ============================================
# TAB 2: COMPLETE FORM
# ============================================

with tab2:
    st.subheader("Step 2: Complete Your Registration")
    
    with st.form("registration_form"):
        st.markdown("### 👤 Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input(
                "First Name *",
                value=parsed_resume.get('first_name', '') if parsed_resume else "",
                placeholder="John"
            )
            email = st.text_input(
                "Email Address *",
                value=parsed_resume.get('email', '') if parsed_resume else "",
                placeholder="john@example.com"
            )
            phone = st.text_input(
                "Phone Number *",
                value=parsed_resume.get('phone', '') if parsed_resume else "",
                placeholder="+91 98765 43210"
            )
            dob = st.date_input(
                "Date of Birth *",
                min_value=datetime.now().date() - timedelta(days=365*60),
                max_value=datetime.now().date() - timedelta(days=365*16)
            )
        
        with col2:
            last_name = st.text_input(
                "Last Name *",
                value=parsed_resume.get('last_name', '') if parsed_resume else "",
                placeholder="Doe"
            )
            phone_2 = st.text_input(
                "Alternate Phone (Optional)",
                placeholder="+91 98765 43211"
            )
            device_access = st.selectbox(
                "Primary Device Access *",
                ["Mobile Phone", "Tablet", "Desktop Computer", "Other"],
                index=0
            )
            preferred_language = st.selectbox(
                "Preferred Language *",
                ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Other"],
                index=0
            )
        
        st.markdown("### 🎓 Education")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            education_level = st.selectbox(
                "Highest Education Level *",
                ["High School", "Diploma", "Bachelor", "Master", "PhD"],
                index=0
            )
        
        with col2:
            institution = st.text_input(
                "Current/Last Institution *",
                placeholder="University Name"
            )
        
        with col3:
            gpa = st.number_input(
                "GPA (Optional)",
                min_value=0.0,
                max_value=4.0,
                step=0.01,
                value=0.0
            )
        
        st.markdown("### 💼 Skills")
        
        default_skills = parsed_resume.get('skills', []) if parsed_resume else []
        
        skills = st.multiselect(
            "Select Your Skills *",
            [
                "Python", "Java", "JavaScript", "SQL", "R",
                "React", "Angular", "Node.js", "Django", "Flask",
                "AWS", "Azure", "Docker", "Kubernetes",
                "Data Analysis", "Machine Learning",
                "Communication", "Leadership", "Teamwork"
            ],
            default=default_skills[:5]
        )
        
        st.markdown("### 📱 Communication Preferences")
        
        communication_preference = st.selectbox(
            "Preferred Communication Channel *",
            ["WhatsApp", "SMS", "Email", "Phone Call"],
            index=0
        )
        
        st.markdown("---")
        
        agree = st.checkbox(
            "I agree to the Terms and Conditions and Privacy Policy *",
            value=False
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("📝 Register", use_container_width=True)
        with col2:
            reset = st.form_submit_button("🔄 Reset Form", use_container_width=True)
        
        if submitted:
            errors = []
            
            if not first_name.strip():
                errors.append("First name is required")
            if not last_name.strip():
                errors.append("Last name is required")
            if not email.strip():
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Invalid email format")
            if not phone.strip():
                errors.append("Phone is required")
            elif not validate_phone(phone):
                errors.append("Invalid phone format")
            if not skills:
                errors.append("Please select at least one skill")
            if not agree:
                errors.append("You must agree to the Terms and Conditions")
            
            today = datetime.now().date()
            age = (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))
            if age < 16:
                errors.append("You must be at least 16 years old")
            
            if errors:
                st.error("❌ Please fix the following errors:")
                for error in errors:
                    st.write(f"• {error}")
            else:
                try:
                    student_id = generate_student_id()
                    login_id, password_hint = generate_login_credentials(student_id)
                    
                    student_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "phone_2": phone_2 if phone_2 else None,
                        "dob": dob,
                        "education_level": education_level,
                        "institution": institution,
                        "gpa": gpa if gpa > 0 else None,
                        "skills": skills,
                        "device_access": device_access.lower().replace(" ", "_"),
                        "preferred_language": preferred_language,
                        "communication_preference": communication_preference.lower()
                    }
                    
                    conn = connect_database()
                    
                    if not conn:
                        st.error("❌ Database connection failed. Please try again later.")
                    else:
                        if check_existing_student(email, conn):
                            st.error(f"❌ Student with email {email} already registered!")
                            conn.close()
                        else:
                            user_id = insert_student_registration(student_data, student_id, login_id, conn)
                            conn.close()
                            
                            st.session_state.registration_data = {
                                "student_id": student_id,
                                "login_id": login_id,
                                "password_hint": password_hint,
                                "student_data": student_data,
                                "user_id": user_id
                            }
                            
                            st.success("✅ Registration successful! Generating your ID card...")
                            st.balloons()
                            st.switch_page("pages/2_confirmation.py")
                
                except Exception as e:
                    st.error(f"❌ Registration failed: {str(e)}")
                    logger.error(f"Registration error: {e}")

# ============================================
# TAB 3: CONFIRMATION (PLACEHOLDER)
# ============================================

with tab3:
    st.subheader("Step 3: Registration Confirmation")
    st.info("👆 Please complete the registration form above first.")
