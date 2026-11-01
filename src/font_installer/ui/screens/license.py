"""Core Fonts license, supplied as a verified offline resource."""

import hashlib
from importlib.resources import files

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ..styles import MODAL_CSS

LICENSE_SHA256 = "117d4a7c95b35fa1b934d46c55f62983fc3b07b1a6e05d4a83b10eb33bbbbf79"


def load_license() -> str:
    data = (
        files("font_installer.ui").joinpath("assets/core-fonts-eula.txt").read_bytes()
    )
    if hashlib.sha256(data).hexdigest() != LICENSE_SHA256:
        raise ValueError("Integridade da licença não confere")
    return data.decode("utf-8")


class CoreFontsLicenseScreen(ModalScreen[bool]):
    DEFAULT_CSS = MODAL_CSS
    BINDINGS = [("escape", "decline", "Não aceitar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Static("Licença • Microsoft Core Fonts", classes="dialog-title")
            yield Static(
                "Leia os termos. Fedora instala no seu usuário; no Debian/Ubuntu, o pacote pode pedir confirmação no terminal."
            )
            with VerticalScroll(classes="dialog-content"):
                try:
                    text = load_license()
                except (OSError, ValueError):
                    text = "Licença indisponível. Retorne e desmarque Core Fonts para continuar."
                    self._unavailable = True
                yield Static(Text(text))
            with Horizontal(classes="dialog-actions"):
                yield Button("Não aceitar", id="license-decline")
                yield Button(
                    "Aceitar e continuar",
                    id="license-accept",
                    disabled=getattr(self, "_unavailable", False),
                )

    def on_mount(self) -> None:
        self.query_one("#license-decline", Button).focus()

    def action_decline(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "license-accept")
