"""
Extract a frequency- and role-weighted top-N color palette.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pydantic import BaseModel


class ExtractedColor(BaseModel):
    hex: str                    # canonical lowercase #rrggbb
    rgb: tuple[int, int, int]
    roles: list[str]            # e.g. ["body-text", "button-bg", "link"]
    frequency: float            # 0..1, weight of this color across the site
    confidence: float           # 0..1, how sure we are this is intentional brand


def extract_colors(captures: list[dict], top_n: int = 8) -> list[ExtractedColor]:
    """Return the top N colors found across captured pages.

    Algorithm sketch (to be refined):
    1. Collect every color value from computed styles + parsed CSS.
    2. Weight by visible pixel area (approximated from element size).
    3. Bucket near-duplicates within a small Lab color distance.
    4. Tag each color with the roles it plays (text, bg, border, ...).
    5. Demote near-blacks/near-whites that are obviously body text/bg.
    6. Return top N with confidence scores.
    """
    raise NotImplementedError("TODO(brandgen): implement color extraction")
