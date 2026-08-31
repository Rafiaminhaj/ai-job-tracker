import os
import logging
from typing import List, Dict, Any
from app.config import settings

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to initialize Firestore
db = None
use_local_sqlite = False

try:
    from google.cloud import firestore
    # If project ID is provided and credentials or local mock is bypassed
    if settings.FIRESTORE_PROJECT_ID:
        db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID)
        # Test connection/client creation
        logger.info(f"Initialized Google Cloud Firestore client for project: {settings.FIRESTORE_PROJECT_ID}")
    else:
        raise ValueError("Firestore Project ID not specified.")
except Exception as e:
    logger.warning(f"Could not initialize Cloud Firestore ({e}). Falling back to local SQLite database.")
    use_local_sqlite = True

# local SQLite setup if Firestore is offline/local
if use_local_sqlite:
    import sqlite3
    SQLITE_DB_PATH = "jobs.db"
    
    def get_sqlite_conn():
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
        
    # Create tables if they don't exist
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            status TEXT,
            date_applied TEXT,
            url TEXT,
            description TEXT,
            match_score INTEGER,
            missing_skills TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

# Interface Functions for Database
def get_all_jobs() -> List[Dict[str, Any]]:
    if not use_local_sqlite and db:
        try:
            jobs_ref = db.collection("jobs")
            docs = jobs_ref.stream()
            jobs_list = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                jobs_list.append(data)
            return jobs_list
        except Exception as e:
            logger.error(f"Firestore get_all_jobs error: {e}. Falling back to SQLite.")
            
    # SQLite fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    jobs_list = []
    for row in rows:
        job = dict(row)
        # deserialize list
        if job.get("missing_skills"):
            job["missing_skills"] = job["missing_skills"].split(",")
        else:
            job["missing_skills"] = []
        jobs_list.append(job)
    conn.close()
    return jobs_list

def add_job(job_data: Dict[str, Any]) -> str:
    job_id = job_data.get("id")
    if not use_local_sqlite and db:
        try:
            doc_ref = db.collection("jobs").document(job_id)
            doc_ref.set(job_data)
            return job_id
        except Exception as e:
            logger.error(f"Firestore add_job error: {e}. Falling back to SQLite.")
            
    # SQLite fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    missing_skills_str = ",".join(job_data.get("missing_skills", []))
    cursor.execute("""
        INSERT OR REPLACE INTO jobs 
        (id, title, company, status, date_applied, url, description, match_score, missing_skills, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        job_data.get("title"),
        job_data.get("company"),
        job_data.get("status"),
        job_data.get("date_applied"),
        job_data.get("url"),
        job_data.get("description"),
        job_data.get("match_score", 0),
        missing_skills_str,
        job_data.get("notes")
    ))
    conn.commit()
    conn.close()
    return job_id

def update_job_status(job_id: str, status: str) -> bool:
    if not use_local_sqlite and db:
        try:
            doc_ref = db.collection("jobs").document(job_id)
            doc_ref.update({"status": status})
            return True
        except Exception as e:
            logger.error(f"Firestore update error: {e}. Falling back to SQLite.")
            
    # SQLite fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def delete_job(job_id: str) -> bool:
    if not use_local_sqlite and db:
        try:
            doc_ref = db.collection("jobs").document(job_id)
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Firestore delete error: {e}. Falling back to SQLite.")
            
    # SQLite fallback
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
