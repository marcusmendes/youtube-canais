---
name: yt-scriptwriter
description: >-
  Escrita de roteiro em voz-over (ElevenLabs) para o canal Marcus
  Maciel | IA & Ciência. DNA Narrativo, Camada Visual e Retenção
  Engenheirada. Para apresentador em câmera, use yt-scriptwriter-presenter.
  Use quando o usuário invocar /yt-scriptwriter com um tema.
---

# YT Scriptwriter — Roteiro Avulso

## Quando usar

O usuário invoca `/yt-scriptwriter "tema"` (ex: `/yt-scriptwriter "IA na cirurgia robótica"`).

Para roteiro com **Marcus em câmera** (teleprompter, sem ElevenLabs),
use o skill **`yt-scriptwriter-presenter`** (`/yt-scriptwriter-presenter`).

## Workflow

Lance o subagent **`/yt-scriptwriter`** passando:
- O tema fornecido
- Metadados se disponíveis (título escolhido, emoção dominante)
- Calibrações de Performance se disponíveis
- Briefing Competitivo se disponível

O subagent lê um modelo de escrita de
`canais/marcus-maciel/modelos-de-escrita/` para calibrar o estilo
narrativo, e então escreve o roteiro completo seguindo os 8 Princípios
do DNA Narrativo, com VISUALs, open loops e CTAs.

A contagem de palavras deve focar na fluidez e densidade do Bloco 4.
**Não há limite máximo estrito**; priorize o "respiro narrativo".
Mínimo de 1.500 palavras para vídeos longos.

Após conclusão, apresente o roteiro ao usuário com contagem de
palavras e duração estimada.
