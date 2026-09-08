import requests
import socket

IPINFO_LITE_TOKEN = "ee906001ea5a90"

def run_ipinfo(domain: str):
    # Step 1: Resolve domain → IP
    try:
        ip = socket.gethostbyname(domain)
    except Exception:
        return {"error": "Could not resolve domain to IP"}

    # Step 2: Query IPinfo Lite API
    url = f"https://ipinfo.io/{ip}?token={IPINFO_LITE_TOKEN}"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"ipinfo.io returned status {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}
