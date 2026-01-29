"""
Email Service Module
Handles sending feedback surveys to employers and youths
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import logging
from typing import Tuple, List
from datetime import datetime
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mb_compass.db"

# Email configuration - using environment variables for security
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
MAGICBUS_NAME = "MagicBus Compass 360"
MAGICBUS_CONTACT = os.getenv("MAGICBUS_CONTACT_EMAIL", "support@magicbus.com")


def send_employer_survey_email(
    employer_email: str,
    employer_name: str,
    student_name: str,
    job_title: str,
    survey_id: int,
    survey_link: str = None
) -> Tuple[bool, str]:
    """Send feedback survey to employer"""
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.warning("⚠️ Email credentials not configured in .env")
        return False, "❌ Email service not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in .env"
    
    try:
        subject = f"MagicBus: Feedback Survey for {student_name}"
        
        # Generate survey link if not provided
        if not survey_link:
            survey_link = f"http://localhost:8501/feedback?type=employer&survey_id={survey_id}"
        
        body = f"""
Dear {employer_name},

Thank you for providing an opportunity to our student, {student_name}, in the role of {job_title}.

We would greatly appreciate your feedback about the student's performance during their placement. Your insights will help us improve our training programs and better prepare future students.

Please take 5-10 minutes to complete this brief feedback survey:
{survey_link}

Your honest feedback is invaluable for:
✓ Understanding student strengths and areas for development
✓ Improving our curriculum and training approach
✓ Building stronger partnerships with organizations like yours
✓ Supporting student growth and professional development

Survey Link: {survey_link}

If you have any questions or prefer to provide feedback via email, please reply to this message.

Thank you for your support!

Best regards,
{MAGICBUS_NAME} Team
{MAGICBUS_CONTACT}

---
This feedback is confidential and will be used solely for program improvement.
        """

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = employer_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        # Log the distribution
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO survey_distribution_logs (
                    survey_type, recipient_email, recipient_type,
                    survey_id, sent_date, survey_link
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', ('employer', employer_email, 'employer', survey_id, datetime.now(), survey_link))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not log distribution: {e}")

        logger.info(f"✅ Employer survey sent to {employer_email}")
        return True, f"✅ Survey sent to {employer_email}"
    
    except smtplib.SMTPAuthenticationError:
        error_msg = "❌ Email authentication failed. Check SENDER_EMAIL and SENDER_PASSWORD in .env"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"❌ SMTP Error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error sending email: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def send_youth_survey_email(
    youth_email: str,
    youth_name: str,
    placement_company: str,
    job_title: str,
    survey_id: int,
    survey_link: str = None
) -> Tuple[bool, str]:
    """Send post-placement feedback survey to youth"""
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.warning("⚠️ Email credentials not configured in .env")
        return False, "❌ Email service not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in .env"
    
    try:
        subject = "Your MagicBus Post-Placement Feedback Survey"
        
        # Generate survey link if not provided
        if not survey_link:
            survey_link = f"http://localhost:8501/feedback?type=youth&survey_id={survey_id}"
        
        body = f"""
Hi {youth_name},

Congratulations on your placement at {placement_company} as a {job_title}!

We hope your experience has been enriching. To help us continuously improve our program and better support future students, we'd like to hear about your journey.

Please take 10-15 minutes to share your feedback:
{survey_link}

Your feedback will help us:
✓ Understand what prepared you well for your role
✓ Identify areas where we need to improve our training
✓ Support your ongoing professional development
✓ Build better relationships with industry partners

Survey Link: {survey_link}

Your responses are completely confidential and will only be used for program improvement.

We're proud of your achievement and look forward to hearing about your experience!

Best regards,
{MAGICBUS_NAME} Team
{MAGICBUS_CONTACT}

---
If you have any questions, please reach out to us at {MAGICBUS_CONTACT}
        """

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = youth_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        # Log the distribution
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO survey_distribution_logs (
                    survey_type, recipient_email, recipient_type,
                    survey_id, sent_date, survey_link
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', ('youth', youth_email, 'youth', survey_id, datetime.now(), survey_link))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not log distribution: {e}")

        logger.info(f"✅ Youth survey sent to {youth_email}")
        return True, f"✅ Survey sent to {youth_name}"
    
    except smtplib.SMTPAuthenticationError:
        error_msg = "❌ Email authentication failed. Check SENDER_EMAIL and SENDER_PASSWORD in .env"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"❌ SMTP Error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error sending email: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def send_bulk_employer_surveys(
    survey_list: List[dict]
) -> Tuple[int, int, List[str]]:
    """
    Send bulk employer surveys
    
    survey_list format:
    [
        {
            'employer_email': 'email@company.com',
            'employer_name': 'John Doe',
            'student_name': 'Student Name',
            'job_title': 'Job Title',
            'survey_id': 1
        },
        ...
    ]
    """
    successful = 0
    failed = 0
    errors = []
    
    for survey in survey_list:
        try:
            success, message = send_employer_survey_email(
                employer_email=survey['employer_email'],
                employer_name=survey['employer_name'],
                student_name=survey['student_name'],
                job_title=survey['job_title'],
                survey_id=survey['survey_id']
            )
            if success:
                successful += 1
            else:
                failed += 1
                errors.append(f"{survey['employer_email']}: {message}")
        except Exception as e:
            failed += 1
            errors.append(f"{survey['employer_email']}: {str(e)}")
    
    logger.info(f"📊 Bulk send: {successful} successful, {failed} failed")
    return successful, failed, errors


def send_bulk_youth_surveys(
    survey_list: List[dict]
) -> Tuple[int, int, List[str]]:
    """
    Send bulk youth surveys
    
    survey_list format:
    [
        {
            'youth_email': 'student@email.com',
            'youth_name': 'Student Name',
            'placement_company': 'Company Name',
            'job_title': 'Job Title',
            'survey_id': 1
        },
        ...
    ]
    """
    successful = 0
    failed = 0
    errors = []
    
    for survey in survey_list:
        try:
            success, message = send_youth_survey_email(
                youth_email=survey['youth_email'],
                youth_name=survey['youth_name'],
                placement_company=survey['placement_company'],
                job_title=survey['job_title'],
                survey_id=survey['survey_id']
            )
            if success:
                successful += 1
            else:
                failed += 1
                errors.append(f"{survey['youth_email']}: {message}")
        except Exception as e:
            failed += 1
            errors.append(f"{survey['youth_email']}: {str(e)}")
    
    logger.info(f"📊 Bulk send: {successful} successful, {failed} failed")
    return successful, failed, errors


def verify_email_configuration() -> Tuple[bool, str]:
    """Verify email service configuration"""
    if not SENDER_EMAIL:
        return False, "❌ SENDER_EMAIL not configured in .env"
    if not SENDER_PASSWORD:
        return False, "❌ SENDER_PASSWORD not configured in .env"
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.quit()
        return True, "✅ Email service configured and working"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Email authentication failed"
    except smtplib.SMTPException as e:
        return False, f"❌ SMTP Error: {str(e)}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
