def generate_report(target_id: int, raw: dict, metadata: dict, correlation: dict, risk: dict):
    lines = []

    lines.append("====================================")
    lines.append(f"        GhostTrace OSINT Report")
    lines.append("====================================")
    lines.append(f"Target ID: {target_id}")
    lines.append("")

    # RAW DATA
    lines.append("---------- RAW DATA ----------")
    for key, val in raw.items():
        lines.append(f"{key}: {val}")
    lines.append("")

    # METADATA
    lines.append("---------- METADATA ----------")
    for key, val in metadata.items():
        lines.append(f"{key}: {val}")
    lines.append("")

    # CORRELATION
    lines.append("------ CORRELATION ANALYSIS ------")
    for key, val in correlation.items():
        lines.append(f"{key}: {val}")
    lines.append("")

    # RISK
    lines.append("---------- RISK SCORE ----------")
    lines.append(f"Risk Score: {risk.get('risk_score')}")
    lines.append("Details:")
    for detail in risk.get("details", []):
        lines.append(f"- {detail}")
    lines.append("")

    lines.append("====================================")
    lines.append("        END OF REPORT")
    lines.append("====================================")

    return "\n".join(lines)
