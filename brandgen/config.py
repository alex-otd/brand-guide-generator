"""
Pydantic models for brandgen configuration.

Two layers of config:

1. Tool defaults (hard-coded here) — sensible behavior out of the box.
2. Per-client YAML at brand-guides/<slug>/config.yaml — overrides for
   tricky sites (custom priority paths, ignore selectors, manual color
   overrides).

The per-client file is auto-generated on first scrape of a client and
is hand-editable for re-runs.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


# Default page priority patterns (regex strings, case-insensitive).
# Higher score = higher priority. Homepage always wins regardless.
DEFAULT_PRIORITY_PATTERNS: dict[str, int] = {
    r"^/?$": 100,                                       # homepage
    r"^/(about|about-us)(/|$)": 80,
    r"^/(services?|what-we-do)(/|$)": 75,
    r"^/(contact|get-quote|quote)(/|$)": 70,
    r"^/(portfolio|gallery|projects|work)(/|$)": 60,
    r"^/(pricing|plans)(/|$)": 55,
    r"^/(team|staff)(/|$)": 50,
    r"^/(faq)(/|$)": 45,
    r"^/(blog|news)/.+": 40,                            # one blog post
}


class ClientConfig(BaseModel):
    """Per-client overrides loaded from brand-guides/<slug>/config.yaml."""

    client_slug: str = Field(..., description="Folder name under brand-guides/")
    display_name: str | None = Field(None, description="Human-readable name for the doc")

    # Page selection
    max_pages: int = 10
    priority_patterns: dict[str, int] = Field(default_factory=lambda: DEFAULT_PRIORITY_PATTERNS.copy())
    forced_paths: list[str] = Field(
        default_factory=list,
        description="Paths that must always be scraped, regardless of pattern matching.",
    )

    # Extraction tuning
    ignore_selectors: list[str] = Field(
        default_factory=list,
        description="CSS selectors to remove before extraction (e.g. '#cookie-banner').",
    )
    top_color_count: int = 8

    # Manual overrides for stubborn sites
    logo_url_hint: str | None = None
    primary_color_override: str | None = None


def load_client_config(brand_guides_dir: Path, client_slug: str) -> ClientConfig:
    """Load (or create with defaults) the per-client config YAML."""
    raise NotImplementedError(
        "TODO(brandgen): implement YAML load with default-on-missing behavior"
    )


def write_default_client_config(brand_guides_dir: Path, client_slug: str) -> Path:
    """Write a fresh default config.yaml for a new client, return the path."""
    raise NotImplementedError(
        "TODO(brandgen): implement default config writer"
    )
