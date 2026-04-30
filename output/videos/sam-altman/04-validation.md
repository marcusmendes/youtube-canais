# Validação de Tema / Keyword (FASE V)

**Slug:** `sam-altman`  
**Keyword principal validada:** `sam altman openai`  
**Data da análise:** 29/04/2026  

---

## 1. Cluster semântico (≥5 keywords)

| Keyword | Volume (0–100) | Competição (0–100) | Overall (0–100) | Buscas/mês (est.) | Notas |
|---------|----------------|--------------------|-----------------|-------------------|--------|
| **sam altman openai** (seed) | 60,7 | 45 | **58,4** | ~11,6K | Âncora principal do calendário |
| sam altman new yorker | 54,6 | 35 | **58,7** | ~4,5K | Ligação direta ao fio abril/2026 |
| openai news | 61,5 | 52 | **56,1** | ~13,2K | Janela “notícia quente” |
| sam altman chatgpt | 55,5 | 48,5 | **53,9** | ~5,2K | Ponte produto ↔ figura |
| sam altman | 83,9 | 67 | **63,5** | ~417K | Cabeça ampla; competição alta |
| sam altman investigado | 0 | — | — | 0 | PT-BR: sem volume medido no VidIQ (título ainda válido por **curiosidade editorial**, não por SEO de cauda) |
| openai ceo controversy | 0 | — | — | 0 | Long-tail fraca no índice VidIQ |

**Regra do cluster (≥3 com volume > 0):** **Cumprida** — quatro linhas acima com volume e overall sólidos.

**Relacionadas úteis** (do `includeRelated` da seed): `openai` (65,5 overall), `ai news` (72,3), `generative ai` (63,2), `openai hardware` (57,6) — úteis para **descrição/tags**, não para mudar o eixo central.

---

## 2. Intent dominante (top 10 busca YouTube — `videos_searchVideos`)

**Consulta:** `sam altman openai` (10 resultados).

**Classificação dominante:** **entrevista / visão oficial / “futuro da IA”** (TED 2025, Bloomberg Stargate, Lex Fridman, podcast OpenAI, DevDay) + **notícia pontual** (CNN/Newsweek sobre Musk × oferta).

**Implicação para o nosso vídeo:** o ângulo do calendário (**investigativo, ética, violência em SF, *New Yorker*, safety**) **não** é o intent médio da SERP genérica. Precisamos **declarar intent na capa e nos 30s**: *Opinião/Debate + Timeline + “o que isso muda para você”* — alinhado ao briefing competitivo (`03-competitive.md`), não competir como “mais um TED recap”.

---

## 3. Competição contextual (faixa 5K–50K inscritos no top 10)

Canais entre posições 1–10 (amostra com estatísticas via `channels_getChannels`):

| Posição (aprox.) | Canal | Inscritos |
|------------------|--------|-----------|
| 1 | TED | 27,3M |
| 2 | Bloomberg Originals | 5,01M |
| 3 | Techbrology™ | **1,4K** |
| 4 | Lex Fridman | 4,98M |
| 5–7 | OpenAI / Lex (repetição de formato) | 1,94M / etc. |
| 8–9 | Newsweek / CNN | 709K / 19,5M |
| 10 | **Alex Kantrowitz** | **52,9K** |

**Veredito estrutural:** **não** há canal **estritamente** na faixa **5K–50K** no top 10 da busca genérica (o mais próximo, Alex Kantrowitz, **ultrapassa** ligeiramente os 50K; demais são megacanais ou micro).

→ **Sinalização `ceiling_bound` para a *head keyword* pura** na busca YouTube: ranquear só com “sam altman openai” é **difícil** sem autoridade de notícia ou breakout.

**Mitigação (já alinhada ao plano):**

1. Título/thumbnail com **gancho temporal e específico** (*New Yorker* abril/2026, SF, safety) — long-tail implícito.  
2. Distribuição: **Shorts** ou clipes citando o caso + remete ao longo (memória do canal: dependência de Shorts).  
3. Incluir na descrição keywords de apoio: `sam altman new yorker`, `openai news`, `ai news`.

---

## 4. Checklist de Ouro

1. **Ângulo universal:** Quem paga plano de saúde, usa ChatGPT no trabalho ou vota em regulação de IA no Brasil precisa entender **quem acumula poder sobre modelos de fronteira** e por que isso vira **violência política e crise de confiança** em abril/2026 — não é “fofoca de bilionário”, é **risco institucional**.  
2. **Premissa curta (≤10 palavras):** *Perfil explosivo, casa atacada, AGI na mesa.*  
3. **Gatilho da persona “Explorador da Fronteira”:** medo de **AGI concentrada + perda de confiança em guardrails**; desejo de **mapa claro** entre fato, rumor e consequência para o Brasil.

---

## 5. Veredicto

| Campo | Valor |
|--------|--------|
| **Decisão** | **`approved`** |
| **Motivo** | `overall` da seed **58,4** (≥ 20) e **volume 60,7** (> 0); cluster com múltiplas keywords com demanda. |
| **Alertas** | **`ceiling_bound`** na SERP da busca exata `sam altman openai` (top 10 dominado por grandes mídias / oficial); PT isolado (`sam altman investigado`) sem volume de ferramenta — compensar com **título bilíngue** ou **gancho visual** + SEO em inglês na descrição. |

**Alternativas se quiser maximizar busca (opcional):** empurrar `sam altman new yorker` e `openai news` para primeira linha da descrição; episódio complementar em inglês só se fizer sentido para o canal (não obrigatório).

---

**Próxima fase (pipeline):** Fase 4 — Narrativa (`05-narrative.md`), lendo `01-performance.md`, `02-research.md`, `03-competitive.md` e este arquivo.
