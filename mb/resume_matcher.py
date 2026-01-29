"""
Resume Matcher - Match resume with job descriptions using Azure OpenAI
"""
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def match_resume_to_job(resume_text, job_description):
    """Analyze resume compatibility with job description using Azure OpenAI"""
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo")
        
        prompt = f"""Analyze the compatibility between the following resume and job description. 
        
Provide:
1. Compatibility Score (0-100)
2. Matching Skills
3. Missing Skills
4. Overall Assessment
5. Recommendations for improvement

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Format response clearly with sections."""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert HR consultant analyzing resume-job compatibility."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in resume matching: {e}")
        return f"Could not generate AI analysis: {str(e)}. Please ensure Azure OpenAI credentials are configured."


def get_quick_match_score(resume_text, job_description):
    """Get a quick match score without full analysis"""
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo")
        
        prompt = f"Given this resume and job description, provide ONLY a match percentage (0-100) and brief reason in 1 sentence.\n\nResume:\n{resume_text[:500]}\n\nJob:\n{job_description[:500]}"
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an HR analyst. Respond with ONLY: 'Match Score: X%' followed by brief reason."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return "Unable to calculate match score"
