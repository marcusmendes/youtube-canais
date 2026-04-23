---
name: yt-pipeline
description: >-
  Orquestra o pipeline completo de produção de vídeo para o canal
  Marcus Maciel | IA & Ciência. Executa 6 fases em sequência:
  Performance, Competitiva, Validação, Metadados, Roteiro e QA.
  Use quando o usuário invocar /yt-pipeline com um tema de vídeo.
---

# YT Pipeline — Produção Completa de Vídeo

## Quando usar

O usuário invoca `/yt-pipeline "tema do vídeo"`.

## Workflow

Execute as fases abaixo em ordem. Após cada fase, apresente um
resumo ao usuário e aguarde confirmação antes de prosseguir.

### Fase 1 — Performance + Competitiva (paralelo)

Lance **dois subagents em paralelo**:

1. **`/yt-performance`** — Diagnóstico do último vídeo publicado.
   Sem parâmetros — o subagent identifica o último vídeo automaticamente.

2. **`/yt-competitive "TEMA"`** — Análise competitiva sobre o tema
   fornecido pelo usuário.

Aguarde ambos completarem. Salve os outputs em:
- `output/videos/{slug}/01-performance.md`
- `output/videos/{slug}/02-competitive.md`

Onde `{slug}` é o tema convertido para kebab-case (ex: "IA na
cirurgia robótica" → `ia-na-cirurgia-robotica`).

### Fase 2 — Validação

Lance **`/yt-validation "KEYWORD"`** com a keyword principal do tema.

Salve em `output/videos/{slug}/03-validation.md`.

**Decisão:**
- `approved` → continuar
- `low_demand` → mostrar alternativas ao usuário e aguardar decisão
- `rejected` → sugerir pivotar e aguardar decisão

### Fase 3 — Metadados

Lance **`/yt-metadata "TEMA"`**, passando como contexto os resultados
das fases anteriores (calibrações da Performance, briefing
Competitivo, dados da Validação).

Salve em `output/videos/{slug}/04-metadata.md`.

### Fase 4 — Roteiro

Lance **`/yt-scriptwriter "TEMA"`**, passando como contexto:
- Metadados gerados (título escolhido, emoção dominante, ângulo editorial)
- Calibrações da Performance
- Briefing Competitivo (manifesto, correções, ângulos)

Salve em `output/videos/{slug}/05-script.md`.

### Fase 5 — QA

Lance **`/yt-qa`**, passando como contexto os metadados e o roteiro
completo.

Salve em `output/videos/{slug}/06-qa-report.md`.

**Decisão:**
- `approved` → consolidar FINAL.md
- `needs_fix` → passar instruções ao roteirista (relançar Fase 4
  com as correções) e repetir QA
- `approved_with_warnings` → consolidar com nota de warnings

### Consolidação

Após QA aprovado, crie `output/videos/{slug}/FINAL.md` com todas as
seções consolidadas: Performance, Competitiva, Validação, Metadados,
Roteiro, QA Report.

## Notas

- Cada fase é um subagent isolado — não polui o contexto principal
- O slug do tema é usado consistentemente em todos os caminhos
- A memória do canal é injetada automaticamente pelo hook `sessionStart`
