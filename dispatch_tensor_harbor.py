import sys
import os
import sqlite3
import uuid
import datetime

sys.path.append(r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker")
from app.ai_engine import send_real_hr_email

print("Dispatching application outreach to amrita.singh@tensorharbor.com...")

to_hr_email = "amrita.singh@tensorharbor.com"
company = "Tensor Harbor (Pune)"
job_title = "Software Developer (Java / Python)"
active_resume = "https://rafiaminhaj.github.io/my-portfolio/Rafia_Minhaj_Resume.pdf"

# Dispatch real outreach email
send_real_hr_email(to_hr_email, company, job_title, active_resume)

# Add to jobs.db
db_path = r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker\jobs.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

job_id = str(uuid.uuid4())
cursor.execute("""
    INSERT INTO jobs (id, title, company, status, date_applied, url, description, match_score, missing_skills, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    job_id,
    job_title,
    company,
    "Applied",
    datetime.date.today().isoformat(),
    "https://tensorharbor.com",
    "Software Developer (Java / Python) role at Tensor Harbor Pune. Direct email outreach dispatched to amrita.singh@tensorharbor.com.",
    96,
    "[]",
    "📧 Direct HR Email Dispatched to amrita.singh@tensorharbor.com"
))

conn.commit()
conn.close()
print("Tensor Harbor job logged and email dispatched successfully!")
