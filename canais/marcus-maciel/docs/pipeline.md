# Pipeline Marcus Maciel — IA & Ciência

> Pipeline v11 — 11 fases ativas, 1 adiada, 2 manuais — Abril 2026

---

## Diagrama Sequencial

```
PRÉ-PRODUÇÃO
─────────────────────────────────────────────────────────

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  FASE P  │────▶│  FASE T  │────▶│  FASE A  │
  │Diagnóst. │     │Validação │     │Competit. │
  └──────────┘     └──────────┘     └──────────┘
       ▲                                  │
       │                                  ▼
       │                            ┌──────────┐
       │                            │  FASE N  │
       │                            │Narrativa │
       │                            └──────────┘
       │                                  │
       │                                  ▼
PRODUÇÃO
─────────────────────────────────────────────────────────

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ Roteiro  │────▶│Metadados │────▶│ FASE QA  │
  │(usa N)   │     │          │     │ 38 itens │
  └──────────┘     └──────────┘     └──────────┘
                                          │
                                          ▼
PÓS-PUBLICAÇÃO
─────────────────────────────────────────────────────────

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │Distrib.  │────▶│PUBLICAÇÃO│────▶│ FASE R   │
  │(manual)  │     │          │     │Repackag. │
  └──────────┘     └──────────┘     └──────────┘
                        │
                        ▼
                   ┌──────────┐     ┌──────────┐
                   │ FASE S   │────▶│ FASE Y   │
                   │Session A.│     │48h Triage│
                   └──────────┘     └──────────┘
                                          │
                                          │ loop de
                                          │ aprendizado
                                          ▼
                                    ┌──────────┐
                                    │  FASE P  │
                                    │(próximo) │
                                    └──────────┘
```

---

## Execução Passo a Passo

| # | Fase | Comando | Status | O que faz |
|---|---|---|---|---|
| 1 | **FASE P** — Diagnóstico | `/yt-performance` | Ativo | Retenção, drops, quadrante CTR×Retenção, benchmarks |
| 2 | **FASE D** — Decision Bridge | *(adiado)* | Adiado | Família semântica, regra 3-em-5, competição contextual |
| 3 | **FASE T** — Validação | `/yt-validation` | Ativo | Cluster semântico 5 keywords, intent dominante, competição |
| 4 | **FASE A** — Competitiva | `/yt-competitive` | Ativo | 3-5 concorrentes, hook, ângulos, manifesto de diferenciação |
| 5 | **FASE N** — Narrativa | `/yt-narrative` | Ativo | Protagonista, espinha dorsal, arco emocional, cenas, micro-histórias, anti-clichês |
| 6 | **Roteiro** | `/yt-scriptwriter` | Ativo | 4 blocos + hook + CTA + Viewer Simulation Pass (baseado na Fase N) |
| 7 | **Metadados** | `/yt-metadata` | Ativo | 10 títulos, thumbnail, descrição SEO, tags cluster, pinned comment |
| 8 | **FASE QA** | `/yt-qa` | Ativo | Checklist 38 itens: narrativa, compliance médico, storytelling |
| 9 | **Distribuição** | *(checklist manual)* | Manual | 5 comunidades, soft launch 24h, janela de publicação |
| 10 | **Publicação** | YouTube Studio | Manual | Upload, chapters, tags, end-screen, card, "Altered content" |
| 11 | **FASE R** — Repackaging | `/yt-repackaging <video-id>` | Ativo | Novos títulos, thumbnail, versionamento (se underperform) |
| 12 | **FASE S** — Session Arch. | *(pipeline output)* | Ativo | 2 playlists, comentário fixado, end-screen, card aos 60% |
| 13 | **FASE Y** — 48h Triage | `/yt-performance-triage <id> <checkpoint>` | Ativo | Checkpoints: 24h (CTR), 48h (retenção), 7d (documentação) |

---

## Agentes Transversais

| Agente | Comando | Quando usar |
|---|---|---|
| Auditoria Algorítmica | `/yt-algorithm-audit` | Mensal — análise de métricas de canal, retention, CTR, traffic |
| Cronograma Mensal | `/yt-calendar` | Mensal — 4 vídeos/mês com sub-nicho, keyword, ângulo |

---

## Regras de Execução

### Pipeline completo (novo vídeo)

```
P → T → A → N → Roteiro → Metadados → QA → Distribuição → Publicação → S → Y
```

### FASE D (Decision Bridge)

Adiada até o canal ter ~15+ vídeos longos. A regra dos 3-em-5 e
famílias semânticas precisam de massa de dados para funcionar.

### FASE N (Narrativa)

Obrigatória antes do roteiro. O roteirista escreve a partir da
arquitetura narrativa (cenas, não tópicos), não do output P+T+A puro.

### Distribuição (FASE X)

Checklist operacional para o criador — não é fase de IA.
Ações: Reddit, LinkedIn, WhatsApp, Discord, fóruns.

### Pós-publicação (obrigatório)

FASE Y com 3 checkpoints:

```
/yt-performance-triage <video-id> 24h   → decisão sobre thumbnail/título
/yt-performance-triage <video-id> 48h   → decisão sobre retenção/shorts
/yt-performance-triage <video-id> 7d    → documentação + ação para próximo
```

O aprendizado da FASE Y alimenta a FASE P do próximo vídeo.

### Regra de bloqueio

Se 3 vídeos consecutivos com CTR < 4% OU retenção < 30%:
pausar publicações por 7 dias e refazer FASE P + validação.
