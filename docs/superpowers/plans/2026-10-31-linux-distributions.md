# Linux distributions Implementation Plan

> **For agentic workers:** Execute the tasks in this session using test-driven development.

**Goal:** Suportar as distribuições aprovadas sem instalar pacotes durante os testes.
**Architecture:** Um módulo de pacotes identifica Linux e os-release e produz comandos por distribuição. O instalador usa esse módulo; CLI e TUI compartilham orientações.
**Tech Stack:** Python 3.11+, pytest, subprocess.
**Spec:** ../specs/2026-10-31-linux-distributions-design.md (aprovado pelo usuário).

## Global Constraints

- Ubuntu/Debian, Fedora, Arch/Manjaro, openSUSE e Alpine.
- Não adicionar repositórios externos automaticamente.
- Core Fonts via pacote apenas na família Debian.
- Preservar os diretórios atuais de fontes do usuário.

## Review Focus

- ID_LIKE com múltiplos valores e prioridade de ID.
- Sistema desconhecido com apt instalado: não executar apt por engano.
- Root sem sudo e usuário comum sem sudo.
- os-release indisponível e gerenciador ausente.
- Instalação bem-sucedida que não disponibiliza as ferramentas esperadas.

### Task 1: Detecção e instalação

**Files:** criar `src/font_installer/core/packages.py` e `tests/test_packages.py`; modificar `core/installer.py` e `utils/system.py`.
**Interfaces:** `detect_package_manager() -> PackageManager`; `PackageManager.install(packages: list[str]) -> None`; `dependency_install_hint() -> str`.

- [x] Escrever testes parametrizados para todas as famílias, derivados, rejeição de outros sistemas, ausência de sudo/gerenciador, falhas de comandos e dependências ainda ausentes.
- [x] Executar `.venv/bin/python -m pytest tests/test_packages.py` e observar falhas antes da implementação.
- [x] Implementar módulo e conectar dependências/Core Fonts ao instalador; identificar Linux via platform.system.
- [x] Reexecutar testes; resultado esperado: todos passam.

### Task 2: Mensagens e documentação

**Files:** modificar `cli.py`, `core/exceptions.py`, `ui/app.py`, `README.md`, `pyproject.toml`.
**Interfaces:** consumir `dependency_install_hint()` e `detect_package_manager()` da tarefa 1.

- [x] Substituir orientações fixas de apt e declarar limitação de Core Fonts na TUI e README.
- [x] Verificar ajuda via `.venv/bin/font-installer --help`.
- [x] Executar `.venv/bin/python -m pytest`; integração permanece opt-in.
- [x] Revisar diff e verificar `git diff --check`.

Não criar commits nem publicar alterações: entregar mudanças locais para revisão.

## Resultado da execução

- Ambiente preparado com Python 3.14 instalado no host; Python 3.12 indicado
  em .python-version não estava disponível. Nenhuma alteração nessa indicação.
- 38 testes aprovados e 4 de integração ignorados (opt-in).
- Ajuda CLI e inicialização TUI com aviso de dependências Fedora verificadas.
- Ruff aprovado nos arquivos alterados; lint global aponta problemas existentes
  em config/__init__.py, config/settings.py, core/__init__.py, core/downloader.py,
  core/extractor.py e tests/test_installer.py.
- Revisão independente sem achados; nenhum pacote do sistema instalado.
