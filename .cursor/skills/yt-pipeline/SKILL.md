---
name: yt-pipeline
description: >-
  Orquestra o pipeline completo de produção de vídeo para o canal
  Marcus Maciel | IA & Ciência. Executa 7 fases em sequência:
  Performance, Competitiva, Validação, Narrativa, Metadados, Roteiro
  e QA. Use quando o usuário invocar /yt-pipeline com um tema de vídeo.
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

### Fase 3 — Narrativa

Lance **`/yt-narrative "TEMA"`**, passando como contexto os resultados
das 3 fases anteriores (Performance, Competitiva, Validação).

O subagent gera a arquitetura narrativa: protagonista, espinha dorsal,
arco emocional, beat map de cenas, micro-histórias, motivos visuais,
pares setup/payoff e anti-clichês.

Salve em `output/videos/{slug}/04-narrative.md`.

### Fase 4 — Metadados

Lance **`/yt-metadata "TEMA"`**, passando como contexto os resultados
das fases anteriores (calibrações da Performance, briefing
Competitivo, dados da Validação).

Salve em `output/videos/{slug}/05-metadata.md`.

### Fase 5 — Roteiro

Lance **`/yt-scriptwriter "TEMA"`**, passando como contexto:
- Arquitetura narrativa da Fase N (protagonista, cenas, arco emocional)
- Metadados gerados (título escolhido, emoção dominante, ângulo editorial)
- Calibrações da Performance
- Briefing Competitivo (manifesto, correções, ângulos)

O roteirista escreve a partir da Fase N — cenas, não tópicos.

Salve em `output/videos/{slug}/06-script.md`.

### Fase 6 — QA

Lance **`/yt-qa`**, passando como contexto os metadados e o roteiro
completo.

Salve em `output/videos/{slug}/07-qa-report.md`.

**Decisão:**
- `approved` → consolidar FINAL.md
- `needs_fix` → passar instruções ao roteirista (relançar Fase 5
  com as correções) e repetir QA
- `approved_with_warnings` → consolidar com nota de warnings

### Consolidação

Após QA aprovado, crie `output/videos/{slug}/FINAL.md` com todas as
seções consolidadas: Performance, Competitiva, Validação, Narrativa,
Metadados, Roteiro, QA Report.

## Passagem de Contexto entre Fases

Cada subagent roda isolado. Para garantir que o output completo das
fases anteriores seja usado, **cada subagent DEVE ler os arquivos do
disco** antes de executar. A instrução de leitura está embutida em
cada subagent, mas o orquestrador (você) deve **sempre informar o
slug** para que o subagent saiba qual pasta ler.

Fluxo de dependências:

```
Fase N (narrative) ← lê 01-performance + 02-competitive + 03-validation
Fase Meta          ← lê 01-performance + 02-competitive + 03-validation
Fase Roteiro       ← lê 04-narrative + 05-metadata + 01-performance + 02-competitive
Fase QA            ← lê 05-metadata + 06-script + 04-narrative
```

## Notas

- Cada fase é um subagent isolado — não polui o contexto principal
- O slug do tema é usado consistentemente em todos os caminhos
- A memória do canal é injetada automaticamente pelo hook `sessionStart`
- Os outputs completos de fases anteriores são lidos do disco por cada subagent
