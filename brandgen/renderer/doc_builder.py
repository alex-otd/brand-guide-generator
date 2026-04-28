"""
Render the final HTML brand doc and brand.json from a BrandProfile.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pathlib import Path

from brandgen.aggregator.merger import BrandProfile


def render_brand_doc(profile: BrandProfile, output_dir: Path) -> Path:
    """Produce branding-doc.html using the Jinja2 template.

    The output mirrors the Premier Remodel reference doc:
    - Color swatches (5-8 colors with hex, RGB, role notes)
    - Typography section (headings, body, samples in real fonts)
    - Buttons (all variants with hover states)
    - WCAG/ADA contrast notes
    - Empty Brand Voice & Identity placeholder for LLM workflow
    - Print-ready CSS with sensible page-break rules

    Also writes brand.json sidecar for programmatic consumption.
    """
    raise NotImplementedError("TODO(brandgen): implement doc renderer")


def write_brand_json(profile: BrandProfile, output_dir: Path) -> Path:
    """Dump the full BrandProfile as JSON for LLM/programmatic use."""
    raise NotImplementedError("TODO(brandgen): implement JSON writer")
