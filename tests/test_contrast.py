"""Tests for extractors.contrast."""
import pytest
from brandgen.extractors.contrast import (
    relative_luminance, 
    contrast_ratio, 
    compute_contrast_matrix
)


def test_white_on_black_is_21():
    """White on black returns ratio of exactly 21.0."""
    white = (255, 255, 255)
    black = (0, 0, 0)
    assert contrast_ratio(white, black) == pytest.approx(21.0)
    assert contrast_ratio(black, white) == pytest.approx(21.0)


def test_same_color_is_1():
    """Same color on itself returns 1.0."""
    color = (184, 92, 56)
    assert contrast_ratio(color, color) == pytest.approx(1.0)


def test_premier_remodel_copper_on_white():
    """Premier Remodel copper (#b85c38) on white (#ffffff) ratio (~4.54)."""
    copper = (184, 92, 56)
    white = (255, 255, 255)
    ratio = contrast_ratio(copper, white)
    assert ratio == pytest.approx(4.54, abs=0.01)


def test_shorthand_hex_expansion():
    """3-char shorthand #fff parses identically to #ffffff."""
    pairings = [("#fff", "#000")]
    results = compute_contrast_matrix([], pairings)
    assert results.foreground == "#ffffff"
    assert results.ratio == pytest.approx(21.0)


def test_invalid_hex_raises_value_error():
    """Invalid hex strings raise ValueError."""
    with pytest.raises(ValueError, match="invalid hex length"):
        compute_contrast_matrix([], [("abcd", "#ffffff")])
    with pytest.raises(ValueError, match="invalid hex characters"):
        compute_contrast_matrix([], [("#zzzzzz", "#ffffff")])


def test_wcag_thresholds():
    """Verify compliance flags against WCAG thresholds using copper on white."""
    results = compute_contrast_matrix([], [("#b85c38", "#ffffff")])
    res = results
    assert res.aa_normal_text is True
    assert res.aa_large_text is True
    assert res.aaa_normal_text is False
    assert res.aaa_large_text is True
    assert res.ui_components is True