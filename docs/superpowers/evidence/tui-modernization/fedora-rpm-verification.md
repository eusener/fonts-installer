# Fedora — script e RPM locais

Solicitação de 2026-11-01: usar msttcore.sh com o RPM fornecido pelo usuário.

- msttcore.sh localiza o RPM ao lado do próprio script, independentemente do cwd.
- RPM é apenas extraído; nenhum gerenciador instala esse pacote no sistema.
- Refresh roda em -d/staging, sem executar sua configuração /etc/X11.
- Somente a cópia temporária recebe atualização dos URLs SourceForge para HTTPS;
  checksums fornecidos pelo RPM permanecem habilitados.
- Manifesto completo de fontes do payload é validado no staging antes da cópia;
  Arial/Calibri são obrigatórias. Fontes antigas não mascaram downloads ausentes.
- O destino padrão é ~/.local/share/fonts/microsoft-core, com cache direcionado.
- A saída do script aparece em eventos package/progress e logs literais da TUI.
- Script e RPM foram conferidos byte a byte dentro do wheel gerado do sdist.

## Verificações executadas

- Execução real do recurso importado diretamente do wheel, com destino isolado
  em /tmp: sucesso, 54 arquivos, Arial e Calibri presentes; cache atualizado.
  Diretórios temporários removidos ao terminar. Fontes pessoais não alteradas.
- 80 testes passaram; 4 integrações excluídas.
- bash -n passou; Ruff sem erros; wheel/sdist gerados.
- Testes específicos: cwd diferente, caminhos com espaços, Calibri ausente,
  Comic ausente, erro de script, resultado sem fontes, logs preservados.
- Revisão independente identificou risco de conjunto parcial; foi corrigido
  validando o manifesto completo. Rechecagem sem questão material restante.

O instalador ainda usa rede: o RPM contém o programa e metadados, não o conjunto
offline de fontes. Não foram alteradas configurações do host ou instalado RPM.

SHA-256 do RPM local: `55d7f3a86533225634ff3ea2384b4356d9665a29cc7eeacff16602a1714afbb4`.
