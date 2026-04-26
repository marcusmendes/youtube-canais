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

Lance **`/yt-scriptwriter "TEMA"`**, passando como contexto:
- Arquitetura narrativa (protagonista, cenas, arco emocional)
- Metadados (título escolhido, emoção dominante, ângulo editorial)
- Dossier de fontes (dados verificados, micro-histórias, lacunas)
- Calibrações da Performance
- Briefing Competitivo (manifesto, correções, ângulos)

O roteirista executa em **dois passes**:
1. **Pass 1 — Esqueleto:** preenche cenas da Fase N com dados do dossier
2. **Pass 2 — Polimento:** ElevenLabs, ritmo, pattern interrupts,
   Viewer Simulation Pass, verificação de fontes

Salve em `output/videos/{slug}/07-script.md`.

### Fase 7 — QA

Lance **`/yt-qa`**, passando como contexto os metadados, roteiro e
dossier de fontes.

Salve em `output/videos/{slug}/08-qa-report.md`.

**Decisão:**
- `approved` → consolidar FINAL.md
- `needs_fix` → passar instruções ao roteirista (relançar Fase 6
  com as correções) e repetir QA
- `approved_with_warnings` → consolidar com nota de warnings

### Consolidação

Após QA aprovado, crie `output/videos/{slug}/FINAL.md` com todas as
seções consolidadas: Performance, Research, Competitiva, Validação,
Narrativa, Metadados, Roteiro, QA Report.

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
Fase QA           ← lê 06-metadata + 07-script + 05-narrative + 02-research
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
| 07 | Script | `07-script.md` |
| 08 | QA | `08-qa-report.md` |
| 09 | Triage (pós-pub) | `09-triage-{checkpoint}.md` |

## Notas

- Cada fase é um subagent isolado — não polui o contexto principal
- O slug do tema é usado consistentemente em todos os caminhos
- A memória do canal é injetada automaticamente pelo hook `sessionStart`
- Os outputs completos de fases anteriores são lidos do disco por cada subagent
- Performance e Research rodam em paralelo (sem dependência mútua)
