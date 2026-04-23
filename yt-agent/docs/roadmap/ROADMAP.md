# ROADMAP — YT-Agent: Agentic Workflow para Produção de Vídeos

**Referência:** [ADR-001](../adr/001-agentic-workflow-langgraph.md)
**Criado em:** 2026-04-19
**Estimativa total:** 9–14 dias de desenvolvimento
**Metodologia:** Entregas incrementais — cada sprint produz um artefato
testável e funcional. Nenhuma sprint depende de código incompleto da
anterior.

---

## Visão geral das Sprints

| Sprint | Nome | Duração | Entregável principal | Dependência |
|---|---|---|---|---|
| **S1** | Foundation | 2–3 dias | Projeto rodando, CLI responde, DB criado, APIs conectadas | Nenhuma |
| **S2** | Agentes de Pesquisa | 2–3 dias | Agentes P, 0 e V funcionais isoladamente com output JSON | S1 |
| **S3** | Agentes de Produção | 2–3 dias | Agentes Meta, Roteirista e QA funcionais isoladamente | S1 |
| **S4** | Orquestração | 2–3 dias | Grafo LangGraph completo com human-in-the-loop e output final | S2, S3 |
| **S5** | Memória e Repackaging | 1–2 dias | Channel memory funcional, Agente R, comandos extras | S4 |
| **S6** | Testes e Hardening | 1–2 dias | Suite de testes, error handling robusto, documentação | S5 |

```
S1 ─────▶ S2 ──┐
         ▶ S3 ──┤──▶ S4 ──▶ S5 ──▶ S6
                │
          (S2 e S3 podem rodar em paralelo)
```

---

## Sprint 1 — Foundation

**Objetivo:** Projeto Python funcional com CLI, configuração, banco de
dados e wrappers de API — sem nenhum agente LLM ainda.

**Duração estimada:** 2–3 dias

### Tarefas

#### 1.1 — Setup do projeto

| Tarefa | Arquivo(s) | Detalhes |
|---|---|---|
| Criar `pyproject.toml` | `pyproject.toml` | Python 3.12+. Dependências: `langgraph`, `langchain-anthropic`, `langchain-core`, `httpx`, `pydantic>=2.0`, `pydantic-settings`, `typer[all]`, `rich`, `sqlalchemy>=2.0`, `ruff`. Dev: `pytest`, `pytest-asyncio`, `pytest-mock`, `respx` (mock HTTP). |
| Criar `.env.example` | `.env.example` | `ANTHROPIC_API_KEY=`, `VIDIQ_API_KEY=`, `YOUTUBE_OAUTH_TOKEN=`, `DATABASE_URL=sqlite:///data/yt_agent.db`, `PROMPT_DIR=../canais/marcus-maciel/prompts/`, `MODELS_DIR=../canais/marcus-maciel/modelos-de-escrita/` |
| Criar `.gitignore` | `.gitignore` | `.env`, `__pycache__`, `*.pyc`, `.ruff_cache`, `data/`, `dist/`, `.venv/` |
| Criar estrutura de diretórios | `src/yt_agent/` e subpastas | Conforme ADR: `agents/`, `tools/`, `memory/`, `prompts/`, `output/` |
| Criar `__init__.py` em todos os pacotes | `src/yt_agent/**/__init__.py` | Arquivos vazios |

**Critério de done:** `pip install -e .` funciona sem erros.

---

#### 1.2 — Configuração (Pydantic Settings)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar `Settings` | `src/yt_agent/config.py` | Classe `Settings(BaseSettings)` com: `anthropic_api_key: SecretStr`, `vidiq_api_key: SecretStr`, `youtube_oauth_token: SecretStr`, `database_url: str`, `prompt_dir: Path`, `models_dir: Path`, `sonnet_model: str = "claude-sonnet-4-20250514"`, `opus_model: str = "claude-opus-4-20250514"`. Carregar de `.env`. |
| Função `get_settings()` | `src/yt_agent/config.py` | Singleton com `@lru_cache`. |

**Critério de done:** `python -c "from yt_agent.config import get_settings; print(get_settings().database_url)"` imprime o valor correto.

