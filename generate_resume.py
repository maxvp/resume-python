#!/usr/bin/env python3
"""
Resume Generator - Convert YAML resume to PDF
Usage: python generate_resume.py
"""

import yaml
from jinja2 import Template
from weasyprint import HTML
import os
import re

def parse_markdown_links(text):
    """Convert Markdown-style links [text](url) to HTML <a> tags."""
    if not text:
        return text
    # Regex to match [text](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.sub(pattern, r'<a href="\2">\1</a>', text)

def convert_hyphens(text):
    """
    Converts standard hyphen-minus (-) used in date ranges to the 
    typographically correct en dash (–).
    
    This is applied specifically to date fields.
    """
    if not text:
        return text
    # Replace single hyphen-minus with en dash, but only if preceded/followed by a word character 
    # (to avoid replacing hyphens in compound words unnecessarily, though dates are the primary target).
    # A simple replacement for date ranges should be sufficient and safe.
    return text.replace('-', '–')

# HTML/CSS template matching your current resume style
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @page {
            size: letter;
            margin: 0.75in 0.75in;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
        }
        
        .header {
            text-align: center;
            margin-bottom: 8pt;
        }
        
        .header h1 {
            font-size: 16pt;
            font-weight: 700;
            margin-bottom: 2pt;
            letter-spacing: 0.02em;
        }
        
        .header .contact {
            font-size: 11pt;
            font-weight: 400;
        }
        
        .section {
            margin-bottom: 10pt;
        }
        
        .section-title {
            font-size: 11pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4pt;
            padding-bottom: 2pt;
            border-bottom: 0.5pt solid #000;
        }
        
        a {
            color: #000;
            text-decoration: none;
            border-bottom: 1px dotted #999;
        }
        
        a:hover {
            background-color: #f0f0f0;
        }
        
        /* --- SKILLS SECTION FIX --- */
        .skills-list {
            /* Now an actual unordered list for proper bullet control */
            list-style: disc;
            /* Indent the whole list slightly for visual space */
            margin-left: 10pt; 
            padding-left: 0;
            list-style-position: outside; /* Ensure wrapped text aligns correctly */
        }
        
        .skill-item {
            margin-bottom: 3pt;
            /* Using list-style takes care of the indent automatically */
            margin-left: 10pt; 
            padding-left: 0;
        }
        /* -------------------------- */
        
        .experience-item, .education-item, .project-item {
            margin-bottom: 8pt;
        }
        
        .company-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0pt;
            font-weight: 600;
        }
        
        .company-name {
            font-weight: 600;
        }
        
        .company-dates {
            font-weight: 400;
            font-style: italic;
        }
        
        .role-item {
            margin-left: 0;
            margin-bottom: 4pt;
        }
        
        .role-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            font-weight: 400;
            margin-top: 1pt;
        }
        
        .role-dates {
            font-style: italic;
            font-weight: 400;
            font-size: 10pt;
        }
        
        .responsibilities {
            margin-left: 12pt;
            margin-top: 1pt;
        }
        
        .responsibilities li {
            margin-bottom: 1pt;
        }
        
        .project-header {
            margin-bottom: 1pt;
        }
        
        .project-name {
            font-weight: 600;
            display: inline;
        }
        
        .project-tech {
            font-style: italic;
            display: inline;
        }
        
        .project-url {
            float: right;
            font-style: italic;
        }
        
        .coursework {
            margin-left: 12pt;
        }
        
        .education-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 1pt;
        }
        
        .institution {
            font-weight: 600;
        }
        
        .degree-line {
            margin-bottom: 1pt;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ name }}</h1>
        <div class="contact">{{ parse_links(location) }} — {{ parse_links(email) | safe }} — {{ parse_links(website) | safe }}</div>
    </div>
    
    <div class="section">
        <div class="section-title">Skills</div>
        <ul class="skills-list">
            {% for skill in skills %}
            <li class="skill-item"><strong>{{ skill.category }}:</strong> {% for item in skill.get('items', []) %}{{ parse_links(item) | safe }}{% if not loop.last %}, {% endif %}{% endfor %}</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <div class="section-title">Experience</div>
        {% for job in experience %}
        <div class="experience-item">
            {% for role in job.roles %}
            <div class="role-item">
                <div class="role-header">
                    <span style="font-weight: 600;">{{ parse_links(role.title) | safe }}</span>
                    <span class="role-dates">{{ convert_hyphens(role.dates) }}</span>
                </div>
                <div style="margin-bottom: 2pt;">{{ parse_links(job.company) | safe }} • {{ job.location }}</div>
                <ul class="responsibilities">
                    {% for resp in role.responsibilities %}
                    <li>{{ parse_links(resp) | safe }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <div class="section-title">Awards</div>
        {% for award in awards %}
        <div class="experience-item">
            <div class="role-header">
                <span style="font-weight: 600;">{{ parse_links(award.name) | safe }}</span>
                <span class="role-dates">{{ convert_hyphens(award.date) }}</span>
            </div>
            <div style="margin-bottom: 2pt;">{{ parse_links(award.organization) | safe }}{% if award.team %} • {{ award.team }}{% endif %}</div>
            {% if award.description %}
            <ul class="responsibilities">
                <li>{{ parse_links(award.description) | safe }}</li>
            </ul>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <div class="section-title">Education</div>
        {% for edu in education %}
        <div class="education-item">
            <div class="education-header">
                <span class="institution">{{ parse_links(edu.degree) | safe }}</span>
                <span style="font-style: italic;">{{ convert_hyphens(edu.graduation) }}</span>
            </div>
            <div style="margin-bottom: 2pt;">{{ parse_links(edu.institution) | safe }}{% if edu.gpa %} • {{ edu.gpa }}{% endif %}</div>
            {% if edu.coursework %}
            <div class="coursework">
                <strong>• Coursework:</strong> {% for course in edu.coursework %}{{ parse_links(course) | safe }}{% if not loop.last %}, {% endif %}{% endfor %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def generate_resume(yaml_file='resume.yaml', output_pdf='resume.pdf', output_html='resume.html'):
    """Generate PDF and HTML resume from YAML file."""
    
    if not os.path.exists(yaml_file):
        print(f"Error: {yaml_file} not found. Please create the file first.")
        return

    # Load YAML data
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return

    # Render template
    template = Template(TEMPLATE)
    # Add the custom functions to Jinja2 environment
    template.globals['parse_links'] = parse_markdown_links
    template.globals['convert_hyphens'] = convert_hyphens
    
    html_content = template.render(**data)
    
    # Generate HTML file
    try:
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML generated: {output_html}")
    except Exception as e:
        print(f"Error generating HTML: {e}")
    
    # Generate PDF
    try:
        HTML(string=html_content).write_pdf(output_pdf)
        print(f"✓ PDF generated: {output_pdf}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == '__main__':
    generate_resume()