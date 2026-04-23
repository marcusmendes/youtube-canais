# ADR-002: Migração do Pipeline Agentic para Cursor Subagents

**Status:** Proposed
**Data:** 2026-04-22
**Autor:** Marcus Maciel
**Supersede:** ADR-001 (complementa — não invalida)

---

## Contexto

A ADR-001 definiu o `yt-agent` como CLI Python + LangGraph chamando a
API do Claude diretamente. O sistema funciona e produz resultados de
qualidade, mas revelou um problema de custo:

| Métrica | Valor |
|---|---|
| Custo por execução do repackaging | ~$4,45 USD |
| Custo estimado do pipeline completo | ~$10-15 USD |
| Frequência de uso esperada | 2-4x por semana |
| Custo mensal estimado | $80-240 USD |

O custo vem de:
1. **System prompts longos** (200-400 linhas cada) reenviados a cada round
2. **Múltiplas rodadas de tool calls** (3-4 rounds com 2-3 tools) acumulando contexto
3. **Claude Sonnet via API** ($3/M input, $15/M output tokens)
4. **Contexto crescente** — o histórico de tool results é reenviado integralmente

### Decisão

Migrar o pipeline agentic para dentro do **Cursor IDE**, usando três
recursos nativos que combinados replicam a funcionalidade do `yt-agent`
com custo zero de API adicional:

1. **Skills** — comandos slash que o usuário invoca
2. **Subagents** — agentes especializados com contexto isolado
3. **Hooks** — scripts de automação para memória persistente

---

## Arquitetura da Solução

### Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                     CURSOR IDE                           │
│                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Skills   │───▶│  Subagents   │───▶│    Hooks      │  │
│  │ (commands)│    │(especialistas)│    │  (automação)  │  │
│  └──────────┘    └──────┬───────┘    └───────┬───────┘  │
│                         │                     │          │
│                  ┌──────▼───────┐      ┌──────▼───────┐  │
│                  │  MCP Servers │      │   SQLite DB  │  │
│                  │ VidIQ + YT   │      │  (memória)   │  │
│                  └──────────────┘      └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Componente 1 — Skills (Interface do Usuário)

Skills são slash commands ativados por `/nome` no chat do Cursor.
Cada skill define **o quê** fazer e delega para o subagent
correspondente. Usam `disable-model-invocation: true` para ativação
exclusivamente explícita.

| Skill | Invocação | Função |
|---|---|---|
| `yt-pipeline` | `/yt-pipeline "tema do vídeo"` | Orquestra o pipeline completo (7 fases) |
| `yt-repackaging` | `/yt-repackaging VIDEO_ID` | Repackaging de vídeo underperforming |
| `yt-performance` | `/yt-performance` | Diagnóstico do último vídeo (Fase P) |
| `yt-competitive` | `/yt-competitive "tema"` | Análise competitiva (Fase 0) |
| `yt-validation` | `/yt-validation "keyword"` | Validação de tema (Fase V) |
| `yt-metadata` | `/yt-metadata "tema"` | Gerar títulos, thumbnail, descrição, tags |
| `yt-scriptwriter` | `/yt-scriptwriter "tema"` | Escrever roteiro completo |
| `yt-qa` | `/yt-qa` | Executar checklist de 28 itens |

**Localização:** `.cursor/skills/{nome}/SKILL.md`

#### Responsabilidades da Skill

1. Receber o input do usuário (tema, video ID, etc.)
2. Delegar para o subagent correspondente com contexto completo
3. Instruir o subagent a salvar output em `output/`
4. No caso do `yt-pipeline`, orquestrar a sequência de subagents

### Componente 2 — Subagents (Especialistas)

Cada subagent é um agente com **contexto isolado** que executa uma
fase específica do pipeline. O prompt completo (especificações do
`prompt-videos-v11.md`) roda na janela do subagent — não polui o
chat principal.

| Subagent | Prompt fonte | Model | MCP Tools |
|---|---|---|---|
| `yt-performance` | `performance.md` | `inherit` | VidIQ + YouTube |
| `yt-competitive` | `competitive.md` | `inherit` | VidIQ + YouTube |
| `yt-validation` | `validation.md` | `inherit` | VidIQ |
| `yt-metadata` | `metadata.md` | `inherit` | VidIQ |
| `yt-scriptwriter` | `scriptwriter.md` | `inherit` | Nenhum |
| `yt-qa` | `qa.md` | `inherit` | Nenhum |
| `yt-repackaging` | `repackaging.md` | `inherit` | VidIQ + YouTube |

**Localização:** `.cursor/agents/{nome}.md`

#### Vantagens do isolamento

- O prompt de 300+ linhas do repackaging roda em janela separada
- O chat principal só recebe o resultado final (summary)
- Múltiplos subagents podem rodar em paralelo
- Cada subagent herda automaticamente os MCP servers configurados

