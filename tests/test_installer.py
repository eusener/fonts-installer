"""Tests for the font installer module."""

import pytest

from font_installer.config.fonts import CLEARTYPE_FONTS, DEV_FONTS, FontCategory
from font_installer.config.settings import Settings
from font_installer.core.exceptions import DependencyError, DownloadError
from font_installer.core.installer import FontInstaller


class TestSettings:
    """Tests for Settings class."""

    def test_font_directories_defined(self):
        """Test that font directories are properly defined."""
        assert Settings.MICROSOFT_FONTS_DIR is not None
        assert Settings.DEV_FONTS_DIR is not None
        assert Settings.FONTS_BASE_DIR is not None

    def test_font_extensions(self):
        """Test that font extensions are defined."""
        assert ".ttf" in Settings.FONT_EXTENSIONS
        assert ".otf" in Settings.FONT_EXTENSIONS
        assert ".ttc" in Settings.FONT_EXTENSIONS

    def test_required_tools(self):
        """Test that required tools are defined."""
        assert "cabextract" in Settings.REQUIRED_TOOLS
        assert "fc-cache" in Settings.REQUIRED_TOOLS


class TestFontDefinitions:
    """Tests for font definitions."""

    def test_cleartype_fonts_not_empty(self):
        """Test that ClearType fonts are defined."""
        assert len(CLEARTYPE_FONTS) > 0

    def test_dev_fonts_not_empty(self):
        """Test that dev fonts are defined."""
        assert len(DEV_FONTS) > 0

    def test_cleartype_fonts_have_correct_category(self):
        """Test that ClearType fonts have correct category."""
        for font in CLEARTYPE_FONTS.values():
            assert font.category == FontCategory.CLEARTYPE

    def test_dev_fonts_have_repos(self):
        """Test that dev fonts have GitHub repos defined."""
        for font in DEV_FONTS.values():
            assert font.repo is not None
            assert "/" in font.repo  # Format: owner/repo


class TestFontInstaller:
    """Tests for FontInstaller class."""

    def test_check_dependencies_returns_tuple(self):
        """Test that check_dependencies returns correct type."""
        result = FontInstaller.check_dependencies()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)

    def test_installer_creation(self):
        """Test that installer can be created."""
        installer = FontInstaller()
        assert installer is not None

    def test_installer_with_callback(self):
        """Test that installer accepts callback."""
        progress_data = []

        def callback(progress):
            progress_data.append(progress)

        installer = FontInstaller(progress_callback=callback)
        assert installer is not None


class TestExceptions:
    """Tests for custom exceptions."""

    def test_download_error(self):
        """Test DownloadError exception."""
        error = DownloadError("http://example.com", "timeout")
        assert "example.com" in str(error)
        assert error.url == "http://example.com"
        assert error.reason == "timeout"

    def test_dependency_error(self):
        """Test DependencyError exception."""
        error = DependencyError(["cabextract", "fc-cache"])
        assert "cabextract" in str(error)
        assert "fc-cache" in str(error)
        assert len(error.missing_tools) == 2
