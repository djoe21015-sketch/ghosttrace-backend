from .model_client import client

def summarize_recon(data: dict):
    """
    Summarize WHOIS, DNS, subdomains, IP intel, tech fingerprinting.
    """
    prompt = f"""
You are an OSINT analyst. Summarize the following recon data clearly and professionally:

{data}

Provide:
- Key findings
- Infrastructure insights
- Exposure risks
- Notable anomalies
- High-level assessment
    """

    return client.ask(prompt)


def summarize_threats(data: dict):
    """
    Summarize threat intelligence (AbuseIPDB, OTX).
    """
    prompt = f"""
You are a cyber threat intelligence analyst. Summarize this threat intel:

{data}

Include:
- Threat score
- Malware associations
- Botnet indicators
- Blacklist status
- Severity assessment
    """

    return client.ask(prompt)


def summarize_social(data: dict):
    """
    Summarize social footprint.
    """
    prompt = f"""
You are an OSINT social analyst. Summarize this social footprint:

{data}

Include:
- Confirmed accounts
- Possible impersonation risks
- Exposure level
- Identity footprint strength
    """

    return client.ask(prompt)


def summarize_darkweb(data: dict):
    """
    Summarize dark web exposure.
    """
    prompt = f"""
You are a dark web intelligence analyst. Summarize this dark web exposure:

{data}

Include:
- Possible leaks
- Mentions
- Exposure severity
- Recommended next steps
    """

    return client.ask(prompt)


def summarize_all(full_report: dict):
    """
    Full combined summary.
    """
    prompt = f"""
You are a senior cyber intelligence analyst. Summarize this entire OSINT report:

{full_report}

Provide:
- Executive summary
- Key risks
- Threat posture
- Exposure level
- Recommended actions
    """

    return client.ask(prompt)
