from .model_client import client

def generate_recommendations(full_report: dict):
    """
    AI-powered security recommendations.
    Produces:
    - prioritized action list
    - remediation steps
    - exposure reduction strategies
    - threat mitigation guidance
    """

    prompt = f"""
You are a cybersecurity advisor. Based on the following OSINT report, generate a prioritized list of security recommendations:

{full_report}

Provide ONLY a JSON object with:
- priority_actions: list of the most important steps (ordered)
- quick_fixes: list of fast, easy improvements
- long_term: list of long-term strategic improvements
- justification: short explanation of why these actions matter
    """

    return client.ask(prompt)
