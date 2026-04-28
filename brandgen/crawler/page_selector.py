"""
Score and pick the top-N pages from a candidate URL list.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from brandgen.config import ClientConfig


def select_pages(candidate_urls: list[str], config: ClientConfig) -> list[str]:
    """Apply priority scoring and return the top-N URLs to scrape.

    Scoring inputs:
    - Pattern match against config.priority_patterns
    - URL depth (shallower paths score higher)
    - Position in source list (earlier ranks higher as a tiebreaker)
    - Forced paths (config.forced_paths) bypass scoring

    Hard cap: config.max_pages. Homepage always included if present.
    """
    raise NotImplementedError("TODO(brandgen): implement priority scoring")
