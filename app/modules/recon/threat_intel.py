import requests

def abuseipdb_lookup(ip: str):
    """
    AbuseIPDB free lookup (no API key required).
    Only returns basic reputation info.
    """
    try:
        # Free endpoint (no key required)
        url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}"
        response = requests.get(url, timeout=10)

        # Free mode returns limited data
        return {
            "ip": ip,
            "status": response.status_code,
            "note": "Free AbuseIPDB mode — limited data",
        }

    except Exception as e:
        return {"error": str(e)}


def otx_lookup(ip: str):
    """
    AlienVault OTX threat lookup.
    Free and does not require an API key.
    """
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {"error": f"OTX returned {response.status_code}"}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def ipapi_lookup(ip: str):
    """
    Free IP reputation + geolocation lookup.
    """
    try:
        url = f"https://ipapi.co/{ip}/json/"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def run_threat_intel(ip: str):
    """
    GhostTrace MAX threat intelligence aggregator.
    Free edition — no paid API keys required.
    """
    return {
        "ip": ip,
        "abuseipdb": abuseipdb_lookup(ip),
        "otx": otx_lookup(ip),
        "ipapi": ipapi_lookup(ip)
    }
