#!/usr/bin/env python3
"""Generate a clean PDF with concise TOC for Totogi Toolkit User Guide"""

import subprocess
import os
from datetime import datetime

# HTML header with title page and TOC
HTML_HEADER = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Totogi Toolkit User Guide</title>
    <style>
        @page {
            size: A4;
            margin: 2cm 2cm 2.5cm 2cm;
            @bottom-center {
                content: "Page " counter(page);
                font-size: 10pt;
                color: #666;
            }
        }
        @page:first { @bottom-center { content: none; } }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
        }
        
        /* Title Page */
        .title-page {
            text-align: center;
            page-break-after: always;
            padding-top: 180px;
        }
        .title-page h1 {
            font-size: 36pt;
            color: #1a365d;
            margin-bottom: 15px;
            border: none;
        }
        .title-page .subtitle {
            font-size: 16pt;
            color: #4a5568;
            margin-bottom: 50px;
        }
        .title-page .author {
            font-size: 14pt;
            color: #718096;
            margin-bottom: 10px;
        }
        .title-page .date {
            font-size: 12pt;
            color: #a0aec0;
        }
        
        /* Table of Contents */
        .toc-page {
            page-break-after: always;
        }
        .toc-page h2 {
            color: #1a365d;
            font-size: 20pt;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }
        .toc-section {
            margin-bottom: 18px;
        }
        .toc-section-title {
            font-size: 12pt;
            font-weight: bold;
            color: #2b6cb0;
            margin-bottom: 6px;
        }
        .toc-section-title a {
            color: #2b6cb0;
            text-decoration: none;
        }
        .toc-items {
            margin-left: 20px;
            font-size: 10pt;
            color: #4a5568;
        }
        .toc-items a {
            color: #3182ce;
            text-decoration: none;
        }
        .toc-items a:hover {
            text-decoration: underline;
        }
        
        /* Links - Blue */
        a { color: #2b6cb0; text-decoration: none; }
        a:hover { text-decoration: underline; }
        
        /* Headings */
        h1 {
            font-size: 22pt;
            color: #1a365d;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 8px;
            margin-top: 35px;
            page-break-after: avoid;
        }
        h2 {
            font-size: 16pt;
            color: #2c5282;
            border-bottom: 1px solid #bee3f8;
            padding-bottom: 5px;
            margin-top: 25px;
            page-break-after: avoid;
        }
        h3 {
            font-size: 13pt;
            color: #2b6cb0;
            margin-top: 20px;
            page-break-after: avoid;
        }
        h4 {
            font-size: 11pt;
            color: #3182ce;
            margin-top: 15px;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10pt;
        }
        th {
            background-color: #ebf8ff;
            color: #2c5282;
            font-weight: bold;
            padding: 10px 8px;
            text-align: left;
            border: 1px solid #bee3f8;
        }
        td {
            padding: 8px;
            border: 1px solid #e2e8f0;
            vertical-align: top;
        }
        tr:nth-child(even) { background-color: #f7fafc; }
        
        /* Code */
        pre {
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 12px;
            font-family: 'Consolas', monospace;
            font-size: 9pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        code {
            font-family: 'Consolas', monospace;
            font-size: 9pt;
            background-color: #edf2f7;
            padding: 2px 5px;
            border-radius: 3px;
        }
        pre code { background: none; padding: 0; }
        
        /* Images */
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }
        
        /* Lists */
        ul, ol { margin: 10px 0; padding-left: 25px; }
        li { margin-bottom: 5px; }
        
        /* Section breaks */
        .section-break { page-break-before: always; }
        hr { border: none; border-top: 1px solid #e2e8f0; margin: 25px 0; }
    </style>
</head>
<body>

<!-- Title Page -->
<div class="title-page">
    <h1>Totogi Toolkit User Guide</h1>
    <div class="subtitle">Complete Documentation for Totogi Capability Installer</div>
    <div class="author">Totogi Platform Team</div>
    <div class="date">''' + datetime.now().strftime("%B %Y") + '''</div>
</div>

<!-- Table of Contents -->
<div class="toc-page">
    <h2>Table of Contents</h2>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#getting-started">1. Getting Started</a></div>
        <div class="toc-items">Prerequisites • Quick Start Guide • What Gets Deployed</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#installation">2. Installation Guide</a></div>
        <div class="toc-items">Windows • macOS • Linux • Verification</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#deployment-wizard">3. Deployment Wizard</a></div>
        <div class="toc-items">Capability Selection • Architecture • Environment • AWS Config • Permissions • Execution • Results</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#aws-configuration">4. AWS Configuration</a></div>
        <div class="toc-items">Authentication Methods • IAM Permissions • Cross-Account Deployment</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#managing-deployments">5. Managing Deployments</a></div>
        <div class="toc-items">Updates • Deletions • Monitoring • Multi-Environment • Kubernetes Management</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#troubleshooting">6. Troubleshooting</a></div>
        <div class="toc-items">Application Issues • Authentication • Deployment • Recovery Procedures</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#faq">7. Frequently Asked Questions</a></div>
        <div class="toc-items">General • Installation • AWS & Security • Deployment • Cost • Management</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#kubernetes-deployment">8. Kubernetes (EKS) Deployment</a></div>
        <div class="toc-items">Prerequisites • Architecture • TotogiCapability CRD • IRSA • Operations</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#build-guide">9. Windows Installer Build Guide</a></div>
        <div class="toc-items">Prerequisites • Build Process • Distribution</div>
    </div>
    
    <div class="toc-section">
        <div class="toc-section-title"><a href="#quick-reference">10. Quick Reference Card</a></div>
        <div class="toc-items">Wizard Steps • Auth Methods • Deployment Strategies • Shortcuts</div>
    </div>
</div>

'''

HTML_FOOTER = '''
</body>
</html>
'''

def main():
    # Files to include (in order), with section IDs
    files = [
        ("01-getting-started.md", "getting-started"),
        ("02-installation.md", "installation"),
        ("03-deployment-wizard.md", "deployment-wizard"),
        ("04-aws-configuration.md", "aws-configuration"),
        ("05-managing-deployments.md", "managing-deployments"),
        ("06-troubleshooting.md", "troubleshooting"),
        ("07-faq.md", "faq"),
        ("08-kubernetes-deployment.md", "kubernetes-deployment"),
        ("BUILD_GUIDE.md", "build-guide"),
        ("QUICK_REFERENCE.md", "quick-reference"),
    ]
    
    # Start building HTML content
    html_content = HTML_HEADER
    
    for filename, section_id in files:
        if os.path.exists(filename):
            print(f"Processing {filename}...")
            
            # Convert markdown to HTML using pandoc
            result = subprocess.run(
                ["pandoc", filename, "-f", "markdown", "-t", "html", 
                 "--embed-resources", "--standalone", "--extract-media=."],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Extract body content from pandoc output
                body = result.stdout
                # Remove pandoc wrapper if present
                if "<body>" in body:
                    start = body.find("<body>") + 6
                    end = body.find("</body>")
                    body = body[start:end]
                
                # Add section with ID and page break
                html_content += f'\n<div class="section-break" id="{section_id}">\n'
                html_content += body
                html_content += '\n</div>\n'
            else:
                print(f"Error processing {filename}: {result.stderr}")
    
    html_content += HTML_FOOTER
    
    # Write combined HTML
    html_file = "combined-guide.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Generated {html_file}")
    
    # Convert to PDF using weasyprint
    print("Converting to PDF...")
    subprocess.run(["weasyprint", html_file, "Totogi-Toolkit-User-Guide.pdf"])
    
    print("Done! Generated Totogi-Toolkit-User-Guide.pdf")

if __name__ == "__main__":
    main()