### Componente 3 — Hooks (Memória e Automação)

Hooks são scripts executados automaticamente em eventos do ciclo de
vida do agente. Dois hooks implementam a memória persistente:

| Hook | Evento | Script | Função |
|---|---|---|---|
| Injetar memória | `sessionStart` | `inject-memory.py` | Lê SQLite e injeta `additional_context` com estado do canal |
| Persistir resultados | `subagentStop` | `save-to-db.py` | Captura `summary` do subagent e salva no SQLite |

**Localização:** `.cursor/hooks.json` + `.cursor/hooks/`

#### Banco de dados (SQLite)

O hook Python usa SQLite para persistir memória entre sessões.
Schema das tabelas:

```sql
-- Execuções dos subagents
CREATE TABLE agent_runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type    TEXT NOT NULL,       -- ex: 'yt-performance', 'yt-repackaging'
    video_topic   TEXT,                -- tema do vídeo (quando aplicável)
    video_id      TEXT,                -- ID do vídeo (quando aplicável)
    summary       TEXT NOT NULL,       -- output completo do subagent
    status        TEXT DEFAULT 'completed',
    created_at    TEXT NOT NULL
);

-- Baseline do canal (atualizado pela Fase P)
CREATE TABLE channel_baseline (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    avg_views         REAL,
    avg_retention_pct REAL,
    avg_like_ratio    REAL,
    avg_comments      REAL,
    total_videos      INTEGER,
    updated_at        TEXT NOT NULL
);

-- Histórico de vídeos analisados
CREATE TABLE video_history (
    id                TEXT PRIMARY KEY,  -- YouTube video ID
    title             TEXT,
    published_at      TEXT,
    views             INTEGER,
    avg_retention_pct REAL,
    like_ratio_pct    REAL,
    comments          INTEGER,
    subscribers_gained INTEGER,
    last_analyzed_at  TEXT
);

-- Histórico de thumbnails (para regra de alternância)
CREATE TABLE thumbnail_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id      TEXT,
    aesthetic     TEXT,     -- 'documental_sombria' ou 'ficcao_cientifica'
    composition   TEXT,     -- 'A', 'B' ou 'C'
    dominant_color TEXT,
    accent_color  TEXT,
    expression    TEXT,     -- expressão facial usada
    created_at    TEXT
);

-- Cache de keyword research (evita chamadas repetidas)
CREATE TABLE keyword_cache (
    keyword       TEXT PRIMARY KEY,
    volume        REAL,
    competition   REAL,
    overall       REAL,
    related_json  TEXT,     -- JSON com keywords relacionadas
    cached_at     TEXT
);
```

**Localização do banco:** `data/memory.db`

#### Dados injetados pelo `sessionStart`

O hook `inject-memory.py` injeta automaticamente no início de cada
sessão:

```
## Channel Memory (auto-loaded)

### Baseline do canal
- Views médias: 150 | Retenção: 32% | Like ratio: 4.2%

### Último diagnóstico (Fase P)
- Vídeo: "título" | Views: 45 | Retenção: 28%
- Calibrações: [lista]

### Última thumbnail
- Estética: Ficção Científica | Composição: B | Paleta: Azul #0A1628
- (próxima deve usar estética diferente)

### Último sub-nicho
- IA + Medicina (próximo deve ser diferente)

### Keywords recentes com volume
- "agentes de ia" (vol: 77) | "automação com ia" (vol: 45)
```

---

## Fluxo de Execução

### Pipeline Completo

