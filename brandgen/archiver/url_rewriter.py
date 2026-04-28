"""
Rewrite absolute URLs in saved HTML/CSS to relative local paths.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pathlib import Path


def rewrite_html_urls(html_path: Path, asset_map: dict[str, Path]) -> None:
    """Update every src/href in saved HTML to point to local files.

    Operates on:
    - <link href> for stylesheets
    - <script src> for JS (kept disabled with a comment)
    - <img src> and <img srcset>
    - <source src> in <picture> / <video>
    - <a href> within the same domain (so internal navigation works
      if the user opens the offline archive)
    """
    raise NotImplementedError("TODO(brandgen): implement HTML URL rewriting")


def rewrite_css_urls(css_path: Path, asset_map: dict[str, Path]) -> None:
    """Update url() references inside CSS to relative local paths.

    Catches: background-image, @font-face src, list-style-image,
    cursor, mask-image, etc. Uses tinycss2 to tokenize so we don't
    trip over edge cases like comments-inside-strings.
    """
    raise NotImplementedError("TODO(brandgen): implement CSS URL rewriting")
