# Revisão anotada Goldfish — resolução aplicada

**Status: resolved**

- **Alvo:** [design da TUI](../superpowers/specs/2026-10-31-tui-modernization-design.md), linhas originais 413–601.
- **Entrada:** [relatório de prontidão](./implementation_readiness_report.md), achados IR-01 a IR-05.
- **Estado:** cinco propostas aceitas e aplicadas somente ao design; código sem alterações nesta resolução.
- **Data:** 2026-10-31.

## Avaliação dos achados e sugestões

### IR-01 — Fases estáveis — Major

- **Lente:** egm-implementation-readiness.
- **Escopo original:** linhas 471–509 e 543–568.
- **Discrepância:** ordem de arquivos sem agrupamento incremental nem verificações intermediárias.
- **Fundamento:** alterar quem lança exceções antes de adaptar consumidores pode quebrar a aplicação entre tarefas.
- **Sugestão:** PROPOSE FIX.
- **Edição proposta:** substituir a ideia de ordem estritamente por arquivo por
  um inventário de arquivos associado às fases abaixo. Inserir a seção
  “Fases de execução e critérios de passagem” antes do inventário:

| Fase | Alterações que entram juntas | Critério de passagem |
| --- | --- | --- |
| 0 — Base de compatibilidade | Alteração da versão mínima em pyproject.toml e atualização de uv.lock, somente se a proposta IR-04 for aceita; ambiente isolado | Importar app, executar suíte existente sem integração e verificar APIs públicas de suspensão, timer e mensagens na versão mínima escolhida e na instalada |
| 1 — Contrato aditivo | Campos opcionais de DownloadProgress e InstallResult, ProgressCallbackError em exceptions.py, respectivos testes; sem mudar ainda quem retorna None ou lança erros na consulta | Construtores antigos funcionam; CLI e suíte simulada continuam passando |
| 2 — Falhas e eventos | Streaming/downloader, consulta de release, capturas do instalador e resultados parciais na mesma fase; testes de downloader e installer | Falha operacional segue ao próximo item, erro inesperado interrompe; callbacks falhos propagam; nenhum erro novo de consulta fica sem consumidor |
| 3 — Recursos e telas | Texto verificado, metadados, empacotamento e três modais, com testes de telas/recurso | Licença no wheel, recusa segura, foco previsível; aplicativo existente continua funcionando antes da integração das telas |
| 4 — Integração da TUI | app.py/styles.py, caixa de eventos, seleção, logs, suspensão, saída adiada e testes UI/CLI; atualizar ajuda CLI na mesma fase | Suíte simulada passa; alvo 120 × 36 e adaptação 80 × 24 demonstrados; suspensão simulada retorna em sucesso/erro/interrupção |
| 5 — Documentação e entrega | Todos os READMEs e DESIGN.md já enumerados | Links resolvem; evidência visual, wheel e regressão final conferidos |

Cada fase depende da anterior, termina com
`.venv/bin/python -m pytest -m "not integration"` e não permite avançar com
falhas novas. Fases são unidades de trabalho, não instruções de commit.

### IR-02 — Fronteiras de erro — Major

- **Lentes:** egm-implementation-readiness e egm-codebase-details.
- **Escopo original:** linhas 449–452, 480–481 e 537–539.
- **Discrepância:** “esperado” versus “inesperado” não define classes nem capturas.
- **Fundamento:** capturas genéricas atuais ocultam erros de programação ou callback como falhas comuns.
- **Sugestão:** PROPOSE FIX.
- **Edição proposta:** inserir “Classificação e fronteiras de exceções” após a
  política de espera, atualizar linhas do inventário e testes conforme abaixo.

| Operação | Falha operacional e conversão | O que não absorver |
| --- | --- | --- |
| HTTP/download/gravação de arquivo | urllib.error.HTTPError, URLError, TimeoutError e OSError viram DownloadError(url, reason), apenas no bloco da operação I/O | Erros de programação e ProgressCallbackError |
| Consulta de release | Mesmas falhas de rede, UnicodeDecodeError e json.JSONDecodeError viram DownloadError(api_url, reason); estrutura JSON inválida é validada explicitamente e também vira DownloadError | Não capturar Exception ou ValueError genéricos; None reservado a uma resposta válida sem ZIP compatível |
| Extração, temporários e cópia | DownloadError, ExtractionError, InstallationError, OSError, shutil.Error e subprocess.SubprocessError viram InstallResult falso na fronteira do item; quantidade copiada distingue falha parcial | TypeError, AttributeError, AssertionError, RuntimeError e outras exceções não listadas propagam |
| Core e cache | Preservar resultado operacional dos métodos atuais; na ponte Core, KeyboardInterrupt vira falha explícita dentro da suspensão, para restaurar o terminal | Não capturar BaseException genericamente nem ignorar erro de restauração |
| Callback | Invocar por helper que captura Exception do consumidor e relança ProgressCallbackError com causa original, fora das capturas de falhas I/O | Não converter ProgressCallbackError em resultado operacional nem emitir novamente o mesmo callback falho |
| Limite externo do worker | Exception não operacional registra erro inesperado, marca itens restantes como não tentados e finaliza a UI | Não continuar o lote nem chamar novamente callback que acabou de falhar |

