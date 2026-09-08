import requests

SOCIAL_PLATFORMS = {
    "twitter": "https://x.com/{}",
    "instagram": "https://www.instagram.com/{}/",
    "facebook": "https://www.facebook.com/{}",
    "tiktok": "https://www.tiktok.com/@{}",
    "github": "https://github.com/{}",
    "reddit": "https://www.reddit.com/user/{}",
    "linkedin": "https://www.linkedin.com/in/{}",
    "pinterest": "https://www.pinterest.com/{}/",
    "tumblr": "https://{}.tumblr.com",
    "medium": "https://medium.com/@{}",
    "youtube": "https://www.youtube.com/@{}"
}

def check_profile(url: str):
    """
    Passive profile existence check using HTTP status codes.
    GhostTrace MAX Free Edition: No scraping, no login, no automation.
    """
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "GhostTrace-OSINT"}
        )

        # 200 = profile exists
        if response.status_code == 200:
            return True

        # 301/302 = redirect (often means profile exists)
        if response.status_code in [301, 302]:
            return True

        return False

    except Exception:
        return False


def run_social_footprint(username: str):
    """
    Main entry point for GhostTrace MAX username OSINT.
    """
    results = {}

    for platform, url_template in SOCIAL_PLATFORMS.items():
        url = url_template.format(username)
        exists = check_profile(url)

        results[platform] = {
            "exists": exists,
            "url": url if exists else None
        }

    return {
        "username": username,
        "profiles": results,
        "total_found": sum(1 for p in results.values() if p["exists"])
    }


def enumerate_social(username: str):
    """
    Alias for compatibility with older GhostTrace modules.
    """
    return run_social_footprint(username)
