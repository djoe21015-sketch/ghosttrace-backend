from app.core.detector import process_target

# Trigger a scan manually
def trigger_scan(target_id: int):
    return process_target(target_id)

# Trigger scan from API or dashboard
def trigger_from_api(target_id: int):
    return process_target(target_id)

# Trigger scan from scheduler (future)
def trigger_from_scheduler(target_id: int):
    return process_target(target_id)
