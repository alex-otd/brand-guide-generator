import pytest
from brandgen.extractors.contrast import compute_contrast

def test_contrast_high_pass():
    # Pure black on pure white (21:1)
    result = compute_contrast("#000000", "#FFFFFF")
    assert result.ratio == 21.0
    assert result.compliance["AAA"] is True

def test_contrast_low_pass():
    # Light gray on white (low contrast)
    result = compute_contrast("#CCCCCC", "#FFFFFF")
    assert result.ratio < 4.5
    assert result.compliance["AA"] is False

def test_contrast_rounding():
    # Ensure ratio is rounded to 2 decimal places
    result = compute_contrast("#333333", "#FEFEFE")
    assert isinstance(result.ratio, float)
    assert len(str(result.ratio).split('.')[-1]) <= 2

def test_compliance_logic():
    # Test specific AA threshold
    result = compute_contrast("#767676", "#FFFFFF")  # Approx 4.5:1
    assert result.ratio >= 4.5
    assert result.compliance["AA"] is True