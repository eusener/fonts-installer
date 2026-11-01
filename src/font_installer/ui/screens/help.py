"""Help and font descriptions, outside the compact catalog."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ...config.fonts import DEV_FONTS
from ...config.settings import Settings
from ..styles import MODAL_CSS


class HelpScreen(ModalScreen):
    DEFAULT_CSS = MODAL_CSS
    BINDINGS = [("escape", "close", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Static("Ajuda • Font Installer", classes="dialog-title")
            with VerticalScroll(classes="dialog-content"):
                yield Static(
                    Text(
                        "Tab / Shift+Tab: navegar · Espaço: selecionar · Enter: ativar\n"
                        "a: selecionar ClearType/Dev · c: limpar seleção · i: instalar\n"
                        "l: logs · f: seguir log · r: limpar log/verificar · q: sair\n\n"
                        f"Microsoft: {Settings.MICROSOFT_FONTS_DIR}\n"
                        f"Dev: {Settings.DEV_FONTS_DIR}\n\n"
                        + "\n".join(
                            f"{info.name}: {info.description}"
                            for info in DEV_FONTS.values()
                        )
                    )
                )
            yield Button("Fechar", id="help-close")

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self) -> None:
        self.dismiss()
