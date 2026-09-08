import re
import requests

# Basic username validation
def is_valid_username(username: str):
    pattern = r"^[A-Za-z0-9_.-]{3,32}$"
    return bool(re.match(pattern, username))

# Check if username exists on a platform
def check_platform(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except Exception as e:
        return False

# Main scraper
def scrape_username(username: str):
    result = {}

    # Validate
    result["valid_format"] = is_valid_username(username)
    if not result["valid_format"]:
        result["error"] = "Invalid username format"
        return result

    # Platforms to check
    platforms = {
        "github": f"https://github.com/{username}",
        "reddit": f"https://www.reddit.com/user/{username}",
        "twitter": f"https://x.com/{username}",
        "instagram": f"https://www.instagram.com/{username}",
    }

    # Check existence
    existence = {}
    for platform, url in platforms.items():
        existence[platform] = check_platform(url)

    result["platforms"] = existence

    return result
