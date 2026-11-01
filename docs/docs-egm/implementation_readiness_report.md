# Revisão de prontidão para implementação — segunda rodada

- **Alvo:** [design da TUI](../superpowers/specs/2026-10-31-tui-modernization-design.md).
- **Data:** 2026-10-31.
- **Etapa:** 9, somente implementação; reauditoria após correções.
- **Escopo:** linhas 420–715; restante do documento lido para contexto.
- **SHA-256:** `1e065b01d972108107effc6e0a7a7ae89749b4e33aebb2dec2ab0acb03b26f46`.
- **Resultado:** nenhum achado confirmado de prontidão, aderência ao código ou estilo.
- **Contagem:** 0 Blocker, 0 Major, 0 Nit.
- **Conclusão:** pronto para iniciar implementação segundo o plano revisado, com a limitação externa descrita abaixo.
- **Design:** inalterado durante esta rodada.

## Estado dos revisores

Três revisores novos, iniciados com `fork_turns: none`, sem histórico da
conversa ou relatórios anteriores. Os dois revisores técnicos leram o padrão
implementation-readiness-standard; estilo aplicou sua persona sem padrão adicional.
Todos concluíram antes desta consolidação.

| Lente | Estado | Resultado |
| --- | --- | --- |
| egm-implementation-readiness | Concluído, com limitação externa | Nenhum achado; arquivos, fases, contratos e critérios suficientes |
| egm-codebase-details | Concluído, com limitação externa | Nenhum achado confirmado na integração proposta com o código atual |
| egm-style | Concluído, com limitação externa | Nenhuma ambiguidade ou redundância consequente no escopo ativo |

As leituras incluíram alvo completo, brief vinculado, fontes e documentação
explicitamente referenciadas, manifesto e infraestrutura de testes. A lente
código também inspecionou as APIs instaladas do Textual 8.2.8. A lente de estilo
teve saída truncada na primeira leitura de apoio e foi retomada para concluir
as leituras em chamadas menores antes de ser contabilizada como concluída.
O lockfile foi processado integralmente como TOML e seus registros de dependência
inspecionados; URLs e hashes de artefatos não exigiram transcrição literal.

Arquivos marcados “criar” foram tratados como entregáveis futuros, não como
referências ausentes. Não houve teste, build, instalação, correção ou mudança
de código nesta rodada.

## Conferência dos temas corrigidos

A comparação com os achados anteriores é uma rastreabilidade do orquestrador;
os revisores avaliaram o texto atual sem receber os relatórios anteriores.

| Tema | Situação no plano atual |
| --- | --- |
| IR-01 — fases estáveis | Fases agrupam alterações compatíveis com consumidores e testes, com critérios de passagem |
| IR-02 — fronteiras de exceção | Classes operacionais, propagação de falhas inesperadas e erro de callback estão definidos |
| IR-03 — entrega de progresso | Caixa local, lock curto, timer e ordenação de eventos concretizam a transferência |
| IR-04 — suspensão/compatibilidade | Base 8.2.8 explícita; ponte síncrona exclusiva de Core e captura dentro da região suspensa descritas |
| IR-05 — aprovação ambígua | Registro de aprovação não deixa as regras aprovadas como pendentes de revisão |

O código local confirma que call_from_thread espera retorno da UI e que
App.suspend está disponível em 8.2.8. A restauração do driver fica após yield,
sem finally envolvendo o corpo: capturar falhas dentro da suspensão, como
previsto no plano, continua sendo condição relevante da implementação.
Isso é inspeção de API, não demonstração de funcionamento do aplicativo futuro.

## Limitação de cobertura externa

A EULA e o fonte oficial Textual vinculados foram acessíveis. A referência aos
[templates Debian 3.8.1](https://sources.debian.org/src/msttcorefonts/3.8.1/debian/templates)
retornou erro às três lentes, inclusive nas variantes adicionais tentadas.
Sua afirmação histórica não foi reconfirmada nesta rodada. Não considerar essa
referência validada nem declarar cobertura integral dos links externos.

Os revisores técnicos não consideraram isso impedimento do plano porque o
fluxo preserva diálogos nativos e exige conferir a licença antes da distribuição.
A inspeção visual, o recurso no wheel e a restauração funcional são tarefas
futuras de implementação com critérios de aceite, não evidências já produzidas.

## Histórico e limite de convergência

- [Primeira rodada e resolução posterior](./implementation_readiness_report_round1.md).
- [Propostas aceitas e registro de aplicação](./goldfish_review_report.md).

Esta reauditoria não encontrou novos achados. Não declarar duas rodadas limpas
consecutivas nem convergência do loop: a primeira rodada tinha problemas, e
esta rodada mantém uma referência externa inacessível. O resultado permite
encaminhar o plano para implementação, sem prometer ausência de novos problemas.

## Encerramento

O usuário escolheu concluir a revisão e manter o design finalizado para
implementação em 2026-10-31. Esta reauditoria terminou sem novos achados nas
três lentes; a limitação de cobertura externa permanece registrada acima.
O design não foi alterado nesta rodada. A implementação não foi iniciada.

O próximo trabalho é executar as fases descritas no design aprovado, com os
respectivos critérios de passagem. O encerramento não equivale à execução
dos testes futuros nem a convergência de duas rodadas limpas.
