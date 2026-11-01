# Telas modais

## Overview

Telas de confirmação e consulta da interface Textual.

## Interface

CoreFontsLicenseScreen (license.py) mostra recurso local validado por SHA-256; retorna booleano, foco na recusa e Escape=False. ConfirmExitScreen (confirm_exit.py) retorna intenção de sair após lote. HelpScreen (help.py) expõe atalhos, descrições e diretórios. Modais usam MODAL_CSS, ModalScreen e restauração de foco do Textual.

## Invariants

Nenhum lote é iniciado antes do aceite. Escape recusa e não altera a seleção.

## Side Effects

Leitura do recurso local de licença; mudança da tela ativa e resultado ao chamador.

## Verification

Na raiz: `.venv/bin/python -m pytest tests/test_ui_screens.py`.
