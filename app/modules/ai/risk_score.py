from .model_client import client

def generate_risk_score(full_report: dict):
    """
    AI-powered risk scoring.
    Produces:
    - numeric score (0–100)
    - severity label
    - explanation
    """

    prompt = f"""
You are a cyber risk analyst. Based on the following OSINT report, generate a risk score:

{full_report}

Provide ONLY a JSON object with:
- score: number from 0 to 100
- severity: one of ["Low", "Medium", "High", "Critical"]
- explanation: short paragraph explaining why
- key_factors: list of the most important factors
    """

    return client.ask(prompt)
