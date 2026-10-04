"""
core/models.py
Canonical Data Schemas for Data Normalization and System Pipeline
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class MetricValue:
    value: Any
    source: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: str = "high"

@dataclass
class CompetitorRecord:
    name: str
    position: int
    rating: Optional[float] = None
    review_count: Optional[int] = None

@dataclass
class BusinessRecord:
    name: MetricValue
    category: MetricValue
    locality: MetricValue
    city: MetricValue
    country: MetricValue
    phone: Optional[MetricValue] = None
    website: Optional[MetricValue] = None
    maps_url: Optional[MetricValue] = None
    rating: Optional[MetricValue] = None
    review_count: Optional[MetricValue] = None
    photos_count: Optional[MetricValue] = None
    observed_rankings: Dict[str, int] = field(default_factory=dict)
    competitors: List[CompetitorRecord] = field(default_factory=list)
    has_local_schema: Optional[MetricValue] = None
    is_https: Optional[MetricValue] = None
    page_load_ms: Optional[MetricValue] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name.value if self.name else None,
            "category": self.category.value if self.category else None,
            "locality": self.locality.value if self.locality else None,
            "city": self.city.value if self.city else None,
            "country": self.country.value if self.country else None,
            "phone": self.phone.value if self.phone else None,
            "website": self.website.value if self.website else None,
            "maps_url": self.maps_url.value if self.maps_url else None,
            "rating": self.rating.value if self.rating else None,
            "review_count": self.review_count.value if self.review_count else None,
            "photos_count": self.photos_count.value if self.photos_count else None,
            "observed_rankings": self.observed_rankings,
            "competitors": [
                {"name": c.name, "position": c.position, "rating": c.rating, "review_count": c.review_count}
                for c in self.competitors
            ],
            "has_local_schema": self.has_local_schema.value if self.has_local_schema else False,
            "is_https": self.is_https.value if self.is_https else False,
            "page_load_ms": self.page_load_ms.value if self.page_load_ms else None,
                }
      