```
Usuário: /yt-pipeline "IA na cirurgia robótica"
                         │
                    Skill yt-pipeline
                    (orquestra as fases)
                         │
        ┌────────────────┼────────────────┐
        ▼                                 ▼
   Subagent                          Subagent
   yt-performance                    yt-competitive
   │                                 │
   ├─ Lê: SQLite (baseline)         ├─ Chama: VidIQ outliers
   ├─ Chama: VidIQ video_stats      ├─ Chama: VidIQ trending
   ├─ Chama: YT analytics           ├─ Chama: VidIQ transcript
   ├─ Gera diagnóstico              ├─ Chama: VidIQ comments
   └─ Hook salva no SQLite          └─ Hook salva no SQLite
        │                                 │
        └────────────┬────────────────────┘
                     │  (resultados de P e 0
                     │   passados como contexto)
                     ▼
               Subagent yt-validation
               │
               ├─ Chama: VidIQ keyword_research
               ├─ Avalia: volume, competition, overall
               ├─ Checklist de Ouro (3 itens)
               └─ Verdict: approved / low_demand / rejected
                     │
                     ▼ (se approved)
               Subagent yt-metadata
               │
               ├─ Recebe: dados de P + 0 + V
               ├─ Gera: 10 títulos (6 fórmulas)
               ├─ Chama: VidIQ keyword_research (validar títulos)
               ├─ Gera: thumbnail prompt (7 seções)
               ├─ Gera: descrição SEO (250-400 palavras)
               ├─ Gera: 8-12 tags com volume
               ├─ Gera: post comunidade
               └─ Hook salva no SQLite + thumbnail_history
                     │
                     ▼
               Subagent yt-scriptwriter
               │
               ├─ Recebe: metadados + calibrações P + briefing 0
               ├─ Aplica: 7 Princípios do DNA Narrativo
               ├─ Escreve: Hook → Contexto → 4 Blocos → CTA
               ├─ Gera: VISUALs (Camada Visual Permanente)
               ├─ Mapeia: open loops + pattern interrupts
               └─ Gera: mapa de open loops
                     │
                     ▼
               Subagent yt-qa
               │
               ├─ Recebe: metadados + roteiro completo
               ├─ Executa: 28 itens da checklist
               ├─ Verdict: approved / needs_fix / approved_with_warnings
               └─ Se needs_fix: gera fix_instructions
                     │
                     ▼
               Output salvo em:
               output/videos/ia-cirurgia-robotica/
               ├── 01-performance.md
               ├── 02-competitive.md
               ├── 03-validation.md
               ├── 04-metadata.md
               ├── 05-script.md
               ├── 06-qa-report.md
               └── FINAL.md (consolidado)
```

### Repackaging (Fase R)

```
Usuário: /yt-repackaging daK_7PofxMU
                    │
              Skill yt-repackaging
                    │
              Subagent yt-repackaging
              │
              ├─ Lê: SQLite (baseline + thumbnail_history)
              ├─ Chama: VidIQ video_stats
              ├─ Chama: YouTube get_video_analytics
              ├─ Chama: VidIQ channel_videos (baseline)
              ├─ Diagnostica: armadilha do título + problemas da thumb
              ├─ Chama: VidIQ keyword_research (2-3 keywords)
              ├─ Gera: 3-5 títulos (6 fórmulas + reframes)
              ├─ Gera: thumbnail prompt (7 seções, estética alternada)
              ├─ Gera: descrição SEO (template completo)
              ├─ Gera: 8-12 tags (todas com volume > 0)
              └─ Hook salva no SQLite + output/repackaging/
```

### Execução Avulsa (fase individual)

Qualquer fase pode ser executada isoladamente:

```
/yt-performance                              → só diagnóstico
/yt-competitive "quantum computing"          → só análise competitiva
/yt-validation "computação quântica"         → só validação de keyword
/yt-metadata "computação quântica"           → só metadados
```

---

## Estrutura de Arquivos

```
.cursor/
├── agents/                              ← Subagents (especialistas)
│   ├── yt-performance.md                   Fase P — diagnóstico
│   ├── yt-competitive.md                   Fase 0 — análise competitiva
│   ├── yt-validation.md                    Fase V — validação de tema
│   ├── yt-metadata.md                      Metadados (títulos, thumb, etc.)
│   ├── yt-scriptwriter.md                  Roteiro completo
│   ├── yt-qa.md                            Checklist de 28 itens
│   └── yt-repackaging.md                   Fase R — repackaging
│
├── skills/                              ← Skills (commands do usuário)
│   ├── yt-pipeline/
│   │   └── SKILL.md                        Orquestra pipeline completo
│   ├── yt-repackaging/
│   │   └── SKILL.md                        Repackaging de vídeo
│   ├── yt-performance/
│   │   └── SKILL.md                        Diagnóstico avulso
│   ├── yt-competitive/
│   │   └── SKILL.md                        Competitiva avulso
│   ├── yt-validation/
│   │   └── SKILL.md                        Validação avulso
│   ├── yt-metadata/
│   │   └── SKILL.md                        Metadados avulso
│   ├── yt-scriptwriter/
│   │   └── SKILL.md                        Roteiro avulso
│   └── yt-qa/
│       └── SKILL.md                        QA avulso
│
├── hooks.json                           ← Configuração dos hooks
└── hooks/                               ← Scripts de automação
    ├── inject-memory.py                    sessionStart → lê SQLite
    └── save-to-db.py                       subagentStop → persiste SQLite

data/
└── memory.db                            ← SQLite (memória persistente)

output/                                  ← Resultados gerados
├── videos/                                 Pipeline completo
│   └── {slug-do-tema}/
│       ├── 01-performance.md
│       ├── 02-competitive.md
│       ├── 03-validation.md
│       ├── 04-metadata.md
│       ├── 05-script.md
│       ├── 06-qa-report.md
│       └── FINAL.md
└── repackaging/                            Repackaging avulso
    └── {video_id}_{timestamp}.md
```

