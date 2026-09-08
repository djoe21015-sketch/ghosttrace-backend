import os
from datetime import datetime
from .html_builder import build_html
from .pdf_builder import build_pdf_report

def export_report(data: dict, output_dir: str = "reports"):
    """
    Build both HTML and PDF reports from full OSINT + AI data.
    """

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Timestamped filenames
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    html_path = os.path.join(output_dir, f"ghosttrace_report_{timestamp}.html")
    pdf_path = os.path.join(output_dir, f"ghosttrace_report_{timestamp}.pdf")

    # Build HTML
    html_content = build_html(data)  
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Build PDF
    pdf_result = build_pdf_report(html_content, pdf_path)

    return {
        "status": "ok",
        "html": html_path,
        "pdf": pdf_path,
        "pdf_status": pdf_result
    }
