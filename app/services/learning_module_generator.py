"""
Learning Module Generation Service
Uses Azure OpenAI to generate personalized learning modules based on career path
"""

import os
from dotenv import load_dotenv
import logging
import json
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

def generate_learning_modules_with_ai(career_interests, strengths, goals, learning_style):
    """
    Generate personalized learning modules using Azure OpenAI
    
    Args:
        career_interests: List of career interests
        strengths: List of student strengths
        goals: Career goals text
        learning_style: Preferred learning style
    
    Returns:
        List of learning module dictionaries
    """
    try:
        from openai import AzureOpenAI
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "gpt-35-turbo")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not all([api_key, endpoint, deployment]):
            logger.warning("Azure OpenAI credentials not configured. Using fallback modules.")
            return get_fallback_modules(career_interests, strengths)
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        prompt = f"""You are an educational career advisor for Magic Bus Compass 360.
        
Based on the student's profile below, generate 5 personalized learning modules that will help them achieve their career goals.

Student Profile:
- Career Interests: {', '.join(career_interests)}
- Strengths: {', '.join(strengths)}
- Career Goals: {goals}
- Learning Style: {learning_style}

For each module, provide:
1. Module Title (catchy, motivating)
2. Duration (in hours)
3. Description (1-2 sentences)
4. Key Skills Learned (3-4 bullet points)
5. Prerequisites (if any)
6. Difficulty Level (Beginner/Intermediate/Advanced)

Format the response as a JSON array with objects containing: title, duration, description, skills, prerequisites, difficulty_level

Generate modules that are:
- Aligned with their interests and career path
- Progressive in difficulty
- Practical and immediately applicable
- Matched to their learning style

Return ONLY valid JSON, no additional text."""
        
        message = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        response_text = message.content[0].text
        
        # Parse JSON response
        modules = json.loads(response_text)
        
        # Transform to our module format
        learning_modules = []
        for i, module in enumerate(modules, 1):
            learning_modules.append({
                "module_id": f"MOD_{i:03d}",
                "title": module.get("title", f"Module {i}"),
                "description": module.get("description", ""),
                "duration": module.get("duration", ""),
                "skills": module.get("skills", []),
                "prerequisites": module.get("prerequisites", ""),
                "difficulty_level": module.get("difficulty_level", "Beginner"),
                "status": "not_started",
                "progress": 0,
                "started_date": None,
                "completed_date": None,
                "created_at": datetime.now().isoformat()
            })
        
        return learning_modules
    
    except Exception as e:
        logger.error(f"Error generating modules with Azure OpenAI: {e}")
        return get_fallback_modules(career_interests, strengths)

def get_fallback_modules(career_interests, strengths):
    """
    Fallback modules when Azure OpenAI is not available
    """
    fallback_modules = [
        {
            "module_id": "MOD_001",
            "title": "Career Foundations",
            "description": "Build a strong foundation in your chosen career path with industry fundamentals.",
            "duration": "8 hours",
            "skills": ["Industry Overview", "Career Planning", "Professional Development", "Networking Basics"],
            "prerequisites": "None",
            "difficulty_level": "Beginner",
            "status": "not_started",
            "progress": 0,
            "started_date": None,
            "completed_date": None,
            "created_at": datetime.now().isoformat()
        },
        {
            "module_id": "MOD_002",
            "title": "Core Technical Skills",
            "description": "Master the essential technical skills required in your field.",
            "duration": "16 hours",
            "skills": ["Technical Fundamentals", "Problem Solving", "Tools & Software", "Best Practices"],
            "prerequisites": "Module 1",
            "difficulty_level": "Intermediate",
            "status": "not_started",
            "progress": 0,
            "started_date": None,
            "completed_date": None,
            "created_at": datetime.now().isoformat()
        },
        {
            "module_id": "MOD_003",
            "title": "Practical Projects",
            "description": "Apply your learning through real-world project scenarios.",
            "duration": "12 hours",
            "skills": ["Project Management", "Collaboration", "Implementation", "Portfolio Building"],
            "prerequisites": "Module 2",
            "difficulty_level": "Intermediate",
            "status": "not_started",
            "progress": 0,
            "started_date": None,
            "completed_date": None,
            "created_at": datetime.now().isoformat()
        },
        {
            "module_id": "MOD_004",
            "title": "Advanced Specialization",
            "description": "Dive deep into specialized areas of your career path.",
            "duration": "20 hours",
            "skills": ["Specialization", "Advanced Techniques", "Industry Trends", "Innovation"],
            "prerequisites": "Module 3",
            "difficulty_level": "Advanced",
            "status": "not_started",
            "progress": 0,
            "started_date": None,
            "completed_date": None,
            "created_at": datetime.now().isoformat()
        },
        {
            "module_id": "MOD_005",
            "title": "Placement Preparation",
            "description": "Get interview-ready with mock interviews and resume building.",
            "duration": "6 hours",
            "skills": ["Interview Skills", "Resume Writing", "Communication", "Job Search Strategies"],
            "prerequisites": "Module 4",
            "difficulty_level": "Beginner",
            "status": "not_started",
            "progress": 0,
            "started_date": None,
            "completed_date": None,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return fallback_modules
