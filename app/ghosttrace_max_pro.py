import os
import json
import sqlite3
import datetime
import threading
import time
import requests
import socket
import dns.resolver
from bs4 import BeautifulSoup
import whois

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse

# ============================================================
# CONFIG / DB
# ============================================================

DB_PATH = os.path.join(os.path.dirname(__file__), "ghosttrace.db")

def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            risk INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        );
    """)

    conn.commit()
    conn.close()

def save_scan(target, risk, modules):
    conn = db_conn()
    cur = conn.cursor()

    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        "INSERT INTO scans (target, risk, created_at) VALUES (?, ?, ?)",
        (target, risk, created_at)
    )
    scan_id = cur.lastrowid

    for name, data in modules.items():
        cur.execute(
            "INSERT INTO modules (scan_id, name, data) VALUES (?, ?, ?)",
            (scan_id, name, json.dumps(data, default=str))
        )

    conn.commit()
    conn.close()
    return scan_id

def list_scans(limit=50):
    conn = db_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, target, risk, created_at FROM scans ORDER ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "target": r["target"],
            "risk": r["risk"],
            "created_at": r["created_at"]
        }
        for r in rows
    ]

def get_scan(scan_id: int):
    conn = db_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, target, risk, created_at FROM scans WHERE id = ?", (scan_id,))
    scan = cur.fetchone()

    if not scan:
        conn.close()
        return None

    cur.execute("SELECT name, data FROM modules WHERE scan_id = ?", (scan_id,))
    modules = cur.fetchall()
    conn.close()

    mod_data = {}
    for m in modules:
        mod_data[m["name"]] = json.loads(m["data"])

    return {
        "id": scan["id"],
        "target": scan["target"],
        "risk": scan["risk"],
        "created_at": scan["created_at"],
        "modules": mod_data
    }

# ============================================================
# BREACH CHECK
# ============================================================

def check_domain_breaches(domain: str):
    try:
        url = f"https://haveibeenpwned.com/api/v3/breaches?domain={domain}"
        response = requests.get(url, timeout=10, headers={"User-Agent": "GhostTrace-OSINT"})

        if response.status_code == 404:
            return {"domain": domain, "breaches": [], "count": 0}

        if response.status_code != 200:
            return {"domain": domain, "error": f"HIBP returned {response.status_code}"}

        breaches = response.json()
        return {"domain": domain, "breaches": breaches, "count": len(breaches)}

    except Exception as e:
        return {"domain": domain, "error": str(e)}

def check_email_breaches(email: str, api_key: str = None):
    if api_key is None:
        return {"email": email, "error": "No HIBP API key provided"}

    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"User-Agent": "GhostTrace-OSINT", "hibp-api-key": api_key}
        response = requests.get(url, timeout=10, headers=headers)

        if response.status_code == 404:
            return {"email": email, "breaches": [], "count": 0}

        if response.status_code != 200:
            return {"email": email, "error": f"HIBP returned {response.status_code}"}

        breaches = response.json()
        return {"email": email, "breaches": breaches, "count": len(breaches)}

    except Exception as e:
        return {"email": email, "error": str(e)}

def run_breach_check(target: str, api_key: str = None):
    if "@" in target:
        return check_email_breaches(target, api_key)
    else:
        return check_domain_breaches(target)

# ============================================================
# DARK WEB
# ============================================================

DARKWEB_SEARCH_ENGINES = [
    "https://ahmia.fi/search/?q={}",
    "https://onionlandsearchengine.com/search?q={}",
]

def search_darkweb(query: str):
    results = []
    for engine in DARKWEB_SEARCH_ENGINES:
        try:
            url = engine.format(query)
            response = requests.get(url, timeout=10, headers={"User-Agent": "GhostTrace-OSINT"})
            if response.status_code == 200:
                text = response.text
                results.append({
                    "engine": engine,
                    "status": "ok",
                    "content_length": len(text),
                    "raw_snippet": text[:500],
                    "mentions_domain": query.lower() in text.lower(),
                    "mentions_email": "@" in query and query.lower() in text.lower()
                })
            else:
                results.append({"engine": engine, "status": f"error {response.status_code}"})
        except Exception as e:
            results.append({"engine": engine, "status": "exception", "error": str(e)})
    return results

def run_darkweb(target: str):
    sr = search_darkweb(target)
    return {
        "target": target,
        "search_results": sr,
        "summary": {
            "domain_mentions": sum(1 for r in sr if r.get("mentions_domain")),
            "email_mentions": sum(1 for r in sr if r.get("mentions_email")),
        }
    }

# ============================================================
# DNS
# ============================================================

def run_dns_scan(domain):
    results = {"domain": domain, "records": {}, "risk": 0}
    for record_type in ["A", "MX", "NS", "TXT"]:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            results["records"][record_type] = [str(rdata) for rdata in answers]
        except Exception:
            results["records"][record_type] = []

    txt_records = results["records"].get("TXT", [])
    if not any("spf" in r.lower() for r in txt_records):
        results["risk"] += 20
    if not any("dmarc" in r.lower() for r in txt_records):
        results["risk"] += 20
    if not results["records"].get("MX"):
        results["risk"] += 10

    return results

# ============================================================
# IPINFO
# ============================================================

IPINFO_LITE_TOKEN = "ee906001ea5a90"

def run_ipinfo(domain: str):
    try:
        ip = socket.gethostbyname(domain)
    except Exception:
        return {"error": "Could not resolve domain to IP"}

    url = f"https://ipinfo.io/{ip}?token={IPINFO_LITE_TOKEN}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"ipinfo.io returned status {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# PORT SCAN
# ============================================================

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    587: "SMTP-SSL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-ALT",
    8443: "HTTPS-ALT"
}

def grab_banner(domain, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((domain, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024).decode(errors="ignore")
        sock.close()
        return banner.strip()
    except Exception:
        return None

def run_port_scan(domain):
    results = {"domain": domain, "open_ports": [], "error": None}
    try:
        for port, service in COMMON_PORTS.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                result = sock.connect_ex((domain, port))
                if result == 0:
                    banner = grab_banner(domain, port)
                    results["open_ports"].append({
                        "port": port,
                        "service": service,
                        "banner": banner
                    })
            except Exception:
                pass
            finally:
                sock.close()
    except Exception as e:
        results["error"] = str(e)
    return results

# ============================================================
# SOCIAL FOOTPRINT
# ============================================================

SOCIAL_PLATFORMS = {
    "twitter": "https://x.com/{}",
    "instagram": "https://www.instagram.com/{}/",
    "facebook": "https://www.facebook.com/{}",
    "tiktok": "https://www.tiktok.com/@{}",
    "github": "https://github.com/{}",
    "reddit": "https://www.reddit.com/user/{}",
    "linkedin": "https://www.linkedin.com/in/{}",
    "pinterest": "https://www.pinterest.com/{}/",
    "tumblr": "https://{}.tumblr.com",
    "medium": "https://medium.com/@{}",
    "youtube": "https://www.youtube.com/@{}"
}

def check_profile(url: str):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "GhostTrace-OSINT"})
        if response.status_code in [200, 301, 302]:
            return True
        return False
    except Exception:
        return False

def run_social_footprint(username: str):
    results = {}
    for platform, url_template in SOCIAL_PLATFORMS.items():
        url = url_template.format(username)
        exists = check_profile(url)
        results[platform] = {"exists": exists, "url": url if exists else None}
    return {
        "username": username,
        "profiles": results,
        "total_found": sum(1 for p in results.values() if p["exists"])
    }

# ============================================================
# SUBDOMAINS
# ============================================================

def run_subdomain_enum(domain):
    results = {"domain": domain, "subdomains": [], "error": None}
    common_subdomains = [
        "www", "mail", "dev", "api", "test",
        "blog", "shop", "ftp", "cpanel", "admin"
    ]
    try:
        for sub in common_subdomains:
            subdomain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(subdomain)
                results["subdomains"].append(subdomain)
            except Exception:
                pass
    except Exception as e:
        results["error"] = str(e)
    return results

# ============================================================
# TECHSTACK
# ============================================================

def wappalyzer_scan(url: str):
    try:
        API_KEY = None
        if API_KEY is None:
            return {"warning": "Wappalyzer API key not configured (free mode)"}
        headers = {"x-api-key": API_KEY}
        response = requests.get(f"https://api.wappalyzer.com/v2/lookup/?url={url}", headers=headers)
        if response.status_code != 200:
            return {"error": f"Wappalyzer returned {response.status_code}"}
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def fallback_scan(url: str):
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        headers = response.headers
        soup = BeautifulSoup(html, "html.parser")

        tech = {
            "server": headers.get("Server"),
            "powered_by": headers.get("X-Powered-By"),
            "frameworks": [],
            "cms": [],
            "javascript_libs": [],
            "cdn": [],
            "meta_generator": None
        }

        generator = soup.find("meta", attrs={"name": "generator"})
        if generator and generator.get("content"):
            tech["meta_generator"] = generator.get("content")
            gen = generator.get("content").lower()
            if "wordpress" in gen:
                tech["cms"].append("WordPress")
            if "joomla" in gen:
                tech["cms"].append("Joomla")
            if "drupal" in gen:
                tech["cms"].append("Drupal")

        scripts = soup.find_all("script")
        for script in scripts:
            src = script.get("src", "").lower()
            if "jquery" in src:
                tech["javascript_libs"].append("jQuery")
            if "react" in src:
                tech["javascript_libs"].append("React")
            if "vue" in src:
                tech["javascript_libs"].append("Vue.js")
            if "angular" in src:
                tech["javascript_libs"].append("Angular")
            if "bootstrap" in src:
                tech["javascript_libs"].append("Bootstrap JS")
            if "tailwind" in src:
                tech["javascript_libs"].append("Tailwind CSS")
            if "cloudflare" in src:
                tech["cdn"].append("Cloudflare CDN")
            if "cdn.jsdelivr" in src:
                tech["cdn"].append("jsDelivr CDN")
            if "cdnjs" in src:
                tech["cdn"].append("cdnjs CDN")

        if "wp-content" in html.lower():
            tech["cms"].append("WordPress")
        if "drupal-settings-json" in html.lower():
            tech["cms"].append("Drupal")
        if "__next" in html.lower():
            tech["frameworks"].append("Next.js")
        if "nuxt" in html.lower():
            tech["frameworks"].append("Nuxt.js")
        if "laravel" in html.lower():
            tech["frameworks"].append("Laravel")
        if "django" in html.lower():
            tech["frameworks"].append("Django")

        return tech
    except Exception as e:
        return {"error": str(e)}

def run_techstack(domain: str):
    url = f"http://{domain}"
    return {
        "domain": domain,
        "wappalyzer": wappalyzer_scan(url),
        "fallback": fallback_scan(url)
    }

# ============================================================
# THREAT INTEL
# ============================================================

def abuseipdb_lookup(ip: str):
    try:
        url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}"
        response = requests.get(url, timeout=10)
        return {"ip": ip, "status": response.status_code, "note": "Free AbuseIPDB mode — limited data"}
    except Exception as e:
        return {"error": str(e)}

def otx_lookup(ip: str):
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": f"OTX returned {response.status_code}"}
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def ipapi_lookup(ip: str):
    try:
        url = f"https://ipapi.co/{ip}/json/"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def run_threat_intel(ip: str):
    return {
        "ip": ip,
        "abuseipdb": abuseipdb_lookup(ip),
        "otx": otx_lookup(ip),
        "ipapi": ipapi_lookup(ip)
    }

# ============================================================
# WHOIS
# ============================================================

def run_whois(domain: str):
    try:
        data = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": data.registrar,
            "creation_date": str(data.creation_date),
            "expiration_date": str(data.expiration_date),
            "updated_date": str(data.updated_date),
            "status": data.status,
            "nameservers": data.name_servers,
            "emails": data.emails,
            "dnssec": data.dnssec,
            "abuse_contact": data.get("abuse_email", None),
            "raw": str(data)
        }
    except Exception as e:
        return {"error": str(e), "domain": domain}

# ============================================================
# RISK SCORING
# ============================================================

def calculate_risk(results):
    score = 0
    bc = results.get("breach_check", {})
    if isinstance(bc, dict) and bc.get("count", 0) > 0:
        score += 25
    dw = results.get("darkweb", {})
    if isinstance(dw, dict):
        summary = dw.get("summary", {})
        if summary.get("domain_mentions", 0) > 0:
            score += 25
    dns = results.get("dns", {})
    if isinstance(dns, dict) and dns.get("risk", 0) > 0:
        score += 15
    ports = results.get("ports", {})
    if isinstance(ports, dict) and len(ports.get("open_ports", [])) > 0:
        score += 20
    ti = results.get("threat_intel", {})
    if isinstance(ti, dict):
        abuse = ti.get("abuseipdb", {})
        if abuse.get("status", 0) == 200:
            score += 15
    return max(0, min(100, score))

# ============================================================
# HTML REPORT
# ============================================================

def build_section(title, content):
    return f"""
    <div class="section">
        <h2>{title}</h2>
        <pre>{json.dumps(content, indent=4, default=str)}</pre>
    </div>
    """

def build_html(results):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk = results.get("risk", 0)
    if risk < 30:
        risk_color = "#4CAF50"
    elif risk < 70:
        risk_color = "#FFC107"
    else:
        risk_color = "#F44336"

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>GhostTrace MAX — Intelligence Report</title>
        <style>
            body {{
                font-family: Arial;
                background: #f5f5f5;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 90%;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
            }}
            h1 {{
                text-align: center;
                color: #222;
            }}
            h2 {{
                color: #333;
                border-bottom: 2px solid #ddd;
                padding-bottom: 5px;
            }}
            .risk-gauge {{
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background: {risk_color};
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 32px;
                margin: auto;
            }}
            .section {{
                margin-top: 30px;
            }}
            pre {{
                background: #eee;
                padding: 10px;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>GhostTrace MAX — Intelligence Report</h1>
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Target:</strong> {results.get("target")}</p>
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="risk-gauge">{risk}</div>
            </div>
            {build_section("WHOIS", results.get("whois"))}
            {build_section("IP Intelligence", results.get("ipinfo"))}
            {build_section("DNS Security", results.get("dns"))}
            {build_section("Open Ports", results.get("ports"))}
            {build_section("Subdomains", results.get("subdomains"))}
            {build_section("Social Footprint", results.get("social_footprint"))}
            {build_section("Tech Stack", results.get("techstack"))}
            {build_section("Breach Intelligence", results.get("breach_check"))}
            {build_section("Dark Web Exposure", results.get("darkweb"))}
            {build_section("Threat Intelligence", results.get("threat_intel"))}
        </div>
    </body>
    </html>
    """
    return html

