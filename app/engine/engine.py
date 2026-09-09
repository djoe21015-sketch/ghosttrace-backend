from app.core.router import route_scan
from app.core.storage import save_raw, save_intel, save_report
from app.analyzers.metadata_analyzer import analyze_metadata
from app.analyzers.correlation_analyzer import correlate
from app.analyzers.risk_analyzer import calculate_risk
from app.reports.report_generator import generate_report

# Import scrapers
from app.scrapers.domain_scraper import scrape_domain
from app.scrapers.email_scraper import scrape_email
from app.scrapers.phone_scraper import scrape_phone
from app.scrapers.ip_scraper import scrape_ip
from app.scrapers.username_scraper import scrape_username

SCRAPER_MAP = {
    "domain_scraper": scrape_domain,
    "email_scraper": scrape_email,
    "phone_scraper": scrape_phone,
    "ip_scraper": scrape_ip,
    "username_scraper": scrape_username,
    "basic_scraper": lambda x: {"note": "No scraper available for this type"}
}

# ⭐ FIX: AutoTarget class so engine NEVER crashes
class AutoTarget:
    def __init__(self, value="auto-generated", target_type="auto"):
        self.id = "auto-000001"
        self.value = value
        self.target_type = target_type

def run_engine(target=None):
    # ⭐ FIX: If backend or auto-runner sends None, create a valid target object
    if target is None:
        target = AutoTarget()

    target_id = target.id
    target_value = target.value
    target_type = target.target_type.lower()

    # Determine which scraper to use
    scraper_key = route_scan(target)[0]
    scraper = SCRAPER_MAP.get(scraper_key)

    # Run scraper
    raw = scraper(target_value)

    # Save raw data
    raw_path = save_raw(target_id, raw)

    # Run analyzers
    metadata = analyze_metadata(raw)
    correlation = correlate(raw, metadata)
    risk = calculate_risk(raw, metadata, correlation)

    # Save intelligence
    intel_text = f"Metadata: {metadata}\nCorrelation: {correlation}\nRisk: {risk}"
    intel_path = save_intel(target_id, "analysis", intel_text)

    # Generate report
    report_text = generate_report(target_id, raw, metadata, correlation, risk)
    report_path = save_report(target_id, report_text)

    # Final unified result
    return {
        "target_id": target_id,
        "raw": raw,
        "metadata": metadata,
        "correlation": correlation,
        "risk": risk,
        "raw_path": raw_path,
        "intel_path": intel_path,
        "report_path": report_path,
        "report_text": report_text
    }
