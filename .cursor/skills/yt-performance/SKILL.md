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

O subagent identifica o último vídeo automaticamente (via
`vidiq_channel_videos` ou fallback `studio_listOwnVideos`), e usa as
tools nativas do MCP YouTube como fonte primária para
analytics privado:

- `analytics_getRetentionCurve` — retention curve com timestamps
- `analytics_getTrafficSources` (+ drill-down via
  `analytics_getTrafficSourceDetail`)
- `analytics_getDeviceAndPlayback` (deviceType / subscribedStatus)
- `analytics_getDemographics` (idade × gênero, normalizado)
- `analytics_getCardPerformance` (cards)
- `reporting_getReachByVideo` — CTR de impressões da thumbnail
  (lag de 24-48h)

VidIQ complementa com VPH hora-a-hora e curva típica do canal.

Após conclusão, apresente o diagnóstico completo ao usuário:
calibrações, lições, alertas, e análise de retenção.
