import sqlite3
from datetime import datetime, timedelta
from .config import SQLITE_DB_PATH

def init_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT NOT NULL,
        schedule TEXT NOT NULL,
        last_run TEXT,
        next_run TEXT,
        status TEXT DEFAULT 'pending',
        report_path TEXT,
        error_message TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_job(target: str, schedule: str):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    next_run = datetime.now().isoformat()

    cur.execute("""
        INSERT INTO jobs (target, schedule, next_run)
        VALUES (?, ?, ?)
    """, (target, schedule, next_run))

    conn.commit()
    conn.close()


def get_due_jobs():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    now = datetime.now().isoformat()

    cur.execute("""
        SELECT * FROM jobs
        WHERE next_run <= ?
        AND status != 'running'
    """, (now,))

    rows = cur.fetchall()
    conn.close()

    return rows


def update_job(job_id: int, status: str, report_path=None, error=None, schedule="daily"):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    last_run = datetime.now()
    if schedule == "hourly":
        next_run = last_run + timedelta(hours=1)
    elif schedule == "weekly":
        next_run = last_run + timedelta(days=7)
    else:
        next_run = last_run + timedelta(days=1)

    cur.execute("""
        UPDATE jobs
        SET status = ?, last_run = ?, next_run = ?, report_path = ?, error_message = ?
        WHERE id = ?
    """, (status, last_run.isoformat(), next_run.isoformat(), report_path, error, job_id))

    conn.commit()
    conn.close()
