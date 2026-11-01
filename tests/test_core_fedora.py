"""Fedora invokes the bundled script/RPM instead of an installed RPM package."""

import io
from pathlib import Path
from unittest.mock import Mock

import pytest

from font_installer.config.settings import Settings
from font_installer.core import installer as installer_module
from font_installer.core import packages
from font_installer.core.downloader import Downloader
from font_installer.core.installer import FontInstaller
from font_installer.utils.system import SystemChecker


@pytest.fixture
def fedora_core(monkeypatch, tmp_path):
    monkeypatch.setattr(packages.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        packages.platform, "freedesktop_os_release", lambda: {"ID": "fedora"}
    )
    monkeypatch.setattr(packages.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        Settings, "CORE_FONTS_DIR", tmp_path / "fonts with spaces" / "microsoft-core"
    )
    install = Mock(side_effect=AssertionError("must not install the RPM as a package"))
    monkeypatch.setattr(packages.PackageManager, "install", install)

    def forbidden_download(*args, **kwargs):
        raise AssertionError(
            "Fedora must use the bundled script, not the Python archive downloader"
        )

    monkeypatch.setattr(Downloader, "download_file", forbidden_download)
    return install


def fake_process(monkeypatch, *, code=0, fonts=True):
    def popen(command, **kwargs):
        assert command[0] == "bash"
        script = Path(command[1])
        assert script.name == "msttcore.sh" and script.is_file()
        assert (script.parent / "msttcore-fonts-installer-2.6-1.noarch.rpm").is_file()
        assert Path(command[2]) == Settings.CORE_FONTS_DIR
        if fonts:
            Settings.CORE_FONTS_DIR.mkdir(parents=True, exist_ok=True)
            for name in ("arial.ttf", "calibri.ttf"):
                (Settings.CORE_FONTS_DIR / name).write_bytes(b"font")

        class Process:
            stdout = io.StringIO(
                "Extraindo fontes do RPM local\nFONT_INSTALLER_FILES_INSTALLED=2\n"
                if code == 0
                else "Falha de download: offline\n"
            )

            def wait(self):
                return code

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        return Process()

    monkeypatch.setattr(installer_module.subprocess, "Popen", popen)


def test_fedora_uses_bundled_script_and_rpm(fedora_core, monkeypatch):
    fake_process(monkeypatch)
    progress = []
    result = FontInstaller.install_core_fonts(progress_callback=progress.append)
    assert result.success, result.message
    assert result.files_installed == 2
    assert result.files_expected == 2
    assert "msttcore.sh" in result.message
    assert any("RPM local" in p.status for p in progress)
    fedora_core.assert_not_called()


def test_fedora_script_failure_returns_actionable_result(fedora_core, monkeypatch):
    fake_process(monkeypatch, code=1, fonts=False)
    result = FontInstaller.install_core_fonts()
    assert not result.success and result.files_installed == 0
    assert "offline" in result.message


def test_script_success_without_required_fonts_is_failure(fedora_core, monkeypatch):
    fake_process(monkeypatch, fonts=False)
    result = FontInstaller.install_core_fonts()
    assert not result.success
    assert "arial.ttf" in result.message


def test_installed_core_fonts_are_listed_and_counted(monkeypatch, tmp_path):
    monkeypatch.setattr(Settings, "MICROSOFT_FONTS_DIR", tmp_path / "microsoft")
    monkeypatch.setattr(Settings, "DEV_FONTS_DIR", tmp_path / "dev")
    monkeypatch.setattr(Settings, "CORE_FONTS_DIR", tmp_path / "microsoft-core")
    Settings.CORE_FONTS_DIR.mkdir()
    (Settings.CORE_FONTS_DIR / "arial.ttf").write_bytes(b"font")
    assert SystemChecker.list_installed_fonts()["core"] == ["arial.ttf"]
    assert SystemChecker.get_installed_fonts_count() == 1
