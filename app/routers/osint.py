from fastapi import APIRouter
from app.modules.recon.whois import run_whois
from app.modules.recon.dns import run_dns_scan
from app.modules.recon.subdomains import run_subdomain_enum as run_subdomains
from app.modules.recon.ipinfo import run_ipinfo
from app.modules.recon.darkweb import run_darkweb

from app.modules.ai.summaries import summarize_recon
from app.modules.ai.risk_score import generate_risk_score
from app.modules.ai.recommendations import generate_recommendations
from app.modules.ai.correlation import correlate

from app.modules.report.export import export_report

# ============================
# JS TECHSTACK ENGINE RUNNER
# ============================

import subprocess
import json
import os

def run_techstack_engine_js(target):
    js_path = os.path.join(os.path.dirname(__file__), "..", "models", "techstack_engine.js")
    js_path = os.path.abspath(js_path)

    result = subprocess.run(
        ["node", js_path],
        input=json.dumps({"domain": target}),
        text=True,
        capture_output=True
    )

    try:
        return json.loads(result.stdout)
    except Exception as e:
        return {
            "error": "techstack_engine_js_failed",
            "exception": str(e),
            "stdout": result.stdout,
            "stderr": result.stderr
        }

router = APIRouter(prefix="/osint", tags=["osint"])

# ============================
# /recon/{target}
# ============================

@router.get("/recon/{target}")
def recon(target: str):
    whois = run_whois(target)
    dns = run_dns_scan(target)
    subs = run_subdomains(target)
    ipinfo = run_ipinfo(target)
    tech = run_techstack_engine_js(target)

    recon_data = {
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech
    }

    summary = summarize_recon(recon_data)

    return {
        "recon": recon_data,
        "summary": summary
    }

# ============================
# /threat/{target}
# ============================

@router.get("/threat/{target}")
def threat_intel(target: str):
    darkweb = run_darkweb(target)
    summary = summarize_recon({"darkweb": darkweb})

    return {
        "darkweb": darkweb,
        "summary": summary
    }

# ============================
# /social/{target}
# ============================

@router.get("/social/{target}")
def social_footprint(target: str):
    try:
        from app.modules.social.enum import enumerate_social
    except ImportError:
        return {"error": "Social module missing"}

    social_data = enumerate_social(target)
    summary = summarize_recon({"social": social_data})

    return {
        "social": social_data,
        "summary": summary
    }

# ============================
# /darkweb/{target}
# ============================

@router.get("/darkweb/{target}")
def darkweb_exposure(target: str):
    darkweb_data = run_darkweb(target)
    summary = summarize_recon({"darkweb": darkweb_data})

    return {
        "darkweb": darkweb_data,
        "summary": summary
    }

# ============================
# /summary/{target}
# ============================

@router.get("/summary/{target}")
def unified_summary(target: str):
    whois = run_whois(target)
    dns = run_dns_scan(target)
    subs = run_subdomains(target)
    ipinfo = run_ipinfo(target)
    tech = run_techstack_engine_js(target)
    darkweb = run_darkweb(target)

    try:
        from app.modules.social.enum import enumerate_social
        social = enumerate_social(target)
    except ImportError:
        social = {"error": "Social module missing"}

    all_data = {
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    }

    summary = summarize_recon(all_data)

    return {
        "data": all_data,
        "summary": summary
    }

# ============================
# /risk/{target}
# ============================

@router.get("/risk/{target}")
def risk_score(target: str):
    whois = run_whois(target)
    dns = run_dns_scan(target)
    subs = run_subdomains(target)
    ipinfo = run_ipinfo(target)
    tech = run_techstack_engine_js(target)
    darkweb = run_darkweb(target)

    try:
        from app.modules.social.enum import enumerate_social
        social = enumerate_social(target)
    except ImportError:
        social = {"error": "Social module missing"}

    all_data = {
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    }

    score = generate_risk_score(all_data)

    return {
        "risk_score": score,
        "data_used": all_data
    }

# ============================
# /recommendations/{target}
# ============================

@router.get("/recommendations/{target}")
def recommendations(target: str):
    whois = run_whois(target)
    dns = run_dns_scan(target)
    subs = run_subdomains(target)
    ipinfo = run_ipinfo(target)
    tech = run_techstack_engine_js(target)
    darkweb = run_darkweb(target)

    try:
        from app.modules.social.enum import enumerate_social
        social = enumerate_social(target)
    except ImportError:
        social = {"error": "Social module missing"}

    all_data = {
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    }

    recs = generate_recommendations(all_data)

    return {
        "recommendations": recs,
        "data_used": all_data
    }

# ============================
# /correlation/{target}
# ============================

@router.get("/correlation/{target}")
def correlation(target: str):
    whois = run_whois(target)
    dns = run_dns_scan(target)
    subs = run_subdomains(target)
    ipinfo = run_ipinfo(target)
    tech = run_techstack_engine_js(target)
    darkweb = run_darkweb(target)

    try:
        from app.modules.social.enum import enumerate_social
        social = enumerate_social(target)
    except ImportError:
        social = {"error": "Social module missing"}

    all_data = {
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    }

    correlations = correlate(all_data)

    return {
        "correlations": correlations,
        "data_used": all_data
    }

# ============================
# /report/{target}
# ============================

@router.get("/report/{target}")
def full_report(target: str):
    whois = run_whois(target)
    dns = run_dns_scan(target)
    subs = run_subdomains(target)
    ipinfo = run_ipinfo(target)
    tech = run_techstack_engine_js(target)
    darkweb = run_darkweb(target)

    try:
        from app.modules.social.enum import enumerate_social
        social = enumerate_social(target)
    except ImportError:
        social = {"error": "Social module missing"}

    summary = summarize_recon({
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    })

    risk = generate_risk_score({
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    })

    recs = generate_recommendations({
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    })

    correlations = correlate({
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social
    })

    full_data = {
        "whois": whois,
        "dns": dns,
        "subdomains": subs,
        "ipinfo": ipinfo,
        "techstack": tech,
        "darkweb": darkweb,
        "social": social,
        "summary": summary,
        "risk": risk,
        "recommendations": recs,
        "correlations": correlations
    }

    report_file = export_report(target, full_data)

    return {
        "target": target,
        "report_file": report_file,
        "data": full_data
    }
