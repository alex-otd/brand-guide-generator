"""
Compute and serialize CSS computed styles for an element sample.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

ELEMENT_SAMPLE_SELECTORS: list[str] = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "a", "button",
    "input", "textarea", "select",
    ".btn", ".button", "[role=button]",
    "header", "footer", "nav",
    "blockquote",
]
# Properties we need to capture from window.getComputedStyle for each
# sampled element. Keep narrow; computed styles dump enormous payloads
# if you ask for everything.
COMPUTED_STYLE_PROPERTIES: list[str] = [
    "color", "background-color", "background-image",
    "font-family", "font-size", "font-weight", "line-height",
    "letter-spacing", "text-transform",
    "border-color", "border-radius", "border-width", "border-style",
    "padding", "margin",
    "box-shadow", "text-shadow",
    "display",
]


async def capture_element_styles(page) -> list[dict]:
    """Run getComputedStyle on each matching element. Returns list of
    {selector, tag, classes, id, text, styles: {prop: value}}.
    """
    raise NotImplementedError("TODO(brandgen): implement computed style capture")
