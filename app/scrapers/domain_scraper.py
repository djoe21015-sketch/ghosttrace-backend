import socket
import whois

def scrape_domain(domain: str):
    result = {}

    # WHOIS lookup
    try:
        w = whois.whois(domain)
        result["whois"] = {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers
        }
    except Exception as e:
        result["whois_error"] = str(e)

    # DNS lookup
    try:
        ip = socket.gethostbyname(domain)
        result["dns"] = {"A_record": ip}
    except Exception as e:
        result["dns_error"] = str(e)

    return result