---

#### 1.3 — Modelos Pydantic (Schemas dos agentes)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Definir todos os schemas de output | `src/yt_agent/state.py` | Implementar como Pydantic `BaseModel`: `PerformanceDiagnosis`, `CompetitiveBriefing`, `ThemeValidation`, `VideoMetadata`, `Script`, `QAReport`, `RepackagingProposal`, `HumanDecision`. Cada campo tipado conforme os JSON schemas da ADR. |
| Definir `WorkflowState` | `src/yt_agent/state.py` | `TypedDict` com todos os campos de input do usuário + outputs dos agentes + campos de controle de fluxo (`qa_attempt`, `current_phase`, `errors`, `human_decisions`). |

**Critério de done:** Instanciar cada model com dados dummy sem erro de validação. Serializar e deserializar para JSON.

---

#### 1.4 — Banco de dados (SQLite + SQLAlchemy)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Definir modelos ORM | `src/yt_agent/memory/models.py` | 3 tabelas conforme ADR: `Video`, `TagPerformance`, `WorkflowRun`. Usar SQLAlchemy 2.0 (mapped_column). |
| Implementar repository | `src/yt_agent/memory/repository.py` | Classe `ChannelMemory` com métodos: `get_last_video() → Video | None`, `get_last_n_videos(n) → list[Video]`, `save_video(video)`, `get_tags_by_performance() → list[TagPerformance]`, `save_workflow_run(run)`, `update_workflow_run(run_id, **kwargs)`. |
| Criar engine e session factory | `src/yt_agent/memory/__init__.py` | `create_engine(settings.database_url)`, `Session = sessionmaker(...)`. Auto-create tables on first run. |

**Critério de done:** Teste que cria um `Video`, salva, recupera com `get_last_video()`, e valida os campos.

---

#### 1.5 — Wrappers de API (VidIQ + YouTube)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Wrapper VidIQ | `src/yt_agent/tools/vidiq.py` | Classe `VidIQClient(httpx.AsyncClient)` com métodos tipados: `keyword_research(keyword, include_related) → KeywordResult`, `outliers(keyword, content_type, published_within, sort, limit) → list[OutlierVideo]`, `trending_videos(video_format, title_query, sort_by, limit) → list[TrendingVideo]`, `video_transcript(video_id) → str`, `video_comments(video_id) → list[Comment]`, `video_stats(video_id, granularity) → VideoStats`, `user_channels() → list[Channel]`, `channel_videos(channel_id, video_format, popular) → list[ChannelVideo]`, `channel_analytics(channel_id, start_date, metrics, dimensions, filters) → AnalyticsResult`, `channel_performance_trends(channel_id) → PerformanceTrends`. Cada resposta mapeada para Pydantic model. |
| Wrapper YouTube | `src/yt_agent/tools/youtube.py` | Classe `YouTubeClient(httpx.AsyncClient)` com métodos: `search_videos(query, duration, published_after, max_results) → list[SearchResult]`, `get_video(video_id) → VideoDetail`, `get_transcript(video_id) → str`, `list_own_videos(status, max_results) → list[OwnVideo]`, `get_video_analytics(video_id, metrics) → AnalyticsResult`, `get_channel_analytics(start_date, metrics) → AnalyticsResult`, `get_top_videos(max_results) → list[TopVideo]`. |
| Registrar como LangChain tools | `src/yt_agent/tools/__init__.py` | Converter cada método para `@tool` do LangChain para que agentes possam invocá-los. Agrupar por agente: `performance_tools`, `competitive_tools`, `validation_tools`, `metadata_tools`, `repackaging_tools`. |

**Critério de done:** Teste de integração (com API real) que chama `vidiq.keyword_research("inteligência artificial")` e retorna dados. Teste unitário com `respx` mock que valida a deserialização.

---

#### 1.6 — CLI básica (Typer)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar CLI | `src/yt_agent/main.py` | Comandos: `new` (com todas as flags do WorkflowState input), `resume --run-id`, `repackage --check / --video-id`, `history`, `update-metrics --video-id`. Cada comando por enquanto imprime "Not implemented yet — Sprint X" com Rich formatting. O comando `new` deve validar os inputs via Pydantic e salvar um `WorkflowRun` com status "created". |
| Entry point | `pyproject.toml` | `[project.scripts] yt-agent = "yt_agent.main:app"` |

