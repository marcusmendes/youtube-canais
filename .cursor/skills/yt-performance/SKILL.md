---
name: yt-performance
description: >-
  Diagnóstico de performance do último vídeo do canal Marcus Maciel
  | IA & Ciência. Fase P avulsa. Use quando o usuário invocar
  /yt-performance.
---

# YT Performance — Diagnóstico Avulso

## Quando usar

O usuário invoca `/yt-performance`.

## Workflow

Lance o subagent **`/yt-performance`** sem parâmetros adicionais.

O subagent identifica o último vídeo automaticamente usando
`vidiq_channel_videos` com o handle `@MarcusMacielIAeCiencia`.

Após conclusão, apresente o diagnóstico completo ao usuário:
calibrações, lições, alertas, e análise de retenção.
