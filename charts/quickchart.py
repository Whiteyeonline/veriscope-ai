"""
charts/quickchart.py
Generates Visual Chart URLs using QuickChart.io (Zero-Auth / Public API)
"""
import urllib.parse
import json
from typing import List, Dict, Any

class QuickChartGenerator:
    BASE_URL = "https://quickchart.io/chart?c="

    @classmethod
    def generate_gbp_gauge(cls, score: int) -> str:
        chart_config = {
            "type": "radialGauge",
            "data": {
                "datasets": [{
                    "data": [score],
                    "backgroundColor": "#1A73E8" if score >= 70 else ("#FBBC04" if score >= 40 else "#EA4335")
                }]
            },
            "options": {
                "title": {"display": True, "text": "GBP Health Score"},
                "domain": [0, 100]
            }
        }
        return cls.BASE_URL + urllib.parse.quote(json.dumps(chart_config))

    @classmethod
    def generate_competitor_chart(cls, client_reviews: int, competitors: List[Dict[str, Any]]) -> str:
        labels = ["Client"] + [c.get("name", f"Comp {i+1}")[:10] for i, c in enumerate(competitors[:3])]
        data = [client_reviews] + [c.get("review_count", 0) or 0 for c in competitors[:3]]

        chart_config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Review Count",
                    "data": data,
                    "backgroundColor": ["#1A73E8", "#80868B", "#80868B", "#80868B"]
                }]
            },
            "options": {
                "title": {"display": True, "text": "Review Count vs Local Competitors"},
                "legend": {"display": False}
            }
        }
        return cls.BASE_URL + urllib.parse.quote(json.dumps(chart_config))
