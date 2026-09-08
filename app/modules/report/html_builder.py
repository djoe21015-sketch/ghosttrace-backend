import datetime

REPORT_TITLE = "GhostTrace MAX — Intelligence Report"

def build_html(results):
    """
    Build full GhostTrace MAX HTML report.
    Compatible with existing pdf_builder.py and export.py.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Risk gauge color
    risk = results.get("risk", 0)
    if risk < 30:
        risk_color = "#4CAF50"  # green
    elif risk < 70:
        risk_color = "#FFC107"  # yellow
    else:
        risk_color = "#F44336"  # red

    screenshot_path = results.get("screenshot_path")

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{REPORT_TITLE}</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
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

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}

            table, th, td {{
                border: 1px solid #ccc;
            }}

            th {{
                background: #eee;
                padding: 8px;
            }}

            td {{
                padding: 8px;
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

            .screenshot {{
                text-align: center;
                margin-top: 20px;
            }}

            .screenshot img {{
                max-width: 100%;
                border: 1px solid #ccc;
                border-radius: 10px;
            }}
        </style>
    </head>

    <body>
        <div class="container">

            <h1>{REPORT_TITLE}</h1>
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Target:</strong> {results.get("target", "Unknown")}</p>

            <div class="section">
                <h2>Executive Summary</h2>
                <div class="risk-gauge">{risk}</div>
                <p>Overall risk score based on DNS security, open ports, subdomains, breaches, and threat intelligence.</p>
            </div>

            <div class="section">
                <h2>WHOIS Information</h2>
                <pre>{results.get("whois")}</pre>
            </div>

            <div class="section">
                <h2>SSL/TLS Information</h2>
                <pre>{results.get("ssl")}</pre>
            </div>

            <div class="section">
                <h2>HTTP Probe</h2>
                <pre>{results.get("http")}</pre>
            </div>

            <div class="section">
                <h2>Screenshot</h2>
                <div class="screenshot">
                    {"<img src='" + screenshot_path + "'>" if screenshot_path else "<p>No screenshot available</p>"}
                </div>
            </div>

            <div class="section">
                <h2>Tech Stack</h2>
                <pre>{results.get("techstack")}</pre>
            </div>

            <div class="section">
                <h2>DNS Security</h2>
                <pre>{results.get("dns_security")}</pre>
            </div>

            <div class="section">
                <h2>Open Ports</h2>
                <pre>{results.get("open_ports")}</pre>
            </div>

            <div class="section">
                <h2>Subdomains</h2>
                <pre>{results.get("subdomains")}</pre>
            </div>

            <div class="section">
                <h2>Breach Intelligence</h2>
                <pre>{results.get("breaches")}</pre>
            </div>

            <div class="section">
                <h2>Dark Web Exposure</h2>
                <pre>{results.get("darkweb")}</pre>
            </div>

            <div class="section">
                <h2>CVE Lookup</h2>
                <pre>{results.get("cves")}</pre>
            </div>

            <div class="section">
                <h2>Attack Path Analysis</h2>
                <pre>{results.get("attack_paths")}</pre>
            </div>

            <div class="section">
                <h2>Recommendations</h2>
                <pre>{results.get("recommendations")}</pre>
            </div>

        </div>
    </body>
    </html>
    """

    return html
