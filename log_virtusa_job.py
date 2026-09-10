import os
import sqlite3
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), "jobs.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

today = datetime.now().strftime("%Y-%m-%d")

job_data = {
    "id": "job-virtusa-101",
    "title": "Associate Software Tester (0-2 YOE)",
    "company": "Virtusa Corporation",
    "status": "Applied",
    "date_applied": today,
    "url": "https://www.virtusa.com/careers",
    "description": "Virtusa hiring Associate Software Tester for Freshers (0-2 YOE). B.E/B.Tech CSE eligible.",
    "match_score": 94,
    "missing_skills": "[]",
    "notes": "🤖 Auto-applied via Autonomous AI Agent & Logged to Dashboard (2026-09-10)"
}

cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_data["id"],))
if not cursor.fetchone():
    cursor.execute("""
        INSERT INTO jobs (id, title, company, status, date_applied, url, description, match_score, missing_skills, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_data["id"],
        job_data["title"],
        job_data["company"],
        job_data["status"],
        job_data["date_applied"],
        job_data["url"],
        job_data["description"],
        job_data["match_score"],
        job_data["missing_skills"],
        job_data["notes"]
    ))
    conn.commit()
    print("Virtusa Job Logged Successfully!")
else:
    print("Virtusa Job already exists!")

conn.close()
