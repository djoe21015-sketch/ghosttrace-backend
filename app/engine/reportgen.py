import datetime
from app.engine.logger import log_event

def generate_report(data):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{timestamp}.txt"

    try:
        with open(filename, "w") as f:
            f.write("GhostTrace Automated Report\n")
            f.write("===========================\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write("Engine Output:\n")
            f.write(str(data))

        log_event(f"Report generated: {filename}")
        return filename

    except Exception as e:
        log_event(f"Report generation failed: {e}")
        return None