# ============================================================
# FULL SCAN PIPELINE
# ============================================================

def run_full_scan(target: str):
    whois_data = run_whois(target)
    ipinfo_data = run_ipinfo(target)
    dns_data = run_dns_scan(target)
    ports_data = run_port_scan(target)
    subdomains_data = run_subdomain_enum(target)
    social_data = run_social_footprint(target)
    techstack_data = run_techstack(target)

    ip_for_threat = None
    if isinstance(ipinfo_data, dict) and ipinfo_data.get("ip"):
        ip_for_threat = ipinfo_data["ip"]
    else:
        try:
            ip_for_threat = socket.gethostbyname(target)
        except Exception:
            ip_for_threat = None

    threat_data = run_threat_intel(ip_for_threat) if ip_for_threat else {"error": "Could not resolve IP for threat intel"}
    breach_data = run_breach_check(target)
    darkweb_data = run_darkweb(target)

    results = {
        "target": target,
        "whois": whois_data,
        "ipinfo": ipinfo_data,
        "dns": dns_data,
        "ports": ports_data,
        "subdomains": subdomains_data,
        "social_footprint": social_data,
        "techstack": techstack_data,
        "breach_check": breach_data,
        "darkweb": darkweb_data,
        "threat_intel": threat_data,
    }

    results["risk"] = calculate_risk(results)
    return results

