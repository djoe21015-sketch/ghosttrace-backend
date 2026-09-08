import re

# Basic phone validation
def is_valid_phone(phone: str):
    pattern = r"^\+?[0-9]{7,15}$"
    return bool(re.match(pattern, phone))

# Region detection (very basic)
def detect_region(phone: str):
    if phone.startswith("+1"):
        return "United States / Canada"
    elif phone.startswith("+44"):
        return "United Kingdom"
    elif phone.startswith("+61"):
        return "Australia"
    elif phone.startswith("+91"):
        return "India"
    else:
        return "Unknown region"

# Placeholder line type
def detect_line_type(phone: str):
    return {
        "line_type": "unknown",
        "note": "Real carrier lookup will be added later."
    }

# Placeholder spam score
def spam_score(phone: str):
    return {
        "score": 0,
        "note": "Real spam scoring will be added later."
    }

# Main scraper
def scrape_phone(phone: str):
    result = {}

    # Validate
    result["valid_format"] = is_valid_phone(phone)
    if not result["valid_format"]:
        result["error"] = "Invalid phone number format"
        return result

    # Region
    result["region"] = detect_region(phone)

    # Line type
    result["line_type"] = detect_line_type(phone)

    # Spam score
    result["spam_score"] = spam_score(phone)

    return result
