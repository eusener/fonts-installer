# Interface Textual

## Overview

Catálogo simultâneo em Gruvbox Dark, atividade por etapa e logs recolhíveis.
Em 120 × 36 células, Dev e Microsoft ocupam duas colunas; abaixo desse tamanho,
`FontInstallerApp.on_resize` empilha categorias e permite rolagem.

## Interface

- `app.py:FontInstallerApp` compõe nove opções, ações, resumo e histórico.
- `action_install`, `_license_answer` e `_start` validam seleção/aceite e capturam o lote.
- `_publish` recebe eventos do worker; `_drain_events` aplica-os em ordem a cada 100 ms.
- `_run_installation` instala sequencialmente; `_finish` resume resultados e libera controles.
- `_install_core_native` suspende a TUI para interação nativa do pacote.
- `action_toggle_logs`, `action_follow_log`, `action_help`, `action_refresh` e `action_quit`
  oferecem consulta e saída adiada.
- [Telas](./screens/README.md): licença, confirmação de saída e ajuda.
- [Widgets](./widgets/README.md): pacote reservado sem implementações atuais.
- `styles.py:APP_CSS`, `MODAL_CSS` e `LOG_COLORS` centralizam Gruvbox.

## Invariants

- `_start` bloqueia seleção e novas instalações antes de agendar o worker.
- `_publish` só troca referências sob lock; nenhum callback espera repaint.
- Amostras do mesmo item/fase são consolidadas; transições e finalização são preservadas.
- `_finish` invalida o lote para descartar eventos atrasados; resumo fica fora dos logs.
- `_log` limita 500 entradas de até 2.048 caracteres, renderizadas como texto literal.
- `action_select_all` seleciona ClearType/Dev e mantém Core como escolha explícita.
- Percentual representa download com tamanho conhecido; demais fases usam spinner.
- `action_quit` confirmado aguarda o lote inteiro, sem cancelamento implícito.

## Side Effects

Widgets, foco e logs são atualizados na thread da UI; o worker delega downloads,
extração, cópia e cache ao core. Core Fonts usa terminal nativo e suspensão apenas no caminho apt;
no Fedora, instalação local roda no worker com progresso e logs ativos. Senha não é coletada nem registrada pela aplicação.

## Verification

Na raiz: `.venv/bin/python -m pytest tests/test_ui.py tests/test_ui_screens.py`.


No Fedora, linhas do script são eventos package/progress: não são consolidadas
como amostras de download, e são registradas no histórico de texto literal.
O spinner indica atividade sem inventar percentual do script externo.
