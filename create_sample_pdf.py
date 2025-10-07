#!/usr/bin/env python3
"""
Simple script to create a sample PDF for testing the RAG system
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_sample_pdf():
    """Create a sample PDF document for testing"""
    
    # Read the text content
    with open('sample_document.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate("sample_document.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
    )
    
    # Build the document
    story = []
    
    # Split content into sections
    sections = content.split('\n\n')
    
    for section in sections:
        if section.strip():
            lines = section.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Determine style based on content
                if line.isupper() and len(line) > 10:  # Title
                    story.append(Paragraph(line, title_style))
                elif line.startswith(('1.', '2.', '3.', '4.')) or line.endswith(':'):  # Headings
                    story.append(Paragraph(line, heading_style))
                else:  # Normal text
                    story.append(Paragraph(line, normal_style))
            
            story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    print("✅ Sample PDF created: sample_document.pdf")

if __name__ == "__main__":
    try:
        create_sample_pdf()
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        create_sample_pdf()
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")