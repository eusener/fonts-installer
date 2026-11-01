import asyncio

from textual.app import App


def test_license_decline_is_initial_focus_and_escape_rejects():
    from font_installer.ui.screens.license import CoreFontsLicenseScreen, load_license

    text = load_license()
    assert "END-USER LICENSE AGREEMENT" in text
    assert "MICROSOFT" in text and "MISCELLANEOUS" in text

    async def scenario():
        app = App()
        result = []
        async with app.run_test() as pilot:
            app.push_screen(CoreFontsLicenseScreen(), result.append)
            await pilot.pause()
            assert app.screen.focused.id == "license-decline"
            await pilot.press("escape")
            assert result == [False]

    asyncio.run(scenario())


def test_exit_confirmation_can_be_cancelled():
    from font_installer.ui.screens.confirm_exit import ConfirmExitScreen

    async def scenario():
        app = App()
        result = []
        async with app.run_test() as pilot:
            app.push_screen(ConfirmExitScreen(), result.append)
            await pilot.pause()
            await pilot.press("escape")
            assert result == [False]

    asyncio.run(scenario())


def test_missing_license_blocks_accept(monkeypatch):
    from font_installer.ui.screens import license

    def unavailable():
        raise OSError("missing")

    monkeypatch.setattr(license, "load_license", unavailable)

    async def scenario():
        app = App()
        async with app.run_test() as pilot:
            app.push_screen(license.CoreFontsLicenseScreen())
            await pilot.pause()
            assert app.screen.query_one("#license-accept").disabled

    asyncio.run(scenario())


def test_native_core_restores_context_after_interruption(monkeypatch):
    from contextlib import contextmanager

    from font_installer.core.installer import FontInstaller
    from font_installer.ui.app import FontInstallerApp

    monkeypatch.setattr(FontInstaller, "check_dependencies", lambda: (True, []))

    def interrupt():
        raise KeyboardInterrupt

    monkeypatch.setattr(FontInstaller, "install_core_fonts", interrupt)
    restored = []

    @contextmanager
    def suspend():
        yield
        restored.append(True)

    async def scenario():
        app = FontInstallerApp()
        monkeypatch.setattr(app, "suspend", suspend)
        async with app.run_test() as pilot:
            result = app._install_core_native()
            assert not result.success and "Interrompido" in result.message
            assert restored == [True]
            await pilot.pause()

    asyncio.run(scenario())
