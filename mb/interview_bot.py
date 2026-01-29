"""
Interview Bot - Generate interview questions using Azure OpenAI
"""
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def simulate_interview(job_title, experience_level="intermediate"):
    """Generate interview questions for a given job title"""
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo")
        
        prompt = f"""Generate 5 interview questions for a {experience_level} candidate applying for a {job_title} position.

Include:
1. 2 Technical questions
2. 2 Behavioral/Situational questions  
3. 1 Question about project experience

Format each as:
Question X: [question]
Expected answer areas: [brief hints]"""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an experienced technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating interview questions: {e}")
        return f"Could not generate interview questions: {str(e)}"


def get_answer_tips(question, job_title):
    """Get tips for answering a specific interview question"""
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo")
        
        prompt = f"""For a {job_title} interview, provide tips on answering this question:

Question: {question}

Include:
1. What the interviewer is looking for
2. Key points to mention
3. Example structure for answer
4. What to avoid"""
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an interview coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error getting answer tips: {e}")
        return "Could not generate tips."
