# ADR-001: Agentic Workflow para Produção de Vídeos — Python + LangGraph

**Status:** Proposed
**Data:** 2026-04-19
**Autor:** Marcus Maciel

---

## Contexto

O canal **Marcus Maciel | IA & Ciência** utiliza um prompt mestre
(`prompt-videos-v11.md`, ~2.165 linhas, ~6.000 palavras) para gerar
roteiros completos de vídeos para YouTube. O prompt define um pipeline
de 7 fases executadas sequencialmente:

1. Fase P (Diagnóstico de performance do vídeo anterior)
2. Fase 0 (Análise competitiva de roteiros)
3. Validação de tema
4. Geração de metadados (títulos, thumbnail, descrição, tags)
5. Escrita do roteiro (hook, contexto, 4 blocos, CTA)
6. Checklist de validação (28 itens)
7. Fase R (Repackaging pós-publicação)

### Problemas do fluxo atual

| Problema | Impacto |
|---|---|
| **Contexto monolítico** | O modelo recebe ~6.000 palavras de instrução + outputs intermediários numa única conversa. Atenção dilui — regras do início são esquecidas no fim. |
| **Execução linear sem decisão** | Se a Fase P revela retenção de 2%, o modelo não pode parar e perguntar "vale continuar com esse tema?". Segue em frente cegamente. |
| **Sem memória entre vídeos** | Qual sub-nicho foi usado no último vídeo? Qual composição de thumbnail? Qual estética? Isso depende do usuário lembrar e informar. |
| **Sem loop de correção** | Se o checklist reprova 5 itens, o output é entregue com falhas. Não há mecanismo automático de revisão. |
| **Fase R desconectada** | O repackaging precisa ser solicitado manualmente. Não há monitoramento proativo. |

### Decisão a ser tomada

Transformar o prompt monolítico em um **agentic workflow** onde
agentes especializados executam cada fase com contexto otimizado,
capacidade de decisão e memória persistente.

---

## Decisão

Implementar o workflow usando **Python 3.12+ com LangGraph** como
framework de orquestração e **Claude (via API Anthropic)** como
modelo de inferência.

### Por que LangGraph (e não CrewAI, n8n ou custom)

| Opção | Prós | Contras | Veredito |
|---|---|---|---|
| **LangGraph** | Controle total sobre grafo de estados · Human-in-the-loop nativo · State management built-in · Ecossistema LangChain maduro · Checkpointing para resume | Curva de aprendizado maior que CrewAI | **Escolhido** |
| CrewAI | API mais simples · Setup rápido | Menos controle sobre branching · Human-in-the-loop menos elegante · Menor maturidade | Descartado |
| n8n / Make | Visual, sem código | Controle limitado sobre prompts · Difícil versionar · Vendor lock-in | Descartado |
| Custom (FastAPI) | Máximo controle | Reinventa orquestração, state management, checkpointing | Desproporcional para o escopo |

---

## Arquitetura

### Visão geral (C4 — Nível 2: Container)

