def correlate(raw: dict, metadata: dict):
    result = {}

    # Email ↔ Domain correlation
    if "domain" in raw and "registrar" in metadata:
        result["email_domain_matches_registrar"] = True if metadata["registrar"] else False

    # Domain ↔ IP correlation
    if "geoip" in raw and "country" in metadata:
        geo_country = raw["geoip"].get("country")
        meta_country = metadata.get("country")
        result["domain_ip_country_match"] = (geo_country == meta_country)

    # Username ↔ Email correlation
    if "domain" in raw and "platforms_found" in metadata:
        domain = raw.get("domain", "")
        platforms = metadata.get("platforms_found", [])
        result["username_related_to_email_domain"] = any(domain in p for p in platforms)

    # Phone ↔ Region correlation
    if "region" in raw and "country" in metadata:
        phone_region = raw.get("region")
        geo_country = metadata.get("country")
        result["phone_region_matches_geoip"] = (phone_region and geo_country and phone_region in geo_country)

    # General correlation score (simple placeholder)
    score = 0
    for key, val in result.items():
        if val:
            score += 1

    result["correlation_score"] = score

    return result
