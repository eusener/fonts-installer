"""End-to-end integration tests for font installer."""

import os
import platform
import shutil
import subprocess

import pytest

from font_installer.config.settings import Settings
from font_installer.core.installer import FontInstaller


def _require_integration() -> None:
    if os.environ.get("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 to run integration tests.")


def _require_linux() -> None:
    if platform.system() != "Linux":
        pytest.skip("Integration tests require Linux.")


def _require_sudo_non_interactive() -> None:
    if shutil.which("sudo") is None:
        pytest.skip("sudo not available.")
    try:
        subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pytest.skip("Passwordless sudo required for apt tests.")


def _require_apt() -> None:
    if shutil.which("apt") is None:
        pytest.skip("apt not available.")


@pytest.mark.integration
def test_install_dev_font_end_to_end(tmp_path, monkeypatch):
    _require_integration()
    _require_linux()

    monkeypatch.setattr(Settings, "DEV_FONTS_DIR", tmp_path / "dev")
    monkeypatch.setattr(Settings, "FONTS_BASE_DIR", tmp_path)

    installer = FontInstaller()
    result = installer.install_dev_font("cascadia")

    assert result.success is True
    assert result.files_installed > 0
    assert any((tmp_path / "dev").rglob("*.ttf")) or any(
        (tmp_path / "dev").rglob("*.otf")
    )


@pytest.mark.integration
def test_install_cleartype_end_to_end(tmp_path, monkeypatch):
    _require_integration()
    _require_linux()

    monkeypatch.setattr(Settings, "MICROSOFT_FONTS_DIR", tmp_path / "microsoft")
    monkeypatch.setattr(Settings, "FONTS_BASE_DIR", tmp_path)

    installer = FontInstaller()
    result = installer.install_cleartype_fonts()

    assert result.success is True
    assert result.files_installed > 0
    assert any((tmp_path / "microsoft").rglob("*.ttf")) or any(
        (tmp_path / "microsoft").rglob("*.otf")
    )


@pytest.mark.integration
@pytest.mark.requires_sudo
def test_install_dependencies_via_apt():
    _require_integration()
    _require_linux()
    _require_apt()
    _require_sudo_non_interactive()

    ok, message = FontInstaller.install_dependencies()
    assert ok is True
    assert message

    ok, missing = FontInstaller.check_dependencies()
    assert ok is True
    assert missing == []


@pytest.mark.integration
@pytest.mark.requires_sudo
def test_install_core_fonts_via_apt():
    _require_integration()
    if os.environ.get("RUN_CORE_FONTS") != "1":
        pytest.skip("Set RUN_CORE_FONTS=1 to run core fonts install test.")
    _require_linux()
    _require_apt()
    _require_sudo_non_interactive()

    result = FontInstaller.install_core_fonts()
    assert result.success is True
    assert result.files_installed >= 1