```
┌─────────────────────────────────────────────────────────────┐
│                        YT-AGENT (Python)                    │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Agente P │───▶│ Agente 0 │───▶│ Agente V │              │
│  │(Diagnóst)│    │(Competit)│    │(Validação│              │
│  └────┬─────┘    └──────────┘    │ de Tema) │              │
│       │ retenção < 20%?          └────┬─────┘              │
│       ▼                               │ volume < 20?       │
│  ┌──────────┐                         ▼                    │
│  │ DECISÃO  │◀─── humano ──▶    ┌──────────┐              │
│  │  HUMANA  │                   │ DECISÃO  │              │
│  └──────────┘                   │  HUMANA  │              │
│       │                         └────┬─────┘              │
│       ▼                              ▼                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │Agente Meta───▶│Agente    │───▶│Agente QA │              │
│  │(Metadados│    │Roteirista│    │(Checklist│              │
│  └──────────┘    └──────────┘    └────┬─────┘              │
│                                       │ falhou 3+?         │
│                                       ▼                    │
│                                  ┌──────────┐              │
│                                  │  LOOP    │──▶ Roteirista│
│                                  │ CORREÇÃO │   (max 2x)   │
│                                  └──────────┘              │
│                                                             │
│  ── Fluxo independente (agendável) ──────────────────────  │
│  ┌──────────┐                                               │
│  │ Agente R │  Repackaging semanal autônomo                 │
│  │(Repackag)│                                               │
│  └──────────┘                                               │
│                                                             │
│  ── Infraestrutura ──────────────────────────────────────  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  State   │    │ Memória  │    │  Config  │              │
│  │  Store   │    │de Canal  │    │(Prompts) │              │
│  │(SQLite)  │    │(SQLite)  │    │ (.md)    │              │
│  └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Anthropic│    │  VidIQ   │    │ YouTube  │
   │   API    │    │   API    │    │ Data API │
   │ (Claude) │    │          │    │          │
   └──────────┘    └──────────┘    └──────────┘
```

### Grafo de estados (LangGraph)

```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   fase_p     │ Diagnóstico de performance
                  └──────┬───────┘
                         │
                    ┌────┴────┐
                    │ decide  │ retenção < 20%?
                    │ _fase_p │
                    └──┬───┬──┘
              ok ──────┘   └────── low_retention
                    │                    │
                    ▼                    ▼
             ┌──────────┐        ┌─────────────┐
             │  fase_0  │        │ human_pause  │
             │          │        │ _retenção    │
             └────┬─────┘        └──────┬──────┘
                  │                     │
                  │         ┌───────────┤
                  │         │ continuar │ repackaging
                  │         ▼           ▼
                  │    ┌────────┐  ┌──────────┐
                  │    │ fase_0 │  │ fase_r   │──▶ END
                  │    └───┬────┘  └──────────┘
                  │        │
                  ▼────────┘
             ┌──────────────┐
             │  validação   │ Checklist de Ouro
             │  _tema       │
             └──────┬───────┘
                    │
               ┌────┴────┐
               │ decide  │ volume < 20 e volume = 0?
               │ _tema   │
               └──┬───┬──┘
          ok ─────┘   └────── low_demand
               │                  │
               ▼                  ▼
        ┌──────────┐       ┌─────────────┐
        │metadados │       │ human_pause  │
        │          │       │ _tema        │
        └────┬─────┘       └──────┬──────┘
             │                    │
             │        ┌───────────┤
             │        │ continuar │ pivotar
             │        ▼           ▼
             │   ┌────────┐  ┌──────────┐
             │   │metadado│  │ validação │ (novo tema)
             │   └───┬────┘  │ _tema     │
             │       │       └──────────┘
             ▼───────┘
        ┌──────────────┐
        │  roteirista  │ Escrita do roteiro
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │    qa        │ Checklist 28 itens
        └──────┬───────┘
               │
          ┌────┴────┐
          │ decide  │ falhas >= 3?
          │ _qa     │
          └──┬───┬──┘
    pass ────┘   └──── fail (tentativa < 2)
          │                │
          ▼                ▼
     ┌─────────┐    ┌──────────────┐
     │  END    │    │  roteirista  │ (com instruções de correção)
     │ (output)│    │  _fix        │
     └─────────┘    └──────────────┘
```

---

## Especificação dos Agentes

### 1. Agente P — Diagnóstico de Performance

| Aspecto | Especificação |
|---|---|
| **Função** | Analisar o último vídeo publicado e gerar calibrações para o próximo roteiro |
| **Modelo** | Claude 4 Sonnet (tarefa analítica, custo otimizado) |
| **Input** | Channel ID (configuração), dados do último vídeo |
| **Output** | `PerformanceDiagnosis` (JSON estruturado) |
| **Tools** | `vidiq_user_channels`, `vidiq_channel_videos`, `vidiq_video_stats`, `vidiq_channel_analytics`, `vidiq_channel_performance_trends` |
| **Fallback tools** | `studio_listOwnVideos`, `analytics_getVideoAnalytics`, `analytics_getChannelAnalytics`, `analytics_getTopVideos` |
| **System prompt** | Extraído de: seção FASE P do prompt v11.3 (~180 linhas) |
| **Decisão** | Se `avg_retention < 20%` → sinalizar para human-in-the-loop |

