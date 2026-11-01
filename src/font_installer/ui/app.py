"""Compact Gruvbox catalog with ordered, nonblocking installation feedback."""

from collections import deque
from dataclasses import replace
from threading import Lock
from time import monotonic

from rich.text import Text
from textual import events, work
from textual.app import App, ComposeResult, SuspendNotSupported
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    LoadingIndicator,
    ProgressBar,
    RichLog,
    Static,
)

from ..config.fonts import DEV_FONTS
from ..core.downloader import DownloadProgress
from ..core.installer import FontInstaller, InstallResult
from ..core.packages import PackageManagerError, detect_package_manager
from .screens.confirm_exit import ConfirmExitScreen
from .screens.help import HelpScreen
from .screens.license import CoreFontsLicenseScreen
from .styles import APP_CSS


class FontInstallerApp(App):
    TITLE = "Font Installer"
    CSS = APP_CSS
    BINDINGS = [
        Binding("a", "select_all", "ClearType/Dev"),
        Binding("c", "clear_selection", "Limpar"),
        Binding("i", "install", "Instalar"),
        Binding("l", "toggle_logs", "Logs"),
        Binding("f", "follow_log", "Seguir"),
        Binding("question_mark", "help", "Ajuda"),
        Binding("r", "refresh", "Verificar"),
        Binding("q", "quit", "Sair"),
    ]

    def __init__(self):
        super().__init__()
        if "gruvbox" in self.available_themes:
            self.theme = "gruvbox"
        self._is_installing = False
        self._preconfirm = False
        self._exit_dialog = False
        self._exit_after = False
        self._active_run = None
        self._run_counter = 0
        self._lock = Lock()
        self._events = deque()
        self._pending_progress = None
        self._sequence = 0
        self._history = deque(maxlen=500)
        self._following = True
        self._last_transition = None
        self._started = 0.0
        self._current_phase = ""
        self._installer = FontInstaller()

    def compose(self) -> ComposeResult:
        yield Static("FONT INSTALLER  /  Linux", id="masthead")
        yield Static(
            "Escolha suas fontes. ClearType e Core são conjuntos de fontes.",
            id="welcome-panel",
        )
        yield Static("Verificando dependências…", id="status-bar")
        yield Static("0 opções selecionadas", id="selection-count")
        with VerticalScroll(id="catalog"):
            with Horizontal(id="categories"):
                with Vertical(id="dev-panel", classes="category"):
                    yield Static(
                        "DESENVOLVIMENTO  /  7 famílias", classes="category-title"
                    )
                    for key, info in DEV_FONTS.items():
                        yield Checkbox(
                            info.name,
                            id=f"dev-{key}",
                            classes="font-checkbox",
                            tooltip=info.description,
                        )
                with Vertical(id="microsoft-panel", classes="category"):
                    yield Static("MICROSOFT  /  pacotes", classes="category-title")
                    yield Checkbox(
                        "ClearType", id="cleartype-all", classes="font-checkbox"
                    )
                    yield Static(
                        "Calibri · Cambria · Consolas\nConstantia · Corbel · Candara",
                        classes="font-names",
                    )
                    yield Checkbox(
                        "Core Fonts", id="core-fonts", classes="font-checkbox"
                    )
                    yield Static(
                        "Arial · Times New Roman · Verdana\nCourier New · Georgia · outras",
                        classes="font-names",
                    )
                    yield Static(
                        "Core: Fedora e Debian/Ubuntu • licença", classes="package-note"
                    )
        with Vertical(id="activity"):
            yield Static("Pronto para instalar", id="progress-label")
            with Horizontal(id="progress-row"):
                yield LoadingIndicator(id="installing-indicator")
                yield ProgressBar(total=100, show_eta=False, id="progress-bar")
            yield Static("Nenhuma instalação iniciada", id="summary")
        with Vertical(id="log-container"):
            with Horizontal(id="log-heading"):
                yield Static("ATIVIDADE", id="log-header")
                yield Button("Seguir", id="follow-btn")
            yield RichLog(
                id="install-log",
                wrap=False,
                markup=False,
                max_lines=500,
                auto_scroll=True,
            )
        with Horizontal(id="action-buttons"):
            yield Button("Selecionar ClearType/Dev", id="select-all-btn")
            yield Button("Limpar seleção", id="clear-btn")
            yield Button("Instalar", id="install-btn", variant="success")
            yield Button("Logs", id="logs-btn")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#log-container").display = False
        self.query_one("#progress-row").display = False
        self._check_dependencies()
        self.set_interval(0.1, self._drain_events)
        self._resize_layout()

    def _check_dependencies(self) -> None:
        ok, missing = FontInstaller.check_dependencies()
        status = self.query_one("#status-bar", Static)
        status.update(
            Text(
                "✓ Dependências disponíveis"
                if ok
                else "! Faltando: "
                + ", ".join(missing)
                + " · execute font-installer --install-deps"
            )
        )
        status.set_class(not ok, "warning")

    def on_resize(self, event: events.Resize) -> None:
        self.set_class(event.size.width < 120 or event.size.height < 36, "compact")

    def _resize_layout(self) -> None:
        self.set_class(self.size.width < 120 or self.size.height < 36, "compact")

    def _log(self, message: str) -> None:
        message = " ".join(str(message).splitlines())
        if len(message) > 2048:
            message = message[:2035] + "… [truncado]"
        self._history.append(message)
        log = self.query_one("#install-log", RichLog)
        log.write(Text(message), scroll_end=self._following)

    def _publish(self, run, kind, payload) -> None:
        """Only exchange references under the lock; never wait for rendering."""
        if kind == "progress":
            payload = replace(payload)
        with self._lock:
            if run != self._active_run:
                return
            self._sequence += 1
            record = (self._sequence, run, kind, payload)
            if (
                kind == "progress"
                and payload.event == "progress"
                and payload.phase != "package"
            ):
                previous = self._pending_progress
                if previous and (previous[3].name, previous[3].phase) != (
                    payload.name,
                    payload.phase,
                ):
                    self._events.append(previous)
                self._pending_progress = record
            else:
                if self._pending_progress:
                    self._events.append(self._pending_progress)
                    self._pending_progress = None
                self._events.append(record)

    def _drain_events(self) -> None:
        with self._lock:
            records = list(self._events)
            self._events.clear()
            if self._pending_progress:
                records.append(self._pending_progress)
                self._pending_progress = None
        for _, run, kind, payload in records:
            if run != self._active_run:
                continue
            if kind == "progress":
                self._update_progress(payload)
            elif kind == "item":
                key, result, processed, total = payload
                self._log(
                    f"{'✓' if result.success else '!'} {result.font_name}: {result.message}"
                )
                self.query_one("#summary", Static).update(
                    Text(f"{processed}/{total} opções processadas")
                )
            elif kind == "log":
                self._log(payload)
            elif kind == "finished":
                self._finish(payload)
        if self._is_installing:
            elapsed = int(monotonic() - self._started)
            self.query_one("#selection-count", Static).update(
                Text(
                    f"{self._current_phase} · {elapsed}s"
                    + (" · Saída após concluir o lote" if self._exit_after else "")
                )
            )

    def _update_progress(self, progress: DownloadProgress) -> None:
        self._current_phase = f"{progress.name}: {progress.status}"
        if progress.phase == "download" and not progress.total_bytes:
            self._current_phase += (
                f" · {progress.bytes_downloaded / 1024:.1f} KiB recebidos"
            )
        self.query_one("#progress-label", Static).update(Text(self._current_phase))
        measured = progress.phase == "download" and progress.total_bytes > 0
        self.query_one("#progress-bar").display = measured
        self.query_one("#installing-indicator").display = not measured
        if measured:
            self.query_one("#progress-bar", ProgressBar).update(
                total=100, progress=progress.percent
            )
        if progress.phase == "package" and progress.event == "progress":
            self._log(self._current_phase)
        transition = (progress.name, progress.phase, progress.event)
        if (
            progress.event in ("started", "completed", "failed")
            and transition != self._last_transition
        ):
            self._log(self._current_phase)
            self._last_transition = transition

    def on_checkbox_changed(self) -> None:
        if not self._is_installing:
            count = sum(widget.value for widget in self.query(Checkbox))
            self.query_one("#selection-count", Static).update(
                f"{count} opções selecionadas"
            )
            self.query_one("#install-btn", Button).label = (
                f"Instalar ({count})" if count else "Instalar"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "install-btn": self.action_install,
            "select-all-btn": self.action_select_all,
            "clear-btn": self.action_clear_selection,
            "logs-btn": self.action_toggle_logs,
            "follow-btn": self.action_follow_log,
        }
        action = actions.get(event.button.id)
        if action:
            action()

    def action_select_all(self) -> None:
        if self._is_installing or self._preconfirm:
            return
        for widget in self.query(Checkbox):
            if widget.id != "core-fonts":
                widget.value = True

    def action_clear_selection(self) -> None:
        if self._is_installing or self._preconfirm:
            return
        for widget in self.query(Checkbox):
            widget.value = False

    def action_install(self) -> None:
        if (
            self._is_installing
            or self._preconfirm
            or self.screen is not self.screen_stack[0]
        ):
            return
        selected = tuple(widget.id for widget in self.query(Checkbox) if widget.value)
        if not selected:
            self.query_one("#summary", Static).update(
                "Selecione ao menos uma opção para instalar."
            )
            return
        if "core-fonts" in selected:
            self._preconfirm = True
            self.push_screen(
                CoreFontsLicenseScreen(),
                lambda accepted: self._license_answer(accepted, selected),
            )
        else:
            self._start(selected)

    def _license_answer(self, accepted, selected) -> None:
        self._preconfirm = False
        if accepted:
            self._start(selected)
        else:
            self.query_one("#summary", Static).update(
                "Licença não aceita. Nenhum item do lote foi iniciado."
            )

    def _start(self, selected) -> None:
        if self._is_installing:
            return
        self._is_installing = True
        self._run_counter += 1
        self._active_run = self._run_counter
        self._started = monotonic()
        self._last_transition = None
        self._current_phase = "Iniciando lote"
        for widget in self.query(Checkbox):
            widget.disabled = True
        for id_ in ("install-btn", "clear-btn", "select-all-btn"):
            self.query_one(f"#{id_}", Button).disabled = True
        self.query_one("#log-container").display = True
        self.query_one("#progress-row").display = True
        self.query_one("#installing-indicator").display = True
        self.query_one("#progress-bar").display = False
        self.query_one("#summary", Static).update(
            f"0/{len(selected)} opções processadas"
        )
        self._log("Iniciando lote de instalação")
        try:
            self._run_installation(self._active_run, selected)
        except Exception as error:
            self._finish(([], False, f"Falha ao iniciar: {error}", len(selected)))

    @work(thread=True, exit_on_error=False)
    def _run_installation(self, run, selected) -> None:
        installer = FontInstaller(
            lambda progress: self._publish(run, "progress", progress)
        )
        self._installer = installer
        results = []
        cache_ok = False
        unexpected = ""
        ordered = (
            (["cleartype-all"] if "cleartype-all" in selected else [])
            + [f"dev-{key}" for key in DEV_FONTS if f"dev-{key}" in selected]
            + (["core-fonts"] if "core-fonts" in selected else [])
        )
        try:
            for key in ordered:
                if key == "cleartype-all":
                    result = installer.install_cleartype_fonts()
                elif key == "core-fonts":
                    self._publish(
                        run,
                        "progress",
                        DownloadProgress(
                            "Core Fonts",
                            0,
                            "Preparando instalação",
                            phase="package",
                            event="started",
                        ),
                    )
                    try:
                        direct = detect_package_manager().name == "dnf"
                    except PackageManagerError:
                        direct = False
                    if direct:
                        result = FontInstaller.install_core_fonts(
                            progress_callback=lambda progress: self._publish(
                                run, "progress", progress
                            )
                        )
                    else:
                        result = self.call_from_thread(self._install_core_native)
                else:
                    result = installer.install_dev_font(key[4:])
                results.append((key, result))
                self._publish(run, "item", (key, result, len(results), len(ordered)))
            self._publish(
                run,
                "progress",
                DownloadProgress(
                    "Cache", 0, "Atualizando cache", phase="cache", event="started"
                ),
            )
            try:
                cache_ok = FontInstaller.update_font_cache()
            except OSError as error:
                self._publish(run, "log", f"Falha no cache: {error}")
        except Exception as error:
            unexpected = f"Erro inesperado: {error} · {len(ordered) - len(results)} opções não concluídas"
            self._publish(run, "log", unexpected)
        finally:
            self._publish(
                run, "finished", (results, cache_ok, unexpected, len(ordered))
            )

    def _install_core_native(self) -> InstallResult:
        self._drain_events()
        try:
            with self.suspend():
                try:
                    return FontInstaller.install_core_fonts()
                except KeyboardInterrupt:
                    return InstallResult(
                        False, "Core Fonts", 0, "Interrompido no terminal"
                    )
                except Exception as error:
                    # Exit context normally so Textual restores its terminal driver.
                    failure = error
            raise failure
        except SuspendNotSupported:
            return InstallResult(
                False, "Core Fonts", 0, "Suspensão indisponível neste terminal"
            )

    def _finish(self, payload) -> None:
        results, cache_ok, unexpected, total = payload
        successful = sum(result.success for _, result in results)
        copied = sum(
            result.files_installed
            for key, result in results
            if key != "core-fonts" or result.files_expected is not None
        )
        if successful == total and cache_ok and not unexpected:
            label = "Sucesso"
        elif successful or copied:
            label = "Falha parcial"
        else:
            label = "Falha"
        message = f"{label} · {successful}/{total} opções completas · {copied} arquivos copiados · cache {'atualizado' if cache_ok else 'falhou/não executado'}"
        if unexpected:
            message += f" · {unexpected}"
        self.query_one("#summary", Static).update(Text(message))
        self.query_one("#progress-label", Static).update("Lote encerrado")
        self._log(message)
        with self._lock:
            self._active_run = None
            self._pending_progress = None
            self._events.clear()
        self._is_installing = False
        self.query_one("#progress-row").display = False
        for widget in self.query(Checkbox):
            widget.disabled = False
        for id_ in ("install-btn", "clear-btn", "select-all-btn"):
            self.query_one(f"#{id_}", Button).disabled = False
        self.on_checkbox_changed()
        if self._exit_after:
            self.exit()

    def action_toggle_logs(self) -> None:
        panel = self.query_one("#log-container")
        panel.display = not panel.display

    def action_follow_log(self) -> None:
        self._following = True
        log = self.query_one("#install-log", RichLog)
        log.auto_scroll = True
        log.scroll_end(animate=False)
        self.query_one("#log-header", Static).update("ATIVIDADE · seguindo")

    def _pause_log(self) -> None:
        self._following = False
        self.query_one("#install-log", RichLog).auto_scroll = False
        self.query_one("#log-header", Static).update(
            "ATIVIDADE · histórico pausado (f: seguir)"
        )

    def on_key(self, event: events.Key) -> None:
        if self.focused is self.query_one("#install-log") and event.key in (
            "pageup",
            "up",
            "home",
            "ctrl+home",
        ):
            self._pause_log()

    def on_mouse_scroll_up(self) -> None:
        if self.query_one("#log-container").display:
            self._pause_log()

    def action_help(self) -> None:
        if len(self.screen_stack) == 1:
            self.push_screen(HelpScreen())

    def action_refresh(self) -> None:
        if self._is_installing or self._preconfirm:
            return
        self._history.clear()
        self.query_one("#install-log", RichLog).clear()
        self._check_dependencies()

    def action_quit(self) -> None:
        if self._is_installing:
            if not self._exit_after and not self._exit_dialog:
                self._exit_dialog = True
                self.push_screen(ConfirmExitScreen(), self._confirm_exit)
        elif not self._preconfirm:
            self.exit()

    def _confirm_exit(self, confirmed) -> None:
        self._exit_dialog = False
        if confirmed:
            self._exit_after = True
            if not self._is_installing:
                self.exit()
