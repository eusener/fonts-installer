"""Application settings and configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    # Directories
    FONTS_BASE_DIR: ClassVar[Path] = Path.home() / ".local" / "share" / "fonts"
    MICROSOFT_FONTS_DIR: ClassVar[Path] = FONTS_BASE_DIR / "microsoft"
    DEV_FONTS_DIR: ClassVar[Path] = FONTS_BASE_DIR / "dev"

    # URLs
    POWERPOINT_VIEWER_URL: ClassVar[str] = (
        "https://web.archive.org/web/20171225132744if_/"
        "http://download.microsoft.com/download/E/6/7/"
        "E675FFFC-2A6D-4AB0-B3EB-27C9F8C8F696/PowerPointViewer.exe"
    )

    # GitHub API
    GITHUB_API_BASE: ClassVar[str] = "https://api.github.com/repos"
    USER_AGENT: ClassVar[str] = "FontInstaller/1.0"

    # Timeouts (seconds)
    DOWNLOAD_TIMEOUT: ClassVar[int] = 300
    API_TIMEOUT: ClassVar[int] = 30

    # Required system tools
    REQUIRED_TOOLS: ClassVar[tuple[str, ...]] = ("cabextract", "fc-cache")

    # Font file extensions
    FONT_EXTENSIONS: ClassVar[tuple[str, ...]] = (".ttf", ".ttc", ".otf")

    @classmethod
    def ensure_directories(cls) -> None:
        """Create font directories if they don't exist."""
        cls.MICROSOFT_FONTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DEV_FONTS_DIR.mkdir(parents=True, exist_ok=True)
