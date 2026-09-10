import time
import random
import requests
from ghosttrace_billing import handle_billing

BACKEND_URL = "https://ghosttrace-backend.onrender.com/run-engine"

PHONE_LIST = [
    "+12682876214",
    "+16708935701",
    "+19355649307",
    "+15790599024",
]

EMAIL_LIST = [
    "admin@example.com",
    "info@target.co",
]

SOCIAL_LIST = [
    "@osintbot",
    "@ghosttrace",
]

DOMAIN_LIST = [
    "fake.net",
    "company.io",
]

def pick_target():
    kinds = ["phone", "email", "social", "domain"]
    kind = random.choice(kinds)

    if kind == "phone":
        return kind, random.choice(PHONE_LIST)
    if kind == "email":
        return kind, random.choice(EMAIL_LIST)
    if kind == "social":
        return kind, random.choice(SOCIAL_LIST)
    if kind == "domain":
        return kind, random.choice(DOMAIN_LIST)

def send_to_backend(target_type, target_value):
    params = {"type": target_type, "target": target_value}
    r = requests.get(BACKEND_URL, params=params, timeout=60)
    print(f"[BACKEND] {target_type}={target_value} -> {r.status_code}")
    print(r.text)

    try:
        data = r.json()
        if "result" in data:
            handle_billing(target_type, target_value, data["result"])
    except Exception as e:
        print(f"[BILLING SKIP] bad JSON: {e}")

def main():
    print("GhostTrace auto-runner started. Hunting everything forever...")
    while True:
        t_type, t_value = pick_target()
        print(f"[TARGET] {t_type}: {t_value}")
        send_to_backend(t_type, t_value)
        time.sleep(10)

if __name__ == "__main__":
    main()

