# Diagnóstico de Performance (FASE P)

**Slug:** `sam-altman`  
**Tema do pipeline:** IA + Poder/Ética — Sam Altman e o lado oculto da OpenAI (calendário maio/2026).

## 1. Último Vídeo Publicado

| Campo | Valor |
|--------|--------|
| **Título** | Você Deixaria um ROBÔ Morar Na Sua Casa? |
| **ID** | `rVUdHTnKkNQ` |
| **Tipo** | Longo (VOD, ~14m50s) |
| **Publicação** | 28/04/2026 20:00 UTC (~24–48h antes deste diagnóstico) |
| **Views (Studio API)** | 2 |
| **Likes / comentários** | 0 / 0 |

## 2. Analytics e Reporting (API YouTube)

- **`analytics_getVideoAnalytics`** (01/04–29/04/2026): linhas diárias com métricas zeradas — típico de **lag de processamento** para vídeo recém-publicado ou janela que não captura ainda o pico inicial.
- **`analytics_getRetentionCurve`** (28–29/04, orgânico, duração injetada ~890s): **curva vazia** (`rowCount: 0`) — retenção por segmento ainda indisponível.
- **`analytics_getTrafficSources`** (28–29/04): **sem linhas**, `totals.views: 0` — tráfego por fonte ainda não populado.
- **`reporting_getReachByVideo`** (20–29/04): `reach: []`, `totals: {}` — **Reporting API** com lag de 24–48h; job ativo mas sem linhas agregadas para este vídeo no período.

**Conclusão técnica:** o diagnóstico quantitativo deste upload **não é confiável ainda**. Recomenda-se **Fase Y (48h triage)** com nova leitura de CTR de impressões, curva de retenção e fontes de tráfego.

## 3. Baseline do Canal (memória injetada + padrão histórico)

- Tráfego muito dependente de **Shorts**; long-form com desafio em **Browse** e retenção.
- Retenção média histórica ~33%; longos anteriores mostram **queda acentuada nos primeiros 5–10%** (ver diagnósticos em `output/videos/agi-em-2027/01-performance.md` como referência de padrão).

## 4. Calibrações para o Roteiro `sam-altman`

1. **Hook e promessa nos 0–30s:** alinhar título/thumbnail investigativos com **fato verificável imediato** (ex.: sequência abril/2026: perfil *New Yorker*, resposta pública de Altman, incidentes em SF) para evitar quadrante **“engano”** (clique alto, retenção colapsada).
2. **Pattern interrupt antes do payoff jurídico/técnico:** alternar timeline pessoal (2026), crise do board (2023) e saída da equipe de safety (2024) para sustentar atenção no meio (~14–16 min alvo).
3. **Ângulo BR explícito:** repetir “por que decisões em SF e Washington afetam **regulação, saúde e trabalho** no Brasil” — ecoa o briefing do calendário e diferencia de reação genérica a “fofoca de celebridade tech”.
4. **CTA de inscrição cedo:** memória do canal sugere testar CTA nos primeiros 60s em longos (hipótese de ativação de inscritos).

## 5. Quadrante CTR × Retenção (este vídeo)

**Indeterminado** — aguardar dados de impressões e `%` médio de visualização.

## 6. Lições do Último Ciclo (transferíveis)

- **Manter:** temas de **IA + hardware/vida real** recentemente performaram em Shorts (Neuralink); o longo atual mexe em **robótica doméstica** — continuidade temática OK para o algoritmo, mas o tema Altman/OpenAI é **outro cluster**; não extrapolar CTR de Neuralink para este vídeo.
- **Evitar:** abertura longa antes da manchete que o espectador veio buscar (nome próprio + tensão ética/política).

## 7. Alertas

| Código | Descrição |
|--------|-----------|
| `api_lag` | Métricas de retenção, tráfego e reach ainda vazias ou zeradas para `rVUdHTnKkNQ`. |
| `low_sample` | Views públicas ainda em unidades, não em milhares — qualquer otimização deve ser **qualitativa** (título, thumbnail, primeiros 60s) até o checkpoint 48h. |

## 8. Session Architecture — Checklist Rápido

- [ ] Vídeo atual e o próximo (`sam-altman`) em **2 playlists** coerentes (Ética IA / OpenAI ou equivalente).
- [ ] Comentário fixado com pergunta sobre **confiança em quem controla a AGI** + link para playlist.
- [ ] End-screen para vídeo com maior **watch time** da mesma série.
- [ ] Card ~60% para vídeo relacionado (ex.: AGI, governança), quando houver métricas.