**Schema do output (`PerformanceDiagnosis`):**

```json
{
  "last_video": {
    "id": "string",
    "title": "string",
    "type": "long | short",
    "published_at": "date",
    "views": "int",
    "avg_retention_pct": "float",
    "like_ratio_pct": "float",
    "comments": "int",
    "subscribers_gained": "int"
  },
  "channel_baseline": {
    "avg_views": "int",
    "avg_retention_pct": "float",
    "avg_like_ratio_pct": "float",
    "avg_comments": "int"
  },
  "retention_drops": [
    {
      "timestamp": "string (mm:ss)",
      "retention_before_pct": "float",
      "retention_after_pct": "float",
      "drop_pct": "float",
      "script_excerpt": "string",
      "diagnosis": "string",
      "corrective_action": "string"
    }
  ],
  "critical_points": {
    "30s_retention_pct": "float | null",
    "2min_retention_pct": "float | null",
    "midpoint_retention_pct": "float | null"
  },
  "lessons": {
    "errors_to_avoid": ["string"],
    "successes_to_keep": ["string"]
  },
  "calibrations": ["string (ações concretas para o roteiro atual)"],
  "alert": "none | low_retention | low_engagement"
}
```

---

### 2. Agente 0 — Análise Competitiva

| Aspecto | Especificação |
|---|---|
| **Função** | Analisar concorrentes, extrair erros/lacunas, gerar briefing competitivo |
| **Modelo** | Claude 4 Sonnet |
| **Input** | Tema do vídeo (campo variável), idioma (PT/EN) |
| **Output** | `CompetitiveBriefing` (JSON estruturado) |
| **Tools** | `vidiq_outliers`, `vidiq_trending_videos`, `vidiq_video_transcript`, `vidiq_video_comments` |
| **Fallback tools** | `videos_searchVideos`, `videos_getVideo`, `transcripts_getTranscript` |
| **System prompt** | Extraído de: seção FASE 0 do prompt v11.3 (~130 linhas) + CREDIBILIDADE CIENTÍFICA (~60 linhas) |

**Schema do output (`CompetitiveBriefing`):**

```json
{
  "competitors_analyzed": [
    {
      "title": "string",
      "channel": "string",
      "views": "int",
      "published_at": "date",
      "breakout_score": "float | null",
      "tags": ["string"]
    }
  ],
  "top_errors": [
    {
      "error": "string",
      "correction": "string",
      "source": "string (fonte real)"
    }
  ],
  "unexplored_angles": [
    {
      "angle": "string",
      "why_possible": "string (fonte real)"
    }
  ],
  "structural_pattern_to_avoid": "string",
  "differentiation_manifesto": "string (1 frase)",
  "audience_insights": {
    "top_questions": ["string"],
    "dominant_sentiment": "string",
    "recurring_objections": ["string"],
    "perceived_gaps": ["string"]
  },
  "competitor_tags": ["string"]
}
```

---

### 3. Agente V — Validação de Tema

| Aspecto | Especificação |
|---|---|
| **Função** | Validar viabilidade do tema via keyword research |
| **Modelo** | Claude 4 Sonnet |
| **Input** | Tema do vídeo, keyword principal |
| **Output** | `ThemeValidation` (JSON estruturado) |
| **Tools** | `vidiq_keyword_research` |
| **System prompt** | Extraído de: Validação do Tema no prompt v11.3 (~15 linhas) |
| **Decisão** | Se `overall < 20` e `volume = 0` → human-in-the-loop com alternativas |

**Schema do output (`ThemeValidation`):**

