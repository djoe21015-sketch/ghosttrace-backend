import requests
from app.engine.logger import log_event

def send_alert(message):
    webhook_url = "https://hooks.slack.com/services/your/webhook/url"
    try:
        requests.post(webhook_url, json={"text": message})
        log_event(f"Alert sent: {message}")
    except Exception as e:
        log_event(f"Alert failed: {e}")
