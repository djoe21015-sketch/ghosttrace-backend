import socket
import requests

# Basic GeoIP lookup using ip-api.com (free)
def geoip_lookup(ip: str):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        return r.json()
    except Exception as e:
        return {"geoip_error": str(e)}

# Reverse DNS
def reverse_dns(ip: str):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception as e:
        return {"reverse_dns_error": str(e)}

# Placeholder blacklist check
def blacklist_check(ip: str):
    return {
        "listed": False,
        "note": "Real blacklist checks will be added later."
    }

# Main scraper
def scrape_ip(ip: str):
    result = {}

    # GeoIP
    result["geoip"] = geoip_lookup(ip)

    # Reverse DNS
    result["reverse_dns"] = reverse_dns(ip)

    # Blacklist placeholder
    result["blacklist"] = blacklist_check(ip)

    return result
