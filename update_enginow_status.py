import sqlite3

db_path = r"C:\Users\adiqu\.gemini\antigravity\scratch\ai-job-tracker\jobs.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    UPDATE jobs
    SET status = 'Interviewing',
        notes = '🎉 Official Google Meet Interview Scheduled for Sep 12, 2026 (04:30 PM - 05:00 PM IST)'
    WHERE company LIKE '%Enginow%'
""")

if cursor.rowcount == 0:
    # If not found, insert
    import uuid, datetime
    job_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO jobs (id, title, company, status, date_applied, url, description, match_score, missing_skills, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        "AI / Backend Developer Intern",
        "Enginow (Hiring Hackathon S1)",
        "Interviewing",
        datetime.date.today().isoformat(),
        "https://enginow.com",
        "Official Online Google Meet Interview scheduled for Sep 12, 2026 (04:30 PM IST).",
        98,
        "[]",
        "🎉 Official Google Meet Interview Scheduled for Sep 12, 2026 (04:30 PM - 05:00 PM IST)"
    ))

conn.commit()
conn.close()
print("Updated Enginow status to Interviewing in jobs.db successfully!")
