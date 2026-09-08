from weasyprint import HTML

def build_pdf_report(html_content: str, output_path: str):
    """
    Convert HTML report into a PDF file using WeasyPrint.
    """

    try:
        HTML(string=html_content).write_pdf(output_path)

        return {
            "status": "ok",
            "output": output_path
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
