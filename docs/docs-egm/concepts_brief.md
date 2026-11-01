# Modernização da TUI do Font Installer

- **Autor:** usuário do projeto, com apoio do Codex.
- **Data:** 2026-10-31.
- **Estado:** conceito consolidado aprovado pelo usuário em 2026-10-31, após revisão pelas seis lentes Goldfish. Implementação ainda não iniciada.

## Visão geral

Modernizar a interface Textual existente mantendo Gruvbox Dark e o uso no
terminal. O usuário quer movimento, interatividade, barra de progresso,
spinners e logs atualizados em tempo real. Quer a lista completa de fontes
visível sem rolagem. Aceitou logs em painel recolhível, aberto automaticamente
durante a instalação.

Esses são os requisitos confirmados. As escolhas técnicas e de interação a
seguir são propostas ou restrições ainda abertas, não concordâncias adicionais
do usuário. A referência informada foi tela HD 16:9; terminal maximizado em
1366 × 768 foi uma hipótese do facilitador e não define colunas, linhas ou
fonte do terminal.

## Análise

### Estado atual e oportunidades de reaproveitamento

A aplicação já tem `ProgressBar`, `LoadingIndicator`, `RichLog`, instalação em
worker e encaminhamento de callbacks à thread principal
(`src/font_installer/ui/app.py:166–176,212–223,282–291`). O objetivo pode ser
atendido reorganizando esses componentes e corrigindo lacunas concretas de
feedback; não há necessidade demonstrada de novo barramento, execução paralela,
serviço externo ou persistência em banco.

O catálogo e a unidade instalável são distintos: há seis famílias ClearType,
mas uma instalação conjunta; sete fontes Dev individuais; e um pacote Core
Fonts, instalado automaticamente apenas em Ubuntu/Debian via apt. Isso resulta
em nove unidades selecionáveis no fluxo atual, e não em seis controles
ClearType independentes (`config/fonts.py:27–112`, `ui/app.py:81–134`,
`core/installer.py:125–178,255–285`, sob `src/font_installer/`). Os nomes das
famílias ClearType podem ficar visíveis como conteúdo do pacote sem alterar a
granularidade de instalação.

### Objeções consolidadas por prioridade

1. **Bloqueio conceitual — visibilidade não tem contrato em células.**
   O usuário confirmou todas as categorias simultâneas, sem abas, e aceitou
   rolagem como alternativa quando o terminal ficar pequeno demais. O catálogo hoje compete com log
   de oito linhas, progresso e aviso de dependências
   (`ui/styles.py:70–75,180–191,236–241`). Definir largura × altura mínima e
   comportamento abaixo dela; verificar também execução com log aberto,
   progresso, aviso de dependências e redimensionamento. Uma lista que cabe
   apenas antes de instalar não comprova o requisito.

2. **Principal — percentual de download não mede instalação completa.**
   A TUI reproduz o percentual recebido; extração e cópia já usam 100%, e o
   próximo download recomeça em zero. Sem tamanho remoto conhecido não há
   incrementos intermediários (`ui/app.py:216–223`,
   `core/installer.py:145–159,225–237`, `core/downloader.py:72–81`).
   Proposta: percentual explicitamente rotulado como download do item atual,
   contador de itens concluídos e spinner com nome da fase nas etapas sem
   medida. Não inventar pesos, ETA ou avanço artificial. Se forem necessários
   eventos adicionais, preservar a semântica do callback `DownloadProgress`
   compartilhado e usar identificadores estáveis de fase, sem interpretar
   texto traduzido para comandar estados.

3. **Principal — feedback final pode anunciar sucesso indevido.**
   A interface ignora o booleano do cache e termina em verde mesmo após falhas
   individuais (`ui/app.py:295–355`). O core descarta erros de cópia e pode
   retornar sucesso com zero arquivos (`core/installer.py:115–123,164–169,
   240–245`). Proposta: resultado por operação e resumo persistente de sucesso,
   falha parcial ou falha, incluindo cache. Contagem de arquivos e contagem de
   pacotes precisam ser distintas; Core não oferece uma contagem real de
   arquivos. Correções necessárias a esse feedback cabem no escopo proposto,
   mas não prometem instalação atômica ou rollback.

