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
from typing import Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

# Import blob storage manager for optional resume archival
try:
    from app.data.blob_storage import get_blob_storage_manager
    BLOB_STORAGE_AVAILABLE = True
except ImportError:
    BLOB_STORAGE_AVAILABLE = False
    logger.warning("Blob storage module not available. Resume archival will be skipped.")

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

def generate_id_card(student_data, student_id, passport_photo=None):
    """Generate PNG ID card with QR code and optional passport photo"""
    try:
        card = Image.new('RGB', (1200, 650), color='white')
        draw = ImageDraw.Draw(card)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            name_font = ImageFont.truetype("arial.ttf", 26)
            label_font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = name_font = label_font = small_font = ImageFont.load_default()
        
        # Draw header background
        header_color = '#003366'
        draw.rectangle([(0, 0), (1200, 80)], fill=header_color)
        
        # Draw header text
        draw.text((40, 15), "Magic Bus Compass 360", font=title_font, fill='white')
        draw.text((40, 50), "Student ID Card", font=small_font, fill='white')
        
        # Draw passport photo if provided
        if passport_photo:
            try:
                photo = Image.open(BytesIO(passport_photo))
                # Resize to passport size (4x5 ratio, about 150x190)
                photo.thumbnail((150, 190), Image.Resampling.LANCZOS)
                photo_x, photo_y = 40, 110
                card.paste(photo, (photo_x, photo_y))
                # Draw border around photo
                draw.rectangle([(photo_x-2, photo_y-2), (photo_x+photo.width+2, photo_y+photo.height+2)], 
                              outline='#003366', width=2)
            except Exception as e:
                logger.warning(f"Could not insert passport photo: {e}")
        
        # Student info starts at different position depending on photo
        info_start_x = 220 if passport_photo else 40
        y_position = 110
        
        # Name
        full_name = f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}"
        draw.text((info_start_x, y_position), full_name, font=name_font, fill='black')
        y_position += 45
        
        # Info fields
        info_fields = [
            ("ID:", student_id),
            ("DOB:", str(student_data.get('dob', 'N/A'))),
            ("Email:", student_data.get('email', 'N/A')),
            ("Phone:", student_data.get('phone', 'N/A')),
            ("Institution:", student_data.get('institution', 'N/A')),
            ("Education:", student_data.get('education_level', 'N/A'))
        ]
        
        for label, value in info_fields:
            draw.text((info_start_x, y_position), label, font=label_font, fill='#666666')
            value_str = str(value)[:35]
            draw.text((info_start_x + 120, y_position), value_str, font=label_font, fill='black')
            y_position += 25
        
        # QR code
        qr_data = {
            "student_id": student_id,
            "name": full_name,
            "email": student_data.get('email'),
            "institution": student_data.get('institution'),
            "dob": str(student_data.get('dob'))
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((180, 180))
        
        qr_position = (950, 110)
        card.paste(qr_img, qr_position)
        
        # Draw border
        border_color = '#003366'
        draw.rectangle([(0, 0), (1199, 649)], outline=border_color, width=4)
        
        # Footer
        footer_text = f"Issued: {datetime.now().strftime('%d-%b-%Y')}"
        draw.text((40, 600), footer_text, font=label_font, fill='#999999')
        draw.text((950, 600), "Valid for 2 years", font=label_font, fill='#999999')
        
        img_bytes = BytesIO()
        card.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    except Exception as e:
        logger.error(f"ID card generation error: {e}")
        return None

def generate_id_card_pdf(student_data, student_id, passport_photo=None):
    """Generate PDF version of ID card"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # Page background
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, letter[0], letter[1], fill=1)
        
        # Header
        c.setFillColorRGB(0, 51, 102)
        c.rect(0, letter[1]-0.8*inch, letter[0], 0.8*inch, fill=1)
        
        # Header text
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(0.4*inch, letter[1]-0.5*inch, "Magic Bus Compass 360 - Student ID Card")
        
        # Set black text
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 14)
        
        # Photo placeholder or actual photo
        if passport_photo:
            try:
                photo = Image.open(BytesIO(passport_photo))
                photo.thumbnail((1.2*inch, 1.5*inch), Image.Resampling.LANCZOS)
                temp_photo = BytesIO()
                photo.save(temp_photo, format='PNG')
                temp_photo.seek(0)
                c.drawImage(temp_photo, 0.4*inch, letter[1]-3.5*inch, width=1.2*inch, height=1.5*inch)
            except:
                pass
        
        # Student info
        y_pos = letter[1] - 1.5*inch
        c.setFont("Helvetica-Bold", 12)
        full_name = f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}"
        c.drawString(2*inch, y_pos, f"Name: {full_name}")
        
        y_pos -= 0.25*inch
        c.setFont("Helvetica", 11)
        
        info_fields = [
            ("Student ID:", student_id),
            ("Email:", student_data.get('email', 'N/A')),
            ("Phone:", student_data.get('phone', 'N/A')),
            ("DOB:", str(student_data.get('dob', 'N/A'))),
            ("Institution:", student_data.get('institution', 'N/A')),
            ("Education Level:", student_data.get('education_level', 'N/A')),
        ]
        
        for label, value in info_fields:
            c.drawString(2*inch, y_pos, f"{label} {value}")
            y_pos -= 0.25*inch
        
        # QR code
        qr_data = {
            "student_id": student_id,
            "name": full_name,
            "email": student_data.get('email'),
            "institution": student_data.get('institution')
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        c.drawImage(qr_buffer, 5*inch, letter[1]-3.5*inch, width=1.2*inch, height=1.2*inch)
        
        # Footer
        c.setFont("Helvetica", 10)
        c.drawString(0.4*inch, 0.4*inch, f"Issued: {datetime.now().strftime('%d-%b-%Y')} | Valid for 2 years")
        
        c.save()
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return None

def init_db():
    """Initialize SQLite database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mb_users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'student',
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            phone TEXT,
            dob TEXT,
            institution TEXT,
            education_level TEXT,
            skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def connect_database():
    """Connect to SQLite database"""
    try:
        init_db()
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def check_existing_student(email, conn):
    """Check if student already exists"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mb_users WHERE email = ?", (email,))
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
        
        # Insert user into mb_users table
        cursor.execute("""
            INSERT INTO mb_users 
            (student_id, email, phone, login_id, password, role, full_name, institution, education_level, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            student_data.get('email'),
            student_data.get('phone'),
            login_id,
            student_data.get('dob', ''),
            'student',
            f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}",
            student_data.get('institution', ''),
            student_data.get('education_level', ''),
            json.dumps(student_data.get('skills', []))
        ))
        
        conn.commit()
        cursor.close()
        
        return student_id
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Database insert error: {e}")
        raise

