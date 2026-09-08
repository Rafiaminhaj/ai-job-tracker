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
Email: rafiaminhaj423@gmail.com | Phone: +91-6206675008
GitHub: github.com/Rafiaminhaj | Portfolio: rafiaminhaj.github.io/my-portfolio/

EDUCATION:
- B.Tech in Computer Science & Engineering (Class of 2027)
  Cambridge Institute of Technology (CIT), Ranchi.

TECHNICAL SKILLS:
- Languages: Python, Java, JavaScript, HTML, CSS, SQL.
- Frameworks & Tools: FastAPI, Spring Boot, Git, GitHub, Docker, Prometheus, Grafana.
- Databases: SQLite, H2 Database, Firestore, PostgreSQL.
- Specializations: AI Agent Workflows, Backend API Development, CI/CD GitOps.

EXPERIENCE:
- AI Developer Intern at InAmigos (July 2026 - Present)
  Building AI-enabled conversational bots and agent workflows.
- GirlScript Summer of Code (GSSoC '26) Contributor
  Globally Ranked #547 (Top 2% of contributors) in open-source projects.
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

