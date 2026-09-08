import os
from datetime import datetime
from app.config import LOG_DIR

LOG_FILE = os.path.join(LOG_DIR, "ghosttrace.log")

def log(message: str):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"

    with open(LOG_FILE, "a") as f:
        f.write(entry)

    return entry
