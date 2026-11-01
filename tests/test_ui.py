"""Headless interaction tests; installers are replaced at the external boundary."""

import asyncio
import threading

from textual.widgets import Checkbox, Static

from font_installer.core.downloader import DownloadProgress
from font_installer.core.installer import FontInstaller, InstallResult
from font_installer.ui.app import FontInstallerApp


def ready(monkeypatch):
    monkeypatch.setattr(FontInstaller, "check_dependencies", lambda: (True, []))


def test_catalog_and_activity_fit_target(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()
            assert len(app.query(Checkbox)) == 9
            for widget in app.query(Checkbox):
                assert widget.region.bottom <= 36 and widget.region.width > 0
            assert (
                app.query_one("#catalog").virtual_size.height
                <= app.query_one("#catalog").size.height
            )
            app.action_toggle_logs()
            await pilot.pause()
            assert app.query_one("#log-container").display
            assert app.query_one("#activity").region.bottom <= 36

    asyncio.run(scenario())


def test_empty_selection_feedback_outside_logs(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app.action_install()
            await pilot.pause()
            assert "Selecione" in str(app.query_one("#summary", Static).content)
            assert not app._is_installing

    asyncio.run(scenario())


def test_progress_producer_does_not_wait_for_ui(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app._active_run = 1
            done = threading.Event()

            def publish():
                for n in range(300):
                    app._publish(
                        1,
                        "progress",
                        DownloadProgress(
                            "Hack",
                            n % 100,
                            "download",
                            phase="download",
                            event="progress",
                        ),
                    )
                done.set()

            thread = threading.Thread(target=publish)
            thread.start()
            assert done.wait(1), "publishing must not wait for the UI event loop"
            thread.join()
            app._drain_events()
            assert app._pending_progress is None
            await pilot.pause()

    asyncio.run(scenario())


def test_failed_item_and_cache_produce_partial_summary(monkeypatch):
    ready(monkeypatch)
    monkeypatch.setattr(
        FontInstaller,
        "install_dev_font",
        lambda self, key: InstallResult(
            key == "hack", key, 1 if key == "hack" else 0, "result"
        ),
    )
    monkeypatch.setattr(FontInstaller, "update_font_cache", lambda: False)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test(size=(120, 36)) as pilot:
            app.query_one("#dev-hack", Checkbox).value = True
            app.query_one("#dev-firacode", Checkbox).value = True
            app.action_install()
            assert app._is_installing
            assert app.query_one("#dev-hack", Checkbox).disabled
            for _ in range(30):
                await pilot.pause(0.05)
                if not app._is_installing:
                    break
            assert not app._is_installing
            assert "Falha parcial" in str(app.query_one("#summary", Static).content)
            assert "cache" in str(app.query_one("#summary", Static).content).lower()
            assert not app.query_one("#dev-hack", Checkbox).disabled

    asyncio.run(scenario())


def test_logs_bounded_and_history_pause(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            for n in range(510):
                app._log(f"entry {n}")
            assert len(app._history) == 500
            assert app._history[0] == "entry 10"
            app.action_toggle_logs()
            app.query_one("#install-log").focus()
            await pilot.press("pageup")
            assert not app._following
            app.action_follow_log()
            assert app._following

    asyncio.run(scenario())


def test_resize_preserves_selection_and_compact_scroll(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test(size=(120, 36)) as pilot:
            app.query_one("#dev-hack", Checkbox).value = True
            await pilot.resize_terminal(80, 24)
            assert app.has_class("compact")
            app.query_one("#core-fonts").focus()
            await pilot.pause()
            assert app.focused.id == "core-fonts"
            assert app.query_one("#dev-hack", Checkbox).value
            await pilot.resize_terminal(120, 36)
            assert not app.has_class("compact")
            assert app.query_one("#dev-hack", Checkbox).value

    asyncio.run(scenario())


def test_core_refusal_and_duplicate_modal_do_not_start_lot(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app.query_one("#core-fonts", Checkbox).value = True
            app.action_install()
            app.action_install()
            await pilot.pause()
            assert len(app.screen_stack) == 2
            await pilot.press("escape")
            assert not app._is_installing and not app._preconfirm
            assert app._active_run is None

    asyncio.run(scenario())


def test_ordered_transitions_discard_old_download_measure_and_stale_events(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app._active_run = 7
            app._publish(
                7,
                "progress",
                DownloadProgress(
                    "Hack", 80, "Baixando", 80, 100, "download", "progress"
                ),
            )
            app._publish(
                7,
                "progress",
                DownloadProgress(
                    "Hack", 0, "Extraindo", phase="extract", event="started"
                ),
            )
            app._drain_events()
            assert not app.query_one("#progress-bar").display
            assert app.query_one("#installing-indicator").display
            app._publish(7, "finished", ([], False, "bug", 1))
            app._drain_events()
            app._publish(
                7,
                "progress",
                DownloadProgress("Hack", 99, "old", phase="download", event="progress"),
            )
            app._drain_events()
            assert app._active_run is None
            assert "Lote encerrado" in str(
                app.query_one("#progress-label", Static).content
            )
            await pilot.pause()

    asyncio.run(scenario())


def test_exit_after_confirmation_completes_all_items(monkeypatch):
    ready(monkeypatch)
    release = threading.Event()
    calls = []

    def install(self, key):
        calls.append(key)
        release.wait(3)
        return InstallResult(True, key, 1, "ok")

    monkeypatch.setattr(FontInstaller, "install_dev_font", install)
    monkeypatch.setattr(FontInstaller, "update_font_cache", lambda: True)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            try:
                app.query_one("#dev-hack", Checkbox).value = True
                app.query_one("#dev-firacode", Checkbox).value = True
                app.action_install()
                app.action_install()
                app.action_quit()
                await pilot.pause()
                await pilot.click("#exit-after")
                assert app._exit_after
                release.set()
                for _ in range(30):
                    await asyncio.sleep(0.05)
                    if not app._is_installing:
                        break
                assert calls == ["firacode", "hack"]
                assert not app._is_installing
            finally:
                release.set()

    asyncio.run(scenario())


def test_unexpected_error_stops_remaining_items(monkeypatch):
    ready(monkeypatch)
    calls = []

    def install(self, key):
        calls.append(key)
        raise TypeError("bug")

    monkeypatch.setattr(FontInstaller, "install_dev_font", install)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app.query_one("#dev-firacode", Checkbox).value = True
            app.query_one("#dev-hack", Checkbox).value = True
            app.action_install()
            for _ in range(30):
                await pilot.pause(0.05)
                if not app._is_installing:
                    break
            assert calls == ["firacode"]
            assert "não concluídas" in str(app.query_one("#summary", Static).content)

    asyncio.run(scenario())


def test_unknown_download_shows_received_bytes(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app._update_progress(
                DownloadProgress(
                    "Hack", 0, "Baixando", 65536, 0, "download", "progress"
                )
            )
            assert "64.0 KiB" in str(app.query_one("#progress-label", Static).content)
            assert app.query_one("#installing-indicator").display
            await pilot.pause()

    asyncio.run(scenario())


def test_fedora_core_runs_in_worker_without_terminal_suspension(monkeypatch):
    from types import SimpleNamespace

    from font_installer.ui import app as app_module

    ready(monkeypatch)
    monkeypatch.setattr(
        app_module, "detect_package_manager", lambda: SimpleNamespace(name="dnf")
    )

    def install(progress_callback=None):
        progress_callback(
            DownloadProgress("Core Fonts", 0, "Copiando", phase="copy", event="started")
        )
        return InstallResult(True, "Core Fonts", 3, "3 arquivos copiados", 3)

    monkeypatch.setattr(FontInstaller, "install_core_fonts", install)
    monkeypatch.setattr(FontInstaller, "update_font_cache", lambda: True)

    def forbidden():
        raise AssertionError("Fedora user-local installation must not suspend the TUI")

    async def scenario():
        app = FontInstallerApp()
        monkeypatch.setattr(app, "suspend", forbidden)
        async with app.run_test(size=(120, 36)) as pilot:
            app.query_one("#core-fonts", Checkbox).value = True
            app.action_install()
            await pilot.pause()
            await pilot.click("#license-accept")
            for _ in range(30):
                await pilot.pause(0.05)
                if not app._is_installing:
                    break
            summary = str(app.query_one("#summary", Static).content)
            assert "Sucesso" in summary and "3 arquivos copiados" in summary
            assert any("Copiando" in entry for entry in app._history)

    asyncio.run(scenario())


def test_script_output_is_preserved_in_live_logs(monkeypatch):
    ready(monkeypatch)

    async def scenario():
        app = FontInstallerApp()
        async with app.run_test() as pilot:
            app._active_run = 1
            for message in ("Baixando pacote A", "Extraindo pacote A"):
                app._publish(
                    1,
                    "progress",
                    DownloadProgress(
                        "Core Fonts", 0, message, phase="package", event="progress"
                    ),
                )
            app._drain_events()
            assert any("Baixando pacote A" in line for line in app._history)
            assert any("Extraindo pacote A" in line for line in app._history)
            await pilot.pause()

    asyncio.run(scenario())
