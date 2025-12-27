"""System utilities and checks."""

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..config.settings import Settings


@dataclass
class SystemInfo:
    """System information for diagnostics."""

    fonts_dir: Path
    fonts_count: int
    has_cabextract: bool
    has_fc_cache: bool
    is_linux: bool


class SystemChecker:
    """System environment checker."""

    @staticmethod
    def get_installed_fonts_count() -> int:
        """Count installed fonts in our directories."""
        count = 0
        for directory in [Settings.MICROSOFT_FONTS_DIR, Settings.DEV_FONTS_DIR]:
            if directory.exists():
                for ext in Settings.FONT_EXTENSIONS:
                    count += len(list(directory.glob(f"*{ext}")))
        return count

    @staticmethod
    def list_installed_fonts() -> dict[str, list[str]]:
        """
        List all installed fonts by category.

        Returns:
            Dictionary with 'microsoft' and 'dev' font lists
        """
        result: dict[str, list[str]] = {"microsoft": [], "dev": []}

        if Settings.MICROSOFT_FONTS_DIR.exists():
            result["microsoft"] = sorted(
                f.name
                for f in Settings.MICROSOFT_FONTS_DIR.iterdir()
                if f.suffix.lower() in Settings.FONT_EXTENSIONS
            )

        if Settings.DEV_FONTS_DIR.exists():
            result["dev"] = sorted(
                f.name
                for f in Settings.DEV_FONTS_DIR.iterdir()
                if f.suffix.lower() in Settings.FONT_EXTENSIONS
            )

        return result

    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get system information for diagnostics."""
        return SystemInfo(
            fonts_dir=Settings.FONTS_BASE_DIR,
            fonts_count=SystemChecker.get_installed_fonts_count(),
            has_cabextract=shutil.which("cabextract") is not None,
            has_fc_cache=shutil.which("fc-cache") is not None,
            is_linux=os.name == "posix",
        )

    @staticmethod
    def verify_font_available(font_name: str) -> bool:
        """
        Check if a font is available in the system.

        Args:
            font_name: Font family name to check

        Returns:
            True if font is available
        """
        try:
            result = subprocess.run(
                ["fc-list", font_name],
                capture_output=True,
                text=True,
            )
            return bool(result.stdout.strip())
        except subprocess.SubprocessError:
            return False
