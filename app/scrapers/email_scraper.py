import re
import dns.resolver

# Basic email validation
def is_valid_email(email: str):
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(pattern, email))

# MX lookup
def get_mx_records(domain: str):
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return [str(r.exchange) for r in answers]
    except Exception as e:
        return {"mx_error": str(e)}

# Placeholder breach check
def breach_check(email: str):
    return {
        "breached": False,
        "note": "Real breach lookup will be added later."
    }

# Main scraper
def scrape_email(email: str):
    result = {}

    # Validate
    result["valid_format"] = is_valid_email(email)

    if not result["valid_format"]:
        result["error"] = "Invalid email format"
        return result

    # Extract domain
    domain = email.split("@")[1]
    result["domain"] = domain

    # MX records
    result["mx_records"] = get_mx_records(domain)

    # Breach check placeholder
    result["breach_check"] = breach_check(email)

    return result
