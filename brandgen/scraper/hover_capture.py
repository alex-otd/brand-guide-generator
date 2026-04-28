"""
Capture button hover states via both static CSS rules and JS simulation.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

async def capture_hover_deltas(page, button_selectors: list[str]) -> list[dict]:
    """For each button selector:

    1. Read computed styles in resting state
    2. page.hover() the element
    3. Re-read computed styles
    4. Diff and return only properties that changed

    This catches both CSS :hover rules (which would be visible in
    stylesheets anyway) AND JS-driven effects that only show up on
    actual hover events (React, Vue, jQuery handlers, Divi modules).
    """
    raise NotImplementedError("TODO(brandgen): implement hover delta capture")


def parse_static_hover_rules(stylesheets: list[str]) -> list[dict]:
    """Parse CSS for :hover selectors and return the rules.

    A complement to capture_hover_deltas — together they give us
    a full picture of hover behavior on the page.
    """
    raise NotImplementedError("TODO(brandgen): implement :hover rule parser")
