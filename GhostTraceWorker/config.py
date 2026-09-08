SQLITE_DB_PATH = "worker_jobs.db"

POSTGRES = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "yourpassword",
    "database": "ghosttrace"
}

SCAN_INTERVAL_SECONDS = 60  # worker checks for jobs every minute
