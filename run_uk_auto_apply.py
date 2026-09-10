import sys
import os
import uuid
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_engine import run_auto_apply_agent
import sqlite3

print("Running Autonomous AI Auto-Apply Agent for UK Software Developer role...")

result = run_auto_apply_agent(
    job_url="https://linkedin.com/jobs/search/?keywords=Software%20Developer%20UK",
    company="Tech Hiring Lead (UK)",
    hr_email="careers.uk@softwaredev-hiring.com",
    resume_url="https://rafiaminhaj.github.io/my-portfolio/Rafia_Minhaj_Resume.pdf"
)

status = result.get('status', 'success')
notes = result.get('notes', f"Autonomous AI Agent Applied ({datetime.date.today().isoformat()})")

print(f"Agent Execution Complete: {status}")

# Update jobs.db status
db_path = r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker\jobs.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    UPDATE jobs
    SET notes = ?
    WHERE company = 'Tech Hiring Lead (UK)'
""", (f"Autonomous AI Agent Applied & Dispatched Outreach | {notes}",))

conn.commit()
conn.close()
print("Updated database with Auto-Apply Agent execution log successfully!")
