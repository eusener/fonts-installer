# Evidências da TUI

Capturas headless com dados simulados, sem downloads nem instalações reais:

- [Catálogo 120 × 36](./catalog.svg): nove opções e nomes ClearType visíveis,
  aviso de dependência, progresso e logs abertos.
- [Licença](./license.svg): texto original, foco em recusa e ações visíveis.
- [Compacto 80 × 24](./compact.svg): catálogo empilhado e rolável.

As capturas são estados montados para inspeção visual, não prova de instalação.
Os testes comportamentais estão em tests/test_ui.py e tests/test_ui_screens.py.
O comando de pacotes foi substituído por uma leitura de Enter no teste PTY;
a suspensão e restauração retornaram sem erro. Apt/sudo reais não foram executados.