```json
{
  "keyword": "string",
  "volume": "int",
  "competition": "int",
  "overall": "int",
  "verdict": "approved | low_demand | rejected",
  "alternatives": [
    {
      "keyword": "string",
      "volume": "int",
      "competition": "int",
      "overall": "int"
    }
  ],
  "golden_checklist": {
    "universal_angle": "string",
    "short_premise": "string (≤10 palavras)",
    "persona_trigger": "string"
  }
}
```

---

### 4. Agente Meta — Metadados

| Aspecto | Especificação |
|---|---|
| **Função** | Gerar títulos, thumbnail prompt, descrição SEO, tags, post de comunidade, hashtags |
| **Modelo** | Claude 4 Sonnet |
| **Input** | Campos variáveis + `CompetitiveBriefing` + `ThemeValidation` + `ChannelMemory` (últimas thumbnails/estéticas) |
| **Output** | `VideoMetadata` (JSON estruturado) |
| **Tools** | `vidiq_keyword_research` (validação de títulos e tags) |
| **System prompt** | Extraído de: seção METADADOS do prompt v11.3 (~600 linhas: títulos, thumbnail, post comunidade, hashtags, tags, descrição SEO) |

**Schema do output (`VideoMetadata`):**

```json
{
  "titles": {
    "all_10": [
      {
        "title": "string",
        "formula": "string (1-6)",
        "char_count": "int",
        "word_count": "int"
      }
    ],
    "top_3": [
      {
        "title": "string",
        "formula": "string",
        "justification": "string",
        "keyword_validation": {
          "keyword": "string",
          "volume": "int",
          "competition": "int",
          "overall": "int"
        }
      }
    ]
  },
  "thumbnail": {
    "aesthetic": "documental_sombria | ficção_científica",
    "composition": "A | B | C",
    "emotion": "string",
    "dominant_color": "string (#hex)",
    "accent_color": "string (#hex)",
    "text_overlay": "string | null",
    "prompt_en": "string (prompt completo para Nano Banana 2)"
  },
  "description_seo": "string (250-400 palavras, template completo)",
  "tags": {
    "list": ["string"],
    "validation_table": [
      {
        "tag": "string",
        "volume": "int",
        "competition": "int",
        "overall": "int"
      }
    ]
  },
  "hashtags": ["string (3-5)"],
  "community_post": "string (≤150 palavras)"
}
```

---

### 5. Agente Roteirista — Escrita do Roteiro

| Aspecto | Especificação |
|---|---|
| **Função** | Escrever o roteiro completo com VISUALs, loops, CTAs |
| **Modelo** | **Claude 4 Opus** (máxima qualidade narrativa) |
| **Input** | Campos variáveis + `PerformanceDiagnosis.calibrations` + `CompetitiveBriefing` + `VideoMetadata.titles.top_3[0]` + regras narrativas |
| **Output** | `Script` (JSON estruturado) |
| **Tools** | Nenhum (execução pura de escrita) |
| **System prompt** | Extraído de: VOZ E TOM (~180 linhas) + DNA NARRATIVO (~130 linhas) + ESCRITA OTIMIZADA PARA VOZ-OVER (~70 linhas) + CAMADA DE RETENÇÃO (~80 linhas) + CTAs NA NARRAÇÃO (~40 linhas) + ESTRUTURA DO ROTEIRO (~200 linhas) — total ~700 linhas de instrução otimizadas |
| **Pré-condição** | Leitura de 1 modelo de escrita de `modelos-de-escrita/` antes de gerar |

**Schema do output (`Script`):**

