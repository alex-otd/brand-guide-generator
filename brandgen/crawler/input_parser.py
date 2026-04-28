"""
Parse the three supported input forms (single URL, CSV, sitemap).

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pathlib import Path


def parse_input(input_source: str) -> list[str]:
    """Detect input type and return a list of candidate URLs.

    Detection rules:
    - Ends in .csv (path or URL)        -> CSV
    - Ends in sitemap.xml or .xml       -> XML sitemap (recurse indexes)
    - Otherwise treated as a single URL -> wrap in a 1-element list

    The returned list is unfiltered. Page selection happens in
    page_selector.py.
    """
    raise NotImplementedError("TODO(brandgen): implement input dispatch")


def parse_csv(path: Path) -> list[str]:
    """Read URLs from a CSV. Expects a `url` column header."""
    raise NotImplementedError("TODO(brandgen): implement CSV reader")


def parse_sitemap(url: str) -> list[str]:
    """Fetch and parse an XML sitemap. Recurses sitemap-index files."""
    raise NotImplementedError("TODO(brandgen): implement sitemap fetcher")
