"""Adapter für Stellen-Feeds gängiger Bewerbermanagementsysteme."""
from .ats_detect import career_links, detect_company, detect_from_text, feed_url_for
from .dedup import canonicalize_url, dedup_all, fingerprint

__all__ = [
    "career_links", "detect_company", "detect_from_text", "feed_url_for",
    "canonicalize_url", "dedup_all", "fingerprint",
]
