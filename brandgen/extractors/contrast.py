"""
WCAG 2.1 Contrast Ratio Computation Engine.
Calculates the relative luminance and contrast ratio between foreground and background colors.
"""

from brandgen.models.contract import ContrastResult


def calculate_relative_luminance(color_hex: str) -> float:
    """
    Computes the relative luminance of a color according to WCAG 2.1 standards.
    Formula: L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    """
    # Normalize hex to RGB values
    hex_val = color_hex.lstrip('#')
    rgb = tuple(int(hex_val[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    components = []
    for val in rgb:
        if val <= 0.03928:
            components.append(val / 12.92)
        else:
            components.append(((val + 0.055) / 1.055) ** 2.4)
            
    r, g, b = components
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def compute_contrast(foreground: str, background: str) -> ContrastResult:
    """
    Computes the contrast ratio between two hex colors and returns a ContrastResult.
    Formula: (L1 + 0.05) / (L2 + 0.05), where L1 is the lighter luminance.
    """
    lum1 = calculate_relative_luminance(foreground)
    lum2 = calculate_relative_luminance(background)
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    ratio = (lighter + 0.05) / (darker + 0.05)
    
    # Determine compliance levels
    compliance = {
        "AA_large": ratio >= 3.0,
        "AA": ratio >= 4.5,
        "AAA_large": ratio >= 4.5,
        "AAA": ratio >= 7.0
    }
    
    return ContrastResult(
        ratio=round(ratio, 2),
        foreground=foreground,
        background=background,
        compliance=compliance,
        reasoning=f"Computed using WCAG 2.1 relative luminance formulas. Ratio: {round(ratio, 2)}:1"
    )