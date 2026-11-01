# Revisão de prontidão para implementação

- **Alvo:** [design da TUI](../superpowers/specs/2026-10-31-tui-modernization-design.md).
- **Data:** 2026-10-31.
- **Etapa:** 9, somente implementação; primeira rodada.
- **Escopo principal:** linhas 413–601; linhas 1–412 lidas como contexto.
- **SHA-256 do alvo:** `9d20d887343e46bc2251b3079d253870fc8e13fbf693e31139b92247475bc8fb`.
- **Resultado:** ainda não pronto pelo critério de executar sem decisões de desenho adicionais.
- **Contagem consolidada:** 0 bloqueadores, 4 problemas principais, 1 ajuste menor.
- **Alterações no alvo:** nenhuma; correções dependem do encaminhamento do usuário.

## Estado dos revisores

Os três revisores foram iniciados diretamente com `fork_turns: none`, sem o
histórico da conversa, e concluíram antes da consolidação. Os dois revisores
técnicos leram o padrão `implementation-readiness-standard.md`; o revisor de
estilo leu sua persona sem padrão adicional.

| Lente | Estado | Leituras e limites |
| --- | --- | --- |
| egm-implementation-readiness | Concluído com limitação externa | Persona, padrão, alvo completo, brief, fontes/documentação referenciadas, manifesto e infraestrutura de testes; EULA acessível; URL Debian inacessível |
| egm-codebase-details | Concluído com limitação externa | Mesmas leituras locais, além de App.suspend e App.call_from_thread no Textual 8.2.8; EULA acessível; URL Debian inacessível |
| egm-style | Concluído com limitação externa | Persona, alvo completo, referências locais e EULA; URL Debian inacessível |

