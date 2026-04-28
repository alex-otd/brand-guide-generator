"""
Core data contracts and Pydantic models for brandgen.
"""

from pydantic import BaseModel, Field


class ContrastResult(BaseModel):
    """
    Results of a WCAG 2.1 contrast ratio calculation.
    """
    ratio: float = Field(..., description="The computed contrast ratio (e.g., 4.5)")
    foreground: str = Field(..., description="Hex code of the foreground color")
    background: str = Field(..., description="Hex code of the background color")
    compliance: dict[str, bool] = Field(
        ..., 
        description="Boolean flags for AA, AAA, AA_large, and AAA_large"
    )
    reasoning: str = Field(..., description="Traceability note on how the ratio was derived")