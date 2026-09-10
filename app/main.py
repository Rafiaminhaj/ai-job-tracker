import uuid
import datetime
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional

from app import database
from app import ai_engine

app = FastAPI(
    title="AI Job Application Tracker",
    description="AUTOMATED CAREER OPTIMIZATION PIPELINE & DASHBOARD FOR CODE KITCHEN",
    version="1.0.0"
)

# Enable CORS for local cross-origin testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resume Template representing Rafia's premium developer profile (used as default)
DEFAULT_RESUME = """
RAFIA MINHAJ
Phone: +91-6206675008 | Email: rafiaminhaj423@gmail.com
LinkedIn: linkedin.com/in/rafia-minhaj | GitHub: github.com/Rafiaminhaj

PROFESSIONAL SUMMARY
Final-year Computer Science student with a strong foundation in Software Testing Life Cycle (STLC) and hands-on experience in 
automated unit, integration, and API testing (JUnit, Mockito, Postman). Built production-style REST APIs and validated them 
under high concurrency (1000+ simulated events), achieving 90%+ test coverage. Comfortable with Java, Python, SQL, and Git-based 
collaborative workflows, with working exposure to CI/CD pipelines. GirlScript Summer of Code 2026 Global Rank #29 (Top 0.8%). 
Eager to build on this foundation with enterprise-grade automation tools such as Selenium in a structured QA / Software Engineering environment.

EDUCATION
Cambridge Institute of Technology (CIT), Ranchi, Jharkhand
Bachelor of Technology in Computer Science & Engineering | CGPA: 8.32/10.0 (Aug 2023 - May 2027)
- Coursework: Data Structures & Algorithms, DBMS, Operating Systems, Software Engineering, Object-Oriented Design.
- Focus: Backend Engineering & QA Automation; ranked in top tier of CSE batch.

TECHNICAL SKILLS
- Testing & QA: JUnit 5, Mockito, Unit & Integration Testing, REST API Testing (Postman), Selenium, Test Coverage Analysis
- Languages: Java, Python, JavaScript (ES6+), SQL
- Frameworks & Libraries: Spring Boot, FastAPI, Django, Node.js, Express
- Databases: PostgreSQL, MySQL, SQLite, MongoDB
- DevOps & CI/CD: Docker, GitHub Actions (CI/CD pipelines), Kubernetes, Google Cloud Run
- Methodologies: Agile fundamentals, SDLC, STLC

PROFESSIONAL EXPERIENCE
- GeeksforGeeks - Campus Mantri (Official Representative) (Jan 2026 - Present)
  Liaison between GeeksforGeeks and 500+ student developer community at CIT Ranchi; organized 5+ workshops & coding contests.
- Elite Coders ECWOC - Open Source Contributor | GSSoC 2026 (Jan 2026 - Present)
  Resolved 12+ GitHub issues across 3+ codebases; achieved GSSoC 2026 Global Rank #29 (Top 0.8%).

PROJECTS
1. CodeKitchen AI Job Tracker & Autonomous Agent (FastAPI, Python, Playwright, Gemini Vision AI)
   Built end-to-end job tracker with multimodal poster parsing, Zapier webhooks, and live browser automation.
2. Concurrent Spring Wallet API (Java, Spring Boot, PostgreSQL, JUnit 5, Mockito)
   Built automated test suite simulating 1000+ concurrent payment events, achieving 90%+ test coverage.
3. Cloud-Native GitOps CI/CD Pipeline (FastAPI, Docker, GitHub Actions, Pytest)
   Configured automated CI pipeline on Google Cloud Run with Pytest test suites on every commit.
4. WhatsApp AI LeadAgent & CRM (Python, FastAPI, Gemini, SQLite)
   API-tested 10+ endpoints with 95% request/response contract validation accuracy.

ACHIEVEMENTS & CERTIFICATIONS
- GirlScript Summer of Code (GSSoC 2026): Global Rank #29 (Top 0.8%) out of thousands of participants.
- Cloud Credentials: 36+ Microsoft Learn Badges covering advanced Azure Cloud Architectures.
- Certifications: McKinsey Forward Program; Google Cloud Intro to Generative AI.
- AI Launchpad (Interview Kickstart, Aug 2026): Hands-on training in AI agent & multi-agent system architectures.
"""

# Pydantic Schemas for validation
class JobCreateSchema(BaseModel):
    title: str = Field(..., example="Python Developer")
    company: str = Field(..., example="Hireflux")
    status: str = Field("Applied", example="Applied") # Applied, Interviewing, Offered, Rejected
    url: Optional[str] = Field("", example="https://hireflux.in/jobs/1")
    description: Optional[str] = Field("", example="Looking for a Python Developer with FastAPI skills.")
    notes: Optional[str] = Field("", example="Referral from HR Naveen.")

class StatusUpdateSchema(BaseModel):
    status: str = Field(..., example="Interviewing")

class AnalysisRequestSchema(BaseModel):
    job_description: str = Field(...)
    resume_text: Optional[str] = Field(None)

class EmailDraftRequestSchema(BaseModel):
    job_title: str = Field(...)
    company: str = Field(...)
    stage: str = Field(...) # Cold Outreach, Follow-up, Nudge
    context: Optional[str] = Field("", example="Mention my FastAPI experience.")