**Critério de done:** `yt-agent new --topic "teste" --sub-niche "IA + Medicina/Saúde" --format long --angle revelador --emotion "Admiração" --detail intermediário --period "2025-2026"` cria um registro no SQLite e imprime o run_id.

---

### Milestone S1: Projeto funcional

```
✅ pip install -e . funciona
✅ .env carregada e validada
✅ Todos os Pydantic models instanciáveis
✅ SQLite criado com 3 tabelas
✅ VidIQ e YouTube wrappers respondem (teste de integração)
✅ CLI cria WorkflowRun no banco
```

---

## Sprint 2 — Agentes de Pesquisa (P, 0, V)

**Objetivo:** Implementar os 3 agentes que coletam dados ANTES da
produção de conteúdo. Cada agente funcional isoladamente.

**Duração estimada:** 2–3 dias

**Nota:** Pode rodar em paralelo com S3 se houver capacidade.

### Tarefas

#### 2.1 — Extração de system prompts

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Extrair prompt do Agente P | `src/yt_agent/prompts/performance.md` | Extrair da seção FASE P do `prompt-videos-v11.md` (linhas ~611–782). Incluir o template de output, regras de fallback, e os 4 passos do processo. Adaptar referências cruzadas para serem autocontidas. |
| Extrair prompt do Agente 0 | `src/yt_agent/prompts/competitive.md` | Extrair da seção FASE 0 (linhas ~786–910) + CREDIBILIDADE CIENTÍFICA (linhas ~193–248). Incluir passos 1-5, template do briefing, manifesto de diferenciação. |
| Extrair prompt do Agente V | `src/yt_agent/prompts/validation.md` | Extrair da Validação do Tema dentro de METADADOS (linhas ~918–924). Incluir o Checklist de Ouro (3 perguntas). |

**Critério de done:** Cada arquivo `.md` é autocontido — um agente que receba apenas esse prompt sabe exatamente o que fazer.

---

#### 2.2 — Agente P (Diagnóstico de Performance)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar nó do agente | `src/yt_agent/agents/performance.py` | Função `async def run_performance_agent(state: WorkflowState) → dict`: (1) carrega system prompt de `prompts/performance.md`, (2) chama Claude Sonnet com as tools de performance, (3) parseia output para `PerformanceDiagnosis` via Pydantic, (4) retry até 2x se JSON inválido, (5) retorna `{"performance_diagnosis": diagnosis, "current_phase": "fase_p_done"}`. |
| Implementar nó de decisão | `src/yt_agent/agents/performance.py` | Função `def decide_after_performance(state: WorkflowState) → str`: retorna `"ok"` se `alert != "low_retention"`, `"low_retention"` caso contrário. |

**Critério de done:** Executar o agente com dados reais do canal → output `PerformanceDiagnosis` válido com calibrações concretas.

---

#### 2.3 — Agente 0 (Análise Competitiva)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar nó do agente | `src/yt_agent/agents/competitive.py` | Função `async def run_competitive_agent(state: WorkflowState) → dict`: (1) carrega system prompt, (2) usa `video_topic` do state + idiomas PT/EN, (3) chama Claude Sonnet com tools de competição, (4) parseia para `CompetitiveBriefing`, (5) retorna `{"competitive_briefing": briefing, "current_phase": "fase_0_done"}`. |

**Critério de done:** Executar com tema "cirurgia robótica IA" → retorna 3+ concorrentes, 3 erros, 3 ângulos, manifesto.

---

#### 2.4 — Agente V (Validação de Tema)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar nó do agente | `src/yt_agent/agents/validation.py` | Função `async def run_validation_agent(state: WorkflowState) → dict`: (1) carrega system prompt, (2) usa `video_topic` + keyword extraída, (3) chama `vidiq_keyword_research`, (4) parseia para `ThemeValidation`, (5) retorna `{"theme_validation": validation, "current_phase": "validation_done"}`. |
| Implementar nó de decisão | `src/yt_agent/agents/validation.py` | Função `def decide_after_validation(state: WorkflowState) → str`: retorna `"ok"` se `verdict == "approved"`, `"low_demand"` caso contrário. |

