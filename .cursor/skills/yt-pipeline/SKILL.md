---
name: yt-pipeline
description: >-
  Orquestra o pipeline completo de produção de vídeo para o canal
  Marcus Maciel | IA & Ciência. Executa 8 fases em sequência:
  Performance, Research, Competitiva, Validação, Narrativa, Metadados,
  Roteiro e QA. Use quando o usuário invocar /yt-pipeline com um tema.
---

# YT Pipeline — Produção Completa de Vídeo

## Quando usar

O usuário invoca `/yt-pipeline "tema do vídeo"`.

## Workflow

Execute as fases abaixo em ordem. Após cada fase, apresente um
resumo ao usuário e aguarde confirmação antes de prosseguir.

### Fase 1 — Performance + Research (paralelo)

Lance **dois subagents em paralelo**:

1. **`/yt-performance`** — Diagnóstico do último vídeo publicado.
   Sem parâmetros — o subagent identifica o último vídeo automaticamente.

2. **`/yt-research "TEMA"`** — Pesquisa de fontes primárias sobre o
   tema. Busca papers, artigos, notícias e dados concretos via
   WebSearch e WebFetch. Gera dossier estruturado.

Aguarde ambos completarem. Salve os outputs em:
- `output/videos/{slug}/01-performance.md`
- `output/videos/{slug}/02-research.md`

Onde `{slug}` é o tema convertido para kebab-case (ex: "IA na
cirurgia robótica" → `ia-na-cirurgia-robotica`).

### Fase 2 — Competitiva

Lance **`/yt-competitive "TEMA"`** — Análise competitiva sobre o tema.
O agente agora usa o dossier de fontes (`02-research.md`) para cruzar
com os transcripts dos concorrentes.

Salve em `output/videos/{slug}/03-competitive.md`.

### Fase 3 — Validação

Lance **`/yt-validation "KEYWORD"`** com a keyword principal do tema.

Salve em `output/videos/{slug}/04-validation.md`.

**Decisão:**
- `approved` → continuar
- `low_demand` → mostrar alternativas ao usuário e aguardar decisão
- `rejected` → sugerir pivotar e aguardar decisão

### Fase 4 — Narrativa

Lance **`/yt-narrative "TEMA"`**, passando como contexto os resultados
das fases anteriores (Performance, Research, Competitiva, Validação).

O subagent gera a arquitetura narrativa: protagonista, espinha dorsal,
arco emocional, beat map de cenas, micro-histórias, motivos visuais,
pares setup/payoff e anti-clichês.

Salve em `output/videos/{slug}/05-narrative.md`.

### Fase 5 — Metadados

Lance **`/yt-metadata "TEMA"`**, passando como contexto os resultados
das fases anteriores.

Salve em `output/videos/{slug}/06-metadata.md`.

### Fase 6 — Roteiro (Two-pass)

**Escolha do modo (pergunte ao usuário se não estiver explícito):**

| Modo | Subagent | Arquivo de saída |
|---|---|---|
| Voz-over (ElevenLabs) — **padrão** | **`/yt-scriptwriter "TEMA"`** | `07-script.md` |
| Marcus em câmera (teleprompter) | **`/yt-scriptwriter-presenter "TEMA"`** | `07-script-presenter.md` |

Passe como contexto (ambos os modos):
- Arquitetura narrativa (protagonista, cenas, arco emocional)
- Metadados (título escolhido, emoção dominante, ângulo editorial)
- Dossier de fontes (dados verificados, micro-histórias, lacunas)
- Calibrações da Performance
- Briefing Competitivo (manifesto, correções, ângulos)

O roteirista executa em **dois passes**:
1. **Pass 1 — Esqueleto:** preenche cenas da Fase N com dados do dossier
2. **Pass 2 — Polimento:** no modo ElevenLabs — formatação v2, ritmo,
   pattern interrupts, Viewer Simulation Pass, fontes; no modo
   apresentador — `[A-ROLL]`/`[B-ROLL]`, teleprompter, **`[pausa]` /
   `[ênfase]`**, CTAs B2–B4, densidade de loops, **Auditoria 30s**,
   contagem **real** de palavras faladas, mesmos audits e **somente**
   fontes/veículos presentes no `02-research.md`.

**Gates antes da Fase 7 (QA):** o `06-metadata.md` deve cumprir contagem
da descrição, disclosure IA, hashtags dedicadas, tabela 7 seções da
thumbnail e Session Architecture; o roteiro apresentador deve cumprir
faixa de palavras, CTAs, anti-`VISUAL:` genérico e item 31 (veículos no
dossiê).

Salve em `output/videos/{slug}/07-script.md` **ou**
`output/videos/{slug}/07-script-presenter.md`, conforme o modo.

### Fase 7 — QA

Lance **`/yt-qa`**, passando como contexto os metadados, roteiro e
dossier de fontes.

Salve em `output/videos/{slug}/08-qa-report.md`.

**Decisão:**
- `approved` → consolidar FINAL.md
- `needs_fix` → passar instruções ao roteirista (relançar Fase 6
  com as correções — **mesmo** subagent e arquivo de roteiro do
  modo escolhido: `yt-scriptwriter` → `07-script.md`, ou
  `yt-scriptwriter-presenter` → `07-script-presenter.md`) e repetir QA
- `approved_with_warnings` → consolidar com nota de warnings

### Consolidação

Após QA aprovado, crie `output/videos/{slug}/FINAL.md` com todas as
seções consolidadas: Performance, Research, Competitiva, Validação,
Narrativa, Metadados, Roteiro (`07-script.md` e/ou
`07-script-presenter.md`, conforme o que existir), QA Report.

## Passagem de Contexto entre Fases

Cada subagent roda isolado. Para garantir que o output completo das
fases anteriores seja usado, **cada subagent DEVE ler os arquivos do
disco** antes de executar. A instrução de leitura está embutida em
cada subagent, mas o orquestrador (você) deve **sempre informar o
slug** para que o subagent saiba qual pasta ler.

Fluxo de dependências:

```
Fase Competitiva  ← lê 02-research (cruzar fontes com concorrentes)
Fase Narrativa    ← lê 01-performance + 02-research + 03-competitive + 04-validation
Fase Metadados    ← lê 01-performance + 02-research + 03-competitive + 04-validation
Fase Roteiro      ← lê 05-narrative + 06-metadata + 02-research + 01-performance + 03-competitive
Fase QA           ← lê 06-metadata + 07-script.md OU 07-script-presenter.md
                   (ou legado `07-scriptwriter-presenter.md`) + 05-narrative
                   + 02-research
```

## Numeração de outputs

| # | Fase | Arquivo |
|---|---|---|
| 01 | Performance | `01-performance.md` |
| 02 | Research | `02-research.md` |
| 03 | Competitive | `03-competitive.md` |
| 04 | Validation | `04-validation.md` |
| 05 | Narrative | `05-narrative.md` |
| 06 | Metadata | `06-metadata.md` |
| 07 | Script (VO / ElevenLabs) | `07-script.md` |
| 07b | Script (apresentador) | `07-script-presenter.md` |
| 08 | QA | `08-qa-report.md` |
| 09 | Triage (pós-pub) | `09-triage-{checkpoint}.md` |

## Notas

- Cada fase é um subagent isolado — não polui o contexto principal
- O slug do tema é usado consistentemente em todos os caminhos
- A memória do canal é injetada automaticamente pelo hook `sessionStart`
- Os outputs completos de fases anteriores são lidos do disco por cada subagent
- Performance e Research rodam em paralelo (sem dependência mútua)
