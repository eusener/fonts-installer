# Modernização da TUI — execução

Design: ../specs/2026-10-31-tui-modernization-design.md
Execução inline conforme solicitação de implementação. Sem commits automáticos.
Preservar alterações locais; backup inicial /tmp/font-installer-before-tui.

- [x] Fase 0: Textual >=8.2.8 e lock; suíte de regressão.
- [x] Fase 1: contratos opcionais e erro de callback; testes RED/GREEN.
- [x] Fase 2: streaming, fases e resultados; testes operacionais/inesperados.
- [x] Fase 3: recursos de licença e modais; recurso no wheel e testes.
- [x] Fase 4: UI compacta, caixa/timer, logs, suspensão e saída; testes headless/visual.
- [x] Fase 5: contratos, ajuda, verificação final e revisão independente.

Ruling: executar no checkout atual, incluindo alterações locais, como solicitado;
nenhum reset, checkout ou commit será feito. O design aprovado já é o plano
vinculante; este arquivo apenas acompanha sua execução.

Base: 38 testes passaram; 4 de integração excluídos.

Fases 0–4: contratos e UI implementados. RED observado para campos opcionais,
resposta inválida, cópia parcial, callback, modais, geometria e bytes recebidos;
GREEN após correções. 67 testes passaram; 4 integrações excluídas.
Ruling: pytest assíncrono executado fora do sandbox depois de diagnosticar
bloqueio no shutdown do executor, reproduzido apenas no ambiente restrito.
Revisão independente: HTTPException operacional corrigida com dois testes RED/GREEN;
bytes desconhecidos agora visíveis. Nenhum apt/sudo executado.
Ruling: Hatch inclui assets por descoberta; force-include duplicava os recursos.
Usar artifacts mais descoberta padrão, comprovados pelo build de wheel a partir do sdist.

Conclusão: 71 testes passaram, 4 integrações excluídas. Ruff check passou;
format check dos arquivos implementados passou após formatar os dois últimos.
Wheel e sdist gerados com sucesso a partir do sdist. Recurso conferido em extração
isolada do wheel. PTY real com comando simulado retornou à TUI após Enter.
9 documentos verificados; alterações locais em system.py, packages.py,
test_packages.py e configuração preservadas por comparação de bytes.
Revisão independente sem achados críticos; achado HTTPException corrigido e
observação de bytes desconhecidos implementada, com testes de regressão.
Sem commits, push, instalação real de fontes/pacotes ou mudanças fora do escopo.


Atualização 2026-11-01: Fedora passa a usar msttcore.sh + RPM local por solicitação
explícita. Wrapper usa staging -d para evitar /etc/X11 e valida manifesto completo;
Python executa Bash e transmite saída. 80 testes, lint, sintaxe shell e build
passaram. Teste real a partir do wheel em /tmp obteve 54 fontes (Arial/Calibri).
Evidência: ../evidence/tui-modernization/fedora-rpm-verification.md.
