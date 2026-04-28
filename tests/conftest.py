"""
Shared pytest fixtures.

Each extractor will get fixtures here that load known-good HTML/CSS
snippets from tests/fixtures/ so tests are deterministic and don't
require live network calls.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Absolute path to tests/fixtures/."""
    return Path(__file__).parent / "fixtures"
