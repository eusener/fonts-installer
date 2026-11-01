# Source Blueprint

## Overview

Production Python code is packaged under `font_installer`. The wheel target in
`../pyproject.toml:tool.hatch.build.targets.wheel` includes `src/font_installer`.

## Subdirectories & Boundaries

- [font_installer](./font_installer/README.md): CLI entry points, configuration,
  installation services, Textual UI, and system utilities.

## Interface

- `font_installer/cli.py:main` is the installed `font-installer` command.
- `font_installer/__main__.py` provides module execution through that same entry point.

## Invariants

- `../pyproject.toml:project.requires-python` requires Python 3.11 or later.

## Side Effects

- `font_installer/cli.py:main` can launch the terminal UI or delegate installations;
  details belong to the linked package contracts.

## Verification

Run from the repository root:

```bash
.venv/bin/python -m pytest -m "not integration"
```


## Interface atualizada da TUI

A TUI apresenta categorias simultâneas e modais; veja o contrato de ui para logs e suspensão nativa.
