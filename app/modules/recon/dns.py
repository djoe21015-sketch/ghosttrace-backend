import dns.resolver

def run_dns_scan(domain):
    results = {
        "domain": domain,
        "records": {},
        "risk": 0
    }

    # Try resolving common DNS records
    for record_type in ["A", "MX", "NS", "TXT"]:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            results["records"][record_type] = [str(rdata) for rdata in answers]
        except Exception:
            results["records"][record_type] = []

    # Basic DNS security scoring
    txt_records = results["records"].get("TXT", [])

    # SPF check
    if not any("spf" in r.lower() for r in txt_records):
        results["risk"] += 20

    # DMARC check
    if not any("dmarc" in r.lower() for r in txt_records):
        results["risk"] += 20

    # MX check
    if not results["records"].get("MX"):
        results["risk"] += 10

    return results
