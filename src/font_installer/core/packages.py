"""Distribution-aware system package installation."""

import os
import platform
import shlex
import shutil
import subprocess
from dataclasses import dataclass


class PackageManagerError(RuntimeError):
    """The current system cannot install packages automatically."""


@dataclass(frozen=True)
class PackageManager:
    """Commands for the native package manager of a Linux distribution."""

    name: str
    install_args: tuple[str, ...]
    update_args: tuple[str, ...] = ()

    def install(self, packages: list[str]) -> None:
        """Install packages, requesting privileges only when necessary."""
        prefix: list[str] = []
        if os.geteuid() != 0:
            if shutil.which("sudo") is None:
                raise PackageManagerError(
                    "Execute como root ou instale sudo para instalar pacotes."
                )
            prefix = ["sudo"]
        if self.update_args:
            subprocess.run(
                [*prefix, self.name, *self.update_args],
                check=True,
            )
        subprocess.run(
            [*prefix, self.name, *self.install_args, *packages],
            check=True,
        )


_APT = PackageManager("apt", ("install", "-y"), ("update",))
_DNF = PackageManager("dnf", ("install", "-y"))
_PACMAN = PackageManager("pacman", ("-S", "--needed", "--noconfirm"))
_ZYPPER = PackageManager("zypper", ("--non-interactive", "install"))
_APK = PackageManager("apk", ("add",))
_DISTRIBUTIONS = {
    "ubuntu": _APT,
    "debian": _APT,
    "fedora": _DNF,
    "arch": _PACMAN,
    "manjaro": _PACMAN,
    "opensuse": _ZYPPER,
    "opensuse-leap": _ZYPPER,
    "opensuse-tumbleweed": _ZYPPER,
    "suse": _ZYPPER,
    "alpine": _APK,
}


def detect_package_manager() -> PackageManager:
    """Use ID first, then ordered ID_LIKE values; never guess from PATH."""
    if platform.system() != "Linux":
        raise PackageManagerError("A instalacao automatica requer Linux.")
    try:
        release = platform.freedesktop_os_release()
    except OSError as error:
        raise PackageManagerError(
            "Nao foi possivel identificar a distribuicao Linux."
        ) from error

    candidates = [release.get("ID", ""), *release.get("ID_LIKE", "").split()]
    for candidate in candidates:
        manager = _DISTRIBUTIONS.get(candidate.lower())
        if manager is not None:
            if shutil.which(manager.name) is None:
                raise PackageManagerError(
                    f"Gerenciador {manager.name} nao encontrado nesta distribuicao."
                )
            return manager
    raise PackageManagerError(
        "Distribuicao nao suportada para instalacao automatica: "
        f"{release.get('ID', 'desconhecida')}."
    )


def dependency_install_hint() -> str:
    """Provide a native manual command, or portable package guidance."""
    try:
        manager = detect_package_manager()
    except PackageManagerError as error:
        return f"{error} Instale manualmente cabextract e fontconfig."
    prefix = [] if os.geteuid() == 0 else ["sudo"]
    commands = []
    if manager.update_args:
        commands.append(shlex.join([*prefix, manager.name, *manager.update_args]))
    commands.append(
        shlex.join(
            [*prefix, manager.name, *manager.install_args, "cabextract", "fontconfig"]
        )
    )
    return "Execute: " + " && ".join(commands)