# Endpoints
@app.get("/api/jobs")
def get_jobs():
    """Retrieve all job applications."""
    try:
        return database.get_all_jobs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs")
def create_job(job: JobCreateSchema):
    """Add a new job application."""
    try:
        job_id = str(uuid.uuid4())
        job_dict = {
            "id": job_id,
            "title": job.title,
            "company": job.company,
            "status": job.status,
            "date_applied": datetime.date.today().isoformat(),
            "url": job.url,
            "description": job.description,
            "match_score": 0,
            "missing_skills": [],
            "notes": job.notes
        }
        database.add_job(job_dict)
        return {"status": "success", "id": job_id, "data": job_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/jobs/{job_id}/status")
def update_status(job_id: str, payload: StatusUpdateSchema):
    """Update status of a job application."""
    if payload.status not in ["Applied", "Interviewing", "Offered", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status type.")
    
    success = database.update_job_status(job_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Job application not found.")
    return {"status": "success", "message": f"Updated status to {payload.status}"}

@app.delete("/api/jobs/{job_id}")
def delete_job_application(job_id: str):
    """Delete a job application."""
    success = database.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job application not found.")
    return {"status": "success", "message": "Job application deleted."}

@app.post("/api/analyze")
def analyze_job(payload: AnalysisRequestSchema):
    """Analyze a job description and compute match scores using Gemini."""
    try:
        resume = payload.resume_text if payload.resume_text else DEFAULT_RESUME
        analysis_result = ai_engine.analyze_job_description(payload.job_description, resume)
        return {"status": "success", "analysis": analysis_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan-poster")
async def scan_job_poster(file: UploadFile = File(...)):
    """Multimodal Vision AI endpoint (Project Astra) to extract job metadata from job poster images or screenshots."""
    try:
        contents = await file.read()
        result = ai_engine.analyze_job_poster_image(contents)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ZapierWebhookSchema(BaseModel):
    title: Optional[str] = Field("Software Engineer Role", example="SDE Intern Position")
    company: Optional[str] = Field("Deloitte / Amazon", example="Deloitte Careers")
    status: Optional[str] = Field("Applied", example="Applied")
    description: Optional[str] = Field("", example="Incoming email job notification")
    notes: Optional[str] = Field("Auto-logged via Zapier Webhook Automation", example="Zapier Gmail Trigger")

@app.post("/api/webhook/zapier")
def zapier_webhook_listener(payload: ZapierWebhookSchema):
    """
    Zapier Automation Webhook Endpoint: Receives automated job application triggers
    from Zapier when emails arrive from Deloitte, Amazon, LinkedIn, or Juspay.
    """
    try:
        job_id = str(uuid.uuid4())
        job_dict = {
            "id": job_id,
            "title": payload.title or "Software Developer Role",
            "company": payload.company or "Automated Hiring Alert",
            "status": payload.status or "Applied",
            "date_applied": datetime.date.today().isoformat(),
            "url": "https://zapier.com/app/zaps",
            "description": payload.description or "Logged via Zapier Gmail Webhook Integration",
            "match_score": 85,
            "missing_skills": [],
            "notes": payload.notes or "⚡ Auto-logged via Zapier Webhook Automation"
        }
        database.add_job(job_dict)
        return {
            "status": "success",
            "message": "Zapier Webhook processed & application logged to Cloud Dashboard!",
            "id": job_id,
            "data": job_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AutoApplyRequestSchema(BaseModel):
    job_url: str = Field(..., example="https://careers.deloitte.com/job/123")
    company: str = Field(..., example="Deloitte India")
    hr_email: Optional[str] = Field(None, example="indiacareers@deloitte.com")
    resume_url: Optional[str] = Field(None, example="https://rafiaminhaj.github.io/my-portfolio/Rafia_Minhaj_Resume.pdf")

@app.post("/api/auto-apply")
def auto_apply_job(payload: AutoApplyRequestSchema):
    """
    Autonomous Auto-Apply Endpoint: Runs AI Agent to auto-fill form fields,
    dispatch tailored HR emails, and log application entry to dashboard.
    """
    try:
        agent_res = ai_engine.run_auto_apply_agent(
            job_url=payload.job_url,
            company=payload.company,
            hr_email=payload.hr_email,
            resume_url=payload.resume_url
        )
        job_id = str(uuid.uuid4())
        job_dict = {
            "id": job_id,
            "title": agent_res["title"],
            "company": agent_res["company"],
            "status": "Applied",
            "date_applied": datetime.date.today().isoformat(),
            "url": payload.job_url,
            "description": f"Automated application via Auto-Apply Agent. HR Email: {agent_res['hr_email']}",
            "match_score": 90,
            "missing_skills": [],
            "notes": agent_res["notes"]
        }
        database.add_job(job_dict)
        return {
            "status": "success",
            "message": f"Autonomous AI Agent successfully applied to {agent_res['company']}!",
            "agent_result": agent_res,
            "job_data": job_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/draft-email")
def draft_email(payload: EmailDraftRequestSchema):
    """Generate a custom email draft for follow-ups or cold pitches using Gemini."""
    try:
        draft = ai_engine.generate_email_draft(
            payload.job_title, 
            payload.company, 
            payload.stage, 
            payload.context
        )
        return {"status": "success", "draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Frontend static files on the root url
app.mount("/", StaticFiles(directory="static", html=True), name="static")



