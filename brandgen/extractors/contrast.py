"""
Compute WCAG 2.0 AA and 2.1 contrast ratios for color pairings.

Implementation follows the W3C relative luminance and contrast formulas.
"""
from __future__ import annotations

from pydantic import BaseModel


class ContrastResult(BaseModel):
    """Results of a WCAG contrast ratio calculation between two colors."""
    foreground: str          # hex
    background: str          # hex
    ratio: float             # 1.0 to 21.0
    aa_normal_text: bool     # ratio >= 4.5
    aa_large_text: bool      # ratio >= 3.0
    aaa_normal_text: bool    # ratio >= 7.0
    aaa_large_text: bool     # ratio >= 4.5
    ui_components: bool      # ratio >= 3.0 (WCAG 2.1)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Compute relative luminance using the WCAG formula."""
    # Normalize each channel to by dividing by 255
    srgb = [c / 255.0 for c in rgb]
    
    # Apply sRGB linearization: if channel <= 0.03928, divide by 12.92;
    # otherwise ((c + 0.055) / 1.055) ** 2.4
    output = []
    for c in srgb:
        if c <= 0.03928:
            output.append(c / 12.92)
        else:
            output.append(((c + 0.055) / 1.055) ** 2.4)
            
    r, g, b = output
    # Return 0.2126 * R + 0.7152 * G + 0.0722 * B
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """Compute the WCAG contrast ratio (L_lighter + 0.05) / (L_darker + 0.05)."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)


def _parse_hex(hex_str: str) -> tuple[int, int, int]:
    """Parse hex string to RGB tuple. Handles # prefix and 3-char shorthand."""
    clean_hex = hex_str.lstrip("#").lower()
    
    # Invalid hex (non-hex characters): raise ValueError
    if not all(c in "0123456789abcdef" for c in clean_hex):
        raise ValueError(f"invalid hex characters: {hex_str}")

    # Expand 3-char shorthand to 6-char
    if len(clean_hex) == 3:
        clean_hex = "".join(c * 2 for c in clean_hex)
        
    # Invalid length: raise ValueError
    if len(clean_hex) != 6:
        raise ValueError(f"invalid hex length: {hex_str}")
        
    return (
        int(clean_hex[0:2], 16),
        int(clean_hex[2:4], 16),
        int(clean_hex[4:6], 16)
    )


def compute_contrast_matrix(
    colors: list[str], pairings: list[tuple[str, str]]
) -> list[ContrastResult]:
    """Compute contrast for every observed foreground/background pair."""
    results = []
    for fg_hex, bg_hex in pairings:
        fg_rgb = _parse_hex(fg_hex)
        bg_rgb = _parse_hex(bg_hex)
        
        ratio = contrast_ratio(fg_rgb, bg_rgb)
        
        # Populate ContrastResult flags per WCAG thresholds
        results.append(ContrastResult(
            foreground=fg_hex.lower() if fg_hex.startswith("#") else f"#{fg_hex.lower()}",
            background=bg_hex.lower() if bg_hex.startswith("#") else f"#{bg_hex.lower()}",
            ratio=round(ratio, 2),
            aa_normal_text=ratio >= 4.5,
            aa_large_text=ratio >= 3.0,
            aaa_normal_text=ratio >= 7.0,
            aaa_large_text=ratio >= 4.5,
            ui_components=ratio >= 3.0
        ))
    return results