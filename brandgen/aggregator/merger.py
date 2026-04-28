"""
Merge per-page extraction outputs into one site-wide brand profile.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pydantic import BaseModel

from brandgen.extractors.buttons import ExtractedButton
from brandgen.extractors.colors import ExtractedColor
from brandgen.extractors.contrast import ContrastResult
from brandgen.extractors.fonts import ExtractedFont
from brandgen.extractors.logo import LogoCandidate


class BrandProfile(BaseModel):
    """The aggregated, deduplicated brand data ready for rendering."""
    client_slug: str
    source_pages: list[str]
    colors: list[ExtractedColor]
    fonts: list[ExtractedFont]
    buttons: list[ExtractedButton]
    logo_candidates: list[LogoCandidate]
    contrast_results: list[ContrastResult]


def merge_extractions(per_page: list[dict], client_slug: str) -> BrandProfile:
    """Combine per-page extractor outputs into one BrandProfile.

    Dedup rules:
    - Colors: bucket by Lab distance, sum frequencies
    - Fonts: union weights/sizes per family
    - Buttons: re-cluster across pages (a primary CTA on page 1 and
      page 5 should be the same entry, not two separate ones)
    - Logos: pick the top candidate by confidence
    """
    raise NotImplementedError("TODO(brandgen): implement cross-page merge")
