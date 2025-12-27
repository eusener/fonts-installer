"""Main Textual TUI Application."""

from rich.text import Text

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    LoadingIndicator,
    ProgressBar,
    RichLog,
    Rule,
    Static,
    TabbedContent,
    TabPane,
)

from ..config.fonts import CLEARTYPE_FONTS, DEV_FONTS
from ..config.settings import Settings
from ..core.downloader import DownloadProgress
from ..core.installer import FontInstaller
from .styles import APP_CSS


class FontInstallerApp(App):
    """Interactive Font Installer TUI Application."""

    TITLE = "Font Installer"
    SUB_TITLE = "Instalador de Fontes para Ubuntu/Debian"
    CSS = APP_CSS

    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("a", "select_all", "Selecionar Tudo"),
        Binding("c", "clear_selection", "Limpar"),
        Binding("i", "install", "Instalar"),
        Binding("r", "refresh", "Atualizar"),
    ]

    def __init__(self):
        super().__init__()
        self._installer = FontInstaller(progress_callback=self._on_progress)
        self._is_installing = False

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        # Welcome Panel
        yield Static(
            "Font Installer - Selecione as fontes para instalar",
            id="welcome-panel",
        )

        # Status bar for dependencies
        yield Static("Verificando dependencias...", id="status-bar")

        # Dependencies Warning (hidden by default)
        yield Static(
            "AVISO: Dependencias faltando! Execute: sudo apt install cabextract fontconfig",
            id="deps-warning",
        )

        # Tabbed Content for Font Categories
        with TabbedContent(id="tabs-container"):
            # ClearType Fonts Tab
            with TabPane("ClearType", id="tab-cleartype"):
                with VerticalScroll():
                    yield Static(
                        "Microsoft ClearType Fonts",
                        classes="category-header",
                    )
                    yield Checkbox(
                        "Instalar fontes ClearType (~26 arquivos)",
                        id="cleartype-all",
                        classes="font-checkbox",
                    )
                    yield Static(
                        "Inclui: Calibri, Cambria, Consolas, Constantia, Corbel, Candara",
                        classes="font-list",
                    )
                    yield Rule()
                    yield Static(
                        "Fontes padrao do Microsoft Office, extraidas do PowerPoint Viewer.",
                        classes="font-list",
                    )

            # Developer Fonts Tab
            with TabPane("Dev Fonts", id="tab-dev"):
                with VerticalScroll():
                    yield Static(
                        "Fontes para Desenvolvimento",
                        classes="category-header",
                    )
                    for key, info in DEV_FONTS.items():
                        yield Checkbox(
                            f"{info.name}",
                            id=f"dev-{key}",
                            classes="font-checkbox",
                        )
                        yield Static(
                            f"{info.description}",
                            classes="font-list",
                        )

            # Core Fonts Tab
            with TabPane("Core Fonts", id="tab-core"):
                with VerticalScroll():
                    yield Static(
                        "Microsoft Core Fonts (via apt)",
                        classes="category-header",
                    )
                    yield Checkbox(
                        "Instalar Core Fonts (requer sudo)",
                        id="core-fonts",
                        classes="font-checkbox",
                    )
                    yield Static(
                        "Arial, Times New Roman, Verdana, Tahoma, Courier New, Georgia, etc.",
                        classes="font-list",
                    )
                    yield Rule()
                    yield Static(
                        "Instaladas via apt (ttf-mscorefonts-installer).",
                        classes="font-list",
                    )

            # Info Tab
            with TabPane("Info", id="tab-info"):
                with VerticalScroll():
                    # Directories section
                    yield Static("Diretorios de Instalacao", classes="info-title")
                    yield Static(
                        f"  Microsoft: {Settings.MICROSOFT_FONTS_DIR}",
                        classes="info-path",
                    )
                    yield Static(
                        f"  Dev Fonts: {Settings.DEV_FONTS_DIR}",
                        classes="info-path",
                    )
                    yield Rule()

                    # Shortcuts section
                    yield Static("Atalhos de Teclado", classes="info-title")
                    yield Static("  [a] Selecionar todas as fontes", classes="info-item")
                    yield Static("  [c] Limpar selecao", classes="info-item")
                    yield Static("  [i] Iniciar instalacao", classes="info-item")
                    yield Static("  [r] Atualizar/Limpar log", classes="info-item")
                    yield Static("  [q] Sair do programa", classes="info-item")
                    yield Rule()

                    # About section
                    yield Static("Sobre", classes="info-title")
                    yield Static("  Font Installer v1.0.0", classes="info-item")
                    yield Static("  Compativel com Ubuntu/Debian", classes="info-item")
                    yield Static("  github.com/seu-usuario/font-installer", classes="info-item")

        # Progress Section
        with Container(id="progress-container"):
            yield Static("Instalando Fontes", id="progress-header")
            yield Static("Aguardando...", id="progress-label")
            yield ProgressBar(id="progress-bar", total=100, show_eta=False, show_percentage=True)
            yield LoadingIndicator(id="installing-indicator")

        # Log Container
        with Vertical(id="log-container"):
            yield Static(" Log de Instalacao", id="log-header")
            yield RichLog(id="install-log", highlight=True, markup=True)

        # Action Buttons
        with Horizontal(id="action-buttons"):
            yield Button("Selecionar Tudo", id="select-all-btn")
            yield Button("Limpar", id="clear-btn")
            yield Button("Instalar", id="install-btn")

        yield Footer()

    def on_mount(self) -> None:
        """Check dependencies on mount."""
        status_bar = self.query_one("#status-bar", Static)
        ok, missing = FontInstaller.check_dependencies()

        if not ok:
            status_bar.update(f"Dependencias faltando: {', '.join(missing)}")
            status_bar.add_class("error")
            warning = self.query_one("#deps-warning")
            warning.add_class("visible")
            self._log("[bold red]Dependencias faltando![/]")
            self._log(f"[red]Faltando: {', '.join(missing)}[/]")
            self._log("[yellow]Execute: sudo apt install cabextract fontconfig[/]")
        else:
            status_bar.update("Todas as dependencias instaladas")
            status_bar.add_class("ok")
            self._log("[green]Sistema pronto![/] Todas as dependencias instaladas.")

    def _log(self, message: str) -> None:
        """Add a message to the log."""
        log = self.query_one("#install-log", RichLog)
        log.write(message)

    def _on_progress(self, progress: DownloadProgress) -> None:
        """Handle progress updates from the installer."""
        self.call_from_thread(self._update_progress, progress)

    def _update_progress(self, progress: DownloadProgress) -> None:
        """Update progress UI (called from main thread)."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_label = self.query_one("#progress-label", Static)

        # Update progress bar (percent is 0-100)
        progress_bar.progress = progress.percent
        progress_label.update(f"{progress.name}: {progress.status}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_actions = {
            "install-btn": self.action_install,
            "select-all-btn": self.action_select_all,
            "clear-btn": self.action_clear_selection,
        }
        action = button_actions.get(event.button.id)
        if action:
            action()

    def action_select_all(self) -> None:
        """Select all font checkboxes."""
        self.query_one("#cleartype-all", Checkbox).value = True
        for key in DEV_FONTS:
            try:
                self.query_one(f"#dev-{key}", Checkbox).value = True
            except Exception:
                pass
        self._log("[blue]Todas as fontes selecionadas[/]")

    def action_clear_selection(self) -> None:
        """Clear all font selections."""
        self.query_one("#cleartype-all", Checkbox).value = False
        try:
            self.query_one("#core-fonts", Checkbox).value = False
        except Exception:
            pass
        for key in DEV_FONTS:
            try:
                self.query_one(f"#dev-{key}", Checkbox).value = False
            except Exception:
                pass
        self._log("[yellow]Selecao limpa[/]")

    def action_install(self) -> None:
        """Start the installation process."""
        if self._is_installing:
            self._log("[yellow]Instalacao ja em andamento...[/]")
            return

        # Gather selections
        install_cleartype = self.query_one("#cleartype-all", Checkbox).value
        install_core = self.query_one("#core-fonts", Checkbox).value

        dev_fonts = [
            key
            for key in DEV_FONTS
            if self.query_one(f"#dev-{key}", Checkbox).value
        ]

        if not install_cleartype and not install_core and not dev_fonts:
            self._log("[yellow]Nenhuma fonte selecionada![/]")
            return

        self._run_installation(install_cleartype, install_core, dev_fonts)

    @work(thread=True)
    def _run_installation(
        self,
        install_cleartype: bool,
        install_core: bool,
        dev_fonts: list[str],
    ) -> None:
        """Run the installation in a background thread."""
        self._is_installing = True
        self.call_from_thread(self._show_progress, True)

        total_installed = 0

        try:
            # Install ClearType fonts
            if install_cleartype:
                self.call_from_thread(
                    self._log, "[bold cyan]>> Instalando fontes ClearType...[/]"
                )
                result = self._installer.install_cleartype_fonts()
                if result.success:
                    total_installed += result.files_installed
                    self.call_from_thread(
                        self._log,
                        f"[green]   ClearType: {result.files_installed} fontes instaladas[/]",
                    )
                else:
                    self.call_from_thread(
                        self._log, f"[red]   ClearType: {result.message}[/]"
                    )

            # Install Dev fonts
            for font_key in dev_fonts:
                font_name = DEV_FONTS[font_key].name
                self.call_from_thread(
                    self._log, f"[bold cyan]>> Instalando {font_name}...[/]"
                )
                result = self._installer.install_dev_font(font_key)
                if result.success:
                    total_installed += result.files_installed
                    self.call_from_thread(
                        self._log,
                        f"[green]   {font_name}: {result.files_installed} arquivos instalados[/]",
                    )
                else:
                    self.call_from_thread(
                        self._log, f"[red]   {font_name}: {result.message}[/]"
                    )

            # Install Core fonts
            if install_core:
                self.call_from_thread(
                    self._log, "[bold cyan]>> Instalando Core Fonts (sudo)...[/]"
                )
                result = FontInstaller.install_core_fonts()
                if result.success:
                    self.call_from_thread(
                        self._log, "[green]   Core Fonts instaladas com sucesso[/]"
                    )
                else:
                    self.call_from_thread(
                        self._log, f"[red]   Core Fonts: {result.message}[/]"
                    )

            # Update font cache
            self.call_from_thread(self._log, "[cyan]>> Atualizando cache de fontes...[/]")
            FontInstaller.update_font_cache()
            self.call_from_thread(self._log, "[green]   Cache atualizado![/]")

            # Summary
            self.call_from_thread(
                self._log,
                f"\n[bold green]Concluido! {total_installed} arquivos instalados.[/]",
            )

        except Exception as e:
            self.call_from_thread(self._log, f"[bold red]Erro: {e}[/]")

        finally:
            self._is_installing = False
            self.call_from_thread(self._show_progress, False)

    def _show_progress(self, show: bool) -> None:
        """Show or hide the progress container."""
        container = self.query_one("#progress-container")
        indicator = self.query_one("#installing-indicator")
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_label = self.query_one("#progress-label", Static)

        if show:
            # Reset progress bar
            progress_bar.progress = 0
            progress_label.update("Iniciando...")
            container.add_class("visible")
            indicator.add_class("visible")
        else:
            container.remove_class("visible")
            indicator.remove_class("visible")

    def action_refresh(self) -> None:
        """Refresh the application state."""
        log = self.query_one("#install-log", RichLog)
        log.clear()
        self._log("[blue]Log limpo[/]")
        self.on_mount()
