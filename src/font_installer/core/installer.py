"""Main font installation orchestrator."""

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..config.fonts import DEV_FONTS, FontInfo
from ..config.settings import Settings
from .downloader import Downloader, DownloadProgress, ProgressCallback
from .exceptions import DependencyError, InstallationError
from .extractor import FontExtractor


@dataclass
class InstallResult:
    """Result of a font installation operation."""

    success: bool
    font_name: str
    files_installed: int
    message: str


class FontInstaller:
    """
    Orchestrates the complete font installation process.

    Handles downloading, extracting, and installing fonts with
    progress reporting and error handling.
    """

    def __init__(self, progress_callback: ProgressCallback | None = None):
        self._callback = progress_callback
        self._downloader = Downloader(progress_callback)
        self._extractor = FontExtractor()

    def _report(self, name: str, percent: int, status: str) -> None:
        """Report progress."""
        if self._callback:
            self._callback(DownloadProgress(name=name, percent=percent, status=status))

    @staticmethod
    def check_dependencies() -> tuple[bool, list[str]]:
        """
        Check if required system tools are installed.

        Returns:
            Tuple of (all_present, missing_tools)
        """
        missing = [
            tool for tool in Settings.REQUIRED_TOOLS if shutil.which(tool) is None
        ]
        return len(missing) == 0, missing

    @staticmethod
    def install_dependencies() -> tuple[bool, str]:
        """
        Install required system dependencies via apt.

        Requires sudo privileges.

        Returns:
            Tuple of (success, message)
        """
        ok, missing = FontInstaller.check_dependencies()
        if ok:
            return True, "Todas as dependencias ja estao instaladas"

        # Map tool names to apt package names
        apt_packages = {
            "cabextract": "cabextract",
            "fc-cache": "fontconfig",
        }

        packages_to_install = [apt_packages.get(tool, tool) for tool in missing]

        try:
            # Update apt cache
            subprocess.run(
                ["sudo", "apt", "update"],
                check=True,
                capture_output=True,
            )

            # Install packages
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + packages_to_install,
                check=True,
            )

            # Verify installation
            ok, still_missing = FontInstaller.check_dependencies()
            if ok:
                return True, f"Dependencias instaladas: {', '.join(packages_to_install)}"
            else:
                return False, f"Falha ao instalar: {', '.join(still_missing)}"

        except subprocess.CalledProcessError as e:
            return False, f"Erro ao executar apt: {e}"
        except FileNotFoundError:
            return False, "Comando apt nao encontrado. Este programa requer Ubuntu/Debian."

    @staticmethod
    def ensure_dependencies() -> None:
        """
        Verify dependencies and raise if missing.

        Raises:
            DependencyError: If required tools are not installed
        """
        ok, missing = FontInstaller.check_dependencies()
        if not ok:
            raise DependencyError(missing)

    def _install_fonts_to_dir(self, fonts: list[Path], target_dir: Path) -> int:
        """
        Copy font files to target directory.

        Returns:
            Number of files installed
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        installed = 0

        for font in fonts:
            dest = target_dir / font.name.lower()
            try:
                shutil.copy2(font, dest)
                installed += 1
            except (shutil.Error, OSError):
                continue

        return installed

    def install_cleartype_fonts(self) -> InstallResult:
        """
        Install Microsoft ClearType fonts from PowerPoint Viewer.

        Returns:
            InstallResult with installation status
        """
        self._report("ClearType", 0, "Iniciando instalacao...")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            ppviewer = tmppath / "PowerPointViewer.exe"

            try:
                # Download PowerPoint Viewer
                self._downloader.download_file(
                    Settings.POWERPOINT_VIEWER_URL, ppviewer, "ClearType"
                )

                # Extract fonts
                self._report("ClearType", 100, "Extraindo fontes...")
                fonts = self._extractor.extract_from_cab(
                    ppviewer, tmppath / "extracted"
                )

                if not fonts:
                    return InstallResult(
                        success=False,
                        font_name="ClearType",
                        files_installed=0,
                        message="Nenhuma fonte encontrada no arquivo",
                    )

                # Install fonts
                self._report("ClearType", 100, "Instalando fontes...")
                installed = self._install_fonts_to_dir(
                    fonts, Settings.MICROSOFT_FONTS_DIR
                )

                self._report("ClearType", 100, f"{installed} fontes instaladas!")
                return InstallResult(
                    success=True,
                    font_name="ClearType",
                    files_installed=installed,
                    message=f"{installed} fontes instaladas com sucesso",
                )

            except Exception as e:
                return InstallResult(
                    success=False,
                    font_name="ClearType",
                    files_installed=0,
                    message=str(e),
                )

    def install_dev_font(self, font_key: str) -> InstallResult:
        """
        Install a developer font from GitHub.

        Args:
            font_key: Key from DEV_FONTS dictionary

        Returns:
            InstallResult with installation status
        """
        if font_key not in DEV_FONTS:
            return InstallResult(
                success=False,
                font_name=font_key,
                files_installed=0,
                message=f"Fonte desconhecida: {font_key}",
            )

        font_info = DEV_FONTS[font_key]
        font_name = font_info.name

        self._report(font_name, 0, "Buscando release...")

        # Get download URL from GitHub
        url = self._downloader.get_github_release_url(
            font_info.repo, font_info.asset_pattern
        )

        if not url:
            return InstallResult(
                success=False,
                font_name=font_name,
                files_installed=0,
                message="Release nao encontrada no GitHub",
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            zip_path = tmppath / f"{font_key}.zip"

            try:
                # Download
                self._downloader.download_file(url, zip_path, font_name)

                # Extract
                self._report(font_name, 100, "Extraindo fontes...")
                fonts = self._extractor.extract_from_zip(zip_path, tmppath / font_key)

                if not fonts:
                    return InstallResult(
                        success=False,
                        font_name=font_name,
                        files_installed=0,
                        message="Nenhuma fonte encontrada no arquivo",
                    )

                # Install
                self._report(font_name, 100, "Instalando fontes...")
                installed = self._install_fonts_to_dir(fonts, Settings.DEV_FONTS_DIR)

                self._report(font_name, 100, f"{installed} arquivos instalados!")
                return InstallResult(
                    success=True,
                    font_name=font_name,
                    files_installed=installed,
                    message=f"{installed} arquivos instalados com sucesso",
                )

            except Exception as e:
                return InstallResult(
                    success=False,
                    font_name=font_name,
                    files_installed=0,
                    message=str(e),
                )

    @staticmethod
    def install_core_fonts() -> InstallResult:
        """
        Install Microsoft Core Fonts via apt.

        Requires sudo privileges.

        Returns:
            InstallResult with installation status
        """
        try:
            subprocess.run(
                ["sudo", "apt", "install", "-y", "ttf-mscorefonts-installer"],
                check=True,
            )
            return InstallResult(
                success=True,
                font_name="Core Fonts",
                files_installed=1,
                message="Core Fonts instaladas via apt",
            )
        except subprocess.CalledProcessError as e:
            return InstallResult(
                success=False,
                font_name="Core Fonts",
                files_installed=0,
                message=f"Erro ao executar apt: {e}",
            )

    @staticmethod
    def update_font_cache() -> bool:
        """
        Update system font cache.

        Returns:
            True if successful
        """
        try:
            subprocess.run(
                ["fc-cache", "-f", str(Settings.FONTS_BASE_DIR)],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