---

## Configuração dos Hooks

### `.cursor/hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "command": "python3 .cursor/hooks/inject-memory.py"
      }
    ],
    "subagentStop": [
      {
        "command": "python3 .cursor/hooks/save-to-db.py",
        "matcher": "yt-performance|yt-competitive|yt-validation|yt-metadata|yt-scriptwriter|yt-qa|yt-repackaging"
      }
    ]
  }
}
```

### `inject-memory.py` — Comportamento

1. Lê `data/memory.db`
2. Busca: baseline do canal, último diagnóstico, última thumbnail,
   último sub-nicho, keywords recentes
3. Formata como Markdown
4. Retorna `{"additional_context": "..."}`

### `save-to-db.py` — Comportamento

1. Recebe JSON via stdin com `subagent_type`, `summary`, `status`
2. Só processa se `status == "completed"`
3. Insere em `agent_runs`
4. Se `subagent_type == "yt-performance"`: atualiza `channel_baseline`
5. Se `subagent_type == "yt-metadata"`: insere em `thumbnail_history`
6. Retorna `{}`

---

## Dependências Externas

### MCP Servers (já configurados)

| Server | Protocolo | Função |
|---|---|---|
| `project-0-yt-vidIQ` | Streamable HTTP | Keyword research, video stats, channel analytics, outliers, trending, transcripts, comments |
| `project-0-yt-youtube` | stdio | YouTube Data API, Analytics API, Studio API |

Os subagents herdam acesso a ambos automaticamente.

### Python (para hooks)

Os hooks usam Python 3 com `sqlite3` (stdlib — sem dependências
externas). Nenhum `pip install` necessário.

---

## Comparação com ADR-001 (yt-agent CLI)

| Aspecto | ADR-001 (yt-agent CLI) | ADR-002 (Cursor Subagents) |
|---|---|---|
| **Custo por execução** | ~$4-5 (API tokens) | $0 (assinatura Cursor) |
| **Qualidade do output** | Claude Sonnet/Opus | Claude Sonnet/Opus |
| **MCP tools** | VidIQ + YouTube | VidIQ + YouTube (herdados) |
| **Memória persistente** | SQLAlchemy + SQLite | Hooks + SQLite |
| **Paralelismo** | Não (sequencial) | Sim (subagents paralelos) |
| **Human-in-the-loop** | `interrupt()` LangGraph | Natural (revisa entre fases) |
| **Orquestração** | Automática (1 comando CLI) | Semi-automática (skill orquestra) |
| **Manutenção** | Python, deps, pyproject | Arquivos .md + 2 scripts Python |
| **Checkpoint/retomar** | LangGraph checkpointer | Dados no SQLite, reexecuta fase |
| **Execução headless** | Sim (cron/CI) | Não (requer Cursor aberto) |
| **Infra** | Python 3.13, pip, venv | Cursor instalado |

### O que se ganha

- **Custo zero de API** — diferença de ~$100-240/mês
- **Paralelismo** — Fase P e Fase 0 rodam simultaneamente
- **Simplicidade** — sem gerenciamento de Python env/deps
- **Visibilidade** — subagents mostram progresso no Cursor IDE
- **Intervenção natural** — revisão humana entre fases sem código

### O que se perde

- **Automação total** — precisa do Cursor aberto e interação manual
- **Execução headless** — não roda em cron/CI (se necessário no
  futuro, o `yt-agent` CLI permanece como alternativa)
- **Checkpoint granular** — se o chat fechar, reexecuta a fase
  (dados anteriores persistem no SQLite)

---

## Decisão

Adotar a **ADR-002** como abordagem principal para uso diário do
pipeline. A **ADR-001** (yt-agent CLI) permanece disponível como
alternativa para cenários de automação total ou execução headless,
caso o custo de API se torne viável no futuro.

### Próximos Passos

1. Criar os 7 subagents em `.cursor/agents/`
2. Criar as 8 skills em `.cursor/skills/`
3. Configurar hooks (`hooks.json` + 2 scripts Python)
4. Inicializar o schema SQLite em `data/memory.db`
5. Testar o fluxo completo com `/yt-repackaging` (fase mais simples)
6. Testar o pipeline completo com `/yt-pipeline`
7. Documentar no README do projeto

---

## Referências

- [Cursor Subagents](https://cursor.com/docs/subagents)
- [Cursor Skills](https://cursor.com/docs/skills)
- [Cursor Hooks](https://cursor.com/docs/hooks)
- [ADR-001: yt-agent CLI](./001-agentic-workflow-langgraph.md)
- [Prompt Videos v11](../../canais/marcus-maciel/prompts/prompt-videos-v11.md)
