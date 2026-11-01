# System Utilities

## Overview

Read system diagnostics and inspect the configured font directories and provide the Fedora Core Fonts wrapper.

## Interface

- The package exports `SystemChecker` through [__init__.py](./__init__.py) [`__init__.py:__all__`].
- [system.py](./system.py) defines the `SystemInfo` dataclass with `fonts_dir`, `fonts_count`, `has_cabextract`, `has_fc_cache`, and `is_linux` fields [`system.py:SystemInfo`].
- `SystemChecker.get_installed_fonts_count()` counts matching entries in configured Microsoft and developer-font directories; `list_installed_fonts()` returns sorted names under `microsoft`, `dev`, and `core` keys [`system.py:SystemChecker.get_installed_fonts_count`, `system.py:SystemChecker.list_installed_fonts`].
- `SystemChecker.get_system_info()` combines configured font paths, counts, executable availability, and platform information; `verify_font_available(font_name)` queries fontconfig [`system.py:SystemChecker.get_system_info`, `system.py:SystemChecker.verify_font_available`].

## Invariants

- Counting uses nonrecursive `glob` patterns for each configured extension. Listing uses immediate entries and lowercases suffixes before checking the extensions; neither method explicitly checks `is_file()` [`system.py:SystemChecker.get_installed_fonts_count`, `system.py:SystemChecker.list_installed_fonts`].
- Listing always returns all three category keys, including empty lists for missing directories [`system.py:SystemChecker.list_installed_fonts`].
- Font availability is determined by nonempty stripped `fc-list` stdout, not the process return code. `subprocess.SubprocessError` returns false; other errors such as a missing executable are not caught [`system.py:SystemChecker.verify_font_available`].

## Side Effects

- Counting and listing inspect directory existence and contents; diagnostics also searches `PATH` for `cabextract` and `fc-cache` and queries `platform.system()` [`system.py:SystemChecker.get_installed_fonts_count`, `system.py:SystemChecker.list_installed_fonts`, `system.py:SystemChecker.get_system_info`].
- Font verification starts `fc-list` with the family name as a separate argument and captures stdout/stderr [`system.py:SystemChecker.verify_font_available`].

## Verification

- From the repository root, run `.venv/bin/python -m pytest`.


Core Fonts no Fedora são contadas/listadas em Settings.CORE_FONTS_DIR;
o diretório de pacotes do sistema Debian não é contado como fonte do usuário.


## Instalador Core Fonts do Fedora

[msttcore.sh](./msttcore.sh) usa o RPM local
[msttcore-fonts-installer-2.6-1.noarch.rpm](./msttcore-fonts-installer-2.6-1.noarch.rpm).
O RPM é extraído em diretório temporário; seu instalador é executado com -d
para não configurar /etc ou X11. URLs HTTP do SourceForge são atualizadas para
HTTPS apenas na cópia temporária; checksums originais permanecem ativos.

O script aceita um destino opcional; padrão ~/.local/share/fonts/microsoft-core.
A localização do RPM é relativa ao script, não ao diretório atual. Arial e
Calibri são verificadas na área temporária antes da cópia. Arquivos temporários
são removidos ao sair; fc-cache é executado apenas para o destino.
Em sucesso, emite FONT_INSTALLER_FILES_INSTALLED=<quantidade>.

Efeitos adicionais: downloads pelo instalador, execução rpm2cpio/cpio/cabextract,
cópia de fontes e cache. Requer Bash, curl, rpm2cpio, cpio, cabextract e fc-cache.
A execução standalone não apresenta a licença da TUI; no app o modal continua
sendo exigido antes de iniciar o lote.

Verificação: tests/test_msttcore_script.py e tests/test_core_fedora.py.
