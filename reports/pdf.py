"""
reports/pdf.py
2-Page Executive PDF Report Engine using ReportLab
"""
import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from typing import Dict, Any
from reports.styles import get_report_styles

class PDFReportGenerator:
    @staticmethod
    def _download_image(url: str, filename: str) -> bool:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                return True
        except Exception:
            pass
        return False

    @classmethod
    def build_pdf(cls, record_dict: Dict[str, Any], ai_insights: Dict[str, Any], chart_urls: Dict[str, str], output_path: str):
        styles = get_report_styles()
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )

        story = []

        # Download charts
        gauge_path = "cache_gauge.png"
        comp_path = "cache_comp.png"
        cls._download_image(chart_urls.get("gauge", ""), gauge_path)
        cls._download_image(chart_urls.get("competitor", ""), comp_path)

        # PAGE 1: EXECUTIVE SUMMARY & OBSERVATIONS
        story.append(Paragraph("LOCAL SEO & GBP AUDIT REPORT", styles['DocTitle']))
        story.append(Paragraph(f"<b>Business:</b> {record_dict.get('name')} | <b>Location:</b> {record_dict.get('city')}, {record_dict.get('country')}", styles['BodyDark']))
        story.append(Spacer(1, 10))

        # Overview Table + Gauge
        exec_text = ai_insights.get("executive_summary", "Audit summary unavailable.")
        overview_data = [
            [Paragraph(f"<b>Executive Summary:</b><br/>{exec_text}", styles['BodyDark']),
             Image(gauge_path, width=150, height=100) if os.path.exists(gauge_path) else "Score Gauge"]
        ]
        t_overview = Table(overview_data, colWidths=[380, 160])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#DADCE0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_overview)
        story.append(Spacer(1, 15))

        # Profile Completeness Grid
        story.append(Paragraph("GBP Profile Completeness & Technical Check", styles['SectionHeader']))
        completeness_data = [
            ["Metric", "Observed State", "Metric", "Observed State"],
            ["Rating", str(record_dict.get("rating") or "N/A"), "Local Schema", "✓ Present" if record_dict.get("has_local_schema") else "✗ Missing"],
            ["Reviews", str(record_dict.get("review_count") or "N/A"), "HTTPS Secure", "✓ Yes" if record_dict.get("is_https") else "✗ No"],
            ["Website", "✓ Listed" if record_dict.get("website") else "✗ Missing", "Page Load", f"{record_dict.get('page_load_ms')} ms" if record_dict.get("page_load_ms") else "N/A"]
        ]
        t_complete = Table(completeness_data, colWidths=[130, 140, 130, 140])
        t_complete.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A73E8")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DADCE0")),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_complete)

        # PAGE BREAK
        story.append(PageBreak())

        # PAGE 2: COMPETITORS & ACTION PLAN
        story.append(Paragraph("Competitor Benchmark & Recommendations", styles['SectionHeader']))
        
        if os.path.exists(comp_path):
            story.append(Image(comp_path, width=400, height=180))
            story.append(Spacer(1, 10))

        # Action Plan
        story.append(Paragraph("Priority Action Plan", styles['SectionHeader']))
        action_plan = ai_insights.get("action_plan", [])
        plan_rows = [["#", "Recommended Action", "Strategic Reason"]]
        for item in action_plan:
            plan_rows.append([
                str(item.get("priority", "-")),
                Paragraph(item.get("action", ""), styles['BodyDark']),
                Paragraph(item.get("reason", ""), styles['BodyDark'])
            ])

        t_plan = Table(plan_rows, colWidths=[30, 230, 280])
        t_plan.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#202124")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DADCE0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_plan)

        doc.build(story)

        # Clean temp images
        for p in [gauge_path, comp_path]:
            if os.path.exists(p):
                os.remove(p)
