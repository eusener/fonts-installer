# Font Installation Core

## Overview

Download em blocos, extração e instalação sequencial de fontes, com eventos
aditivos e resultados que distinguem cópia completa de cópia parcial.

## Interface

- `downloader.py:DownloadProgress(name, percent, status, bytes_downloaded=0,
  total_bytes=0, phase=None, event=None)` preserva os cinco argumentos antigos.
- `Downloader.download_file(url, dest, name)` grava o destino e retorna Path;
  `get_github_release_url(repo, asset_pattern)` retorna ZIP compatível ou None.
- `emit_progress` preserva erros do consumidor via `ProgressCallbackError`.
- `extractor.py:FontExtractor.extract_from_cab` e `extract_from_zip` retornam caminhos de fontes.
- `installer.py:InstallResult` acrescenta `files_expected=None` aos quatro campos antigos.
- `FontInstaller` expõe check_dependencies, install_dependencies, ensure_dependencies,
  install_cleartype_fonts, install_dev_font, install_core_fonts e update_font_cache.
- `packages.py:PackageManager.install`, detect_package_manager e dependency_install_hint
  mantêm comandos nativos por distribuição.
- `exceptions.py` contém FontInstallerError, DownloadError, ExtractionError,
  InstallationError, DependencyError e ProgressCallbackError(RuntimeError).

## Invariants

- Download usa Settings.DOWNLOAD_TIMEOUT; consulta usa API_TIMEOUT. Erros HTTP,
  inclusive HTTPException/IncompleteRead, rede e JSON inválido tornam-se DownloadError.
- Consulta válida sem ZIP retorna None; erro de programação e callback não são absorvidos.
- `_install_archive` emite lookup/extract/copy; Downloader emite download.
- Sucesso de cópia exige quantidade positiva e completa. Contagens são operações
  de cópia, não garantia de nomes únicos no destino; falhas individuais são contadas.
- `_install_fonts_to_dir` usa basenames minúsculos e ignora falhas individuais de cópia.
- Core usa apt no Debian/Ubuntu, mantendo files_installed=1 como indicador
  histórico do pacote. No Fedora, _install_core_fonts_script materializa msttcore.sh e o RPM local
  por importlib.resources e executa Bash, sem instalar o RPM via gerenciador.
  Linhas stdout/stderr são eventos package/progress, com saída limitada no erro.
  O marcador FONT_INSTALLER_FILES_INSTALLED informa a contagem. Sucesso exige
  retorno zero, contagem positiva e Arial/Calibri não vazias no destino.
- Atualização de cache não é automática nos métodos de instalação; o chamador a executa.
- Detecção do gerenciador usa ID antes de ID_LIKE e exige o executável selecionado.

## Side Effects

Rede, arquivos temporários, extração ZIP/CAB, cópia que pode sobrescrever destinos,
callbacks síncronos e execução de cabextract/fc-cache. PackageManager pode executar
sudo, atualizar metadados e instalar pacotes; não muda repositórios habilitados.

## Verification

Na raiz: `.venv/bin/python -m pytest -m "not integration"`.
