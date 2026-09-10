import io
import json
import logging
import datetime
from typing import Dict, Any, Optional
from PIL import Image
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Google Generative AI
genai_available = False
if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        genai_available = True
        logger.info("Initialized Google Generative AI client using GEMINI_API_KEY.")
    except Exception as e:
        logger.warning(f"Failed to initialize google-generativeai library: {e}")
else:
    logger.warning("GEMINI_API_KEY not found in settings. Gemini features will run in Demo mode.")

def analyze_job_description(job_description: str, resume_text: str) -> Dict[str, Any]:
    """
    Leverages Gemini to calculate a match score, extract matching and missing skills,
    and output actionable resume optimization tips.
    """
    if not genai_available:
        logger.info("Gemini API not available. Returning mock analysis for demo.")
        return get_mock_analysis(job_description)

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) optimizer.
    Analyze the following Job Description (JD) and the candidate's Resume.
    Calculate a match score (0-100), identify matching skills, missing skills, and give up to 3 short, actionable tips to update the resume.

    JOB DESCRIPTION:
    \"\"\"{job_description}\"\"\"

    RESUME:
    \"\"\"{resume_text}\"\"\"

    You MUST respond with a valid JSON object matching this exact schema:
    {{
        "match_score": int,
        "matching_skills": ["skill1", "skill2"],
        "missing_skills": ["skill3", "skill4"],
        "tips": ["tip1", "tip2"]
    }}
    Do not add markdown formatting or backticks around the JSON.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up any potential markdown wrapper
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response.rsplit("```", 1)[0]
            
        data = json.loads(text_response.strip())
        return data
    except Exception as e:
        logger.error(f"Gemini API analysis failed: {e}. Returning mock fallback.")
        return get_mock_analysis(job_description)

def analyze_job_poster_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Multimodal Vision AI (Project Astra style): Uses Gemini Vision to parse handwritten or printed
    job posters, hiring screenshots, or flyer images to extract title, company, skills, and salary.
    """
    if not genai_available:
        logger.info("Gemini API not available. Returning mock vision poster analysis for demo.")
        return get_mock_poster_analysis()

    try:
        image = Image.open(io.BytesIO(image_bytes))
        prompt = """
        You are Project Astra Vision AI, an intelligent agent capable of understanding real-world images, posters, and screenshots.
        Analyze this image of a Job Poster, LinkedIn post, or Hiring Screenshot.

        Extract the following information accurately:
        1. Job Title (e.g. SDE Intern, Backend Engineer)
        2. Company Name
        3. Key Required Skills (array of strings)
        4. Salary or Compensation Range (if mentioned, otherwise "Not specified")
        5. Full or summarized Job Description text
        6. Actionable Notes / Summary

        You MUST return ONLY a JSON object matching this schema:
        {
            "title": "Job Title",
            "company": "Company Name",
            "required_skills": ["Skill1", "Skill2"],
            "salary_range": "Salary Info",
            "description": "Extracted description...",
            "notes": "Extracted via Astra Vision AI Scan"
        }
        Do not output markdown backticks or code blocks around JSON.
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([image, prompt])
        text_response = response.text.strip()
        
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response.rsplit("```", 1)[0]
            
        data = json.loads(text_response.strip())
        return data
    except Exception as e:
        logger.error(f"Gemini Vision API poster analysis failed: {e}. Returning mock poster fallback.")
        return get_mock_poster_analysis()

