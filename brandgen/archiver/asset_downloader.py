"""
Download every external asset a page references and save to disk.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pathlib import Path


def download_assets(asset_urls: list[str], output_dir: Path) -> dict[str, Path]:
    """Download each URL into output_dir, returning a {url: local_path} map.

    Handles:
    - CSS files (saved verbatim, will be rewritten by url_rewriter)
    - Web fonts (woff, woff2, ttf, otf)
    - Images (PNG, JPG, SVG, WebP) — including those referenced from CSS
    - Favicons

    Skips:
    - Tracking pixels (Google Analytics, Facebook, etc — configurable)
    - Analytics JS (we want post-JS DOM, not the JS itself)
    """
    raise NotImplementedError("TODO(brandgen): implement asset downloader")


def deduplicate_shared_assets(site_dir: Path) -> None:
    """Move assets shared across pages into _shared/ folders.

    After scraping all pages, identical CSS files (by hash) get moved
    to site/_shared/css/ and per-page references are rewritten to
    point there. Keeps the archive smaller and easier to inspect.
    """
    raise NotImplementedError("TODO(brandgen): implement shared-asset dedup")
