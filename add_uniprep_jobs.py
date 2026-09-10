import sqlite3
from datetime import datetime

conn = sqlite3.connect('C:/Users/adiqu/.gemini/antigravity/scratch/ai-job-tracker/jobs.db')
cursor = conn.cursor()

today = datetime.now().strftime("%Y-%m-%d")

jobs = [
    {
        "title": "Software Developer (Fresher Remote ₹45k/mo)",
        "company": "Simpli Learn (Uniprep)",
        "status": "Applied",
        "date_applied": today,
        "url": "https://job.uniprep.ai/view/e8cb7876-943b-4376-b281-6e2b2231e5e4/1011",
        "description": "Remote Software Developer role for Freshers at Simpli Learn. Salary: INR 45,000/month.",
        "match_score": 96,
        "missing_skills": "[]",
        "notes": "Direct link provided by Nithesh B (Uniprep Cutshort Hiring Manager). Ideal for Freshers!"
    },
    {
        "title": "Software Developer (Dubai Remote $3500/mo)",
        "company": "D4 Insight (Uniprep)",
        "status": "Applied",
        "date_applied": today,
        "url": "https://job.uniprep.ai/view/f113717a-82e8-457b-83ad-c3ad7ab35f91/1011",
        "description": "Remote Software Developer for D4 Insight HQ Dubai. Salary: $3500/month.",
        "match_score": 88,
        "missing_skills": "[\"2+ YOE\"]",
        "notes": "Direct referral link from Nithesh B (Cutshort Hiring Manager)."
    },
    {
        "title": "Software Developer (Remote ₹1.15L/mo)",
        "company": "SystematizeHA (Uniprep)",
        "status": "Applied",
        "date_applied": today,
        "url": "https://job.uniprep.ai/view/107ef347-51e6-4b82-82d2-f878a1b22b09/1011",
        "description": "Remote Software Developer for SystematizeHA. Salary: INR 1,15,000/month.",
        "match_score": 85,
        "missing_skills": "[\"2+ YOE\"]",
        "notes": "Direct referral link from Nithesh B (Cutshort Hiring Manager)."
    }
]

for j in jobs:
    # Check if URL already exists
    cursor.execute("SELECT id FROM jobs WHERE url = ?", (j["url"],))
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            """INSERT INTO jobs (title, company, status, date_applied, url, description, match_score, missing_skills, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (j["title"], j["company"], j["status"], j["date_applied"], j["url"], j["description"], j["match_score"], j["missing_skills"], j["notes"])
        )
        print(f"Added: {j['company']}")
    else:
        print(f"Already exists: {j['company']}")


conn.commit()
conn.close()
