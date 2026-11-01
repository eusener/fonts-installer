"""Exit confirmation without cancelling active work."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ..styles import MODAL_CSS


class ConfirmExitScreen(ModalScreen[bool]):
    DEFAULT_CSS = MODAL_CSS
    BINDINGS = [("escape", "stay", "Continuar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog exit-dialog"):
            yield Static("Sair após concluir o lote?", classes="dialog-title")
            yield Static(
                "A instalação atual e os próximos itens serão concluídos antes de sair."
            )
            with Horizontal(classes="dialog-actions"):
                yield Button("Continuar no aplicativo", id="exit-stay")
                yield Button("Concluir lote e sair", id="exit-after")

    def on_mount(self) -> None:
        self.query_one("#exit-stay", Button).focus()

    def action_stay(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "exit-after")
