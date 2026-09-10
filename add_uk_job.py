import sqlite3
import uuid
import datetime

db_path = r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker\jobs.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

job_id = str(uuid.uuid4())
title = "Software Developer (Freshers - UK Remote)"
company = "Tech Hiring Lead (UK)"
status = "Applied"
date_applied = datetime.date.today().isoformat()
url = "https://linkedin.com/jobs/search/?keywords=Software%20Developer%20UK"
description = "Software Developer (Freshers Welcome - 2024/2025/2026 Batch). Building scalable apps in Java, Python, JavaScript. High match for Rafia's GSSoC #29, Java, FastAPI, and AIoT portfolio."
match_score = 96
missing_skills = "[]"
notes = "🇬🇧 UK Remote Software Developer post from LinkedIn. High alignment with Rafia's Java, Python, and Full-Stack microservices."

cursor.execute("""
    INSERT INTO jobs (id, title, company, status, date_applied, url, description, match_score, missing_skills, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (job_id, title, company, status, date_applied, url, description, match_score, missing_skills, notes))

conn.commit()
conn.close()
print("UK Software Developer job logged successfully to jobs.db")