Definir `ProgressCallbackError(RuntimeError)` em `core/exceptions.py`, com
mensagem fixa de falha no callback e causa preservada via encadeamento.
Não exportar em core/__init__.py sem consumidor público. Os emissores em
Downloader e FontInstaller usam o helper de chamada; callbacks existentes
continuam recebendo um único DownloadProgress. Capturas de I/O ficam restritas
à operação real, e não abrangem arbitrariamente a renderização.

Mover a consulta GitHub e criação/limpeza do temporário para o tratamento de
falhas operacionais do item. Validar que JSON tenha objeto e lista de assets;
assets usados devem ter nome e URL em string. Falta de asset ZIP compatível é
None; resposta com esquema inválido é DownloadError. Preservar a preferência
atual de ZIP por padrão e o fallback de ZIP.

Nos testes, simular separadamente HTTP, rede, timeout, JSON inválido, resposta
sem ZIP, diretório temporário sem permissão, extração com falha, cópia parcial,
TypeError inesperado e callback que lança OSError ou RuntimeError. OSError do
callback deve ser ProgressCallbackError, não DownloadError. No worker,
comprovar continuação apenas para falha operacional e itens não tentados no
erro inesperado. A finalização continua responsável por liberar a UI.

Acrescentar `src/font_installer/core/exceptions.py` ao inventário de arquivos
modificados, com a justificativa de preservar origem do erro do consumidor.

### IR-03 — Entrega de progresso sem travessia síncrona por bloco — Major

- **Lente:** egm-codebase-details.
- **Escopo original:** linhas 487 e 528–531.
- **Discrepância:** o plano limita repaints mas não define transferência ou ordenação.
- **Fundamento:** call_from_thread atual espera o retorno da UI em cada callback.
- **Sugestão:** PROPOSE FIX.
- **Edição proposta:** inserir “Caixa local de eventos e consumo pela UI” antes
  dos critérios de comportamento e substituir o trecho que deixa o mecanismo implícito.

Usar uma caixa local em `ui/app.py`, sem serviço ou módulo adicional, protegida
por threading.Lock. Ela contém sequência crescente, identificador do lote,
última amostra de progresso pendente e deque de eventos não descartáveis.
O callback da TUI só copia o payload e publica nessa caixa; não chama widgets,
call_from_thread, sleep ou espera de futura renderização. O pequeno lock não
espera a UI executar: adquirir apenas para troca de referências; processar e
renderizar fora dele.

Uma amostra nova substitui a anterior apenas se pertencer ao mesmo lote/item/fase.
Antes de inserir transição, resultado ou finalização, mover a última amostra
pendente para a deque, seguida do evento não descartável. Não descartar eventos
started/completed/failed, resultados de item ou finalização. Como a execução é
sequencial e não há uma entrada por bloco, a deque armazena transições e no
máximo uma amostra por segmento entre transições; não precisa bloquear produtor
para limitar repaints.

Um timer da UI em intervalos de 0,1 segundo retira atomicamente os eventos e a
última amostra. Fora do lock, processa-os na ordem de sequência, atualiza logs
de transição e aplica a última medida pertinente ao estado atual. Múltiplas
medidas intermediárias no mesmo tick não exigem repaints separados. Finalização
é evento terminal: ao processá-la, consumir os eventos anteriores, liberar
controles, invalidar o lote e descartar amostras posteriores desse lote.

Para Core, antes da chamada síncrona exclusiva da ponte de suspensão, o handler
da UI drena a caixa e aplica a fase package. Durante a suspensão não há itens
concorrentes. Ao retornar, resultado/finalização entram na mesma caixa. Reservar
call_from_thread exclusivamente à ponte que precisa devolver o resultado de
Core; eventos normais e finalização usam a caixa.

Testar produtor emitindo centenas de amostras enquanto o consumidor da caixa
está pausado por um evento controlado; o produtor deve terminar antes de liberar
o consumidor. Não bloquear o próprio loop que executa o teste. Testar retenção
da última amostra, transição download→extract sem percentual antigo, ordem de
erro/resultado/finalização e eventos atrasados após lote invalidado. Testes
usam sincronização determinística, não sleep como prova de ausência de bloqueio.