**Critério de done:** Executar com tema de volume zero → retorna `verdict: "low_demand"` com alternativas.

---

### Milestone S2: Pesquisa funcional

```
✅ Agente P gera PerformanceDiagnosis válido
✅ Agente P detecta low_retention corretamente
✅ Agente 0 gera CompetitiveBriefing com concorrentes reais
✅ Agente V valida temas com volume e detecta low_demand
✅ Cada agente roda isoladamente via função Python
✅ 3 system prompts extraídos e autocontidos
```

---

## Sprint 3 — Agentes de Produção (Meta, Roteirista, QA)

**Objetivo:** Implementar os 3 agentes que produzem o conteúdo final.
Cada agente funcional isoladamente.

**Duração estimada:** 2–3 dias

**Nota:** Pode rodar em paralelo com S2.

### Tarefas

#### 3.1 — Extração de system prompts

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Extrair prompt do Agente Meta | `src/yt_agent/prompts/metadata.md` | Extrair de: seção METADADOS (linhas ~918–1146) — títulos (6 fórmulas, armadilhas, validação VidIQ), thumbnail (2 estéticas, 3 composições, paletas, text overlay, anti-padrões), post comunidade, hashtags, tags, descrição SEO (template completo com capítulos). ~600 linhas. |
| Extrair prompt do Agente Roteirista | `src/yt_agent/prompts/scriptwriter.md` | Extrair e unificar de: VOZ E TOM (~180 linhas) + DNA NARRATIVO 7 Princípios (~130 linhas) + ESCRITA VOZ-OVER (~70 linhas) + CAMADA DE RETENÇÃO (~80 linhas) + CTAs NA NARRAÇÃO (~40 linhas) + ESTRUTURA DO ROTEIRO (hook, contexto, desenvolvimento, loops, CTA final, ~200 linhas). ~700 linhas. Incluir INSTRUÇÕES DE PRIORIDADE no topo. |
| Extrair prompt do Agente QA | `src/yt_agent/prompts/qa.md` | Extrair de: CHECKLIST DE VALIDAÇÃO (28 itens) + INSTRUÇÕES DE PRIORIDADE. ~50 linhas. Adicionar instrução: "Se failures >= 3, gerar fix_instructions específicas referenciando os itens que falharam." |

**Critério de done:** Cada prompt autocontido. O Roteirista não precisa saber nada sobre Fase P ou Fase 0 — recebe as calibrações/briefing como input, não como prompt.

---

#### 3.2 — Agente Meta (Metadados)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar nó do agente | `src/yt_agent/agents/metadata.py` | Função `async def run_metadata_agent(state: WorkflowState) → dict`: (1) carrega system prompt, (2) consulta `ChannelMemory` para últimas thumbnails (estética, composição, paleta, expressão), (3) injeta no prompt as regras de alternância + dados do `CompetitiveBriefing` + `ThemeValidation`, (4) chama Claude Sonnet com tool `vidiq_keyword_research`, (5) parseia para `VideoMetadata`, (6) retorna. |
| Lógica de alternância | `src/yt_agent/agents/metadata.py` | Função auxiliar `get_alternation_constraints(memory: ChannelMemory) → dict` que retorna: `last_aesthetic`, `last_composition`, `last_palette`, `last_expression`, `last_sub_niche`. Injetado no prompt do agente como contexto. |

**Critério de done:** Executar com briefing + validação de tema real → retorna 10 títulos (todos ≤55 chars), thumbnail prompt em inglês, descrição com template completo, tags com tabela de volume.

---

