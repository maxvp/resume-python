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
            margin: 0.5in 0.75in;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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
        
        .skills-list {
            margin-left: 15pt;
        }
        
        .skill-item {
            margin-bottom: 3pt;
        }
        
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
        <div class="skills-list">
            {% for skill in skills %}
            <div class="skill-item">• <strong>{{ skill.category }}:</strong> {% for item in skill.get('items', []) %}{{ parse_links(item) | safe }}{% if not loop.last %}, {% endif %}{% endfor %}</div>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Experience</div>
        {% for job in experience %}
        <div class="experience-item">
            {% for role in job.roles %}
            <div class="role-item">
                <div class="role-header">
                    <span style="font-weight: 600;">{{ parse_links(role.title) | safe }}</span>
                    <span class="role-dates">{{ role.dates }}</span>
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
        <div class="section-title">Education</div>
        {% for edu in education %}
        <div class="education-item">
            <div class="education-header">
                <span class="institution">{{ parse_links(edu.degree) | safe }}</span>
                <span style="font-style: italic;">{{ edu.graduation }}</span>
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
    
    <div class="section">
        <div class="section-title">Selected Work</div>
        {% for project in projects %}
        <div class="project-item">
            <div class="project-header">
                <span class="project-name">{{ parse_links(project.name) | safe }}</span>
                <span class="project-url">{{ parse_links(project.url) | safe }}</span>
            </div>
            <div style="margin-bottom: 1pt;">{% for tech in project.technologies %}{{ parse_links(tech) | safe }}{% if not loop.last %}, {% endif %}{% endfor %}</div>
            <ul class="responsibilities">
                <li>{{ parse_links(project.description) | safe }}</li>
            </ul>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def generate_resume(yaml_file='resume.yaml', output_file='resume.pdf'):
    """Generate PDF resume from YAML file."""
    
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
    # Add the parse_markdown_links function to Jinja2 environment
    template.globals['parse_links'] = parse_markdown_links
    html_content = template.render(**data)
    
    # Generate PDF
    try:
        HTML(string=html_content).write_pdf(output_file)
        print(f"✓ Resume generated: {output_file}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == '__main__':
    generate_resume()