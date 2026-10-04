"""
identity/business_matcher.py
Strict Business Verification Engine
"""
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

class IdentityResolutionError(Exception):
    """Raised when target business identity cannot be verified with high confidence."""
    pass

class BusinessMatcher:
    @staticmethod
    def extract_domain(url: str) -> str:
        if not url:
            return ""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.lower().replace("www.", "").strip("/")

    @classmethod
    def verify_identity(
        cls, 
        target_input: Dict[str, str], 
        candidates: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], float]:
        target_maps = target_input.get("maps_url", "")
        target_site = cls.extract_domain(target_input.get("website", ""))
        target_phone = "".join(filter(str.isdigit, target_input.get("phone", "")))
        target_name = target_input.get("name", "").lower()
        target_locality = target_input.get("locality", "").lower()

        best_match = None
        highest_score = 0.0

        for candidate in candidates:
            score = 0.0
            
            # Rule 1: Maps URL Match
            if target_maps and candidate.get("maps_url") == target_maps:
                return candidate, 1.0

            # Rule 2: Domain match
            cand_site = cls.extract_domain(candidate.get("website", ""))
            if target_site and cand_site and target_site == cand_site:
                score += 0.90

            # Rule 3: Phone match
            cand_phone = "".join(filter(str.isdigit, candidate.get("phone", "")))
            if target_phone and cand_phone and target_phone == cand_phone:
                score += 0.85

            # Rule 4: Name & Locality match
            cand_name = candidate.get("title", candidate.get("name", "")).lower()
            cand_address = candidate.get("address", "").lower()
            
            if target_name in cand_name or cand_name in target_name:
                score += 0.40
            if target_locality and target_locality in cand_address:
                score += 0.30

            if score > highest_score:
                highest_score = score
                best_match = candidate

        if highest_score < 0.65 or not best_match:
            raise IdentityResolutionError(
                "Multiple candidates or low-confidence match found. "
                "Please provide an exact Google Maps Listing URL."
            )

        return best_match, highest_score