A [referência Debian](https://sources.debian.org/src/msttcorefonts/3.8.1/debian/templates)
retornou erro aos revisores. A afirmação histórica correspondente não foi
revalidada nesta rodada. Isso limita a cobertura externa e não equivale a uma
verificação limpa. Os achados abaixo usam evidência local independente dessa
referência. Nenhum teste, build ou instalação foi executado. Os arquivos
marcados como criação futura não foram tratados como referências ausentes.

## Achados consolidados

### IR-01 — Faltam fases com estados intermediários verificáveis — Principal

- **Origem:** `readiness-1-1`.
- **Escopo:** linhas 471–509 e 543–568.
- **Problema:** a ordem por arquivo não define fases que deixem o aplicativo
  estável, compilável e testável. Testes novos aparecem depois das mudanças
  de produção e a verificação fica concentrada no final.
- **Consequência:** a consulta de release pode passar a lançar erros antes
  de o instalador receber o tratamento correspondente; a lista não define
  quais alterações precisam entrar juntas.
- **Encaminhamento:** agrupar contrato/downloader e testes; instalador/resultados
  e testes; recursos/modais e empacotamento; integração TUI e testes;
  documentação/verificação final. Definir dependências e critério de passagem
  para cada fase, inclusive execução da suíte simulada.

### IR-02 — A fronteira entre falha operacional e erro inesperado está indefinida — Principal

- **Origens:** `readiness-1-2`, `codebase-1-1`.
- **Escopo:** linhas 449–452, 480–481 e 537–539.
- **Problema:** o plano exige continuar após falhas esperadas e interromper
  após exceções inesperadas, mas não especifica quais classes pertencem a
  cada grupo nem em que fronteira são capturadas.
- **Evidência:** `core/installer.py:172–178,248–254` converte qualquer Exception
  em resultado falso; `Downloader.download_file` também envolve exceções
  genéricas em DownloadError, e a consulta atual suprime exceções como None.
  Um erro de callback ou programação pode virar falha comum e deixar o lote
  continuar.
- **Encaminhamento:** definir as classes operacionais para HTTP/rede/JSON,
  extração e cópia, e as exceções que devem propagar. Definir a conversão na
  consulta e no instalador sem ocultar falhas do callback. Testar falha
  operacional seguida do próximo item e erro inesperado seguido de itens
  não tentados. Trata-se de lacuna na mudança proposta, não alegação de
  contradição sobre o comportamento atual.

### IR-03 — Falta o mecanismo de entrega de progresso sem espera por atualização visual — Principal

- **Origem:** `codebase-1-2`.
- **Escopo:** linhas 487 e 528–531.
- **Problema:** limitar repaints a dez por segundo não define onde ficam
  amostras pendentes nem como são transferidas sem esperar a UI por bloco.
- **Evidência:** `ui/app.py:212–214` usa call_from_thread por callback; no
  Textual instalado esse método espera o resultado da execução na UI.
- **Encaminhamento:** especificar armazenamento da última amostra, mecanismo
  de transferência, timer e drenagem/invalidação em transições/finalização.
  Testar UI ocupada, entrega da última amostra, ordem das transições e
  rejeição de eventos de lote já finalizado. Evitar apenas deslocar a
  limitação de repaints para depois da mesma travessia síncrona por bloco.

### IR-04 — A compatibilidade da suspensão continua uma dependência por resolver — Principal

- **Origem:** `codebase-1-3`.
- **Escopo:** linhas 457–469 e 556–558.
- **Problema:** a ponte de suspensão é central, mas o plano adia verificar
  suporte no mínimo Textual 0.40.0. Se essa versão não suportar o mecanismo,
  será necessária nova decisão; o plano ainda não define uma execução certa.
- **Evidência:** o manifesto permite 0.40.0; somente a implementação instalada
  em 8.2.8 foi inspecionada. Não há incompatibilidade concreta demonstrada.
- **Encaminhamento:** verificar a API no mínimo antes de fechar o plano e
  registrar caminho de teste nas duas versões e comportamento sem suporte.
  O tratamento de interrupção dentro da região suspensa deve ser preservado:
  a implementação instalada retoma o driver após yield sem finally envolvendo
  a retomada. Não elevar a dependência sem decisão explícita.
- **Ressalva de triagem:** o revisor de prontidão aceitou validações técnicas
  como tarefas futuras com condição de parada; a lente de código considera
  esta validação central demais para permanecer aberta. Não apresentar essa
  diferença de rigor como incompatibilidade já provada.

### IR-05 — Registro de aprovação deixa pendência editorial ambígua — Ajuste menor

- **Origem:** `style-1-1`.
- **Escopo:** linhas 582–589.
- **Problema:** o registro mantém “regras de recusa e integração descritas
  para revisão”, embora o plano técnico e a implementação estejam aprovados.
- **Encaminhamento:** atualizar o estado dessas regras conforme a aprovação
  registrada ou identificar exatamente o ponto que continua pendente.

## Rastreabilidade dos achados originais

| ID original | Lente | Severidade original | Ação consolidada |
| --- | --- | --- | --- |
| readiness-1-1 | Prontidão | Major | IR-01 |
| readiness-1-2 | Prontidão | Major | IR-02 |
| codebase-1-1 | Código | Major | IR-02 |
| codebase-1-2 | Código | Major | IR-03 |
| codebase-1-3 | Código | Major | IR-04 |
| style-1-1 | Estilo | Nit | IR-05 |

## Limites da conclusão

Não foram identificadas contradições comprovadas nos argumentos preservados
pelos dataclasses, na proposta de cópia parcial, nos comandos atuais de teste
ou no uso de recursos empacotados. Isso não comprova a implementação futura.
A primeira rodada não é convergência: existem problemas principais abertos e
uma referência externa não revalidada. O design continua inalterado.

## Encerramento

O usuário escolheu concluir a revisão com os achados registrados, sem
remediação, em 2026-10-31. A etapa 9 foi encerrada após uma rodada. Os quatro
problemas principais e o ajuste menor continuam abertos; encerrar a revisão
não significa validar o plano como pronto nem aceitar implicitamente os riscos.
Não houve nova rodada, convergência ou alteração no design. Etapas 5–8 não
foram executadas porque o usuário selecionou somente implementação.

O documento de design permanece no caminho escolhido. Uma futura correção
pode partir dos IDs IR-01 a IR-05 e ser seguida de nova revisão.


## Resolução posterior ao encerramento

O usuário retomou os achados com egm-resolve e aceitou as cinco propostas,
incluindo Textual >= 8.2.8. Todos foram tratados documentalmente no design;
o relatório original acima preserva a evidência e o estado da primeira rodada.

| Achado | Tratamento aplicado |
| --- | --- |
| IR-01 | Fases incrementais com testes e critérios de passagem |
| IR-02 | Classes e fronteiras de exceção, erro de callback e testes contrastantes |
| IR-03 | Caixa local, lock curto, consolidação, timer e ordem terminal |
| IR-04 | Base mínima 8.2.8 aprovada, evidência de API e atualização futura de manifesto/lock |
| IR-05 | Registro de aprovação corrigido |

Não há achado sem tratamento nesta resolução. Isso não demonstra ausência de
novos problemas: não houve reauditoria nem convergência de rodadas. A limitação
da referência Debian da rodada original continua registrada. Fontes, manifesto
e lockfile não foram modificados por esta etapa.

Ver [registro de resolução](./goldfish_review_report.md).
