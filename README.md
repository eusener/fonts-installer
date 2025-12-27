# Font Installer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ubuntu](https://img.shields.io/badge/platform-Ubuntu%2FDebian-orange.svg)](https://ubuntu.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-unit%20%2B%20integration-brightgreen.svg)]()

Instalador interativo de fontes Microsoft e Developer para **Ubuntu/Debian** com interface TUI moderna.

> **Nota:** Este programa foi desenvolvido exclusivamente para sistemas Ubuntu/Debian. Não é compatível com outras distribuições Linux, macOS ou Windows.

## Funcionalidades

- Interface TUI interativa com [Textual](https://textual.textualize.io/)
- Navegação por abas (ClearType, Dev Fonts, Core Fonts)
- Seleção múltipla com checkboxes
- Barra de progresso em tempo real
- Download automático do GitHub (fontes dev)
- Extração automática de arquivos .exe/.cab/.zip
- Atualização automática do cache de fontes
- Detecção e instalação automática de dependências do sistema

## Instalação

### Requisitos do Sistema

- **Sistema Operacional:** Ubuntu ou Debian (obrigatório)
- **Python:** 3.11 ou superior
- **Dependências do sistema:** `cabextract`, `fontconfig`

O programa detecta automaticamente dependências faltantes e oferece instalação automática:

```
$ uv run font-installer
Font Installer para Ubuntu
----------------------------------------
Dependências faltando: cabextract, fontconfig
Deseja instalar automaticamente? [S/n] s

Instalando dependências...
Dependências instaladas: cabextract, fontconfig
```

Ou instale manualmente:

```bash
sudo apt update && sudo apt install cabextract fontconfig
```

### Instalar o Font Installer

```bash
# Clonar o repositório
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

# Instalar dependências do sistema (cabextract, fontconfig)
uv run font-installer --install-deps

# Listar fontes instaladas
uv run font-installer list

# Exibir ajuda
uv run font-installer --help
```

### Atalhos de Teclado

| Tecla | Ação |
|:-----:|------|
| `Tab` | Navegar entre elementos |
| `Space` | Marcar/desmarcar checkbox |
| `a` | Selecionar todas as fontes |
| `c` | Limpar seleção |
| `i` | Iniciar instalação |
| `q` | Sair |

## Fontes Disponíveis

### Microsoft ClearType (~26 arquivos)

Fontes incluídas no PowerPoint Viewer, baixadas automaticamente.

| Fonte | Tipo | Descrição |
|-------|:----:|-----------|
| **Calibri** | Sans-serif | Padrão do Microsoft Office |
| **Cambria** | Serif | Elegante para documentos |
| **Consolas** | Monospace | Ideal para programação |
| **Constantia** | Serif | Clássica e refinada |
| **Corbel** | Sans-serif | Humanista e legível |
| **Candara** | Sans-serif | Suave e moderna |

### Fontes para Desenvolvimento

Baixadas diretamente das releases do GitHub.

| Fonte | Repositório | Descrição |
|-------|-------------|-----------|
| **Cascadia Code** | microsoft/cascadia-code | Fonte oficial do Windows Terminal |
| **JetBrains Mono** | JetBrains/JetBrainsMono | Otimizada para IDEs |
| **Fira Code** | tonsky/FiraCode | Monospace com ligaduras |
| **Hack** | source-foundry/Hack | Limpa e legível |
| **Source Code Pro** | adobe-fonts/source-code-pro | Fonte Adobe |
| **Victor Mono** | rubjo/victor-mono | Itálico cursivo elegante |
| **Inconsolata** | googlefonts/Inconsolata | Clássica do Google Fonts |

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
│   ├── config/              # Configurações
│   │   ├── settings.py      # Constantes, paths, URLs
│   │   └── fonts.py         # Catálogo de fontes (dataclasses)
│   │
│   ├── core/                # Lógica de negócio
│   │   ├── exceptions.py    # Exceções customizadas
│   │   ├── downloader.py    # Download com callback de progresso
│   │   ├── extractor.py     # Extração de cab/zip
│   │   └── installer.py     # Orquestrador principal
│   │
│   ├── ui/                  # Interface TUI
│   │   ├── app.py           # Aplicação Textual
│   │   ├── styles.py        # CSS/Estilos
│   │   ├── widgets/         # Widgets customizados
│   │   └── screens/         # Telas adicionais
│   │
│   └── utils/               # Utilitários
│       └── system.py        # Verificações do sistema
│
├── tests/                   # Testes automatizados
│   ├── conftest.py          # Fixtures pytest
│   ├── test_installer.py    # Testes unitários
│   └── test_integration_flow.py  # Fluxo principal com rede/apt
│
├── pyproject.toml           # Configuração do projeto
└── README.md
```

## Diretórios de Instalação

| Categoria | Diretório |
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

# Executar testes de integração (usa rede e apt)
RUN_INTEGRATION=1 uv run pytest -m integration -v

# Incluir teste de Core Fonts (requer sudo sem senha e pode solicitar EULA)
RUN_INTEGRATION=1 RUN_CORE_FONTS=1 uv run pytest -m integration -v

> Os testes de integração exigem Linux com `apt`, acesso à rede e `sudo` sem senha (`sudo -n`).

# Executar com cobertura
uv run pytest tests/ --cov=font_installer

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
uv run ruff format src/
```

## FAQ

### Funciona em outras distribuições Linux?

Não. Este programa foi desenvolvido especificamente para **Ubuntu/Debian** e depende do gerenciador de pacotes `apt`. Para outras distribuições, seria necessário adaptar a instalação de dependências.

### Onde fica a fonte Segoe UI?

A fonte Segoe UI é propriedade da Microsoft e não está disponível para download público.

**Alternativas:**
- **Selawik** (clone open-source): `sudo apt install fonts-selawik`
- **Open Sans** (visual similar)
- Copiar de uma instalação Windows licenciada: `C:\Windows\Fonts\segoeui*.ttf`

### As fontes não aparecem nos aplicativos

Após a instalação, reinicie os aplicativos ou execute:

```bash
fc-cache -fv ~/.local/share/fonts/
```

### Erro "cabextract not found"

Instale a dependência:

```bash
sudo apt install cabextract
```

## Tecnologias

- [Python 3.11+](https://www.python.org/)
- [Textual](https://textual.textualize.io/) - Framework TUI
- [uv](https://github.com/astral-sh/uv) - Gerenciador de pacotes
- [pytest](https://pytest.org/) - Framework de testes
- [Ruff](https://github.com/astral-sh/ruff) - Linter/Formatter

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

**Nota:** As fontes instaladas por este software são propriedade de seus respectivos donos. Este instalador apenas automatiza o processo de download e instalação de fontes disponibilizadas publicamente.
