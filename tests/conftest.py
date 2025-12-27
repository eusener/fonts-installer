"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_font_path(temp_dir: Path) -> Path:
    """Create a sample font file path."""
    font_path = temp_dir / "sample.ttf"
    font_path.write_bytes(b"fake font data")
    return font_path
