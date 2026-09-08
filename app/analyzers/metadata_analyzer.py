def analyze_metadata(raw: dict):
    result = {}

    # WHOIS metadata
    if "whois" in raw:
        whois = raw["whois"]
        result["registrar"] = whois.get("registrar")
        result["creation_date"] = whois.get("creation_date")
        result["expiration_date"] = whois.get("expiration_date")

    # GeoIP metadata
    if "geoip" in raw:
        geo = raw["geoip"]
        result["country"] = geo.get("country")
        result["city"] = geo.get("city")
        result["isp"] = geo.get("isp")
        result["asn"] = geo.get("as")

    # Username platform metadata
    if "platforms" in raw:
        result["platforms_found"] = [
            p for p, exists in raw["platforms"].items() if exists
        ]

    # Email metadata
    if "mx_records" in raw:
        result["mx_count"] = len(raw["mx_records"]) if isinstance(raw["mx_records"], list) else 0

    # Phone metadata
    if "region" in raw:
        result["region"] = raw["region"]

    return result
