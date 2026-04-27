---
name: yt-algorithm-audit
description: >-
  Auditoria algorítmica do canal. Mapeia sinais de distribuição
  do YouTube cruzando dados internos com o nicho. Use quando o
  usuário invocar /yt-algorithm-audit.
---

# YT Algorithm Audit — Auditoria Algorítmica

## Quando usar

O usuário invoca `/yt-algorithm-audit`.

## Workflow

Lance o subagent **`yt-algorithm-audit`** sem parâmetros adicionais.

O subagent executa 3 fases automaticamente:
1. **Fase 1 — Dados internos do canal:** usa MCP YouTube como fonte
   primária (`analytics_getTrafficSources`,
   `analytics_getDeviceAndPlayback`, `analytics_getDemographics`,
   `reporting_getReachByVideo`) + VidIQ para velocidade e curva de
   acumulação.
2. **Fase 2 — Dados do nicho:** outliers, trending, canais similares,
   breakout channels, keywords em crescimento (VidIQ).
3. **Fase 3 — Análise cruzada:** benchmarks, sinais algorítmicos,
   oportunidades de timing, hipóteses testáveis.

Após conclusão, apresente ao usuário:
- Os 5-7 sinais algorítmicos mais relevantes
- O mapa de distribuição (Browse/Suggested/Search)
- Os benchmarks do canal vs nicho
- As hipóteses testáveis para os próximos vídeos
- O link para o arquivo salvo em `output/algorithm-audit/`

## Frequência

Recomendado **1x por mês** ou quando houver mudança significativa
no canal (vídeo viralizar, queda de views).
