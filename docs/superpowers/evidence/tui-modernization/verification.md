# Verificação da implementação

- Suíte: 71 testes passaram, 4 integrações excluídas (`pytest -m "not integration"`).
- Ruff: sem erros nos arquivos de implementação e testes alterados. Aviso de
  configuração antiga do Ruff já existente; sem migração de configuração nesta mudança.
- Build: wheel e sdist gerados em /tmp/font-installer-dist; licença presente sem
  duplicação e carregável por importlib.resources fora da árvore fonte, com SHA-256.
- Interface: inspeção das capturas catalog.svg, license.svg e compact.svg;
  testes de geometria, teclado, recusa, redimensionamento, logs e resultados.
- Terminal real: suspensão/retorno verificados em PTY com substituto de Core
  que lê Enter; nenhuma instalação real executada.
- Revisão independente: nenhuma falha crítica; HTTPException corrigida e testada
  como falha operacional; bytes desconhecidos adicionados e testados.
- Preservação: backup inicial em /tmp/font-installer-before-tui; arquivos fora
  do escopo comparados byte a byte, sem reset ou commit.

## Limites

Apt/sudo e downloads reais não foram executados nos testes. O texto de licença
foi obtido da referência Core Fonts, extraído sem resumir ou traduzir e conferido
por hash do recurso empacotado; variantes futuras dos pacotes podem exibir sua
confirmação própria no terminal nativo. O aplicativo não grava aceite no debconf.
A versão mínima validada é Textual 8.2.8; não foram testadas todas as versões
futuras que satisfaçam a faixa sem teto.
