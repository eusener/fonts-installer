# Font Installer Package

## Overview

Application entry points shared by the command-line interface and Textual UI.
The `font-installer` script is registered in the repository's `pyproject.toml`
as `font_installer.cli:main`; `python -m font_installer` uses the same function.

## Interface

- `__init__.py:__version__` is `1.0.0`; `__author__` identifies the package team.
- `cli.py:main()` dispatches no arguments to the TUI; accepts `help`, `--help`,
  `-h`, `--install-deps`, `--cli`, and `list`.
- `cli.py:print_help()`, `check_and_install_deps()`, `install_deps_command()`,
  `run_cli_mode()`, and `list_fonts()` implement the individual command flows.
- [config](./config/README.md): `Settings`, `FontInfo`, and font catalogs.
- [core](./core/README.md): download, extraction, package commands, and installation.
- [ui](./ui/README.md): `FontInstallerApp` and Textual presentation.
- [utils](./utils/README.md): `SystemChecker` for tools, platform, and installed fonts.

## Invariants

- `cli.py:main` lowercases only the first argument; trailing arguments are ignored.
  Unknown commands return 1; help and normal TUI completion return 0.
- `cli.py:check_and_install_deps` accepts empty input, `s`, `sim`, `y`, or `yes`
  after stripping and lowercasing. EOF and keyboard interruption return false.
- `cli.py:run_cli_mode` checks dependencies before ClearType installation and
  updates the cache only after a successful installation result.
- `cli.py:install_deps_command` and `run_cli_mode` return 0 on success and 1
  on their reported failure paths.

## Side Effects

- `cli.py:print_help`, `list_fonts`, and installation flows write to stdout;
  `check_and_install_deps` also reads stdin.
- `cli.py:install_deps_command` and `check_and_install_deps` may delegate system
  package installation to `FontInstaller.install_dependencies`.
- `cli.py:run_cli_mode` delegates downloads, font installation, and cache updates
  to `FontInstaller`; `list_fonts` delegates discovery to `SystemChecker`.
- `cli.py:main` starts the interactive terminal UI through `FontInstallerApp.run`.
- `__main__.py:__name__` calls `sys.exit(main())` when executed as a module.

## Verification

Run from the repository root with the development environment installed:

```bash
.venv/bin/python -m pytest -m "not integration"
```


## Interface atualizada da TUI

FontInstallerApp usa catálogo simultâneo, caixa de eventos com timer, modais de licença/saída e suspensão Core. A CLI mantém os comandos existentes.
