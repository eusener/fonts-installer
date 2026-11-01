# Identidade visual

A interface Textual do instalador usa **Gruvbox Dark**.

- Fundo: `#282828`; superfícies: `#3c3836`; bordas: `#665c54`.
- Texto principal: `#ebdbb2`; secundário: `#d5c4a1`; descrições: `#a89984`.
- Azul: `#83a598`; amarelo: `#fabd2f`; verde: `#b8bb26`;
  vermelho: `#fb4934`; roxo: `#d3869b`; aqua: `#8ec07c`.
- Erros usam vermelho, sucesso verde, avisos amarelo e atividade aqua.
- Os estilos são centralizados em `src/font_installer/ui/styles.py` (`APP_CSS`);
  `LOG_COLORS` aplica os mesmos tons à marcação Rich dos logs.
- Nas versões do Textual que oferecem Gruvbox, o tema nativo também é ativado
  para os componentes internos. O CSS mantém a paleta em versões anteriores.
- Catálogo simultâneo em duas colunas a partir de 120 × 36 células; abaixo disso,
  categorias empilhadas e roláveis. O terminal controla a tipografia.
- Foco usa fundo, negrito e inversão, além de cores. pt-BR em toda a navegação;
  o texto original da licença permanece em inglês.
- App é dono de seleção/lote; core é dono de I/O. Callbacks publicam na caixa,
  timer da UI a cada 100 ms consome em ordem. Core usa suspensão nativa.
- Logs: 500 entradas, no máximo 2.048 caracteres cada; texto literal e histórico
  pausado durante consulta. Estado final fica fora do painel recolhível.
- Fontes e ações ficam bloqueadas durante lote; logs e ajuda continuam acessíveis.
  Licença/saída usam ModalScreen, foco inicial seguro e Escape para recusa.
- Rolagem segue estilos globais em styles.py; sem esconder scrollbars.
- Verificação: tests/test_ui.py e tests/test_ui_screens.py; capturas em
  docs/superpowers/evidence/tui-modernization/.