# ============================================================
# JSON / PDF EXPORT
# ============================================================

def export_json(scan_id: int):
    data = get_scan(scan_id)
    if not data:
        return None
    out = os.path.join(os.path.dirname(__file__), f"scan_{scan_id}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str)
    return out

def export_pdf(scan_id: int):
    try:
        import pdfkit
    except ImportError:
        return None

    data = get_scan(scan_id)
    if not data:
        return None

    html = build_html({
        "target": data["target"],
        "risk": data["risk"],
        "whois": data["modules"].get("whois"),
        "ipinfo": data["modules"].get("ipinfo"),
        "dns": data["modules"].get("dns"),
        "ports": data["modules"].get("ports"),
        "subdomains": data["modules"].get("subdomains"),
        "social_footprint": data["modules"].get("social_footprint"),
        "techstack": data["modules"].get("techstack"),
        "breach_check": data["modules"].get("breach_check"),
        "darkweb": data["modules"].get("darkweb"),
        "threat_intel": data["modules"].get("threat_intel"),
    })

    out = os.path.join(os.path.dirname(__file__), f"scan_{scan_id}.pdf")
    pdfkit.from_string(html, out)
    return out

# ============================================================
# SCHEDULER (AUTO SCAN)
# ============================================================

SCHEDULED_TARGETS = []

def scheduler_loop(interval_minutes: int = 60):
    while True:
        if SCHEDULED_TARGETS:
            for t in SCHEDULED_TARGETS:
                results = run_full_scan(t)
                modules = {
                    "whois": results["whois"],
                    "ipinfo": results["ipinfo"],
                    "dns": results["dns"],
                    "ports": results["ports"],
                    "subdomains": results["subdomains"],
                    "social_footprint": results["social_footprint"],
                    "techstack": results["techstack"],
                    "breach_check": results["breach_check"],
                    "darkweb": results["darkweb"],
                    "threat_intel": results["threat_intel"],
                }
                scan_id = save_scan(results["target"], results["risk"], modules)
                print(f"[SCHEDULER] Auto scan #{scan_id} for {t}")
        time.sleep(interval_minutes * 60)

def start_scheduler(interval_minutes: int = 60):
    th = threading.Thread(target=scheduler_loop, args=(interval_minutes,), daemon=True)
    th.start()

# ============================================================
# FASTAPI API
# ============================================================

app = FastAPI(title="GhostTrace MAX API")

@app.on_event("startup")
def startup_event():
    init_db()
    start_scheduler(interval_minutes=60)

@app.get("/scan")
def api_scan(target: str):
    results = run_full_scan(target)
    modules = {
        "whois": results["whois"],
        "ipinfo": results["ipinfo"],
        "dns": results["dns"],
        "ports": results["ports"],
        "subdomains": results["subdomains"],
        "social_footprint": results["social_footprint"],
        "techstack": results["techstack"],
        "breach_check": results["breach_check"],
        "darkweb": results["darkweb"],
        "threat_intel": results["threat_intel"],
    }
    scan_id = save_scan(results["target"], results["risk"], modules)
    return JSONResponse({"scan_id": scan_id, "results": results})

@app.get("/scans")
def api_list_scans(limit: int = 50):
    return JSONResponse(list_scans(limit=limit))

@app.get("/scan/{scan_id}")
def api_get_scan(scan_id: int):
    data = get_scan(scan_id)
    if not data:
        return JSONResponse({"error": "Scan not found"}, status_code=404)
    return JSONResponse(data)

@app.get("/scan/{scan_id}/json")
def api_get_scan_json(scan_id: int):
    path = export_json(scan_id)
    if not path:
        return JSONResponse({"error": "Scan not found or export failed"}, status_code=404)
    return FileResponse(path, media_type="application/json", filename=os.path.basename(path))

@app.get("/scan/{scan_id}/pdf")
def api_get_scan_pdf(scan_id: int):
    path = export_pdf(scan_id)
    if not path:
        return JSONResponse({"error": "Scan not found or PDF export failed"}, status_code=404)
    return FileResponse(path, media_type="application/pdf", filename=os.path.basename(path))

@app.post("/schedule")
def api_schedule_target(target: str):
    if target not in SCHEDULED_TARGETS:
        SCHEDULED_TARGETS.append(target)
    return JSONResponse({"scheduled": SCHEDULED_TARGETS})

# ============================================================
# CLI MAIN
# ============================================================

def cli_main():
    init_db()
    target = input("Enter target domain or email: ").strip()
    results = run_full_scan(target)
    modules = {
        "whois": results["whois"],
        "ipinfo": results["ipinfo"],
        "dns": results["dns"],
        "ports": results["ports"],
        "subdomains": results["subdomains"],
        "social_footprint": results["social_footprint"],
        "techstack": results["techstack"],
        "breach_check": results["breach_check"],
        "darkweb": results["darkweb"],
        "threat_intel": results["threat_intel"],
    }
    scan_id = save_scan(results["target"], results["risk"], modules)
    print(f"Saved scan #{scan_id}")
    html = build_html(results)
    out = os.path.join(os.path.dirname(__file__), f"report_{scan_id}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report written: {out}")
    print("\nRecent scans:")
    for s in list_scans():
        print(s)

if __name__ == "__main__":
    # CLI mode
    cli_main()
    # To run API instead:
    # import uvicorn
    # uvicorn.run("ghosttrace_max_pro:app", host="0.0.0.0", port=8000, reload=True)
