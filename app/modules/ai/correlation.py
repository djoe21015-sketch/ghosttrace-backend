from .model_client import client

def correlate(full_report: dict):
    """
    AI-powered correlation engine.
    Links:
    - WHOIS
    - DNS
    - Subdomains
    - IP intel
    - Tech fingerprinting
    - Breach data
    - Social footprint
    - Dark web exposure
    - Threat intel

    Produces:
    - infrastructure relationships
    - pattern detection
    - threat linkage
    - exposure mapping
    """

    prompt = f"""
You are a senior cyber intelligence analyst. Correlate the following OSINT data:

{full_report}

Provide ONLY a JSON object with:
- infrastructure_links: list of relationships between IPs, domains, subdomains, hosting, tech stack
- threat_links: list of connections between threat intel and recon data
- exposure_map: list of how different findings relate to each other
- anomalies: list of unusual or suspicious patterns
- summary: short paragraph explaining the overall correlation
    """

    return client.ask(prompt)
