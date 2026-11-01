# Suporte a outras distribuições Linux

## Objetivo e escopo

Manter Ubuntu/Debian e adicionar Fedora, Arch/Manjaro, openSUSE e Alpine,
conforme solicitado. Preservar a instalação de fontes no diretório do usuário.

## Abordagens

- Detectar somente executáveis de gerenciadores: simples, mas pode selecionar um
  gerenciador secundário que não administra o sistema atual.
- Detectar a distribuição por `ID` e `ID_LIKE` de `/etc/os-release` e verificar
  seu gerenciador: abordagem recomendada por corresponder ao sistema atual.

A escolha técnica é a segunda. O usuário aprovou este desenho em 2026-10-31.

## Comportamento proposto

- Centralizar a detecção e os comandos para apt, dnf, pacman, zypper e apk.
- Instalar apenas dependências ausentes, mapeando `fc-cache` para `fontconfig`
  e `cabextract` para o pacote de mesmo nome.
- Executar diretamente como root ou usar sudo quando necessário; informar
  claramente quando faltarem privilégios, gerenciador ou suporte à distribuição.
- Não adicionar repositórios externos automaticamente.
- Preservar Core Fonts via pacote em Ubuntu/Debian. Nas demais distribuições,
  informar sua indisponibilidade pela instalação automática e manter ClearType
  e fontes de desenvolvimento disponíveis. A disponibilidade de Core Fonts nos
  repositórios de cada distribuição não será presumida.
- Atualizar ajuda da CLI, textos da TUI, erros e README para refletir o suporte
  e a limitação de Core Fonts.
- Corrigir a identificação de Linux para não incluir todos os sistemas POSIX.

## Verificação

Testes sem alterar o sistema, simulando identificação das distribuições,
comandos de instalação, permissões e falhas. Executar a suíte existente;
instalações reais em cada distribuição permanecem fora desta validação local.

## Limites

macOS, Windows, gerenciadores adicionais e configuração de repositórios não
fazem parte desta alteração. Detalhes internos e organização dos testes ficam
a critério da implementação.