#### 3.3 — Agente Roteirista

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar nó do agente | `src/yt_agent/agents/scriptwriter.py` | Função `async def run_scriptwriter_agent(state: WorkflowState) → dict`: (1) carrega system prompt (~700 linhas), (2) carrega 1 modelo de escrita de `models_dir`, (3) constrói o user message com: campos variáveis + `PerformanceDiagnosis.calibrations` + `CompetitiveBriefing` resumido (manifesto + top ângulos + top erros) + `VideoMetadata.titles.top_3[0]` como título escolhido, (4) chama **Claude Opus**, (5) parseia para `Script`, (6) retorna. |
| Implementar nó de correção | `src/yt_agent/agents/scriptwriter.py` | Função `async def run_scriptwriter_fix(state: WorkflowState) → dict`: recebe o `QAReport.fix_instructions` do state e reescreve as seções problemáticas. Incrementa `qa_attempt`. |
| Loader de modelos de escrita | `src/yt_agent/agents/scriptwriter.py` | Função `load_writing_model(models_dir: Path) → str`: lê um arquivo `.md` aleatório da pasta de modelos e retorna o conteúdo. |

**Critério de done:** Executar com inputs reais → roteiro de 1.400–2.000 palavras, todas as seções presentes (hook, contexto, 4 blocos, CTA), VISUALs em cada bloco, mapa de open loops documentado.

---

#### 3.4 — Agente QA (Checklist)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar nó do agente | `src/yt_agent/agents/qa.py` | Função `async def run_qa_agent(state: WorkflowState) → dict`: (1) carrega system prompt com 28 itens, (2) injeta `Script` + `VideoMetadata` completos, (3) chama Claude Sonnet, (4) parseia para `QAReport`, (5) retorna. |
| Implementar nó de decisão | `src/yt_agent/agents/qa.py` | Função `def decide_after_qa(state: WorkflowState) → str`: retorna `"pass"` se `verdict in ("approved", "approved_with_warnings")`, `"fail"` se `verdict == "needs_fix"` e `qa_attempt < 2`, `"pass_forced"` se `qa_attempt >= 2` (evita loop infinito). |

**Critério de done:** Executar com roteiro deliberadamente incompleto (sem VISUALs) → QA detecta falhas nos itens 6 e 21, gera `fix_instructions` específicas.

---

### Milestone S3: Produção funcional

```
✅ Agente Meta gera VideoMetadata completo e válido
✅ Alternância de thumbnail respeitada (via ChannelMemory)
✅ Agente Roteirista gera Script com 1.400–2.000 palavras
✅ Modelo de escrita lido e usado como referência
✅ Agente QA valida 28 itens e detecta falhas
✅ QA gera fix_instructions quando necessário
✅ 3 system prompts extraídos e autocontidos
```

---

## Sprint 4 — Orquestração (Grafo LangGraph)

**Objetivo:** Conectar todos os agentes no grafo de estados com
human-in-the-loop, branching condicional e output renderizado.

**Duração estimada:** 2–3 dias

### Tarefas

#### 4.1 — Definição do grafo

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar grafo principal | `src/yt_agent/graph.py` | Usar `StateGraph(WorkflowState)` do LangGraph. Definir nós: `fase_p`, `decide_fase_p`, `human_pause_retention`, `fase_0`, `validacao_tema`, `decide_tema`, `human_pause_tema`, `metadados`, `roteirista`, `qa`, `decide_qa`, `roteirista_fix`, `render_output`. Definir edges conforme o diagrama de estados da ADR. Compilar com `graph.compile(checkpointer=SqliteSaver(...))`. |
| Implementar nós de pausa humana | `src/yt_agent/graph.py` | 2 nós `human_pause_*` que usam `interrupt_before` do LangGraph. Quando o grafo pausa, o CLI apresenta as opções ao usuário via Rich prompt e injeta a decisão no state via `HumanDecision`. |

**Critério de done:** O grafo compila sem erros. Executar com mock de todos os agentes (retornando dados hardcoded) → fluxo completo do START ao END.

---

#### 4.2 — Human-in-the-loop

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Pausa pós-Fase P | `src/yt_agent/graph.py` | Se `decide_fase_p` retorna `"low_retention"`: (1) CLI exibe diagnóstico com Rich Table, (2) pergunta: "[1] Continuar com reforço de hooks, [2] Executar Repackaging no vídeo anterior, [3] Mudar de tema", (3) injeta decisão no state, (4) roteia para o nó correto. |
| Pausa pós-Validação | `src/yt_agent/graph.py` | Se `decide_tema` retorna `"low_demand"`: (1) CLI exibe keyword + volume + alternativas com Rich Table, (2) pergunta: "[1] Continuar mesmo assim, [2] Usar keyword alternativa [escolher], [3] Informar novo tema", (3) injeta decisão no state. |