4. **Principal — interação durante execução ainda é ambígua.**
   A guarda é verificada na UI, mas ativada dentro do worker, após agendamento
   (`ui/app.py:260–290`). Seleção e limpeza continuam disponíveis, embora o
   lote já tenha sido capturado. “Selecionar Tudo” exclui Core, e “Atualizar”
   apaga logs (`ui/app.py:236–258,381–386`). Proposta mínima: marcar execução
   antes do worker, capturar o lote e congelar edição até terminar; preservar
   consulta e navegação. Definir alcance de “Tudo”, limpeza e saída durante
   execução. Cancelamento robusto exige decisão própria e não está confirmado.

5. **Principal — logs recolhíveis precisam de contrato e sinais externos.**
   Hoje callbacks atualizam barra/rótulo, enquanto o log registra sobretudo
   início e resultado (`ui/app.py:204–223,295–355`). Registrar cada bloco do
   download causaria volume e trabalho desnecessários
   (`core/downloader.py:74–78`). Proposta: eventos de início/fim/falha das
   etapas; atualizações contínuas na barra; retenção limitada em memória;
   acompanhamento automático pausado ao consultar histórico e ação para
   seguir novamente. Validação de seleção vazia e resultado final devem
   permanecer visíveis fora do painel. Decidir se “tempo real” significa
   eventos da aplicação ou saída contínua de subprocessos; esta última não
   está confirmada. Exportação de diagnóstico é alternativa, não requisito.

6. **Principal — animação não resolve espera ou diagnóstico indefinido.**
   Download usa `urlretrieve` sem timeout explícito, e a consulta GitHub suprime
   exceções, convertendo problemas distintos em release não encontrada
   (`core/downloader.py:80,108–125`). Proposta: etapa atual e duração visíveis,
   política explícita de timeout e erros distinguíveis; não adicionar retries
   ilimitados ou consultas causadas apenas por atualizar a tela.

7. **Principal — compatibilidade e verificação ainda precisam ser definidas.**
   `pyproject.toml:24` declara `textual>=0.40.0`; novos componentes devem
   respeitar essa faixa ou motivar mudança consciente da versão mínima.
   `tests/test_installer.py:55–79` verifica criação e aceitação do callback,
   sem exercer estados da interface ou resultados. Futuro aceite precisa
   cobrir layout, teclado, log aberto, download sem tamanho, execução única,
   falha parcial e cache falhando, com instalador simulado. Não há evidência
   de incompatibilidade concreta antes da escolha de APIs.

8. **Ajuste documental — diretriz visual conflitante.**
   `DESIGN.md:14` pede preservar layout/textos/atalhos. Atualizar essa diretriz
   quando o conceito for aprovado, distinguindo a paleta confirmada da
   reorganização proposta. Nenhuma mudança nesse arquivo foi feita nesta
   revisão.

As referências abreviadas `ui/`, `core/` e `config/` nesta seção são relativas
a `src/font_installer/`.

## Objetivos e limites

### Confirmado pelo usuário

- TUI em Textual e paleta Gruvbox preservada.
- ClearType, Dev e Core Fonts simultaneamente na mesma tela, sem abas.
- Lista completa sem rolagem no tamanho-alvo; mínimo em células ainda pendente.
- Rolagem permitida como alternativa em terminais menores.
- Movimento, interatividade, barra de progresso e spinners.
- Logs em tempo real em painel recolhível, aberto durante a instalação.

### Escopo proposto para viabilizar esses objetivos

- Reorganizar componentes existentes e manter execução sequencial.
- Preservar unidades instaláveis, diretórios e gerenciadores atuais.
- Corrigir somente o necessário para feedback fiel e interação consistente:
  execução única, etapas identificadas e resultados coerentes.
- Explicitar comportamento responsivo, navegação por teclado e foco perceptível
  sem depender apenas de cor.

### Fora do escopo proposto pelo facilitador

- Interface gráfica ou web; nova paleta, novos catálogos ou gerenciadores.
- Seleção independente de famílias ClearType, downloads paralelos ou novo
  sistema externo de logs.
- Cancelamento transacional, rollback de fontes/pacotes ou migração de dados
  persistidos; nada disso está demonstrado como necessário ao pedido.
