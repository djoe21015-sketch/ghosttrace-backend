from app.modules.recon.ipinfo import run_ipinfo
from app.modules.recon.techstack import run_techstack
from app.modules.recon.dns import run_dns_scan
from app.modules.recon.ports import run_port_scan
from app.modules.recon.subdomains import run_subdomain_enum

# REMOVE all modules that don't exist:
# - social
# - darkweb
# - threat/otx
# - anything else missing

def run_full_scan(target):
    results = {}

    # IPInfo
    try:
        results["ipinfo"] = run_ipinfo(target)
    except Exception as e:
        results["ipinfo"] = {"error": str(e)}

    # Tech Stack
    try:
        results["techstack"] = run_techstack(target)
    except Exception as e:
        results["techstack"] = {"error": str(e)}

    # DNS Security
    try:
        results["dns_security"] = run_dns_scan(target)
    except Exception as e:
        results["dns_security"] = {"error": str(e)}

    # Open Ports
    try:
        results["open_ports"] = run_port_scan(target)
    except Exception as e:
        results["open_ports"] = {"error": str(e)}

    # Subdomains
    try:
        results["subdomains"] = run_subdomain_enum(target)
    except Exception as e:
        results["subdomains"] = {"error": str(e)}

    # Executive Summary (simple auto‑generated)
    results["executive_summary"] = {
        "domain": target,
        "scanned_at": "now",
        "overall_risk_score": results["dns_security"].get("risk", "N/A"),
        "key_findings": [
            "Tech stack identified",
            "DNS security evaluated",
            "Open ports scanned",
            "Subdomains enumerated"
        ]
    }

    # Screenshot placeholder
    results["screenshot_path"] = "report/screenshot.png"

    # Risk score for DB
    results["risk"] = results["dns_security"].get("risk", 0)

    return results, "report/report_data.json"
