"""Public CLI dispatch stays available alongside the new TUI."""

import sys

import pytest

from font_installer import cli


@pytest.mark.parametrize("command", ["help", "--help", "-h"])
def test_help_keeps_cli_dispatch_and_describes_new_shortcuts(
    monkeypatch, capsys, command
):
    monkeypatch.setattr(sys, "argv", ["font-installer", command])
    assert cli.main() == 0
    text = capsys.readouterr().out
    assert "--cli" in text and "--install-deps" in text
    assert "l - Abrir/recolher logs" in text


def test_unknown_command_still_returns_failure(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["font-installer", "unknown"])
    assert cli.main() == 1
    assert "Comando desconhecido" in capsys.readouterr().out