- Alteração da CLI sem necessidade para o comportamento da TUI; consumidores
  compartilhados de callbacks devem continuar compatíveis.

## Alternativas consideradas

| Alternativa | Benefício | Custo ou condição | Situação |
| --- | --- | --- | --- |
| Janela própria | Liberdade de layout em pixels | Contraria escolha por terminal | Descartada pelo usuário |
| Nova paleta | Outra direção estética | Contraria Gruvbox | Descartada pelo usuário |
| Lista/tabela compacta única agrupada | Todas as unidades em uma visão; usa pouca altura | Descrições precisam ser compactadas sem ocultar nomes necessários | Proposta a comparar |
| Categorias lado a lado | Visão simultânea; aproveita largura | Exige mínimo de colunas e cuidado com rótulos longos | Proposta a comparar |
| Abas compactas | Menor pressão por largura e altura | Esconde outras categorias | Descartada pela confirmação de visão simultânea |
| Logs sempre abertos | Diagnóstico imediatamente visível | Reserva altura permanentemente | Preferência por painel recolhível já aceita |
| Log recolhível com faixa compacta de atividade | Libera espaço e mantém estado visível | Precisa caber aberto no contrato de aceite | Direção proposta sobre escolha confirmada |
| Percentual global ponderado por fases | Uma barra global contínua | Sem denominador temporal honesto no código atual | Não recomendado |
| Contagem de itens + percentual do download + spinner por fase | Reaproveita medidas disponíveis e explica esperas | Exige rotulagem clara e resultado separado de “itens concluídos” | Recomendado tecnicamente, não aprovado |

## Decisões e próximos passos

Não iniciar implementação a partir desta revisão. A próxima conversa deve
resolver primeiro a composição da lista e o orçamento do terminal:

1. Confirmado: todas as categorias simultaneamente, sem abas; rolagem aceita
   abaixo do tamanho-alvo. Categorias lado a lado são proposta do facilitador,
   ainda sem aprovação específica de layout. Preservar instalação por pacote.
2. Qual é o mínimo em colunas × linhas, inclusive durante instalação com logs
   abertos? Qual degradação é aceitável abaixo dele?
3. Em seguida, fechar semântica de progresso, logs e política de ações durante
   execução, incluindo saída, limpeza e alcance de “Selecionar Tudo”.

Depois dessas respostas, transformar propostas selecionadas em critérios de
aceite verificáveis e atualizar a diretriz de design. Propostas não escolhidas
continuam alternativas; a revisão não substitui aprovação do usuário.

## Estado dos revisores

Cada revisor foi iniciado com contexto novo (`fork_turns: none`), leu sua persona,
o brief original e a lista explícita completa: `DESIGN.md`, `pyproject.toml`,
`ui/app.py`, `ui/styles.py`, `core/installer.py`, `core/downloader.py`,
`config/fonts.py` e `tests/test_installer.py`. Todos declararam leitura integral
e concluíram antes desta síntese. Não houve edição de fontes, commits ou web.

| Lente | Estado | Contribuição principal |
| --- | --- | --- |
| egm-design | concluído | Orçamento em células, feedback fiel e proteção de interação |
| egm-codebase-details | concluído | Diagnóstico, falhas silenciosas e contrato de eventos |
| egm-zoom-out | concluído | Reuso, limite de escopo e alternativas simples |
| egm-comprehension | concluído | Significado de lista completa e clareza de estados |
| egm-implementation-readiness | concluído | Compatibilidade de callbacks/Textual e saída durante execução |
| egm-structural | concluído | Estado único do lote, unidades instaláveis e manutenção |


### Atualização após revisão

O usuário confirmou visão simultânea de ClearType, Dev e Core Fonts, sem abas,
e aceitou rolagem como alternativa em terminais pequenos. Categorias lado a lado
com logs abaixo continuam proposta de composição. A dimensão mínima em células permanece uma proposta a validar. O usuário
aprovou bloquear edição da seleção e novas instalações durante a execução,
mantendo navegação e consulta aos logs disponíveis.


## Conceito consolidado para aprovação

Esta seção foi aprovada pelo usuário e substitui as pendências de composição e
interação listadas na revisão original acima. As observações técnicas da revisão
continuam como base do desenho. A aprovação inclui a composição recomendada e
as regras propostas abaixo; o alvo em células permanece sujeito à validação.

