# Font Installer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ubuntu](https://img.shields.io/badge/platform-Ubuntu%2FDebian-orange.svg)](https://ubuntu.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-unit%20%2B%20integration-brightgreen.svg)]()

Instalador interativo de fontes Microsoft e Developer para **Ubuntu/Debian** com interface TUI moderna.

> **Nota:** Este programa foi desenvolvido exclusivamente para sistemas Ubuntu/Debian. Nao e compativel com outras distribuicoes Linux, macOS ou Windows.

## Funcionalidades

- Interface TUI interativa com [Textual](https://textual.textualize.io/)
- Navegacao por abas (ClearType, Dev Fonts, Core Fonts)
- Selecao multipla com checkboxes
- Barra de progresso em tempo real
- Download automatico do GitHub (fontes dev)
- Extracao automatica de arquivos .exe/.cab/.zip
- Atualizacao automatica do cache de fontes
- Deteccao e instalacao automatica de dependencias do sistema

## Instalacao

### Requisitos do Sistema

- **Sistema Operacional:** Ubuntu ou Debian (obrigatorio)
- **Python:** 3.11 ou superior
- **Dependencias do sistema:** `cabextract`, `fontconfig`

O programa detecta automaticamente dependencias faltantes e oferece instalacao automatica:

```
$ uv run font-installer
Font Installer para Ubuntu
----------------------------------------
Dependencias faltando: cabextract, fontconfig
Deseja instalar automaticamente? [S/n] s

Instalando dependencias...
Dependencias instaladas: cabextract, fontconfig
```

Ou instale manualmente:

```bash
sudo apt update && sudo apt install cabextract fontconfig
```

### Instalar o Font Installer

```bash
# Clonar o repositorio
git clone https://github.com/seu-usuario/font-installer.git
cd font-installer

# Instalar com uv (recomendado)
uv sync

# Ou com pip
pip install -e .
```

## Uso

### Interface Interativa (TUI)

```bash
uv run font-installer
```

```
┌──────────────────────────────────────────────────────────┐
│         Font Installer - Selecione as fontes            │
├──────────────────────────────────────────────────────────┤
│ [ClearType] [Dev Fonts] [Core Fonts] [Info]             │
├──────────────────────────────────────────────────────────┤
│  [x] Instalar todas as fontes ClearType (~26 arquivos)  │
│                                                          │
│  calibri | cambria | consolas | constantia | corbel     │
├──────────────────────────────────────────────────────────┤
│ [Selecionar Tudo]  [Limpar]  [Instalar]                 │
└──────────────────────────────────────────────────────────┘
 q Sair | a Selecionar | c Limpar | i Instalar
```

### Modo CLI

```bash
# Instalar fontes ClearType diretamente (sem TUI)
uv run font-installer --cli

# Instalar dependencias do sistema (cabextract, fontconfig)
uv run font-installer --install-deps

# Listar fontes instaladas
uv run font-installer list

# Exibir ajuda
uv run font-installer --help
```

### Atalhos de Teclado

| Tecla | Acao |
|:-----:|------|
| `Tab` | Navegar entre elementos |
| `Space` | Marcar/desmarcar checkbox |
| `a` | Selecionar todas as fontes |
| `c` | Limpar selecao |
| `i` | Iniciar instalacao |
| `q` | Sair |

## Fontes Disponiveis

### Microsoft ClearType (~26 arquivos)

Fontes incluidas no PowerPoint Viewer, baixadas automaticamente.

| Fonte | Tipo | Descricao |
|-------|:----:|-----------|
| **Calibri** | Sans-serif | Padrao do Microsoft Office |
| **Cambria** | Serif | Elegante para documentos |
| **Consolas** | Monospace | Ideal para programacao |
| **Constantia** | Serif | Classica e refinada |
| **Corbel** | Sans-serif | Humanista e legivel |
| **Candara** | Sans-serif | Suave e moderna |

### Fontes para Desenvolvimento

Baixadas diretamente das releases do GitHub.

| Fonte | Repositorio | Descricao |
|-------|-------------|-----------|
| **Cascadia Code** | microsoft/cascadia-code | Fonte oficial do Windows Terminal |
| **JetBrains Mono** | JetBrains/JetBrainsMono | Otimizada para IDEs |
| **Fira Code** | tonsky/FiraCode | Monospace com ligaduras |
| **Hack** | source-foundry/Hack | Limpa e legivel |
| **Source Code Pro** | adobe-fonts/source-code-pro | Fonte Adobe |
| **Victor Mono** | rubjo/victor-mono | Italico cursivo elegante |
| **Inconsolata** | googlefonts/Inconsolata | Classica do Google Fonts |

### Microsoft Core Fonts

Instaladas via `apt` (requer sudo).

- Arial, Times New Roman, Verdana, Tahoma, Courier New, Georgia, etc.

## Estrutura do Projeto

```
font-installer/
├── src/font_installer/
│   ├── __init__.py          # Metadata do pacote
│   ├── __main__.py          # Entry point: python -m font_installer
│   ├── cli.py               # Interface de linha de comando
│   │
│   ├── config/              # Configuracoes
│   │   ├── settings.py      # Constantes, paths, URLs
│   │   └── fonts.py         # Catalogo de fontes (dataclasses)
│   │
│   ├── core/                # Logica de negocio
│   │   ├── exceptions.py    # Excecoes customizadas
│   │   ├── downloader.py    # Download com callback de progresso
│   │   ├── extractor.py     # Extracao de cab/zip
│   │   └── installer.py     # Orquestrador principal
│   │
│   ├── ui/                  # Interface TUI
│   │   ├── app.py           # Aplicacao Textual
│   │   ├── styles.py        # CSS/Estilos
│   │   ├── widgets/         # Widgets customizados
│   │   └── screens/         # Telas adicionais
│   │
│   └── utils/               # Utilitarios
│       └── system.py        # Verificacoes do sistema
│
├── tests/                   # Testes automatizados
│   ├── conftest.py          # Fixtures pytest
│   ├── test_installer.py    # Testes unitarios
│   └── test_integration_flow.py  # Fluxo principal com rede/apt
│
├── pyproject.toml           # Configuracao do projeto
└── README.md
```

## Diretorios de Instalacao

| Categoria | Diretorio |
|-----------|-----------|
| Microsoft ClearType | `~/.local/share/fonts/microsoft/` |
| Developer Fonts | `~/.local/share/fonts/dev/` |
| Core Fonts (apt) | `/usr/share/fonts/truetype/msttcorefonts/` |

## Desenvolvimento

```bash
# Clonar e configurar ambiente
git clone https://github.com/seu-usuario/font-installer.git
cd font-installer
uv sync

# Executar testes
uv run pytest tests/ -v

# Executar testes de integracao (usa rede e apt)
RUN_INTEGRATION=1 uv run pytest -m integration -v

# Incluir teste de Core Fonts (requer sudo sem senha e pode solicitar EULA)
RUN_INTEGRATION=1 RUN_CORE_FONTS=1 uv run pytest -m integration -v

> Os testes de integracao exigem Linux com `apt`, acesso a rede e `sudo` sem senha (`sudo -n`).

# Executar com cobertura
uv run pytest tests/ --cov=font_installer

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
uv run ruff format src/
```

## FAQ

### Funciona em outras distribuicoes Linux?

Nao. Este programa foi desenvolvido especificamente para **Ubuntu/Debian** e depende do gerenciador de pacotes `apt`. Para outras distribuicoes, seria necessario adaptar a instalacao de dependencias.

### Onde fica a fonte Segoe UI?

A fonte Segoe UI e propriedade da Microsoft e nao esta disponivel para download publico.

**Alternativas:**
- **Selawik** (clone open-source): `sudo apt install fonts-selawik`
- **Open Sans** (visual similar)
- Copiar de uma instalacao Windows licenciada: `C:\Windows\Fonts\segoeui*.ttf`

### As fontes nao aparecem nos aplicativos

Apos a instalacao, reinicie os aplicativos ou execute:

```bash
fc-cache -fv ~/.local/share/fonts/
```

### Erro "cabextract not found"

Instale a dependencia:

```bash
sudo apt install cabextract
```

## Tecnologias

- [Python 3.11+](https://www.python.org/)
- [Textual](https://textual.textualize.io/) - Framework TUI
- [uv](https://github.com/astral-sh/uv) - Gerenciador de pacotes
- [pytest](https://pytest.org/) - Framework de testes
- [Ruff](https://github.com/astral-sh/ruff) - Linter/Formatter

## Licenca

Este projeto esta licenciado sob a [MIT License](LICENSE).

---

**Nota:** As fontes instaladas por este software sao propriedade de seus respectivos donos. Este instalador apenas automatiza o processo de download e instalacao de fontes disponibilizadas publicamente.
