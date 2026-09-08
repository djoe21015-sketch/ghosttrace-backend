import requests
from bs4 import BeautifulSoup

def wappalyzer_scan(url: str):
    """
    Passive technology detection using Wappalyzer API (optional).
    GhostTrace MAX Free Edition: API key not required.
    """
    try:
        API_KEY = None  # Free mode

        if API_KEY is None:
            return {"warning": "Wappalyzer API key not configured (free mode)"}

        headers = {"x-api-key": API_KEY}
        response = requests.get(f"https://api.wappalyzer.com/v2/lookup/?url={url}", headers=headers)

        if response.status_code != 200:
            return {"error": f"Wappalyzer returned {response.status_code}"}

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def fallback_scan(url: str):
    """
    GhostTrace MAX — Enhanced fingerprinting without Wappalyzer.
    Detects:
    - Server
    - X-Powered-By
    - CMS
    - Frameworks
    - JS libraries
    - Meta generator
    - Common CDN usage
    """
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        headers = response.headers

        soup = BeautifulSoup(html, "html.parser")

        tech = {
            "server": headers.get("Server"),
            "powered_by": headers.get("X-Powered-By"),
            "frameworks": [],
            "cms": [],
            "javascript_libs": [],
            "cdn": [],
            "meta_generator": None
        }

        # Detect CMS via meta generator tag
        generator = soup.find("meta", attrs={"name": "generator"})
        if generator and generator.get("content"):
            tech["meta_generator"] = generator.get("content")

            gen = generator.get("content").lower()
            if "wordpress" in gen:
                tech["cms"].append("WordPress")
            if "joomla" in gen:
                tech["cms"].append("Joomla")
            if "drupal" in gen:
                tech["cms"].append("Drupal")

        # Detect common JS libraries
        scripts = soup.find_all("script")
        for script in scripts:
            src = script.get("src", "").lower()

            if "jquery" in src:
                tech["javascript_libs"].append("jQuery")
            if "react" in src:
                tech["javascript_libs"].append("React")
            if "vue" in src:
                tech["javascript_libs"].append("Vue.js")
            if "angular" in src:
                tech["javascript_libs"].append("Angular")
            if "bootstrap" in src:
                tech["javascript_libs"].append("Bootstrap JS")
            if "tailwind" in src:
                tech["javascript_libs"].append("Tailwind CSS")

            # Detect CDNs
            if "cloudflare" in src:
                tech["cdn"].append("Cloudflare CDN")
            if "cdn.jsdelivr" in src:
                tech["cdn"].append("jsDelivr CDN")
            if "cdnjs" in src:
                tech["cdn"].append("cdnjs CDN")

        # Detect frameworks via HTML clues
        if "wp-content" in html.lower():
            tech["cms"].append("WordPress")

        if "drupal-settings-json" in html.lower():
            tech["cms"].append("Drupal")

        if "__next" in html.lower():
            tech["frameworks"].append("Next.js")

        if "nuxt" in html.lower():
            tech["frameworks"].append("Nuxt.js")

        if "laravel" in html.lower():
            tech["frameworks"].append("Laravel")

        if "django" in html.lower():
            tech["frameworks"].append("Django")

        return tech

    except Exception as e:
        return {"error": str(e)}


def run_techstack(domain: str):
    """
    Main entry point for GhostTrace MAX.
    """
    url = f"http://{domain}"

    return {
        "domain": domain,
        "wappalyzer": wappalyzer_scan(url),
        "fallback": fallback_scan(url)
    }