Essa proposta concretiza uma escolha técnica nova no documento; sua aplicação
fica sujeita à aprovação das propostas pelo usuário.

### IR-04 — Compatibilidade de suspensão — Major

- **Lente:** egm-codebase-details.
- **Escopo original:** linhas 457–469 e 556–558.
- **Discrepância:** compatibilidade mínima central deixada para validação posterior.
- **Sugestão:** PROPOSE FIX, com decisão de dependência explicitamente pendente.
- **Evidência nova:** o código-fonte oficial de
  [Textual v0.40.0 App](https://raw.githubusercontent.com/Textualize/textual/v0.40.0/src/textual/app.py)
  não define App.suspend ou SuspendNotSupported. O Textual instalado, 8.2.8,
  define esse contexto e a ponte call_from_thread. A consulta ao código-fonte
  verifica existência da API; não substitui teste funcional da implementação.
- **Proposta de edição A:** trocar a versão mínima planejada de `textual>=0.40.0`
  para `textual>=8.2.8`, a base instalada cuja API foi inspecionada. Atualizar
  pyproject.toml e uv.lock como parte da futura fase 0; testar 8.2.8 como mínimo
  e a versão resolvida no ambiente de entrega. Não afirmar que 8.2.8 é a primeira
  versão com suspensão. Corrigir as menções anteriores de que nenhuma elevação
  foi aprovada apenas depois da aprovação explícita desta proposta.
- **Alternativa B:** manter mínimo 0.40.0, com detecção de capacidade. Em versões
  sem suspensão, não executar Core na TUI e mostrar comando para usar o terminal
  diretamente; ClearType/Dev continuam. Não usar APIs privadas do driver. Essa
  alternativa reduz o comportamento disponível na TUI antiga e precisa ser
  aceita explicitamente em vez de aparecer como fallback implícito.
- **Decisão necessária:** escolher A ou B antes de aplicar este achado.
  A proposta A preserva o fluxo TUI planejado para todos os ambientes suportados,
  mas exclui instalações com Textual antigo. B preserva a faixa de instalação,
  mas oferece menos funcionalidade nesses ambientes. Nenhuma foi aplicada.

### IR-05 — Estado de aprovação — Nit

- **Lente:** egm-style.
- **Escopo original:** linhas 582–589.
- **Discrepância:** “descritas para revisão” contradiz o estado aprovado das regras.
- **Sugestão:** PROPOSE FIX.
- **Edição proposta:** substituir “regras de recusa e integração descritas para
  revisão” por “regras de recusa e integração aprovadas pelo usuário”.
- **Justificativa:** ajuste pequeno que elimina ambiguidade no registro usado
  para retomar o trabalho, sem alterar comportamento.

## Alcance da aplicação futura

Aplicar as alterações aprovadas apenas ao design final. Corrigir referências
cruzadas nas seções anteriores quando uma definição nova substituir texto
anterior, para não deixar contratos conflitantes. Registrar os novos limites de
linha após a edição. `design_draft.md` é o rascunho histórico; o arquivo final
continua sendo a fonte da revisão. Não alterar código, dependências ou lockfile
nesta resolução documental; estes aparecem apenas como tarefas do plano.

Após aplicar, atualizar a situação dos achados no relatório de prontidão,
preservando o histórico da primeira rodada e sem alegar aprovação de revisores
novos. Uma nova rodada só ocorre se o usuário a solicitar.

## Decisões de triagem

- PROPOSE FIX: IR-01, IR-02, IR-03, IR-04, IR-05.
- CONTEST: nenhum.
- ESCALATE: nenhum.
- DECLINE: nenhum.
- Decisão recebida: aplicar todas as propostas e usar variante A de IR-04.
- Aceitas e aplicadas: 5; contestadas: 0; escaladas: 0; recusadas: 0.
- Achados sem tratamento nesta resolução: 0; nova revisão independente não executada.


## Registro de aplicação

O usuário selecionou a opção 1: aceitar todas as propostas e exigir Textual
>= 8.2.8 no plano. As alternativas e condicionais acima preservam o histórico
da proposta; a variante B não foi escolhida. IR-01, IR-02, IR-03, IR-04 e IR-05
foram tratados no design. O manifesto, lockfile e fontes continuam sem alteração
por esta resolução; são arquivos da futura implementação.

- **Novo escopo DetailedRange:** 420–715.
- **SHA-256 após resolução:** `1e065b01d972108107effc6e0a7a7ae89749b4e33aebb2dec2ab0acb03b26f46`.

Conferidos estrutura Markdown, links locais e referências cruzadas. Esta
verificação documental não equivale a teste da implementação nem a nova
aprovação Goldfish. O rascunho design_draft.md permanece como histórico.