```json
{
  "word_count": "int",
  "estimated_duration_min": "float",
  "sections": [
    {
      "type": "hook | context | block_1 | block_2 | block_3 | block_4 | cta_final",
      "label": "string (Âncora, Escalada, Clímax, Implicação...)",
      "narration": "string",
      "visual": "string",
      "pattern_interrupt": "string | null",
      "editorial_insertion": "string | null",
      "cta": "string | null (CTA 1, 2 ou 3)"
    }
  ],
  "open_loops_map": [
    {
      "loop_number": "int",
      "opens_at": "string (seção + timestamp estimado)",
      "content": "string",
      "closes_at": "string",
      "payoff_type": "string"
    }
  ],
  "retention_audit": {
    "hook_delivers_promise_in_8s": "bool",
    "zero_institutional_intro": "bool",
    "first_visual_specific": "bool",
    "numeric_data_in_15s": "bool",
    "context_opens_loop": "bool"
  },
  "differentiation_manifesto_location": "string (seção onde aparece)"
}
```

---

### 6. Agente QA — Validação (Checklist)

| Aspecto | Especificação |
|---|---|
| **Função** | Executar os 28 itens da checklist e reportar aprovação/reprovação |
| **Modelo** | Claude 4 Sonnet |
| **Input** | `Script` + `VideoMetadata` + checklist de 28 itens |
| **Output** | `QAReport` (JSON estruturado) |
| **Tools** | Nenhum |
| **System prompt** | Extraído de: CHECKLIST DE VALIDAÇÃO (~35 linhas) + INSTRUÇÕES DE PRIORIDADE (~10 linhas) |
| **Decisão** | Se `failures >= 3` e `attempt < 2` → devolver ao Roteirista com instruções de correção |

**Schema do output (`QAReport`):**

```json
{
  "total_items": 28,
  "passed": "int",
  "failed": "int",
  "attempt": "int (1 ou 2)",
  "items": [
    {
      "number": "int",
      "name": "string",
      "status": "pass | fail | skip",
      "detail": "string (motivo da falha ou skip)"
    }
  ],
  "verdict": "approved | needs_fix | approved_with_warnings",
  "fix_instructions": ["string (instruções específicas para o Roteirista)"]
}
```

---

### 7. Agente R — Repackaging (fluxo independente)

| Aspecto | Especificação |
|---|---|
| **Função** | Identificar vídeos subperformando e gerar novo pacote (título, thumbnail, descrição) |
| **Modelo** | Claude 4 Sonnet |
| **Input** | Channel ID, baseline de performance |
| **Output** | `RepackagingProposal` (JSON estruturado) |
| **Tools** | `vidiq_channel_videos`, `vidiq_video_stats`, `vidiq_keyword_research` |
| **System prompt** | Extraído de: FASE R do prompt v11.3 (~120 linhas) |
| **Trigger** | Manual ou agendamento semanal (cron) |

---

## Memória Persistente (Channel Memory)

Para resolver o problema de falta de contexto entre vídeos,
implementar um SQLite local com as seguintes tabelas:

### Tabela: `videos`

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | TEXT PK | YouTube video ID |
| `title` | TEXT | Título publicado |
| `sub_niche` | TEXT | Sub-nicho usado |
| `published_at` | DATE | Data de publicação |
| `format` | TEXT | "long" ou "short" |
| `thumbnail_aesthetic` | TEXT | "documental_sombria" ou "ficção_científica" |
| `thumbnail_composition` | TEXT | "A", "B" ou "C" |
| `thumbnail_palette` | TEXT | Cor dominante hex |
| `thumbnail_expression` | TEXT | Expressão facial usada |
| `views_7d` | INT | Views após 7 dias |
| `avg_retention_pct` | FLOAT | Retenção média |
| `like_ratio_pct` | FLOAT | Like ratio |

### Tabela: `tags_performance`

| Coluna | Tipo | Descrição |
|---|---|---|
| `tag` | TEXT | Tag utilizada |
| `video_id` | TEXT FK | Vídeo onde foi usada |
| `volume_at_use` | INT | Volume quando selecionada |
| `video_views_7d` | INT | Views do vídeo após 7 dias |

