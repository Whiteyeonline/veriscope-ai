"""
reports/styles.py
ReportLab PDF Design Tokens and Stylesheet
"""
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def get_report_styles():
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1A73E8")
    dark_text = colors.HexColor("#202124")

    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='BodyDark',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=dark_text,
        spaceAfter=6
    ))

    return styles
