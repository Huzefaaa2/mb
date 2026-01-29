"""
JobGPT - Job Scraper Module
Fetches job listings from Google Jobs via SerpAPI
"""
import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def fetch_jobs(query="AI Engineer", location="Remote", num_results=10):
    """Fetch jobs from Google Jobs via SerpAPI"""
    api_key = os.getenv("SERPAPI_KEY")
    
    if not api_key:
        logger.warning("SERPAPI_KEY not found in .env - using demo jobs")
        # Return demo jobs for testing without API key
        return get_demo_jobs(query, num_results)
    
    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_jobs",
            "q": f"{query} in {location}",
            "api_key": api_key,
            "num": num_results
        }
        
        logger.info(f"Fetching jobs for '{query}' in '{location}'")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json().get("jobs_results", [])
            logger.info(f"Found {len(jobs)} jobs")
            return jobs[:num_results]
        else:
            logger.error(f"SerpAPI Error: {response.status_code}")
            return get_demo_jobs(query, num_results)
            
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return get_demo_jobs(query, num_results)


def get_demo_jobs(query, num_results=10):
    """Return demo/sample jobs for testing"""
    demo_jobs = [
        {
            "title": "Senior AI Engineer",
            "company_name": "OpenAI",
            "location": "San Francisco, CA",
            "description": "Join our team to develop cutting-edge large language models. Experience with Python, PyTorch, and distributed systems required.",
            "url": "https://openai.com/careers",
            "via": "https://openai.com"
        },
        {
            "title": "Machine Learning Scientist",
            "company_name": "Google DeepMind",
            "location": "Remote",
            "description": "Research and develop reinforcement learning systems at scale. PhD in ML/AI preferred. Experience with TensorFlow essential.",
            "url": "https://deepmind.com/careers",
            "via": "https://deepmind.com"
        },
        {
            "title": "Data Scientist",
            "company_name": "Microsoft Azure",
            "location": "Seattle, WA",
            "description": "Build scalable ML solutions on Azure. Proficiency in Python, SQL, and cloud technologies required.",
            "url": "https://careers.microsoft.com",
            "via": "https://microsoft.com"
        },
        {
            "title": "Python Developer",
            "company_name": "Amazon Web Services",
            "location": "Remote",
            "description": "Develop backend services using Python. Experience with AWS and microservices architecture required.",
            "url": "https://amazon.jobs",
            "via": "https://amazon.com"
        },
        {
            "title": "Full Stack Engineer",
            "company_name": "Meta Platforms",
            "location": "Menlo Park, CA",
            "description": "Build scalable web applications. React, Python, and SQL expertise needed.",
            "url": "https://metacareers.com",
            "via": "https://meta.com"
        }
    ]
    
    return demo_jobs[:num_results]