**Critério de done:** Executar com retenção de 5% → CLI pausa, apresenta opções, aceita input, retoma execução.

---

#### 4.3 — Loop de correção QA → Roteirista

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar loop | `src/yt_agent/graph.py` | Edge condicional de `decide_qa`: se `"fail"` → `roteirista_fix` → `qa` (novo ciclo). Se `qa_attempt >= 2` → forçar `"pass_forced"` e seguir (com warning). Logar cada tentativa. |

**Critério de done:** Executar com roteiro intencionalmente fraco → QA reprova → Roteirista corrige → QA re-executa → aprovado ou forced pass na tentativa 2.

---

#### 4.4 — Renderer de output

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar renderer | `src/yt_agent/output/renderer.py` | Função `render_to_markdown(state: WorkflowState) → str`: monta o documento final em Markdown com todas as seções na ordem: Diagnóstico (Fase P) → Briefing Competitivo (Fase 0) → Metadados (títulos, thumbnail, tags, descrição, post) → Roteiro completo → Mapa de Open Loops → QA Report. Salva em `output/<run_id>.md`. |
| Output no terminal | `src/yt_agent/output/renderer.py` | Exibir resumo executivo no terminal com Rich: título escolhido, word count, score QA, caminho do arquivo salvo. |

**Critério de done:** Após execução completa, arquivo `.md` legível e bem formatado salvo em `output/`.

---

#### 4.5 — Checkpointing e resume

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Configurar checkpointer | `src/yt_agent/graph.py` | Usar `SqliteSaver` do LangGraph com o mesmo SQLite da channel memory. Cada execução salva state automaticamente a cada nó. |
| Implementar comando `resume` | `src/yt_agent/main.py` | `yt-agent resume --run-id <uuid>`: carrega o checkpoint do SQLite, retoma o grafo do nó onde parou. |

**Critério de done:** Executar workflow → pausa no human-in-the-loop → fechar o terminal → `yt-agent resume --run-id X` → retoma do ponto exato.

---

#### 4.6 — Conectar CLI `new` ao grafo

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Atualizar comando `new` | `src/yt_agent/main.py` | Remover o placeholder "Not implemented". Criar `WorkflowState` a partir das flags, salvar `WorkflowRun` no banco, executar o grafo compilado, renderizar output. |

**Critério de done:** `yt-agent new --topic "..." ...` executa o workflow completo end-to-end.

---

### Milestone S4: Workflow funcional end-to-end

```
✅ Grafo LangGraph compila e executa
✅ Fluxo completo: Fase P → Fase 0 → Validação → Metadados → Roteiro → QA → Output
✅ Human-in-the-loop funciona nos 2 pontos de decisão
✅ Loop QA → Roteirista funciona (max 2 tentativas)
✅ Output renderizado em Markdown
✅ Checkpointing: pause/resume funcional
✅ CLI `new` executa o workflow completo
```

---

## Sprint 5 — Memória e Repackaging

**Objetivo:** Tornar o sistema inteligente entre execuções —
memória de canal alimenta decisões e o repackaging roda de forma
independente.

**Duração estimada:** 1–2 dias

### Tarefas

#### 5.1 — População automática da memória

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Salvar após cada run | `src/yt_agent/graph.py` | Adicionar nó `save_to_memory` antes do `render_output`. Extrai do state: título escolhido, sub-nicho, formato, dados de thumbnail (estética, composição, paleta, expressão), e salva na tabela `videos`. Salva tags na tabela `tags_performance`. |
| Atualizar métricas | `src/yt_agent/main.py` | Comando `update-metrics --video-id <id>`: consulta VidIQ/YouTube para views, retenção, like ratio 7 dias após publicação e atualiza o registro em `videos`. |

