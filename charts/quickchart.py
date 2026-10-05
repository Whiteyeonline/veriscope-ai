"""
charts/quickchart.py
Visualization Chart Generation using QuickChart Public API
No API key required - production ready
"""
import urllib.parse
import json
from typing import List, Dict, Any


class QuickChartGenerator:
    """Generate chart URLs using QuickChart.io (no auth required)."""
    
    BASE_URL = "https://quickchart.io/chart?c="

    @classmethod
    def generate_gbp_gauge(cls, score: int) -> str:
        """Generate GBP Health Score gauge chart.
        
        Args:
            score: Health score 0-100
            
        Returns:
            Full URL to chart image
        """
        score = max(0, min(100, int(score)))  # Clamp 0-100
        
        # Color based on score
        if score >= 75:
            color = "#00A651"  # Green
        elif score >= 50:
            color = "#FBBC04"  # Amber
        else:
            color = "#EA4335"  # Red
        
        chart_config = {
            "type": "radialGauge",
            "data": {
                "datasets": [{
                    "data": [score],
                    "backgroundColor": [color]
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": "Google Business Profile Health Score",
                    "fontSize": 14,
                    "fontColor": "#202124"
                },
                "domain": [0, 100],
                "centerPercentage": 75
            }
        }
        
        return cls.BASE_URL + urllib.parse.quote(json.dumps(chart_config))

    @classmethod
    def generate_competitor_chart(cls, client_reviews: int, competitors: List[Dict[str, Any]]) -> str:
        """Generate competitor review count comparison chart.
        
        Args:
            client_reviews: Target business review count
            competitors: List of competitor records
            
        Returns:
            Full URL to chart image
        """
        labels = ["Your Business"] + [
            c.get("name", f"Competitor {i+1}")[:15] 
            for i, c in enumerate(competitors[:3])
        ]
        
        data = [client_reviews] + [
            int(c.get("review_count") or 0) 
            for c in competitors[:3]
        ]
        
        chart_config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Review Count",
                    "data": data,
                    "backgroundColor": [
                        "#1A73E8",  # Blue for your business
                        "#80868B",  # Gray for competitors
                        "#80868B",
                        "#80868B"
                    ]
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": "Review Count vs Local Competitors",
                    "fontSize": 14,
                    "fontColor": "#202124"
                },
                "legend": {"display": False},
                "scales": {
                    "yAxes": [{
                        "beginAtZero": True,
                        "ticks": {"stepSize": max(1, max(data) // 5)}
                    }]
                }
            }
        }
        
        return cls.BASE_URL + urllib.parse.quote(json.dumps(chart_config))

    @classmethod
    def generate_rating_comparison(cls, your_rating: float, avg_competitor_rating: float) -> str:
        """Generate rating comparison gauge.
        
        Args:
            your_rating: Your business rating (0-5)
            avg_competitor_rating: Average competitor rating
            
        Returns:
            Full URL to chart image
        """
        chart_config = {
            "type": "bar",
            "data": {
                "labels": ["Your Business", "Competitor Avg"],
                "datasets": [{
                    "label": "Rating (out of 5.0)",
                    "data": [
                        float(your_rating or 0),
                        float(avg_competitor_rating or 0)
                    ],
                    "backgroundColor": ["#1A73E8", "#80868B"]
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": "Rating Comparison",
                    "fontSize": 14,
                    "fontColor": "#202124"
                },
                "scales": {
                    "yAxes": [{
                        "beginAtZero": True,
                        "max": 5.0
                    }]
                }
            }
        }
        
        return cls.BASE_URL + urllib.parse.quote(json.dumps(chart_config))
