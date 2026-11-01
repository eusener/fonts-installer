"""Main font installation orchestrator."""

import os
import shutil
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from ..config.fonts import DEV_FONTS
from ..config.settings import Settings
from .downloader import Downloader, DownloadProgress, ProgressCallback, emit_progress
from .exceptions import (
    DependencyError,
    DownloadError,
    ExtractionError,
    InstallationError,
)
from .extractor import FontExtractor
from .packages import PackageManagerError, detect_package_manager


@dataclass
class InstallResult:
    """Result of a font installation operation."""

    success: bool
    font_name: str
    files_installed: int
    message: str
    files_expected: int | None = None


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

    def _report(self, name: str, phase: str, event: str, status: str) -> None:
        emit_progress(
            self._callback, DownloadProgress(name, 0, status, phase=phase, event=event)
        )

    @staticmethod
    def check_dependencies() -> tuple[bool, list[str]]:
        """
        Check if required system tools are installed.

        Returns:
            Tuple of (all_present, missing_tools)
        """
        tools = list(Settings.REQUIRED_TOOLS)
        try:
            if detect_package_manager().name == "dnf":
                tools.extend(("bash", "rpm2cpio", "cpio", "curl"))
        except PackageManagerError:
            pass
        missing = [tool for tool in tools if shutil.which(tool) is None]
        return len(missing) == 0, missing

    @staticmethod
    def install_dependencies() -> tuple[bool, str]:
        """
        Install required system dependencies using the native package manager.

        Requires root or sudo privileges.

        Returns:
            Tuple of (success, message)
        """
        ok, missing = FontInstaller.check_dependencies()
        if ok:
            return True, "Todas as dependencias ja estao instaladas"

        package_names = {
            "cabextract": "cabextract",
            "fc-cache": "fontconfig",
            "rpm2cpio": "rpm",
        }
        packages_to_install = list(
            dict.fromkeys(package_names.get(tool, tool) for tool in missing)
        )
        try:
            manager = detect_package_manager()
        except PackageManagerError as error:
            return False, str(error)

        try:
            manager.install(packages_to_install)
            ok, still_missing = FontInstaller.check_dependencies()
            if ok:
                return (
                    True,
                    f"Dependencias instaladas: {', '.join(packages_to_install)}",
                )
            return False, f"Falha ao instalar: {', '.join(still_missing)}"
        except (PackageManagerError, subprocess.SubprocessError, OSError) as error:
            return False, f"Erro ao executar {manager.name}: {error}"

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

    def _install_archive(
        self,
        name: str,
        target: Path,
        *,
        url: str | None = None,
        repo: str | None = None,
        pattern: str = "",
    ) -> InstallResult:
        phase = "lookup"
        installed = 0
        expected = None
        try:
            if repo:
                self._report(name, phase, "started", "Buscando release")
                url = self._downloader.get_github_release_url(repo, pattern)
                self._report(name, phase, "completed", "Consulta concluída")
            if not url:
                return InstallResult(
                    False, name, 0, "Release sem arquivo ZIP compatível"
                )
            with tempfile.TemporaryDirectory() as tmpdir:
                work = Path(tmpdir)
                archive = work / ("archive.exe" if repo is None else "archive.zip")
                phase = "download"
                self._downloader.download_file(url, archive, name)
                phase = "extract"
                self._report(name, phase, "started", "Extraindo fontes")
                extract = (
                    self._extractor.extract_from_cab
                    if repo is None
                    else self._extractor.extract_from_zip
                )
                fonts = extract(archive, work / "extracted")
                self._report(name, phase, "completed", "Extração concluída")
                expected = len(fonts)
                if not fonts:
                    return InstallResult(False, name, 0, "Nenhuma fonte encontrada", 0)
                phase = "copy"
                self._report(name, phase, "started", "Copiando fontes")
                installed = self._install_fonts_to_dir(fonts, target)
                complete = installed == expected
                message = f"{installed}/{expected} arquivos copiados"
                self._report(
                    name, phase, "completed" if complete else "failed", message
                )
            return InstallResult(complete, name, installed, message, expected)
        except (
            DownloadError,
            ExtractionError,
            InstallationError,
            OSError,
            shutil.Error,
            subprocess.SubprocessError,
        ) as error:
            self._report(name, phase, "failed", str(error))
            return InstallResult(False, name, installed, str(error), expected)

    def install_cleartype_fonts(self) -> InstallResult:
        return self._install_archive(
            "ClearType",
            Settings.MICROSOFT_FONTS_DIR,
            url=Settings.POWERPOINT_VIEWER_URL,
        )

    def install_dev_font(self, font_key: str) -> InstallResult:
        if font_key not in DEV_FONTS:
            return InstallResult(False, font_key, 0, f"Fonte desconhecida: {font_key}")
        info = DEV_FONTS[font_key]
        return self._install_archive(
            info.name,
            Settings.DEV_FONTS_DIR,
            repo=info.repo,
            pattern=info.asset_pattern or "",
        )

    @staticmethod
    def install_core_fonts(
        progress_callback: ProgressCallback | None = None,
    ) -> InstallResult:
        """
        Install via apt on Debian or the bundled script/RPM on Fedora.

        Debian package installation requires root or sudo; Fedora writes user fonts.

        Returns:
            InstallResult with installation status
        """
        try:
            manager = detect_package_manager()
            if manager.name == "dnf":
                installer = FontInstaller(progress_callback)
                return installer._install_core_fonts_script()
            if manager.name != "apt":
                raise PackageManagerError(
                    "Instalação automática de Core Fonts disponível em "
                    "Ubuntu/Debian e Fedora. ClearType e fontes Dev continuam disponíveis."
                )
            manager.install(["ttf-mscorefonts-installer"])
            return InstallResult(
                success=True,
                font_name="Core Fonts",
                files_installed=1,
                message="Core Fonts instaladas via apt",
            )
        except (PackageManagerError, subprocess.SubprocessError, OSError) as error:
            return InstallResult(
                success=False,
                font_name="Core Fonts",
                files_installed=0,
                message=f"Falha ao instalar Core Fonts: {error}",
            )

    def _install_core_fonts_script(self) -> InstallResult:
        """Run the bundled wrapper and RPM without installing a system package."""
        resources = files("font_installer.utils")
        count = 0
        tail: list[str] = []
        self._report(
            "Core Fonts", "package", "started", "Iniciando msttcore.sh com RPM local"
        )
        try:
            with tempfile.TemporaryDirectory(prefix="msttcore-bundle-") as tmpdir:
                bundle = Path(tmpdir)
                for name in (
                    "msttcore.sh",
                    "msttcore-fonts-installer-2.6-1.noarch.rpm",
                ):
                    (bundle / name).write_bytes(resources.joinpath(name).read_bytes())
                with subprocess.Popen(
                    ["bash", str(bundle / "msttcore.sh"), str(Settings.CORE_FONTS_DIR)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                    start_new_session=True,
                ) as process:
                    try:
                        assert process.stdout is not None
                        for raw in process.stdout:
                            line = raw.strip()
                            if line.startswith("FONT_INSTALLER_FILES_INSTALLED="):
                                value = line.partition("=")[2]
                                if value.isdigit():
                                    count = int(value)
                            elif line:
                                tail.append(line[:2048])
                                tail = tail[-8:]
                                self._report(
                                    "Core Fonts", "package", "progress", line[:2048]
                                )
                        code = process.wait()
                    except BaseException:
                        # Terminate only the process group created above, including download children.
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        raise
            if code:
                return InstallResult(
                    False,
                    "Core Fonts",
                    count,
                    f"msttcore.sh retornou {code}: " + " | ".join(tail),
                    count,
                )
            missing = [
                name
                for name in ("arial.ttf", "calibri.ttf")
                if not (Settings.CORE_FONTS_DIR / name).is_file()
                or (Settings.CORE_FONTS_DIR / name).stat().st_size == 0
            ]
            if missing or count == 0:
                return InstallResult(
                    False,
                    "Core Fonts",
                    0,
                    "msttcore.sh não confirmou fontes instaladas; ausentes: "
                    + ", ".join(missing),
                    0,
                )
            return InstallResult(
                True,
                "Core Fonts",
                count,
                f"msttcore.sh: {count} arquivos instalados em {Settings.CORE_FONTS_DIR}",
                count,
            )
        except (OSError, subprocess.SubprocessError) as error:
            return InstallResult(
                False,
                "Core Fonts",
                count,
                f"Falha ao executar msttcore.sh: {error}",
                count,
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