**Critério de done:** Após 2 runs completos, `yt-agent history` exibe ambos os vídeos com dados de thumbnail diferentes (alternância).

---

#### 5.2 — Agente R (Repackaging)

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Extrair system prompt | `src/yt_agent/prompts/repackaging.md` | Extrair da seção FASE R do `prompt-videos-v11.md` (linhas ~1984–2107). ~120 linhas. |
| Implementar agente | `src/yt_agent/agents/repackaging.py` | Função `async def run_repackaging_agent(video_id: str) → RepackagingProposal`: (1) carrega system prompt, (2) consulta VidIQ para dados do vídeo + baseline do canal, (3) chama Claude Sonnet, (4) parseia para `RepackagingProposal`. |
| Implementar detecção de candidatos | `src/yt_agent/agents/repackaging.py` | Função `async def find_repackaging_candidates() → list[dict]`: consulta VidIQ, compara cada vídeo com baseline, retorna os que têm `views < 50%` da média após 5+ dias e `retention > 25%`. |

**Critério de done:** `yt-agent repackage --check` lista candidatos. `yt-agent repackage --video-id X` gera proposta com novos títulos, thumbnail prompt e descrição.

---

#### 5.3 — Comando `history`

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Implementar comando | `src/yt_agent/main.py` | `yt-agent history`: exibe Rich Table com todos os vídeos da memória: título, sub-nicho, data, estética, composição, views 7d, retenção. Ordenado por data (mais recente primeiro). |

**Critério de done:** Tabela formatada com dados reais do banco.

---

### Milestone S5: Sistema com memória

```
✅ Memória populada automaticamente após cada workflow
✅ Alternância garantida (consulta memória antes de gerar thumbnail)
✅ update-metrics atualiza dados pós-publicação
✅ Agente R identifica candidatos a repackaging
✅ Agente R gera proposta completa
✅ history exibe histórico do canal
```

---

## Sprint 6 — Testes e Hardening

**Objetivo:** Garantir robustez, cobertura de testes e documentação
mínima para uso em produção.

**Duração estimada:** 1–2 dias

### Tarefas

#### 6.1 — Testes unitários dos agentes

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Testes do Agente P | `tests/test_agents/test_performance.py` | (1) Mock da API VidIQ com dados de retenção normal → verifica `alert == "none"`. (2) Mock com retenção 5% → verifica `alert == "low_retention"`. (3) Mock com API indisponível → verifica fallback message. |
| Testes do Agente 0 | `tests/test_agents/test_competitive.py` | (1) Mock com 5 concorrentes → verifica 3+ erros e 3+ ângulos. (2) Mock sem concorrentes → verifica handling graceful. |
| Testes do Agente V | `tests/test_agents/test_validation.py` | (1) Mock com volume alto → `verdict == "approved"`. (2) Mock com volume zero → `verdict == "low_demand"` + alternativas. |
| Testes do Agente Meta | `tests/test_agents/test_metadata.py` | (1) Verifica 10 títulos ≤55 chars. (2) Verifica alternância de thumbnail vs. memória. (3) Verifica tags com volume > 0. |
| Testes do Agente QA | `tests/test_agents/test_qa.py` | (1) Script completo → 28/28 pass. (2) Script sem VISUALs → itens 6 e 21 fail. (3) Verifica fix_instructions geradas. |

**Critério de done:** `pytest tests/test_agents/ -v` → 100% pass.

---

#### 6.2 — Teste de integração do grafo

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Fluxo completo (happy path) | `tests/test_graph.py` | Mock de todos os agentes com outputs válidos. Verifica: (1) todos os nós são visitados na ordem correta, (2) state final contém todos os outputs, (3) output renderizado contém todas as seções. |
| Fluxo com branching | `tests/test_graph.py` | (1) Mock low_retention → verifica pausa e roteamento. (2) Mock low_demand → verifica pausa e roteamento. (3) Mock QA fail → verifica loop de correção (max 2). |

**Critério de done:** `pytest tests/test_graph.py -v` → 100% pass.

---

