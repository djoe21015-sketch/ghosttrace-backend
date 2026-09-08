import requests

def check_domain_breaches(domain: str):
    """
    Check if a domain appears in known breaches using HaveIBeenPwned.
    This endpoint does NOT require an API key.
    """
    try:
        url = f"https://haveibeenpwned.com/api/v3/breaches?domain={domain}"
        response = requests.get(url, timeout=10, headers={"User-Agent": "GhostTrace-OSINT"})

        if response.status_code == 404:
            return {
                "domain": domain,
                "breaches": [],
                "count": 0
            }

        if response.status_code != 200:
            return {
                "domain": domain,
                "error": f"HIBP returned {response.status_code}"
            }

        breaches = response.json()

        return {
            "domain": domain,
            "breaches": breaches,
            "count": len(breaches)
        }

    except Exception as e:
        return {
            "domain": domain,
            "error": str(e)
        }


def check_email_breaches(email: str, api_key: str = None):
    """
    Email breach check (requires API key).
    """
    if api_key is None:
        return {
            "email": email,
            "error": "No HIBP API key provided"
        }

    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {
            "User-Agent": "GhostTrace-OSINT",
            "hibp-api-key": api_key
        }

        response = requests.get(url, timeout=10, headers=headers)

        if response.status_code == 404:
            return {
                "email": email,
                "breaches": [],
                "count": 0
            }

        if response.status_code != 200:
            return {
                "email": email,
                "error": f"HIBP returned {response.status_code}"
            }

        breaches = response.json()

        return {
            "email": email,
            "breaches": breaches,
            "count": len(breaches)
        }

    except Exception as e:
        return {
            "email": email,
            "error": str(e)
        }


def run_breach_check(target: str, api_key: str = None):
    """
    Main entry point for GhostTrace.
    Detects whether target is a domain or email.
    """
    if "@" in target:
        return check_email_breaches(target, api_key)
    else:
        return check_domain_breaches(target)
