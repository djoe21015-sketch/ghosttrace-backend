import socket

def run_subdomain_enum(domain):
    results = {
        "domain": domain,
        "subdomains": [],
        "error": None
    }

    # Common subdomains to check
    common_subdomains = [
        "www",
        "mail",
        "dev",
        "api",
        "test",
        "blog",
        "shop",
        "ftp",
        "cpanel",
        "admin"
    ]

    try:
        for sub in common_subdomains:
            subdomain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(subdomain)
                results["subdomains"].append(subdomain)
            except Exception:
                pass

    except Exception as e:
        results["error"] = str(e)

    return results
