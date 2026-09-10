import sqlite3
import os
from datetime import datetime

db_paths = [
    r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker\jobs.db",
    r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker\app\jobs.db"
]

today = datetime.now().strftime("%Y-%m-%d")

jobs = [
    {
        "title": "Software Developer - Systematize HA (Remote ₹90k/mo)",
        "company": "Systematize HA (Uniprep)",
        "status": "Applied",
        "date_applied": today,
        "url": "https://job.uniprep.ai/view/9b11c9f0-ab54-4c77-9a5b-72e10945b695/1021",
        "description": "Remote Software Developer position at Systematize HA. Bengaluru / Remote. Salary: INR 90,000/month. Experience: 0-3 years.",
        "match_score": 92,
        "missing_skills": "[]",
        "notes": "Direct application link received via email from HR Admin Gokul (hradmin@uniprep.ai)."
    },
    {
        "title": "Software Developer - Simplilearn (Remote ₹45k/mo)",
        "company": "Simplilearn (Uniprep)",
        "status": "Applied",
        "date_applied": today,
        "url": "https://job.uniprep.ai/view/e8cb7876-943b-4376-b281-6e2b2231e5e4/1021",
        "description": "Remote Software Developer position for Freshers at Simplilearn HQ Bengaluru. Salary: INR 45,000/month. Experience level: Fresher.",
        "match_score": 98,
        "missing_skills": "[]",
        "notes": "Direct application link received via email from HR Admin Gokul (hradmin@uniprep.ai). Perfect match for Freshers!"
    }
]

for db_path in db_paths:
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for j in jobs:
            cursor.execute("SELECT id FROM jobs WHERE url = ?", (j["url"],))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    """INSERT INTO jobs (title, company, status, date_applied, url, description, match_score, missing_skills, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (j["title"], j["company"], j["status"], j["date_applied"], j["url"], j["description"], j["match_score"], j["missing_skills"], j["notes"])
                )
                print(f"Added to {os.path.basename(db_path)}: {j['company']}")
            else:
                print(f"Already exists in {os.path.basename(db_path)}: {j['company']}")
        conn.commit()
        conn.close()

print("Database update complete.")