### Decisões confirmadas

- Manter TUI em Textual, Gruvbox Dark e textos em português brasileiro.
- Mostrar ClearType, Dev e Core Fonts ao mesmo tempo, sem abas.
- Tornar a lista inteira visível sem rolagem no tamanho-alvo; permitir rolagem
  em terminais menores para preservar acesso ao conteúdo.
- Usar barra de progresso, spinners e logs em tempo real.
- Logs recolhíveis, abertos automaticamente ao iniciar uma instalação.
- Durante a execução, bloquear edição da seleção e início de outro lote,
  mantendo navegação e consulta aos logs disponíveis.

### Proposta de composição e alternativas

Recomenda-se um catálogo compacto com duas colunas: as sete opções Dev em uma
coluna e os pacotes Microsoft na outra. Os seis nomes ClearType ficam visíveis
como conteúdo do pacote, não como seis opções independentes. Ações e estado
ficam em faixas compactas, com logs abaixo do catálogo. Isso usa a largura do
terminal e evita multiplicar bordas e descrições longas.

A alternativa é uma lista única agrupada de nove unidades selecionáveis:
é mais simples em largura, mas compete mais pela altura com logs e progresso.
Abas foram descartadas pelo requisito de visão simultânea. A composição em
colunas é recomendação do facilitador, ainda sujeita à aprovação deste conceito.

O alvo técnico inicial proposto é **120 colunas × 36 linhas**, inclusive com
painel de logs aberto, progresso e aviso compacto de dependências. É uma
hipótese de teste, não uma conversão garantida de 1366 × 768 pixels. Um protótipo
Textual deve validá-la antes de fixar o layout. Abaixo desse tamanho, empilhar
categorias e permitir rolagem sem perder seleção ou foco. Descrições extensas
podem ficar em ajuda contextual; nomes e controles permanecem acessíveis.

### Proposta de feedback e logs

- Mostrar percentual apenas para o download atual quando o tamanho for conhecido.
- Nas etapas sem medida, mostrar spinner e nome da etapa: consulta, extração,
  cópia ou atualização de cache. Não simular percentual ou tempo restante.
- Mostrar itens processados em relação ao lote, separando sucesso e falha;
  não usar esse contador como estimativa de tempo.
- Registrar início, mudança de etapa, conclusão e erro; não inserir uma linha
  de log para cada callback de progresso. “Tempo real” significa eventos da
  aplicação, sem prometer transmissão integral da saída de apt/sudo.
- Limitar inicialmente o histórico a 500 entradas em memória. Ao consultar
  entradas antigas, pausar acompanhamento automático até ação explícita.
- Permitir recolher o painel durante a execução; reabrir automaticamente no
  início do próximo lote. Ao terminar, manter resumo visível fora dos logs.
- Distinguir sucesso, falha parcial e falha; verificar também resultado do cache.
  A animação termina em todos esses casos e os controles são reabilitados.
- Manter movimentos discretos, foco estável e informação textual além das cores.

### Limites e validação propostos

Não adicionar cancelamento ou rollback nesta mudança. A saída durante execução
precisa de confirmação para evitar fechamento acidental; confirmar saída não
significa desfazer nem garantir interrupção de um gerenciador já iniciado.
Preservar a semântica atual de selecionar todas as opções ClearType/Dev e manter
Core como escolha explícita, com rótulo que deixe esse alcance claro.

No desenho detalhado, validar 120 × 36 e um tamanho menor, com dados simulados:
lista completa, logs abertos, aviso de dependências, foco por teclado, duplo
acionamento de instalar, download sem tamanho, falha de item e falha do cache.
Preservar compatibilidade da CLI e dos callbacks compartilhados. Timeout e
mensagens de erro devem ser avaliados dentro do necessário ao feedback, sem
ampliar este trabalho para uma reescrita do instalador.

### Próximo passo

Conceito e composição recomendada aprovados pelo usuário. Escolher o
encaminhamento para RFC, desenho formal via egm-draft, refinamento ou conclusão
do brainstorming. Nenhuma implementação foi iniciada; DESIGN.md permanece
sem alterações nesta etapa.