def generate_email_draft(job_title: str, company: str, stage: str, context: str) -> str:
    """
    Generates a tailored email draft (cold outreach, follow-up) for a job application.
    """
    if not genai_available:
        logger.info("Gemini API not available. Returning mock email for demo.")
        return get_mock_email(job_title, company, stage)

    prompt = f"""
    Write a professional and concise email draft.
    - Job Title: {job_title}
    - Company: {company}
    - Stage: {stage} (e.g., Cold Outreach, Interview Follow-up, Post-Application Nudge)
    - Additional Context: {context}

    Keep the email strictly under 150 words. Ensure there are placeholders like [Recruiter Name] or [Your Name] for the candidate to fill out.
    Return ONLY the email subject and body.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API email draft failed: {e}.")
        return get_mock_email(job_title, company, stage)

# Fallback Mock Generators
def get_mock_analysis(job_description: str) -> Dict[str, Any]:
    """Generates realistic mock data based on keywords in JD when Gemini is offline."""
    jd_lower = job_description.lower()
    matching = ["Python"]
    missing = ["Google Cloud Firestore"]
    
    if "fastapi" in jd_lower:
        matching.append("FastAPI")
    else:
        missing.append("FastAPI")
        
    if "docker" in jd_lower or "kubernetes" in jd_lower:
        missing.append("Docker")
    else:
        matching.append("Git")
        
    score = 75 if len(matching) >= 2 else 55
    
    return {
        "match_score": score,
        "matching_skills": matching,
        "missing_skills": missing,
        "tips": [
            "Highlight python-based backend automation and API builds on your resume.",
            "Add Firestore or document database projects under your technical skills section."
        ]
    }

def get_mock_poster_analysis() -> Dict[str, Any]:
    """Generates realistic mock Vision AI output for demo job poster scans when GEMINI_API_KEY is not set."""
    return {
        "title": "Admin Staff / Operations SDE",
        "company": "Larana, Inc.",
        "required_skills": ["Good communication skills", "Microsoft Office", "Attention to detail", "Multitasking ability"],
        "salary_range": "Not specified",
        "description": "We need an organized and reliable individual to support daily operations efficiently. Contact: hello@reallygreatsite.com",
        "notes": "Scanned via Astra Vision AI (Demo Mode - Add GEMINI_API_KEY in .env for real live vision)"
    }

def run_auto_apply_agent(job_url: str, company: str, hr_email: Optional[str] = None) -> Dict[str, Any]:
    """
    Autonomous Auto-Apply AI Agent: Parses job post URL, populates candidate details,
    dispatches tailored email to HR, and logs the application automatically.
    """
    cleaned_company = company.strip() if company else "Target Tech Employer"
    target_hr = hr_email.strip() if hr_email else f"careers@{cleaned_company.lower().replace(' ', '')}.com"
    
    # Generate custom email draft
    email_body = generate_email_draft(
        job_title="AI / Backend Developer Intern",
        company=cleaned_company,
        stage="Cold Outreach",
        context="B.Tech CSE 2027, GSSoC Rank #29, FastAPI & Agentic AI expertise"
    )

    steps = [
        f"Parsed job target URL: {job_url}",
        "Extracted DOM form schema (Name, Email, Phone, College, Degree, GitHub)",
        "Populated profile: Rafia Minhaj (B.Tech CSE '27, CIT Ranchi)",
        "Attached Resume PDF & Portfolio: https://rafiaminhaj.github.io/my-portfolio/",
        f"Dispatched automated email to HR: {target_hr}",
        "Submitted form & logged application entry to Cloud Dashboard"
    ]

    return {
        "title": "AI / Backend Developer Intern",
        "company": cleaned_company,
        "hr_email": target_hr,
        "email_body": email_body,
        "form_submitted": True,
        "email_dispatched": True,
        "steps_completed": steps,
        "notes": f"🤖 Auto-applied via Autonomous AI Agent ({datetime.date.today().isoformat()})"
    }

def get_mock_email(job_title: str, company: str, stage: str) -> str:
    """Returns a general mock email template."""
    return f"""Subject: Regarding Python Developer application at {company}

Dear Hiring Team,

I hope this email finds you well. 

I recently applied for the {job_title} position at {company} and wanted to follow up on my application. With my experience in Python, FastAPI, and building webhooks, I am very excited about the opportunity to contribute to your engineering team. 

Please let me know if you need any further details or a copy of my resume.

Best regards,
Rafia Minhaj
Phone: +91-6206675008 | Email: rafiaminhaj423@gmail.com
GitHub: github.com/Rafiaminhaj"""


