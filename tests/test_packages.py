"""Distribution support without running package managers on the host."""

import subprocess
from unittest.mock import Mock

import pytest

from font_installer.core import packages
from font_installer.core.installer import FontInstaller
from font_installer.utils.system import SystemChecker


@pytest.fixture
def linux(monkeypatch):
    monkeypatch.setattr(packages.platform, "system", lambda: "Linux")
    monkeypatch.setattr(packages.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(packages.shutil, "which", lambda name: f"/usr/bin/{name}")


@pytest.mark.parametrize(
    "release, manager, command",
    [
        ({"ID": "ubuntu"}, "apt", ["apt", "install", "-y"]),
        ({"ID": "debian"}, "apt", ["apt", "install", "-y"]),
        ({"ID": "fedora"}, "dnf", ["dnf", "install", "-y"]),
        ({"ID": "arch"}, "pacman", ["pacman", "-S", "--needed", "--noconfirm"]),
        (
            {"ID": "manjaro", "ID_LIKE": "arch"},
            "pacman",
            ["pacman", "-S", "--needed", "--noconfirm"],
        ),
        (
            {"ID": "opensuse-tumbleweed", "ID_LIKE": "opensuse suse"},
            "zypper",
            ["zypper", "--non-interactive", "install"],
        ),
        ({"ID": "opensuse-leap"}, "zypper", ["zypper", "--non-interactive", "install"]),
        ({"ID": "alpine"}, "apk", ["apk", "add"]),
        (
            {"ID": "linuxmint", "ID_LIKE": "ubuntu debian"},
            "apt",
            ["apt", "install", "-y"],
        ),
        ({"ID": "fedora", "ID_LIKE": "debian"}, "dnf", ["dnf", "install", "-y"]),
    ],
)
def test_distribution_install_commands(linux, monkeypatch, release, manager, command):
    monkeypatch.setattr(packages.platform, "freedesktop_os_release", lambda: release)
    run = Mock()
    monkeypatch.setattr(packages.subprocess, "run", run)

    selected = packages.detect_package_manager()
    assert selected.name == manager
    selected.install(["cabextract", "fontconfig"])
    commands = [call.args[0] for call in run.call_args_list]
    assert commands[-1] == ["sudo", *command, "cabextract", "fontconfig"]
    assert commands[:-1] == ([["sudo", "apt", "update"]] if manager == "apt" else [])
    assert all(call.kwargs["check"] for call in run.call_args_list)


def test_unknown_distribution_does_not_use_available_apt(linux, monkeypatch):
    monkeypatch.setattr(
        packages.platform, "freedesktop_os_release", lambda: {"ID": "unknown"}
    )
    with pytest.raises(packages.PackageManagerError, match="suportada"):
        packages.detect_package_manager()


def test_missing_os_release(linux, monkeypatch):
    def unavailable():
        raise OSError("missing os-release")

    monkeypatch.setattr(packages.platform, "freedesktop_os_release", unavailable)
    with pytest.raises(packages.PackageManagerError, match="distribuicao"):
        packages.detect_package_manager()


def test_non_linux_rejected(linux, monkeypatch):
    monkeypatch.setattr(packages.platform, "system", lambda: "Darwin")
    assert SystemChecker.get_system_info().is_linux is False
    with pytest.raises(packages.PackageManagerError, match="Linux"):
        packages.detect_package_manager()


@pytest.fixture
def fedora(linux, monkeypatch):
    monkeypatch.setattr(
        packages.platform, "freedesktop_os_release", lambda: {"ID": "fedora"}
    )


def test_missing_manager_does_not_fall_back(fedora, monkeypatch):
    monkeypatch.setattr(
        packages.shutil, "which", lambda name: None if name == "dnf" else f"/bin/{name}"
    )
    with pytest.raises(packages.PackageManagerError, match="dnf"):
        packages.detect_package_manager()


def test_root_does_not_need_sudo(fedora, monkeypatch):
    monkeypatch.setattr(packages.os, "geteuid", lambda: 0)
    monkeypatch.setattr(
        packages.shutil,
        "which",
        lambda name: None if name == "sudo" else f"/bin/{name}",
    )
    run = Mock()
    monkeypatch.setattr(packages.subprocess, "run", run)
    packages.detect_package_manager().install(["fontconfig"])
    assert run.call_args.args[0] == ["dnf", "install", "-y", "fontconfig"]


def test_missing_sudo_reports_privileges(fedora, monkeypatch):
    monkeypatch.setattr(
        packages.shutil,
        "which",
        lambda name: None if name == "sudo" else f"/bin/{name}",
    )
    with pytest.raises(packages.PackageManagerError, match="root|sudo"):
        packages.detect_package_manager().install(["fontconfig"])


def test_install_only_missing_packages(fedora, monkeypatch):
    checks = Mock(side_effect=[(False, ["fc-cache"]), (True, [])])
    monkeypatch.setattr(FontInstaller, "check_dependencies", checks)
    run = Mock()
    monkeypatch.setattr(packages.subprocess, "run", run)
    assert FontInstaller.install_dependencies()[0] is True
    assert run.call_args.args[0] == ["sudo", "dnf", "install", "-y", "fontconfig"]


def test_present_dependencies_do_not_require_supported_distribution(monkeypatch):
    monkeypatch.setattr(FontInstaller, "check_dependencies", lambda: (True, []))
    assert FontInstaller.install_dependencies()[0] is True


def test_install_rechecks_tools(fedora, monkeypatch):
    monkeypatch.setattr(
        FontInstaller, "check_dependencies", lambda: (False, ["cabextract"])
    )
    monkeypatch.setattr(packages.subprocess, "run", Mock())
    success, message = FontInstaller.install_dependencies()
    assert success is False
    assert "cabextract" in message


@pytest.mark.parametrize(
    "error",
    [
        subprocess.CalledProcessError(1, "dnf"),
        FileNotFoundError("dnf"),
        PermissionError("denied"),
    ],
)
def test_command_failure_is_returned(fedora, monkeypatch, error):
    monkeypatch.setattr(
        FontInstaller, "check_dependencies", lambda: (False, ["cabextract"])
    )
    monkeypatch.setattr(packages.subprocess, "run", Mock(side_effect=error))
    success, message = FontInstaller.install_dependencies()
    assert success is False
    assert "dnf" in message


def test_core_fonts_unsupported_without_running_apt(linux, monkeypatch):
    monkeypatch.setattr(
        packages.platform, "freedesktop_os_release", lambda: {"ID": "arch"}
    )
    run = Mock()
    monkeypatch.setattr(packages.subprocess, "run", run)
    result = FontInstaller.install_core_fonts()
    assert result.success is False
    assert "Ubuntu/Debian" in result.message
    run.assert_not_called()


def test_core_fonts_on_debian(linux, monkeypatch):
    monkeypatch.setattr(
        packages.platform, "freedesktop_os_release", lambda: {"ID": "debian"}
    )
    run = Mock()
    monkeypatch.setattr(packages.subprocess, "run", run)
    assert FontInstaller.install_core_fonts().success is True
    assert run.call_args.args[0] == [
        "sudo",
        "apt",
        "install",
        "-y",
        "ttf-mscorefonts-installer",
    ]


def test_hint_uses_package_names(fedora):
    assert "dnf install -y cabextract fontconfig" in packages.dependency_install_hint()


def test_hint_for_unknown_distribution(linux, monkeypatch):
    monkeypatch.setattr(
        packages.platform, "freedesktop_os_release", lambda: {"ID": "unknown"}
    )
    hint = packages.dependency_install_hint()
    assert "manualmente" in hint
    assert "fontconfig" in hint
