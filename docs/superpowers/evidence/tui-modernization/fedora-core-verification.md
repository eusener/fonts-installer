# Core Fonts no Fedora — verificação

Causa: install_core_fonts exigia apt; dependências já suportavam dnf.
Correção: caminho Fedora usa 11 arquivos originais SourceForge, cabextract e
Settings.CORE_FONTS_DIR. A TUI mantém licença e callback no worker, sem suspensão.
Debian/Ubuntu preservam o comando apt e interação nativa.

## Evidências

- Host de teste: Fedora Linux 44 Workstation, cabextract e dnf disponíveis.
- Download e extração reais dos 11 arquivos em TemporaryDirectory sob /tmp:
  sucesso, 30 arquivos de fontes copiados. Diretório temporário removido ao
  encerrar; nenhuma fonte instalada no diretório pessoal por esta verificação.
- 76 testes passaram; 4 integrações excluídas.
- Ruff sem erros nos arquivos alterados; wheel e sdist gerados.
- Revisão independente estática sem problemas materiais.
- Casos simulados: download parcial, eventos, listagem/contagem de Core e
  aceite seguido de instalação no worker sem suspender a TUI.

## Alterações de contrato

Core local usa files_expected não nulo e contagem real de arquivos;
resultado apt mantém indicador histórico de pacote separado da contagem.
SystemChecker e CLI incluem a categoria core do usuário. Outros gerenciadores
não ganharam instalação Core automática nesta mudança.

Referências: [Core Fonts](https://corefonts.sourceforge.net/) e
[lista de arquivos no instalador Debian](https://sources.debian.org/data/contrib/m/msttcorefonts/3.8.1/update-ms-fonts).
