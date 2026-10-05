"""
identity/business_matcher.py
Strict Business Verification Engine with Confidence Scoring
"""
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
import difflib


class IdentityResolutionError(Exception):
    """Raised when target business identity cannot be verified with high confidence."""
    pass


class BusinessMatcher:
    """Matches user input business to search results with confidence scoring."""

    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL, normalized."""
        if not url:
            return ""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.lower().replace("www.", "").strip("/")

    @staticmethod
    def name_similarity(name1: str, name2: str) -> float:
        """Calculate similarity ratio between two business names."""
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        return difflib.SequenceMatcher(None, n1, n2).ratio()

    @classmethod
    def verify_identity(
        cls,
        target_input: Dict[str, str],
        candidates: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], float]:
        """Verify which candidate matches the target business input.
        
        Returns:
            (matched_candidate, confidence_score)
            
        Raises:
            IdentityResolutionError if no high-confidence match found
        """
        target_maps = target_input.get("maps_url", "").strip()
        target_site = cls.extract_domain(target_input.get("website", ""))
        target_phone = "".join(filter(str.isdigit, target_input.get("phone", "")))
        target_name = target_input.get("name", "").lower().strip()
        target_locality = target_input.get("locality", "").lower().strip()

        best_match = None
        highest_score = 0.0

        for candidate in candidates:
            score = 0.0

            # Rule 1: Exact Maps URL match (highest confidence)
            if target_maps and candidate.get("maps_url") == target_maps:
                return candidate, 1.0
            if target_maps and candidate.get("link") == target_maps:
                return candidate, 1.0

            # Rule 2: Domain match (strong signal)
            cand_site = cls.extract_domain(candidate.get("website", ""))
            if target_site and cand_site and target_site in cand_site or cand_site in target_site:
                score += 0.90

            # Rule 3: Phone match (strong signal)
            cand_phone = "".join(filter(str.isdigit, candidate.get("phone", "")))
            if target_phone and cand_phone and target_phone == cand_phone:
                score += 0.85

            # Rule 4: Name similarity
            cand_name = candidate.get("title", candidate.get("name", "")).lower().strip()
            name_sim = cls.name_similarity(target_name, cand_name)
            if name_sim > 0.75:
                score += 0.60
            elif name_sim > 0.5:
                score += 0.30
            elif target_name in cand_name or cand_name in target_name:
                score += 0.40

            # Rule 5: Address/Locality match
            cand_address = candidate.get("address", "").lower()
            if target_locality and target_locality in cand_address:
                score += 0.25

            if score > highest_score:
                highest_score = score
                best_match = candidate

        # Require minimum confidence threshold
        if highest_score < 0.50 or not best_match:
            raise IdentityResolutionError(
                f"Low confidence match (score: {highest_score:.2f}). "
                "Please provide a Google Maps listing URL for precise verification."
            )

        return best_match, highest_score
