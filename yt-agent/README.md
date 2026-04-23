# YT-Agent

Agentic workflow para produção de vídeos YouTube — powered by **LangGraph** + **Claude** (Anthropic).

Transforma o processo manual de criação de vídeos em um pipeline inteligente de 7 agentes que colaboram para gerar: diagnóstico de performance, análise competitiva, validação de tema, metadados (títulos, thumbnail, SEO, tags), roteiro completo, e validação de qualidade (QA).

---

## Arquitetura

O workflow é orquestrado como um **StateGraph** (LangGraph):

```
START → Agent P → decide_p
          ├─ ok → Agent 0 → Agent V → decide_tema
          │                               ├─ ok → Agent Meta → Roteirista → QA → decide_qa
          │                               │                                       ├─ pass → Save Memory → Render → END
          │                               │                                       └─ fail → Fix → QA (loop, max 2)
          │                               └─ low_demand → [Human] → Agent Meta → ...
          └─ low_retention → [Human] → Agent 0 → ...
```

### Agentes

| Agente | Modelo | Função |
|---|---|---|
| **Agent P** | Sonnet | Diagnóstico de performance do último vídeo |
| **Agent 0** | Sonnet | Análise competitiva (outliers, erros, ângulos inexplorados) |
| **Agent V** | Sonnet | Validação de tema via keyword research |
| **Agent Meta** | Sonnet | Geração de metadados (títulos, thumbnail, tags, SEO) |
| **Roteirista** | Opus | Escrita do roteiro completo |
| **Agent QA** | Sonnet | Checklist de 28 itens de validação |
| **Agent R** | Sonnet | Repackaging de vídeos com baixo desempenho |

---

## Instalação

### Pré-requisitos

