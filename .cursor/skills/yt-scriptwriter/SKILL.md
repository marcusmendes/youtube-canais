---
name: yt-scriptwriter
description: >-
  Escrita de roteiro para vídeo do canal Marcus Maciel | IA &
  Ciência. Aplica DNA Narrativo, Camada Visual e Retenção
  Engenheirada. Use quando o usuário invocar /yt-scriptwriter com
  um tema.
---

# YT Scriptwriter — Roteiro Avulso

## Quando usar

O usuário invoca `/yt-scriptwriter "tema"` (ex: `/yt-scriptwriter "IA na cirurgia robótica"`).

## Workflow

Lance o subagent **`/yt-scriptwriter`** passando:
- O tema fornecido
- Metadados se disponíveis (título escolhido, emoção dominante)
- Calibrações de Performance se disponíveis
- Briefing Competitivo se disponível

O subagent escreve o roteiro completo seguindo os 7 Princípios do
DNA Narrativo, com VISUALs, open loops e CTAs.

Após conclusão, apresente o roteiro ao usuário com contagem de
palavras e duração estimada.
