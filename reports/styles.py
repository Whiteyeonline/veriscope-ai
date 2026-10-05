"""
reports/styles.py
ReportLab PDF Styling & Typography
"""
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import pt


def get_report_styles(language: str = "English") -> dict:
    """Get styled stylesheet for PDF reports.
    
    Args:
        language: English or Malayalam
        
    Returns:
        Dict of named styles
    """
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1A73E8")
    dark_text = colors.HexColor("#202124")
    light_gray = colors.HexColor("#F8F9FA")

    # Document Title
    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=6,
        alignment=0  # Left aligned
    ))

    # Section Headers
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=8,
        alignment=0
    ))

    # Sub Headers
    styles.add(ParagraphStyle(
        name='SubHeader',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=dark_text,
        spaceBefore=8,
        spaceAfter=6,
        alignment=0
    ))

    # Body Text
    styles.add(ParagraphStyle(
        name='BodyText',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=dark_text,
        spaceAfter=8,
        alignment=4  # Justified
    ))

    # Small Body Text
    styles.add(ParagraphStyle(
        name='BodySmall',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=dark_text,
        spaceAfter=6,
        alignment=0
    ))

    # Table content
    styles.add(ParagraphStyle(
        name='TableContent',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=dark_text,
        alignment=0
    ))

    # Footer
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#5F6368"),
        alignment=1  # Center
    ))

    return styles
