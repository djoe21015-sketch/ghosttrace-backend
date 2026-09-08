def calculate_risk(raw: dict, metadata: dict, correlation: dict):
    score = 0
    details = []

    # Correlation score
    corr_score = correlation.get("correlation_score", 0)
    score += corr_score * 10
    details.append(f"Correlation score contributed {corr_score * 10} points")

    # Email risk
    if raw.get("breach_check", {}).get("breached"):
        score += 25
        details.append("Email breach detected (+25)")

    # IP blacklist risk
    if raw.get("blacklist", {}).get("listed"):
        score += 20
        details.append("IP appears on blacklist (+20)")

    # Username risk
    platforms = metadata.get("platforms_found", [])
    if len(platforms) > 3:
        score += 10
        details.append("Username found on many platforms (+10)")

    # Domain age risk
    creation = metadata.get("creation_date")
    if creation and "202" in str(creation):  # crude check for recent domains
        score += 5
        details.append("Domain appears recently created (+5)")

    # Normalize score to 0–100
    if score > 100:
        score = 100

    return {
        "risk_score": score,
        "details": details
    }
