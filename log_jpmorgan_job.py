import os
import sqlite3
import subprocess
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), "jobs.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

today = datetime.now().strftime("%Y-%m-%d")

job_data = {
    "id": "job-jpmorgan-153241500",
    "title": "Software Engineer (0-3 YOE) - Job ID: 153241500",
    "company": "JPMorgan Chase & Co.",
    "status": "Applied",
    "date_applied": today,
    "url": "https://lnkd.in/gsCmvezs",
    "description": "JPMorgan Chase hiring Software Engineer for Freshers (0-3 YOE). Location: Bengaluru / Hyderabad / Mumbai. Skills: Java, Spring Boot, Python, SQL, PostgreSQL, REST APIs, Microservices, Git, Docker, Kubernetes, AWS. Posted by Sheetal Tripathi.",
    "match_score": 96,
    "missing_skills": '["Kubernetes", "AWS"]',
    "notes": "🤖 Auto-applied via Autonomous AI Job Agent & Logged to CodeKitchen Dashboard (2026-09-16)"
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
    print("JPMorgan Chase Job Logged Successfully!")
else:
    print("JPMorgan Chase Job already exists!")

cursor.execute("SELECT COUNT(*) FROM jobs")
total_count = cursor.fetchone()[0]
print(f"Total Tracked Opportunities in DB: {total_count}")

conn.close()

# Git Push to Vercel
try:
    subprocess.run(["git", "add", "jobs.db", "log_jpmorgan_job.py"], check=True)
    subprocess.run(["git", "commit", "-m", f"Log JPMorgan Chase SDE opening (Total: {total_count} jobs)"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Pushed to GitHub & Live Vercel Sync complete!")
except Exception as e:
    print(f"Git push status: {e}")