### Tabela: `workflow_runs`

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | TEXT PK | UUID do run |
| `started_at` | DATETIME | Início da execução |
| `status` | TEXT | "running", "paused", "completed", "failed" |
| `current_node` | TEXT | Nó atual do grafo |
| `state_json` | TEXT | State serializado do LangGraph (para resume) |

### Como os agentes usam a memória

- **Agente Meta** consulta `videos` para garantir alternância de
  estética, composição e paleta. Também consulta `tags_performance`
  para priorizar tags que historicamente correlacionam com mais views.
- **Agente P** popula `videos` com os dados de performance do último
  vídeo após cada execução.
- **Agente R** consulta `videos` para identificar candidatos a
  repackaging (views < 50% da média).

---

## Stack Tecnológica

| Componente | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| Linguagem | Python | 3.12+ | Ecossistema LangChain/LangGraph nativo |
| Orquestração | LangGraph | latest | Grafo de estados, human-in-the-loop, checkpointing |
| LLM | Anthropic Claude | 4 Sonnet + 4 Opus | Sonnet para análise, Opus para escrita narrativa |
| Banco de dados | SQLite | built-in | Zero infra, portátil, suficiente para 1 canal |
| HTTP client | httpx | latest | Chamadas assíncronas a VidIQ e YouTube API |
| Config | Pydantic Settings | v2 | Tipagem + validação de env vars |
| CLI | Typer | latest | Interface de linha de comando |
| Schemas | Pydantic | v2 | Validação de inputs/outputs dos agentes |
| Testes | pytest | latest | Com fixtures para mock de APIs |
| Formatação | Ruff | latest | Linter + formatter unificado |

### Dependências externas (APIs)

| API | Autenticação | Rate limit | Custo |
|---|---|---|---|
| Anthropic (Claude) | API key | Generoso (tier 1: 60 req/min) | ~US$ 0,40-0,80 por vídeo |
| VidIQ | API key (via MCP existente) | Depende do plano | Incluído no plano atual |
| YouTube Data API v3 | OAuth2 (já configurado) | 10.000 unidades/dia (gratuito) | Gratuito |

---

## Estrutura do Projeto

```
yt-agent/
├── docs/
│   └── adr/
│       └── 001-agentic-workflow-langgraph.md  ← este documento
├── src/
│   └── yt_agent/
│       ├── __init__.py
│       ├── main.py                  # Entry point CLI (Typer)
│       ├── config.py                # Pydantic Settings (API keys, paths)
│       ├── graph.py                 # Definição do grafo LangGraph
│       ├── state.py                 # TypedDict do state compartilhado
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── performance.py       # Agente P
│       │   ├── competitive.py       # Agente 0
│       │   ├── validation.py        # Agente V
│       │   ├── metadata.py          # Agente Meta
│       │   ├── scriptwriter.py      # Agente Roteirista
│       │   ├── qa.py                # Agente QA
│       │   └── repackaging.py       # Agente R
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── vidiq.py             # Wrapper VidIQ API
│       │   └── youtube.py           # Wrapper YouTube Data API
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── models.py            # SQLAlchemy/SQLite models
│       │   └── repository.py        # Queries de leitura/escrita
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── performance.md       # System prompt do Agente P
│       │   ├── competitive.md       # System prompt do Agente 0
│       │   ├── validation.md        # System prompt do Agente V
│       │   ├── metadata.md          # System prompt do Agente Meta
│       │   ├── scriptwriter.md      # System prompt do Agente Roteirista
│       │   ├── qa.md                # System prompt do Agente QA
│       │   └── repackaging.md       # System prompt do Agente R
│       └── output/
│           ├── __init__.py
│           └── renderer.py          # Renderiza output final em Markdown
├── tests/
│   ├── conftest.py
│   ├── test_agents/
│   │   ├── test_performance.py
│   │   ├── test_competitive.py
│   │   └── ...
│   └── test_graph.py                # Testes do fluxo completo
├── pyproject.toml                   # Dependências e config do projeto
├── .env.example                     # Template de variáveis de ambiente
└── .gitignore
```

---

