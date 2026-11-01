# Configuration

## Overview

This package defines application settings and the ClearType and developer font
catalogs. It stores download URLs, destination paths, tool requirements, and font
metadata; directory creation is an explicit operation.

## Interface

- [`__init__.py`](./__init__.py) exports `Settings`, `CLEARTYPE_FONTS`,
  `DEV_FONTS`, and `FontInfo` through `__all__`.
- [`fonts.py:FontCategory`](./fonts.py) defines `CLEARTYPE = "cleartype"`,
  `DEVELOPER = "developer"`, and `CORE = "core"`.
- `fonts.py:FontInfo` is a frozen dataclass with `name`, `description`,
  `category`, and optional `repo` and `asset_pattern` fields.
- `fonts.py:CLEARTYPE_FONTS` maps `calibri`, `cambria`, `consolas`,
  `constantia`, `corbel`, and `candara` to font metadata.
- `fonts.py:DEV_FONTS` maps `cascadia`, `jetbrains`, `firacode`, `hack`,
  `sourcecodepro`, `victormono`, and `inconsolata` to metadata including GitHub
  repository names and release asset patterns.
- `fonts.py:get_all_fonts()` returns a new dictionary combining both catalogs.
  `get_fonts_by_category(category)` returns a new dictionary filtered by
  `FontInfo.category`.
- [`settings.py:Settings`](./settings.py) exposes class variables
  `FONTS_BASE_DIR`, `MICROSOFT_FONTS_DIR`, `DEV_FONTS_DIR`,
  `POWERPOINT_VIEWER_URL`, `GITHUB_API_BASE`, `USER_AGENT`,
  `DOWNLOAD_TIMEOUT`, `API_TIMEOUT`, `REQUIRED_TOOLS`, and `FONT_EXTENSIONS`.
  Its class method `ensure_directories()` creates the two font destinations.

## Invariants

- `fonts.py:FontInfo` and `settings.py:Settings` use `dataclass(frozen=True)`;
  `Settings` configuration values are `ClassVar` attributes, not instance
  dataclass fields.
- `settings.py:Settings.FONTS_BASE_DIR` is computed from `Path.home()` as
  `~/.local/share/fonts` when the class is defined. Its Microsoft and developer
  destinations append `microsoft` and `dev`, respectively.
- `settings.py:Settings.DOWNLOAD_TIMEOUT` is 300 seconds and `API_TIMEOUT` is
  30 seconds. `REQUIRED_TOOLS` is `("cabextract", "fc-cache")`, and
  `FONT_EXTENSIONS` is `(".ttf", ".ttc", ".otf")`.
- `fonts.py:get_all_fonts` unpacks `DEV_FONTS` after `CLEARTYPE_FONTS`, so a
  duplicate key takes the developer catalog's value. The dictionaries are
  mutable; the frozen metadata records do not freeze the catalogs.
- `fonts.py:get_fonts_by_category` includes only entries whose category equals
  the requested enum value. Neither declared catalog currently contains `CORE`
  entries.

## Side Effects

- `settings.py:Settings.ensure_directories` calls `mkdir(parents=True,
  exist_ok=True)` first on `MICROSOFT_FONTS_DIR`, then on `DEV_FONTS_DIR`.
  Filesystem errors propagate to the caller.

## Verification

Run from the repository root:

```sh
.venv/bin/python -m pytest
```


## Core Fonts no Fedora

Settings.CORE_FONTS_DIR aponta para ~/.local/share/fonts/microsoft-core.
O script msttcore.sh e o RPM incluído em utils são a origem do instalador.
ensure_directories cria também esse destino. Não há catálogo Python de URLs
Core: o instalador extraído do RPM gerencia downloads e checksums.
