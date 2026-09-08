import sys
import time
from .pipeline import run_full_scan
from .postgres_client import save_report_to_postgres

def run_single_scan(target):
    print(f"[Worker] Running single scan for: {target}")

    # Run the recon pipeline
    results, report_path = run_full_scan(target)

    print("[Worker] Scan complete.")

    # Skip PostgreSQL entirely
    print("[Worker] Database saving disabled. Report stored locally.")

    print("[Worker] Single scan finished.")
    
    return

def run_queue_mode():
    print("GhostTraceWorker started.")
    print("Waiting for jobs in queue...")

    while True:
        time.sleep(5)
        # Your original queue logic would go here
        # But since you're running manual scans, this stays idle
        pass

if __name__ == "__main__":
    # If a domain was passed, run a single scan
    if len(sys.argv) > 1:
        target = sys.argv[1]
        run_single_scan(target)
    else:
        # Otherwise start normal worker mode
        run_queue_mode()