## State do LangGraph (TypedDict)

O state compartilhado entre todos os nós do grafo:

```python
class WorkflowState(TypedDict):
    # Inputs (preenchidos pelo usuário)
    video_topic: str
    sub_niche: str
    format: Literal["long", "short"]
    editorial_angle: str
    dominant_emotion: str
    technical_detail: Literal["basic", "intermediate", "advanced"]
    reference_period: str
    related_video: str | None
    context_notes: str | None

    # Outputs dos agentes (preenchidos durante execução)
    performance_diagnosis: PerformanceDiagnosis | None
    competitive_briefing: CompetitiveBriefing | None
    theme_validation: ThemeValidation | None
    video_metadata: VideoMetadata | None
    script: Script | None
    qa_report: QAReport | None

    # Controle de fluxo
    human_decisions: list[HumanDecision]
    qa_attempt: int
    current_phase: str
    errors: list[str]
```

---

## Interface do Usuário (CLI)

### Fluxo principal — gerar roteiro

```bash
# Execução interativa (human-in-the-loop nos pontos de decisão)
python -m yt_agent new \
  --topic "IA reverter envelhecimento" \
  --sub-niche "IA + Medicina/Saúde" \
  --format long \
  --angle revelador \
  --emotion "Admiração" \
  --detail intermediário \
  --period "2025-2026"

# Retomar execução pausada
python -m yt_agent resume --run-id <uuid>
```

### Repackaging

```bash
# Verificar candidatos a repackaging
python -m yt_agent repackage --check

# Executar repackaging para um vídeo específico
python -m yt_agent repackage --video-id <id>
```

### Memória

```bash
# Listar histórico de vídeos
python -m yt_agent history

# Atualizar métricas do último vídeo
python -m yt_agent update-metrics --video-id <id>
```

---

## Estimativa de Custo por Execução

| Agente | Modelo | Input tokens | Output tokens | Custo estimado |
|---|---|---|---|---|
| Agente P | Sonnet | ~3.000 | ~1.500 | ~US$ 0,02 |
| Agente 0 | Sonnet | ~5.500 | ~2.000 | ~US$ 0,03 |
| Agente V | Sonnet | ~500 | ~300 | < US$ 0,01 |
| Agente Meta | Sonnet | ~3.000 | ~3.000 | ~US$ 0,03 |
| Roteirista | **Opus** | ~3.000 | ~5.000 | ~US$ 0,30 |
| Agente QA | Sonnet | ~7.000 | ~1.500 | ~US$ 0,03 |
| **Total (sem loop)** | | | | **~US$ 0,42** |
| **Total (com 1 loop de correção)** | | | | **~US$ 0,72** |

**Para 4 vídeos/mês**: ~US$ 1,70–2,90/mês

---

## Plano de Implementação (fases)

### Fase 1 — Foundation (estimativa: 2-3 dias)

- [ ] Setup do projeto (pyproject.toml, configs, .env)
- [ ] Definição do state (Pydantic models + TypedDict)
- [ ] Wrappers de ferramentas (VidIQ, YouTube API)
- [ ] SQLite + modelos de memória
- [ ] CLI básica com Typer

### Fase 2 — Agentes Core (estimativa: 3-4 dias)

- [ ] Agente P (Diagnóstico)
- [ ] Agente 0 (Competitivo)
- [ ] Agente V (Validação)
- [ ] Agente Meta (Metadados)
- [ ] Agente Roteirista
- [ ] Agente QA (Checklist)
- [ ] Extração dos system prompts do v11.3 para arquivos .md individuais

### Fase 3 — Orquestração (estimativa: 2-3 dias)

- [ ] Grafo LangGraph com todos os nós
- [ ] Human-in-the-loop nos pontos de decisão
- [ ] Loop de correção QA → Roteirista
- [ ] Checkpointing (resume de execuções pausadas)
- [ ] Renderer de output (Markdown final)

### Fase 4 — Memória e Repackaging (estimativa: 1-2 dias)

