"""
Best-effort logo identification (heuristic, flagged for human review).

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pydantic import BaseModel


class LogoCandidate(BaseModel):
    src: str
    alt: str | None
    width: int | None
    height: int | None
    location: str             # "header", "footer", "nav", "other"
    confidence: float         # 0..1
    reason: str               # human-readable why-it-matched


def extract_logo_candidates(captures: list[dict]) -> list[LogoCandidate]:
    """Return ranked logo candidates. Top item is the best guess.

    Heuristics (in priority order):
    1. <img>/<svg> inside <header> with 'logo' in alt/src/class/id
    2. First <img> in <header> by DOM order
    3. <img>/<svg> in top-left of viewport
    4. Branded-looking image referenced in <link rel="icon">

    We never auto-confirm a logo. The extracted doc shows the top
    candidate flagged for client confirmation.
    """
    raise NotImplementedError("TODO(brandgen): implement logo heuristics")
