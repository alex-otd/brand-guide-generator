"""
Extract typography: families, weights, sizes, line-heights actually used.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pydantic import BaseModel


class ExtractedFont(BaseModel):
    family: str                       # canonical family name
    fallbacks: list[str]              # fallback chain as declared
    weights_used: list[int]           # e.g. [400, 500, 700]
    sizes_used: list[float]           # in px, sorted
    line_heights_used: list[float]
    roles: list[str]                  # ["heading", "body", "button"]
    source: str | None                # "Google Fonts", "self-hosted", "system"


def extract_fonts(captures: list[dict]) -> list[ExtractedFont]:
    """Detect every font family in active use plus its weights/sizes.

    Pulls from two sources:
    - Computed styles on sampled elements (the canonical truth)
    - @font-face rules in collected stylesheets (for source detection)
    """
    raise NotImplementedError("TODO(brandgen): implement font extraction")
