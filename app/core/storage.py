import os
import json
from datetime import datetime
from app.config import STORAGE_DIR

RAW_DIR = os.path.join(STORAGE_DIR, "raw")
INTEL_DIR = os.path.join(STORAGE_DIR, "intel")
REPORT_DIR = os.path.join(STORAGE_DIR, "reports")

# Ensure directories exist
for d in [RAW_DIR, INTEL_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)

# Save raw scraper output
def save_raw(target_id: int, data: dict):
    filename = f"{target_id}_{datetime.utcnow().timestamp()}.json"
    path = os.path.join(RAW_DIR, filename)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    return path

# Save intelligence output
def save_intel(target_id: int, category: str, content: str):
    filename = f"{target_id}_{category}_{datetime.utcnow().timestamp()}.txt"
    path = os.path.join(INTEL_DIR, filename)

    with open(path, "w") as f:
        f.write(content)

    return path

# Save generated report file
def save_report(target_id: int, report_text: str):
    filename = f"{target_id}_report_{datetime.utcnow().timestamp()}.txt"
    path = os.path.join(REPORT_DIR, filename)

    with open(path, "w") as f:
        f.write(report_text)

    return path
