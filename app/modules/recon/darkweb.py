import requests

DARKWEB_SEARCH_ENGINES = [
    "https://ahmia.fi/search/?q={}",                     # Ahmia (legal onion search)
    "https://onionlandsearchengine.com/search?q={}",     # OnionLand mirror
]

def search_darkweb(query: str):
    """
    Passive dark web search using public onion search mirrors.
    Safe, legal, and compliant with GhostTrace MAX Free Edition.
    """
    results = []

    for engine in DARKWEB_SEARCH_ENGINES:
        try:
            url = engine.format(query)
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "GhostTrace-OSINT"}
            )

            if response.status_code == 200:
                text = response.text

                results.append({
                    "engine": engine,
                    "status": "ok",
                    "content_length": len(text),
                    "raw_snippet": text[:500],  # preview only
                    "mentions_domain": query.lower() in text.lower(),
                    "mentions_email": "@" in query and query.lower() in text.lower()
                })
            else:
                results.append({
                    "engine": engine,
                    "status": f"error {response.status_code}"
                })

        except Exception as e:
            results.append({
                "engine": engine,
                "status": "exception",
                "error": str(e)
            })

    return results


def run_darkweb(target: str):
    """
    GhostTrace MAX dark web intelligence.
    Passive-only:
    - domain mentions
    - email mentions
    - keyword exposure
    """
    return {
        "target": target,
        "search_results": search_darkweb(target),
        "summary": {
            "domain_mentions": sum(1 for r in search_darkweb(target) if r.get("mentions_domain")),
            "email_mentions": sum(1 for r in search_darkweb(target) if r.get("mentions_email")),
        }
    }
