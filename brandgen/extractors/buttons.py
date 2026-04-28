"""
Cluster buttons by visual style and identify primary vs secondary CTAs.

Implementation status: stub. See TODO(brandgen): implement markers below.
"""
from __future__ import annotations

from pydantic import BaseModel


class ExtractedButton(BaseModel):
    label: str                          # "primary", "secondary", "tertiary"
    background: str                     # hex
    color: str                          # hex
    border: str | None
    border_radius: str
    padding: str
    font_family: str
    font_size: float
    font_weight: int
    text_transform: str
    hover_background: str | None
    hover_color: str | None
    example_text: str                   # actual text from a real button
    frequency: int                      # how many times this style appears


def extract_buttons(captures: list[dict]) -> list[ExtractedButton]:
    """Cluster every button-like element into visual variants.

    Includes <button>, <input type=button|submit>, anchors with
    .btn/.button classes, and elements with role="button".

    Clustering: hash each button on a tuple of normalized style
    properties; merge clusters within small visual distance.
    """
    raise NotImplementedError("TODO(brandgen): implement button clustering")