- [ ] Agente R (Repackaging)
- [ ] População automática da memória após cada run
- [ ] Consultas de alternância (estética, composição, sub-nicho)
- [ ] Comando `repackage --check`

### Fase 5 — Testes e polimento (estimativa: 1-2 dias)

- [ ] Testes unitários dos agentes (com mock de APIs)
- [ ] Teste de integração do grafo completo
- [ ] Documentação de uso

**Total estimado: 9-14 dias de desenvolvimento**

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| VidIQ API muda/deprecia endpoints | Média | Alto | Fallback para YouTube Data API em todos os agentes · Wrapper abstraído |
| Custo da API Anthropic sobe | Baixa | Médio | Agentes analíticos podem migrar para Sonnet/Haiku · Só Roteirista precisa de Opus |
| Output do LLM não respeita JSON schema | Média | Médio | Pydantic validation + retry automático com mensagem de erro |
| Roteiro gerado pelo agente isolado perde qualidade vs. prompt monolítico | Média | Alto | System prompts extraídos literalmente do v11.3 · Modelo de escrita injetado no contexto · Testes de qualidade comparativos |
| SQLite não escala para múltiplos canais | Baixa | Baixo | Migrar para PostgreSQL se necessário (SQLAlchemy abstrai) |

---

## Alternativas Consideradas

### 1. Manter o prompt monolítico no Cursor

- **Prós**: Zero investimento, funciona hoje.
- **Contras**: Diluição de contexto, sem memória, sem decisão automática,
  sem loop de correção.
- **Veredito**: Suficiente para produção casual, insuficiente para escala.

### 2. CrewAI em vez de LangGraph

- **Prós**: Setup mais rápido, API mais intuitiva.
- **Contras**: Menos controle sobre branching condicional, human-in-the-loop
  menos elegante, menor maturidade do framework.
- **Veredito**: Viável, mas LangGraph oferece melhor controle para este
  workflow específico que tem múltiplos pontos de decisão.

### 3. Workflow visual (n8n/Make)

- **Prós**: Zero código, interface visual.
- **Contras**: Limitado em prompt engineering, difícil versionar,
  vendor lock-in, custo mensal da plataforma.
- **Veredito**: Inadequado para a complexidade dos system prompts.

---

## Consequências

### Positivas

- Cada agente opera com **contexto otimizado** (~700 linhas vs. ~2.165)
  → melhor qualidade de output.
- **Memória persistente** garante alternância automática e aprendizado
  incremental entre vídeos.
- **Human-in-the-loop** nos pontos certos evita trabalho desperdiçado
  (roteiro inteiro para tema sem demanda).
- **Loop de correção** do QA reduz entrega de roteiros com falhas.
- **Reprodutibilidade** — mesmo input gera mesmo fluxo.
- **Custo previsível** — ~US$ 2-3/mês para 4 vídeos.

### Negativas

- **Investimento inicial** de 9-14 dias de desenvolvimento.
- **Manutenção** quando o prompt v11 evoluir (precisa atualizar os
  system prompts extraídos).
- **Dependência** de API key da Anthropic separada do Cursor.
- **Perda de flexibilidade conversacional** — no Cursor, é possível
  pedir ajustes ad-hoc no meio do fluxo. No workflow, as interações
  são estruturadas.

### Mitigação da manutenção

Os system prompts ficam em arquivos `.md` separados no diretório
`prompts/`. Quando o prompt mestre evolui, basta atualizar o arquivo
correspondente — a lógica de orquestração não muda.

---

## Referências

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Anthropic API Pricing](https://docs.anthropic.com/en/docs/about-claude/pricing)
- [Prompt v11.3](../../../canais/marcus-maciel/prompts/prompt-videos-v11.md)
- [VidIQ MCP Tools](../../../mcps/project-0-yt-vidIQ/tools/)
- [YouTube MCP Tools](../../../mcps/project-0-yt-youtube/tools/)
