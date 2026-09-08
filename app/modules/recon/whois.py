import whois

def run_whois(domain: str):
    try:
        data = whois.whois(domain)

        return {
            "domain": domain,
            "registrar": data.registrar,
            "creation_date": str(data.creation_date),
            "expiration_date": str(data.expiration_date),
            "updated_date": str(data.updated_date),
            "status": data.status,
            "nameservers": data.name_servers,
            "emails": data.emails,
            "dnssec": data.dnssec,
            "abuse_contact": data.get("abuse_email", None),
            "raw": str(data)
        }

    except Exception as e:
        return {
            "error": str(e),
            "domain": domain
        }
