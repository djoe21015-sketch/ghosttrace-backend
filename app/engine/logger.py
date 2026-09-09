import logging, datetime

logging.basicConfig(filename="ghosttrace.log", level=logging.INFO)

def log_event(event):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{timestamp}] {event}")
