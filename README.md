# Font Installer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-Linux-orange.svg)](https://www.kernel.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Tests](https://img.shields.io/badge/tests-unit%20%2B%20integration-brightgreen.svg)

Instalador interativo de fontes Microsoft e Developer para **Linux** com interface TUI moderna.

> **Distribuições:** Ubuntu/Debian, Fedora, Arch/Manjaro, openSUSE e Alpine. Microsoft Core Fonts: pacote nativo em Ubuntu/Debian e instalação no diretório do usuário no Fedora. macOS e Windows não são suportados.

## Funcionalidades

- Interface TUI interativa com [Textual](https://textual.textualize.io/)
- Catálogo simultâneo de ClearType, Dev e Core Fonts, sem abas
- Seleção múltipla com checkboxes
- Barra de progresso em tempo real
- Download automático do GitHub (fontes dev)
- Extração automática de arquivos .exe/.cab/.zip
- Atualização automática do cache de fontes
- Detecção e instalação automática de dependências do sistema

## Instalação

### Requisitos do Sistema

- **Sistema Operacional:** Ubuntu/Debian, Fedora, Arch/Manjaro, openSUSE ou Alpine
- **Privilégios:** root ou `sudo` para instalar pacotes do sistema; fontes ClearType/Dev são instaladas no diretório do usuário
- **Python:** 3.11 ou superior; **Textual:** 8.2.8 ou superior
- **Dependências do sistema:** `cabextract`, `fontconfig`

O programa detecta automaticamente dependências faltantes e oferece instalação automática:

```
$ uv run font-installer
Font Installer para Linux
----------------------------------------
Dependências faltando: cabextract, fc-cache
Deseja instalar automaticamente? [S/n] s

Instalando dependências...
Dependências instaladas: cabextract, fontconfig
```

A distribuição é identificada por `ID` e `ID_LIKE` de `/etc/os-release`.
O gerenciador correspondente precisa estar instalado. Nenhum repositório externo
é adicionado automaticamente; os pacotes precisam estar nos repositórios habilitados.
Em distribuições desconhecidas, instale `cabextract` e `fontconfig` manualmente.

| Distribuição | Instalação manual das dependências |
|-------------|-----------------------------------|
| Ubuntu/Debian | `sudo apt update && sudo apt install -y cabextract fontconfig` |
| Fedora | `sudo dnf install -y cabextract fontconfig` |
| Arch/Manjaro | `sudo pacman -S --needed --noconfirm cabextract fontconfig` |
| openSUSE | `sudo zypper --non-interactive install cabextract fontconfig` |
| Alpine | `sudo apk add cabextract fontconfig` |

Como root, omita `sudo`. Em Arch/Manjaro, mantenha o sistema atualizado pelo
procedimento habitual da distribuição antes de instalar novos pacotes.

Referências dos gerenciadores: [pacman](https://man.archlinux.org/man/pacman.8.en),
[zypper](https://manpages.opensuse.org/Tumbleweed/zypper/zypper.8.en.html) e
[apk](https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html).

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

```text
Font Installer / Linux
Desenvolvimento                  Microsoft
[ ] Cascadia Code                [ ] ClearType
[ ] JetBrains Mono                   Calibri · Cambria · Consolas
[ ] Fira Code                        Constantia · Corbel · Candara
[ ] Hack                         [ ] Core Fonts (Fedora e Ubuntu/Debian)
[ ] Source Code Pro
[ ] Victor Mono
[ ] Inconsolata

Atividade: etapa atual / download / itens processados
Logs recolhíveis: início, mudança de etapa, resultado e erro
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
| `a` | Selecionar ClearType e Dev (Core é escolha individual) |
| `c` | Limpar seleção |
| `i` | Iniciar instalação |
| `l` | Abrir/recolher logs |
| `f` | Retomar acompanhamento do log |
| `?` | Ajuda, descrições e diretórios |
| `r` | Limpar log/verificar dependências fora da instalação |
| `q` | Sair; com lote ativo, confirmar e aguardar sua conclusão |

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

Em Ubuntu/Debian, instaladas via `apt` (`ttf-mscorefonts-installer`),
como root ou com `sudo`. O pacote precisa estar nos repositórios habilitados.
No Fedora, o aplicativo executa `src/font_installer/utils/msttcore.sh`, que
extrai o instalador de `msttcore-fonts-installer-2.6-1.noarch.rpm` incluído no
app. O instalador baixa e verifica os arquivos de fontes; o wrapper valida
Arial e Calibri e copia para `~/.local/share/fonts/microsoft-core/`. O RPM não
é instalado no sistema, e a cópia não solicita sudo. As dependências
`cabextract`, `fontconfig`, `rpm` (rpm2cpio), `cpio`, `curl` e `bash` são
verificadas e podem ser instaladas via `dnf` quando faltantes.

A licença é apresentada antes de iniciar o lote. O fluxo Fedora mantém a TUI
e os logs ativos; somente o fluxo de pacote Debian/Ubuntu suspende a interface
para senha e eventuais confirmações adicionais. Outras distribuições continuam
com ClearType e Dev; Core ainda não possui instalação automática nelas.

No Fedora, o conjunto do instalador local inclui Arial e Calibri; a instalação
é considerada incompleta se uma dessas fontes não for obtida. O conjunto
exato de fontes difere do pacote apt. O RPM contém o instalador e os checksums,
não uma cópia offline completa das fontes: ainda é necessária conexão à rede.

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
│   │   ├── packages.py      # Detecção da distribuição e gerenciador
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
│   ├── test_packages.py     # Distribuições, comandos e falhas simuladas
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
| Core Fonts (Ubuntu/Debian via apt) | `/usr/share/fonts/truetype/msttcorefonts/` |
| Core Fonts (Fedora, usuário) | `~/.local/share/fonts/microsoft-core/` |

## Desenvolvimento

```bash
# Clonar e configurar ambiente
git clone https://github.com/seu-usuario/font-installer.git
cd font-installer
uv sync --extra dev

# Executar testes
uv run pytest tests/ -v

# Executar testes de integração (usa rede e apt)
RUN_INTEGRATION=1 uv run pytest -m integration -v

# Incluir teste de Core Fonts (requer sudo sem senha e pode solicitar EULA)
RUN_INTEGRATION=1 RUN_CORE_FONTS=1 uv run pytest -m integration -v

# Testes de instalação de pacotes exigem Ubuntu/Debian, apt e sudo sem senha.
# Testes de download exigem rede; a extração ClearType exige cabextract.

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

Sim: Fedora, Arch/Manjaro, openSUSE e Alpine, além de Ubuntu/Debian.
As dependências são instaladas pelo gerenciador nativo. Core Fonts via pacote
ficam restritas à família Debian; no Fedora, o app extrai os arquivos originais
no diretório do usuário usando o script e o RPM locais. Os testes automatizados simulam essas
distribuições; instalações reais em todas elas ainda precisam de validação.

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

Execute a instalação de dependências para sua distribuição:

```bash
font-installer --install-deps
```

Ou consulte a tabela de comandos de instalação manual acima.

## Tecnologias

- [Python 3.11+](https://www.python.org/)
- [Textual](https://textual.textualize.io/) - Framework TUI
- [uv](https://github.com/astral-sh/uv) - Gerenciador de pacotes
- [pytest](https://pytest.org/) - Framework de testes
- [Ruff](https://github.com/astral-sh/ruff) - Linter/Formatter

## Licença

Este projeto está licenciado sob a MIT License.

---

**Nota:** As fontes instaladas por este software são propriedade de seus respectivos donos. Este instalador apenas automatiza o processo de download e instalação de fontes disponibilizadas publicamente.


## System Overview

O ponto de entrada `font-installer` é definido em `pyproject.toml`
(`project.scripts`) e chama `font_installer.cli:main`. O módulo
`src/font_installer/__main__.py` oferece o mesmo fluxo com `python -m font_installer`.
A CLI e a aplicação Textual compartilham o instalador, o catálogo e as verificações
de sistema. Os contratos abaixo descrevem os limites internos do código atual.

## Interface

- `font-installer`: comando publicado por `pyproject.toml:project.scripts`.
- `main()`: seleciona ajuda, listagem, instalação de dependências, instalação
  ClearType em CLI ou TUI (`src/font_installer/cli.py:main`).

## Subdirectories & System Boundaries

- [src](./src/README.md): índice dos pacotes de produção e seus contratos.
- `tests/`: testes pytest; excluído da geração de contratos por conter testes.
- `docs/`: planos e especificações existentes; excluído por não conter código.

## Invariants

- A distribuição requer Python 3.11 ou superior (`pyproject.toml:project.requires-python`).
- Sem argumentos, a CLI verifica dependências antes de iniciar a TUI;
  comando desconhecido retorna 1 (`src/font_installer/cli.py:main`).

## Global Invariants

- A escolha do gerenciador utiliza primeiro `ID`, depois `ID_LIKE`, e exige o
  executável correspondente (`src/font_installer/core/packages.py:detect_package_manager`).
- As extensões de fonte aceitas são `.ttf`, `.ttc` e `.otf`
  (`src/font_installer/config/settings.py:Settings.FONT_EXTENSIONS`).

## Side Effects

- A CLI escreve no terminal e pode solicitar confirmação no stdin
  (`src/font_installer/cli.py:print_help`, `check_and_install_deps`).

## Global Side Effects

- Instalações podem baixar arquivos, extrair arquivos temporários e copiar fontes
  para diretórios do usuário (`src/font_installer/core/installer.py:FontInstaller`).
- Instalações de pacotes executam processos do gerenciador nativo, com `sudo`
  quando necessário (`src/font_installer/core/packages.py:PackageManager.install`).
- A atualização do cache executa `fc-cache`
  (`src/font_installer/core/installer.py:FontInstaller.update_font_cache`).

## System Verification

Na raiz do repositório, com o ambiente de desenvolvimento instalado:

```bash
.venv/bin/python -m pytest -m "not integration"
```

O runner e os marcadores são definidos em `pyproject.toml:tool.pytest.ini_options`.
Os comandos de integração e seus requisitos estão na seção Desenvolvimento.


## Interface compacta e acompanhamento

O alvo é 120 colunas × 36 linhas, inclusive com logs abertos. Em terminais
menores, a lista empilha as categorias e permite rolagem. `l` recolhe os logs;
ao iniciar um lote, eles abrem novamente. Rolagem no histórico pausa o avanço
automático; `f` retoma. O histórico tem até 500 entradas em memória.

O percentual pertence ao download atual, não à instalação inteira. Quando não
há tamanho conhecido, a tela mostra spinner e bytes recebidos. Extração, cópia
e cache aparecem como etapas, com resumo de sucesso, falha parcial ou falha.

Core Fonts requer aceite no modal com cópia local conferida da licença. Escape
ou recusa retorna à seleção sem iniciar o lote. No Debian/Ubuntu, a TUI fica suspensa durante o
comando de pacotes: senha e eventuais confirmações adicionais são respondidas
no terminal nativo. O aplicativo não armazena senha nem persiste o aceite.

A dependência mínima é Textual 8.2.8. Para testar sem instalações reais:

```bash
uv run pytest -m "not integration"
```

[Captura do catálogo](./docs/superpowers/evidence/tui-modernization/catalog.svg)
e [modal de licença](./docs/superpowers/evidence/tui-modernization/license.svg).