#### 6.3 — Error handling robusto

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| Retry com backoff | `src/yt_agent/agents/*.py` | Todas as chamadas à API Anthropic devem ter retry com exponential backoff (3 tentativas, 2s/4s/8s). Se falhar após 3, logar erro e salvar state para resume posterior. |
| JSON parse retry | `src/yt_agent/agents/*.py` | Se o LLM retornar JSON inválido, re-enviar a mensagem com o erro de validação Pydantic como feedback. Max 2 retries. |
| Timeout | `src/yt_agent/tools/*.py` | Timeout de 30s para chamadas VidIQ, 60s para YouTube. Timeout de 120s para chamadas ao Claude Opus (roteiro longo). |
| Graceful degradation | `src/yt_agent/agents/*.py` | Se VidIQ falhar, todos os agentes devem cair para o fallback YouTube. Se ambos falharem, logar warning e continuar sem os dados (com sinalização na checklist). |

**Critério de done:** Desligar VidIQ (key inválida) → workflow completa usando fallback → output tem warning "VidIQ indisponível".

---

#### 6.4 — Documentação

| Tarefa | Arquivo | Detalhes |
|---|---|---|
| README do projeto | `yt-agent/README.md` | Instalação, configuração (.env), comandos disponíveis, exemplos de uso, custo estimado, como atualizar system prompts. |

**Critério de done:** Um usuário seguindo apenas o README consegue instalar, configurar e executar o primeiro workflow.

---

### Milestone S6: Pronto para produção

```
✅ Testes unitários: todos os agentes cobertos
✅ Testes de integração: happy path + branching + QA loop
✅ Retry e backoff em todas as chamadas externas
✅ Fallback VidIQ → YouTube funcional
✅ JSON parse retry funcional
✅ README completo
✅ Primeiro roteiro real gerado end-to-end
```

---

## Pós-MVP — Backlog de evolução

Itens para considerar após a v1.0 funcional. Não fazem parte do
escopo inicial, mas estão documentados para decisão futura.

| # | Item | Valor | Esforço |
|---|---|---|---|
| E1 | **Agente de Shorts Companion** | Gera 2-3 Shorts automaticamente após roteiro longo | 1 dia |
| E2 | **Agendamento de Repackaging** (cron) | Fase R semanal automática com notificação | 0,5 dia |
| E3 | **Dashboard web** (Streamlit ou Gradio) | Interface visual em vez de CLI | 2-3 dias |
| E4 | **Multi-canal** | Suporte a múltiplos canais com configs separadas | 1-2 dias |
| E5 | **Geração automática de thumbnail** | Integrar API de imagem (Gemini/DALL-E) para gerar thumbnail diretamente | 1 dia |
| E6 | **Upload automático** | Usar YouTube Upload API para subir vídeo, título, descrição, tags de uma vez | 1-2 dias |
| E7 | **A/B testing de títulos** | Publicar com título A, agendar troca para título B após 48h, comparar CTR | 1 dia |
| E8 | **Análise de comentários do próprio canal** | Agente que lê comentários e extrai insights/perguntas recorrentes | 0,5 dia |
| E9 | **Integração com Obsidian/Notion** | Salvar outputs no sistema de notas do usuário | 0,5 dia |
| E10 | **Observabilidade** (LangSmith/LangFuse) | Tracing de cada chamada LLM, custo real por run, latência | 0,5 dia |

---

## Critérios de Aceitação do MVP (v1.0)

O projeto é considerado **pronto para uso em produção** quando:

- [ ] `yt-agent new` executa o workflow completo sem intervenção manual
      (exceto nos 2 pontos de human-in-the-loop)
- [ ] Output final é um arquivo `.md` com: diagnóstico, briefing,
      metadados completos (10 títulos, thumbnail, tags, descrição,
      post comunidade), roteiro completo com VISUALs, mapa de loops,
      e QA report
- [ ] Memória persiste entre execuções — alternância de thumbnail
      e sub-nicho funciona
- [ ] `yt-agent repackage --check` identifica vídeos candidatos
- [ ] `yt-agent resume` retoma execuções pausadas
- [ ] Custo real de uma execução completa está dentro de US$ 0,40–0,80
- [ ] Suite de testes passa (`pytest` verde)
- [ ] README suficiente para uso sem assistência
