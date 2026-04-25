---
name: yt-performance-triage
description: >-
  48h Performance Triage (FASE Y) — coleta métricas reais
  de um vídeo publicado e gera decisões de ação baseadas
  em thresholds de CTR e retenção.
---

# /yt-performance-triage

Executa a FASE Y do pipeline: triage de performance pós-publicação.

## Uso

```
/yt-performance-triage <video-id> <checkpoint>
```

- `video-id`: ID do vídeo no YouTube
- `checkpoint`: `24h`, `48h` ou `7d`

## Exemplo

```
/yt-performance-triage daK_7PofxMU 24h
/yt-performance-triage daK_7PofxMU 7d
```

## O que faz

O subagent `yt-performance-triage` coleta métricas via YouTube
Analytics, classifica o vídeo no quadrante CTR×Retenção, e gera
decisões de ação:

- **24h**: foco em CTR → decisão sobre thumbnail/título
- **48h**: foco em retenção → decisão sobre shorts + diagnóstico de drops
- **7d**: documentação completa → hipóteses + ação para próximo vídeo

Output salvo em `output/videos/{slug}/07-triage-{checkpoint}.md`.
