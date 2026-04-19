#!/usr/bin/env python3
"""Generate PDF for AWS Prerequisites & IAM Setup from aws-prerequisites.md"""

import subprocess
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(SCRIPT_DIR, "aws-prerequisites.md")
HTML_FILE = os.path.join(SCRIPT_DIR, "aws-prerequisites-pdf.html")
PDF_FILE = os.path.join(SCRIPT_DIR, "AWS-Prerequisites.pdf")

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AWS Prerequisites & IAM Setup</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 2cm 2.5cm 2cm;
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
        }}
        @page:first {{ @bottom-center {{ content: none; }} }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
        }}
        
        .title-page {{
            text-align: center;
            page-break-after: always;
            padding-top: 180px;
        }}
        .title-page h1 {{
            font-size: 28pt;
            color: #1a365d;
            margin-bottom: 15px;
            border: none;
        }}
        .title-page .subtitle {{
            font-size: 14pt;
            color: #4a5568;
            margin-bottom: 50px;
        }}
        .title-page .date {{ font-size: 12pt; color: #a0aec0; }}
        
        a {{ color: #2b6cb0; text-decoration: none; }}
        h1 {{ font-size: 22pt; color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 8px; margin-top: 35px; page-break-after: avoid; }}
        h2 {{ font-size: 16pt; color: #2c5282; border-bottom: 1px solid #bee3f8; padding-bottom: 5px; margin-top: 25px; page-break-after: avoid; }}
        h3 {{ font-size: 13pt; color: #2b6cb0; margin-top: 20px; page-break-after: avoid; }}
        h4 {{ font-size: 11pt; color: #3182ce; margin-top: 15px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 10pt; }}
        th {{ background-color: #ebf8ff; color: #2c5282; font-weight: bold; padding: 10px 8px; text-align: left; border: 1px solid #bee3f8; }}
        td {{ padding: 8px; border: 1px solid #e2e8f0; vertical-align: top; }}
        tr:nth-child(even) {{ background-color: #f7fafc; }}
        
        pre {{
            background-color: #1a202c;
            color: #e2e8f0;
            border-radius: 6px;
            padding: 14px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        code {{ font-family: 'Consolas', 'Monaco', monospace; font-size: 9pt; background-color: #edf2f7; padding: 2px 5px; border-radius: 3px; }}
        pre code {{ background: none; padding: 0; color: #e2e8f0; }}
        
        ul, ol {{ margin: 10px 0; padding-left: 25px; }}
        li {{ margin-bottom: 5px; }}
        hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 25px 0; }}
    </style>
</head>
<body>

<div class="title-page">
    <h1>AWS Prerequisites & IAM Setup</h1>
    <div class="subtitle">Totogi Kubernetes Operator</div>
    <div class="date">''' + datetime.now().strftime("%B %Y") + '''</div>
</div>

'''  # BODY inserted below


def main():
    os.chdir(SCRIPT_DIR)
    if not os.path.exists(MD_FILE):
        print(f"Error: {MD_FILE} not found")
        return 1

    print(f"Converting {MD_FILE} to HTML...")
    result = subprocess.run(
        ["pandoc", MD_FILE, "-f", "markdown", "-t", "html", "--wrap=preserve"],
        capture_output=True, text=True, cwd=SCRIPT_DIR
    )
    if result.returncode != 0:
        print(f"Pandoc error: {result.stderr}")
        return 1

    body = result.stdout
    if "<body>" in body:
        start = body.find("<body>") + 6
        end = body.find("</body>")
        body = body[start:end].strip()

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE + body + "\n</body>\n</html>\n")
    print(f"Wrote {HTML_FILE}")

    print("Converting to PDF...")
    result = subprocess.run(["weasyprint", HTML_FILE, PDF_FILE], cwd=SCRIPT_DIR)
    if result.returncode != 0:
        print("WeasyPrint failed. Install with: pip install weasyprint")
        return 1
    print(f"Done. Generated {PDF_FILE}")
    return 0


if __name__ == "__main__":
    exit(main())