- Python 3.12+
- API Key do [Anthropic](https://console.anthropic.com/) (Claude)
- (Opcional) API Key do [VidIQ](https://vidiq.com/)
- (Opcional) YouTube OAuth Token

### Setup

```bash
cd yt-agent
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

pip install -e ".[dev]"
```

### Configuração

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
# Obrigatório
ANTHROPIC_API_KEY=sk-ant-...

# Opcionais (workflow completo precisa de pelo menos um)
VIDIQ_API_KEY=your-vidiq-key
YOUTUBE_OAUTH_TOKEN=your-oauth-token

# Database (padrão: SQLite local)
DATABASE_URL=sqlite+aiosqlite:///data/yt_agent.db

# Caminhos para prompts e modelos de escrita
PROMPT_DIR=../canais/marcus-maciel/prompts/
MODELS_DIR=../canais/marcus-maciel/modelos-de-escrita/
```

---

## Comandos

### `yt-agent new` — Criar novo workflow

```bash
yt-agent new \
  --topic "Como a IA está revolucionando diagnósticos médicos" \
  --sub-niche "IA + Medicina/Saúde" \
  --format long \
  --angle revelador \
  --emotion "Admiração" \
  --detail intermediate \
  --period "2025-2026" \
  --notes "Focar em casos reais brasileiros" \
  --verbose
```

| Opção | Padrão | Descrição |
|---|---|---|
| `--topic`, `-t` | *(obrigatório)* | Tema do vídeo |
| `--sub-niche`, `-s` | *(obrigatório)* | Sub-nicho do canal |
| `--format`, `-f` | `long` | Formato: `long` ou `short` |
| `--angle`, `-a` | `revelador` | Ângulo editorial |
| `--emotion`, `-e` | `Admiração` | Emoção dominante |
| `--detail`, `-d` | `intermediate` | Nível técnico: `basic`, `intermediate`, `advanced` |
| `--period`, `-p` | `2025-2026` | Período de referência |
| `--notes`, `-n` | `None` | Notas de contexto adicionais |
| `--verbose`, `-v` | `False` | Ativar logging detalhado |

O output final é salvo em `output/<run-id>.md`.

### `yt-agent resume` — Retomar workflow pausado

Quando o workflow pausa para uma decisão humana (retenção baixa ou tema com baixa demanda):

```bash
yt-agent resume --run-id <run-id> --input "1"
```

Opções de input:
- `1` — Continuar com o fluxo padrão
- `2` — Alternativa sugerida
- `3` — Mudar de tema/ação

### `yt-agent history` — Ver histórico

```bash
# Últimos workflow runs
yt-agent history

# Vídeos na memória do canal (thumbnail, views, retenção)
yt-agent history --videos
```

### `yt-agent repackage` — Repackaging de vídeos

```bash
# Listar candidatos a repackaging
yt-agent repackage --check

# Gerar proposta para um vídeo específico
yt-agent repackage --video-id <video-id>
```

Critérios de candidatura:
- Publicado há 5+ dias
- Views em 7 dias < 50% da média do canal
- Retenção > 25%

### `yt-agent update-metrics` — Atualizar métricas

```bash
yt-agent update-metrics \
  --video-id "draft-20260419-143000" \
  --views 1200 \
  --retention 38.5 \
  --like-ratio 9.2
```

### `yt-agent version` — Versão

```bash
yt-agent version
```

---

## Custo estimado

Cada execução completa do workflow consome aproximadamente:

| Agente | Modelo | Tokens (entrada/saída) | Custo estimado |
|---|---|---|---|
| Agent P | Sonnet | ~8K / ~2K | ~$0.04 |
| Agent 0 | Sonnet | ~12K / ~3K | ~$0.06 |
| Agent V | Sonnet | ~4K / ~1K | ~$0.02 |
| Agent Meta | Sonnet | ~8K / ~3K | ~$0.05 |
| Roteirista | Opus | ~10K / ~6K | ~$0.30 |
| Agent QA | Sonnet | ~12K / ~2K | ~$0.06 |
| **Total** | | | **~$0.53** |

Valores aproximados com base nos preços de Abril 2026 ($3/MTok input, $15/MTok output para Sonnet; $15/MTok input, $75/MTok output para Opus).

---

## Resiliência e Error Handling

O sistema é projetado para funcionar mesmo com falhas parciais:

- **Retry com backoff exponencial** (2s → 4s → 8s) em chamadas à API Anthropic para erros transitórios (timeout, 429, 5xx, 529).
- **JSON parse retry**: se o LLM retorna JSON inválido, re-envia a mensagem com o erro Pydantic como feedback (max 2 retries).
- **Timeouts**: VidIQ (30s), YouTube (60s), Sonnet (60s), Opus (120s).
- **Graceful degradation**: se qualquer agente falha, o workflow continua com `None` no slot correspondente. Agentes downstream adaptam-se à ausência de dados. Erros são acumulados em `state["errors"]` e aparecem no output final.

---

## System Prompts

Os prompts de cada agente estão em `src/yt_agent/prompts/`:

```
prompts/
├── performance.md      # Agent P — Diagnóstico de Performance
├── competitive.md      # Agent 0 — Análise Competitiva
├── validation.md       # Agent V — Validação de Tema
├── metadata.md         # Agent Meta — Metadados
├── scriptwriter.md     # Roteirista — Escrita do Roteiro
├── qa.md               # Agent QA — Checklist de Validação
└── repackaging.md      # Agent R — Repackaging
```

Para customizar o comportamento de qualquer agente, basta editar o `.md` correspondente. Não é necessário alterar código Python.

---

## Testes

```bash
# Todos os testes
pytest -v

# Apenas testes dos agentes
pytest tests/test_agents/ -v

# Apenas testes de integração do grafo
pytest tests/test_graph.py -v

# Com coverage
pytest --cov=yt_agent -v
```

---

## Estrutura do projeto

```
yt-agent/
├── src/yt_agent/
│   ├── agents/           # Implementação dos 7 agentes
│   │   ├── base.py       # Utilitários compartilhados (retry, JSON parse)
│   │   ├── performance.py
│   │   ├── competitive.py
│   │   ├── validation.py
│   │   ├── metadata.py
│   │   ├── scriptwriter.py
│   │   ├── qa.py
│   │   └── repackaging.py
│   ├── memory/           # Persistência (SQLAlchemy + SQLite)
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── database.py
│   ├── tools/            # Clientes API (VidIQ, YouTube)
│   │   ├── vidiq.py
│   │   ├── youtube.py
│   │   └── schemas.py
│   ├── prompts/          # System prompts dos agentes
│   ├── output/           # Renderer (Markdown)
│   ├── graph.py          # LangGraph StateGraph
│   ├── state.py          # Pydantic schemas + WorkflowState
│   ├── config.py         # Pydantic Settings
│   └── main.py           # CLI (Typer)
├── tests/
├── docs/
│   ├── adr/              # Architecture Decision Record
│   └── roadmap/          # Development roadmap
├── pyproject.toml
└── .env.example
```