def archive_resume_to_blob(resume_file, student_id: str) -> Optional[str]:
    """
    Archive uploaded resume to writable blob storage.
    
    Args:
        resume_file: Streamlit UploadedFile object
        student_id: Student ID for blob path organization
    
    Returns:
        URL of archived blob, or None if storage not available
    
    Raises:
        RuntimeError: If writable storage is not configured and user tries to upload
    """
    if not resume_file or not BLOB_STORAGE_AVAILABLE:
        return None
    
    try:
        blob_manager = get_blob_storage_manager()
        
        # Check if writable storage is configured
        if not blob_manager.write_client:
            logger.warning(
                f"Writable storage not configured. Resume for {student_id} will not be archived."
            )
            return None
        
        # Create blob path: resumes/{year}/{student_id}/{filename}
        timestamp = datetime.now()
        blob_name = f"resumes/{timestamp.year}/{student_id}/{resume_file.name}"
        
        # Upload file to writable storage
        file_data = BytesIO(resume_file.getvalue())
        blob_url = blob_manager.upload_blob(
            blob_name=blob_name,
            data=file_data,
            overwrite=True
        )
        
        logger.info(f"Resume archived for student {student_id}: {blob_url}")
        return blob_url
    
    except RuntimeError as e:
        # Write operation failed due to missing credentials
        logger.error(f"Cannot archive resume: {e}")
        st.warning(
            f"⚠️ Resume archival unavailable. Please contact support if this persists."
        )
        return None
    except Exception as e:
        logger.error(f"Resume archival error: {e}")
        return None

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
        
        st.markdown("### 📸 Passport Photo")
        st.write("Upload a passport-size photo (4x5 ratio, min 200x250 pixels)")
        
        passport_photo = st.file_uploader(
            "Choose passport photo",
            type=["jpg", "jpeg", "png"],
            help="Maximum 2MB - Passport size photo",
            key="passport_photo"
        )
        
        if passport_photo:
            try:
                img = Image.open(BytesIO(passport_photo.getvalue()))
                st.image(img, width=150, caption="✓ Photo preview")
            except:
                st.warning("⚠️ Could not load image preview")
        
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
        
        skills_options = [
            "Python", "Java", "JavaScript", "SQL", "R",
            "React", "Angular", "Node.js", "Django", "Flask",
            "AWS", "Azure", "Docker", "Kubernetes",
            "Data Analysis", "Machine Learning",
            "Communication", "Leadership", "Teamwork"
        ]
        
        default_skills = parsed_resume.get('skills', []) if parsed_resume else []
        # Filter default skills to only include those in the options
        default_skills = [skill for skill in default_skills if skill in skills_options][:5]
        
        skills = st.multiselect(
            "Select Your Skills *",
            skills_options,
            default=default_skills
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
            submitted = st.form_submit_button("📝 Register", width="stretch")
        with col2:
            reset = st.form_submit_button("🔄 Reset Form", width="stretch")
        
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
                    
                    # Get passport photo bytes if uploaded
                    passport_photo_bytes = None
                    if passport_photo:
                        passport_photo_bytes = passport_photo.getvalue()
                    
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
                            
                            # Archive resume to blob storage (optional, with safety checks)
                            resume_url = None
                            if uploaded_file and BLOB_STORAGE_AVAILABLE:
                                resume_url = archive_resume_to_blob(uploaded_file, student_id)
                            
                            # Generate ID cards
                            id_card_png = generate_id_card(student_data, student_id, passport_photo_bytes)
                            id_card_pdf = generate_id_card_pdf(student_data, student_id, passport_photo_bytes)
                            
                            st.session_state.registration_data = {
                                "student_id": student_id,
                                "login_id": login_id,
                                "password_hint": password_hint,
                                "student_data": student_data,
                                "user_id": user_id,
                                "resume_url": resume_url,
                                "id_card_png": id_card_png,
                                "id_card_pdf": id_card_pdf
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
