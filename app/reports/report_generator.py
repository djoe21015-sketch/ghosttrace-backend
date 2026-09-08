def generate_report(target_id: int, metadata: dict, correlations: dict, risk: dict):
    lines = []
    lines.append(f"GhostTrace Report for Target {target_id}")
    lines.append("=" * 50)
    lines.append("")

    # Metadata section
    lines.append("Metadata:")
    for key, value in metadata.items():
        lines.append(f"  {key}: {value}")
    lines.append("")

    # Correlation section
    lines.append("Correlations:")
    for key, value in correlations.items():
        lines.append(f"  {key}: {value}")
    lines.append("")

    # Risk section
    lines.append("Risk Assessment:")
    lines.append(f"  Risk Score: {risk.get('risk_score')}")
    lines.append("  Details:")
    for detail in risk.get("risk_details", []):
        lines.append(f"    - {detail}")
    lines.append("")

    return "\n".join(lines)
