"""Font extraction from various archive formats."""

import os
import subprocess
import zipfile
from pathlib import Path

from ..config.settings import Settings
from .exceptions import ExtractionError


class FontExtractor:
    """Extracts font files from archives."""

    @staticmethod
    def _is_font_file(path: Path) -> bool:
        """Check if file is a font file."""
        return path.suffix.lower() in Settings.FONT_EXTENSIONS

    @staticmethod
    def _find_fonts_in_directory(directory: Path) -> list[Path]:
        """Recursively find all font files in a directory."""
        fonts = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if FontExtractor._is_font_file(file_path):
                    fonts.append(file_path)
        return fonts

    def extract_from_cab(self, archive_path: Path, output_dir: Path) -> list[Path]:
        """
        Extract fonts from Windows cabinet/executable file.

        Args:
            archive_path: Path to .exe or .cab file
            output_dir: Directory to extract to

        Returns:
            List of extracted font file paths

        Raises:
            ExtractionError: If extraction fails
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        fonts_found: list[Path] = []

        try:
            # First extraction attempt
            result = subprocess.run(
                ["cabextract", "-L", "-d", str(output_dir), str(archive_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise ExtractionError(str(archive_path), result.stderr)

            # Find fonts after first extraction
            fonts_found = self._find_fonts_in_directory(output_dir)

            # If no fonts found, try nested archives
            if not fonts_found:
                fonts_found = self._extract_nested(output_dir)

        except subprocess.SubprocessError as e:
            raise ExtractionError(str(archive_path), str(e))

        return fonts_found

    def _extract_nested(self, directory: Path) -> list[Path]:
        """Extract fonts from nested archives within a directory."""
        fonts_found: list[Path] = []

        # Try nested .exe files
        for exe_file in directory.rglob("*.exe"):
            try:
                subprocess.run(
                    ["cabextract", "-L", "-d", str(directory), str(exe_file)],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                continue

        # Try nested .cab files
        for cab_file in directory.rglob("*.cab"):
            try:
                subprocess.run(
                    ["cabextract", "-L", "-d", str(directory), str(cab_file)],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                continue

        # Collect all fonts after nested extraction
        fonts_found = self._find_fonts_in_directory(directory)
        return fonts_found

    def extract_from_zip(self, zip_path: Path, output_dir: Path) -> list[Path]:
        """
        Extract fonts from ZIP archive.

        Args:
            zip_path: Path to .zip file
            output_dir: Directory to extract to

        Returns:
            List of extracted font file paths

        Raises:
            ExtractionError: If extraction fails
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(output_dir)
        except zipfile.BadZipFile as e:
            raise ExtractionError(str(zip_path), str(e))

        # Find fonts, preferring static versions over variable
        fonts_found: list[Path] = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                if not file.startswith(".") and self._is_font_file(Path(file)):
                    file_path = Path(root) / file
                    # Prefer static fonts over variable fonts
                    if "static" in str(root).lower() or "variable" not in file.lower():
                        fonts_found.append(file_path)

        # Fallback: get all fonts if no static fonts found
        if not fonts_found:
            fonts_found = self._find_fonts_in_directory(output_dir)

        return fonts_found
