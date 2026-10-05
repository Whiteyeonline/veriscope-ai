"""
reports/pdf.py
Executive PDF Report Generation - Production Ready
"""
import os
import requests
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, 
    PageBreak, KeepTogether, Frame, PageTemplate
)
from reportlab.lib import colors
from reportlab.lib.units import inch
from typing import Dict, Any
from reports.styles import get_report_styles


class PDFReportGenerator:
    """Generate professional 2-page executive PDF reports."""
    
    CACHE_DIR = "pdf_cache"

    @classmethod
    def build_pdf(cls, record_dict: Dict[str, Any], ai_insights: Dict[str, Any], 
                  chart_urls: Dict[str, str], output_path: str, language: str = "English"):
        """Build complete executive PDF report.
        
        Args:
            record_dict: Normalized business data
            ai_insights: AI-generated analysis
            chart_urls: QuickChart image URLs
            output_path: Output PDF file path
            language: Report language (English/Malayalam)
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        
        styles = get_report_styles(language=language)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        story = []
        
        # Download chart images
        gauge_path = os.path.join(cls.CACHE_DIR, "gauge.png")
        comp_path = os.path.join(cls.CACHE_DIR, "competitors.png")
        
        cls._download_image(chart_urls.get("gauge", ""), gauge_path)
        cls._download_image(chart_urls.get("competitor", ""), comp_path)

        # ===== PAGE 1: EXECUTIVE SUMMARY =====
        story.append(Paragraph(
            "LOCAL SEO & GBP AUDIT REPORT",
            styles['DocTitle']
        ))
        
        # Business header
        header_text = (
            f"<b>Business:</b> {record_dict.get('name', 'N/A')} | "
            f"<b>Location:</b> {record_dict.get('city', 'N/A')}, {record_dict.get('country', 'N/A')} | "
            f"<b>Generated:</b> "
        )
        from datetime import datetime
        header_text += datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(header_text, styles['BodySmall']))
        story.append(Spacer(1, 15))

        # Executive Summary Section
        story.append(Paragraph("Executive Summary", styles['SectionHeader']))
        exec_summary = ai_insights.get("executive_summary", "Unable to generate summary.")
        story.append(Paragraph(exec_summary, styles['BodyText']))
        story.append(Spacer(1, 12))

        # GBP Score with Gauge
        gbp_score = ai_insights.get("gbp_score", 0)
        score_data = [
            [
                Paragraph(
                    f"<b>GBP Health Score:</b><br/><font size=24 color='#1A73E8'><b>{int(gbp_score)}/100</b></font>",
                    styles['BodyText']
                ),
                Image(gauge_path, width=120, height=90) if os.path.exists(gauge_path) else "[Score Gauge]"
            ]
        ]
        t_score = Table(score_data, colWidths=[280, 160])
        t_score.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#DADCE0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (1, 0), (1, -1), 0),
        ]))
        story.append(t_score)
        story.append(Spacer(1, 15))

        # Profile Completeness Grid
        story.append(Paragraph("GBP Profile Assessment", styles['SectionHeader']))
        completeness_data = [
            ["Metric", "Status", "Metric", "Status"],
            [
                "Business Rating",
                f"{record_dict.get('rating', 'N/A')}/5.0" if record_dict.get('rating') else "No Rating",
                "Local Schema",
                "✓ Present" if record_dict.get('has_local_schema') else "✗ Missing"
            ],
            [
                "Review Count",
                str(record_dict.get('review_count', 0) or "0"),
                "HTTPS Security",
                "✓ Yes" if record_dict.get('is_https') else "✗ No"
            ],
            [
                "Website Listed",
                "✓ Yes" if record_dict.get('website') else "✗ No",
                "Page Load Speed",
                f"{record_dict.get('page_load_ms', 'N/A')}ms" if record_dict.get('page_load_ms') else "N/A"
            ]
        ]
        t_complete = Table(completeness_data, colWidths=[130, 130, 130, 130])
        t_complete.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A73E8")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DADCE0")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_complete)

        # PAGE BREAK
        story.append(PageBreak())

        # ===== PAGE 2: ANALYSIS & RECOMMENDATIONS =====
        story.append(Paragraph("Competitor Landscape", styles['SectionHeader']))
        
        # Competitor chart
        if os.path.exists(comp_path):
            story.append(Image(comp_path, width=420, height=220))
            story.append(Spacer(1, 10))
        
        # Competitors table
        competitors = record_dict.get('competitors', [])
        if competitors:
            story.append(Paragraph("Top Local Competitors", styles['SubHeader']))
            comp_data = [["Rank", "Business Name", "Rating", "Reviews"]]
            for comp in competitors[:5]:
                comp_data.append([
                    str(comp.get('position', '-')),
                    comp.get('name', 'N/A')[:20],
                    f"{comp.get('rating', 'N/A')}/5" if comp.get('rating') else "N/A",
                    str(comp.get('review_count', 0) or 0)
                ])
            t_comp = Table(comp_data, colWidths=[40, 200, 80, 80])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#202124")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DADCE0")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            story.append(t_comp)
            story.append(Spacer(1, 12))

        # Key Findings
        story.append(Paragraph("Key Findings", styles['SectionHeader']))
        findings = ai_insights.get("findings", [])
        for finding in findings[:3]:
            story.append(Paragraph(f"• {finding}", styles['BodyText']))
        story.append(Spacer(1, 12))

        # Priority Action Plan
        story.append(Paragraph("Priority Action Plan", styles['SectionHeader']))
        action_plan = ai_insights.get("action_plan", [])
        plan_rows = [["#", "Action", "Why It Matters"]]
        for item in action_plan[:3]:
            plan_rows.append([
                str(item.get("priority", "-")),
                Paragraph(item.get("action", ""), styles['BodySmall']),
                Paragraph(item.get("reason", ""), styles['BodySmall'])
            ])
        
        t_plan = Table(plan_rows, colWidths=[25, 200, 215])
        t_plan.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#202124")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DADCE0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]))
        story.append(t_plan)

        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "<font size=7><i>This report was generated by Veriscope AI - Professional Local SEO Audit Engine. "
            "Data accurate as of report generation date. Recommendations based on current Google Search & Maps algorithms.</i></font>",
            styles['Footer']
        ))

        # Build PDF
        doc.build(story)

        # Cleanup temp images
        for path in [gauge_path, comp_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass

    @staticmethod
    def _download_image(url: str, filename: str, timeout: int = 10) -> bool:
        """Download image from URL with timeout."""
        if not url:
            return False
        
        try:
            response = requests.get(url, timeout=timeout, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
        except Exception as e:
            print(f"Failed to download image {url}: {e}")
        
        return False
