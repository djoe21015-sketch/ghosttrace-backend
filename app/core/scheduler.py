import threading
import time
from app.core.detector import process_target

# Simple background scheduler (placeholder)
def start_scheduler():
    def loop():
        while True:
            # In the future, this will check for pending targets
            time.sleep(5)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
