# Relatório de QA — Sam Altman (`/yt-qa`)

**Data da auditoria:** 2026-04-29  
**Arquivos lidos:** `06-metadata.md`, `07-scriptwriter-presenter.md`, `05-narrative.md`, `02-research.md`, `01-performance.md`, `03-competitive.md`, `04-validation.md`.

---

## 1. Resumo

| Métrica | Valor |
|--------|--------|
| Itens verificados | 38 |
| **PASS** | 18 |
| **FAIL** | 14 |
| **SKIP** (não aplicável / sem evidência no disco) | 6 |
| **Veredicto** | **`needs_fix`** |

**Motivo binário:** falha no **item 31** (claims técnicos sem correspondência inequívoca no dossiê) — pela regra do agente QA, isso força `needs_fix` independentemente do restante.

**Nota de consistência interna:** o cabeçalho de `07-scriptwriter-presenter.md` alega ~2.100 palavras e 15–18 min; a contagem das falas em `**Marcus:**` / `**Marcus (V.O.):**` fica em ~**834 palavras**, incompatível com a meta declarada no próprio arquivo.

---

## 2. Tabela completa (38 itens)

| # | Verificação | Status | Detalhe |
|---|-------------|--------|---------|
| 1 | Metadados completos | **FAIL** | Pacote forte, mas o checklist pede também **hashtags** explícitos no pacote; não há bloco dedicado. Disclosure (item 22) ausente na descrição. |
| 2 | Títulos validados | **PASS** | Amostra checada: dentro de ~55 caracteres, tom conversacional, CAPS pontuais. |
| 3 | Contagem de palavras | **FAIL** | Long-form exige **1.400–2.000** palavras faladas; texto atual ~**834** palavras só nas falas. Cabeçalho contradiz o arquivo. |
| 4 | Seções presentes | **PASS** | Hook + atos + payoff + CTA final presentes. |
| 5 | Escalonamento progressivo | **PASS** | Ato 1→4 escala tensão e implicação (alinhado ao `05-narrative.md`). |
| 6 | VISUAL em todos os blocos | **PASS** | Cada ato com `**VISUAL:**` em B-roll. |
| 7 | Camada visual permanente | **PASS** | Paleta/documental coerente com metadados. |
| 8 | Loops de retenção | **FAIL** | Para longo, esperado ≥1 loop a cada 250–400 palavras; densidade atual não atende ao critério quantitativo. |
| 9 | Credibilidade científica | **FAIL** | Dossiê (`02-research.md`) registra **lacuna** sobre confirmação pública de incidente “molotov”; o roteiro afirma **“ataques com coquetel molotov a tiros”** como pano de fundo factual sem nuance de incerteza. |
| 10 | Descrição SEO | **FAIL** | Bloco de descrição + capítulos no `06-metadata.md` ≈ **137 palavras** de corpo; meta do checklist é **250–400** + keyword 3–4× de forma orgânica. |
| 11 | Post comunidade | **PASS** | Curto, com emoji limitado (2), tom adequado. |
| 12 | Thumbnail completa | **FAIL** | Checklist pede **7 seções** + alternância formal; há tabela resumida (composição, paleta, headline, intrigue gap), não o pacote completo de 7 seções. |
| 13 | Sub-nicho diferente | **SKIP** | Memória de canal não amarrada ao slug nesta sessão; não auditável só pelos arquivos. |
| 14 | Função do Short | **SKIP** | Entrega é long-form; campo Short não preenchido no pacote. |
| 15 | Fase P executada | **PASS** | `01-performance.md` com diagnóstico e **≥2 calibrações** (ex.: capa, visual hooks, loop na ética). |
| 16 | Fase 0 executada | **PASS** | `03-competitive.md`: ≥3 concorrentes, erros/lacunas, ângulo. |
| 17 | Validação de tema | **PASS** | `04-validation.md` com keywords e intent. |
| 18 | DNA narrativo (P1–P8) | **PASS** | `05-narrative.md` cobre protagonista, espinha, arco, cenas, anti-clichês. |
| 19 | Revisão anti-IA | **PASS** | Tom majoritariamente específico ao caso OpenAI/Altman. |
| 20 | Modelo de escrita consultado | **FAIL** | Nenhuma evidência no output de que arquivo em `canais/marcus-maciel/modelos-de-escrita/` tenha sido aplicado/citado. |
| 21 | Especificidade visual | **FAIL** | Ex.: “Gráficos matemáticos complexos” é **genérico** (não cena acionável). |
| 22 | Disclosure IA | **FAIL** | Frase **“Imagens ilustrativas…”** ausente da descrição em `06-metadata.md`. |
| 23 | Teste de voz alta | **FAIL** | Sem marcações **`[pausa]`** / **`[ênfase]`** no roteiro apresentador. |
| 24 | Camada de retenção | **FAIL** | Sem auditoria explícita dos primeiros 30s no artefato; pattern interrupts não documentados como no checklist. |
| 25 | CTAs na narração | **FAIL** | Só CTA de vídeo no final; faltam CTAs posicionados conforme regra (entre B2–B3, dentro do bloco final de desenvolvimento, últimos 10s para inscrição/engajamento). |
| 26 | Voice-over + tradução | **SKIP** | Modo **apresentador** (`07-scriptwriter-presenter.md`), não voz-over ElevenLabs. |
| 27 | Manifesto de diferenciação | **PASS** | Ângulo bunk/safety + fontes aparece no competitivo e no roteiro. |
| 28 | Label “Altered content” | **FAIL** | Nota para marcar no YouTube Studio **não** está no `06-metadata.md`. |
| 29 | Stress test título ↔ thumbnail | **PASS** | Título promete identidade/contradição; thumb “LADO OCULTO” sustenta pergunta sem redundância total com o top título escolhido. |
| 30 | Session Architecture | **FAIL** | Não documenta 2 playlists, comentário fixo **com link de playlist**, end screen/card conforme checklist. |
| 31 | Fonte primária por claim | **FAIL** | **Q\*** atribuído a “**Reuters**” no roteiro; **`02-research.md` não lista Reuters** como fonte do dossiê. Claims sensíveis de incidente (molotov/tiros) sem fonte primária alinhada ao dossiê. |
| 32 | Zero recomendação médica | **PASS** | Sem conselho clínico. |
| 33 | Medical misinfo (YouTube) | **PASS** | Sem violações do tipo vacina/cura milagrosa. |
| 34 | Viewer Simulation Pass | **FAIL** | Blocos densos de A-roll sem quebras marcadas; risco de trechos longos sem interrupt explícito. |
| 35 | Translation-friendly | **PASS** | Frases majoritariamente quebráveis; poucos idiomasismos opacos. |
| 36 | Protagonista identificável | **PASS** | Altman em <15s no gancho. |
| 37 | Cenas, não tópicos | **PASS** | Atos funcionam como cenas (lugar + conflito). |
| 38 | Arco emocional variado | **PASS** | Tabela em `05-narrative.md` com ≥3 emoções ao longo do arco. |

---

## 3. Veredicto

**`needs_fix`**

---

## 4. Instruções de correção (acionáveis)

1. **Item 31 / 9 — Fontes e tom factual**  
   - **Q\*:** cite apenas o que está no dossiê (ex.: **processo Musk**, **MIT Tech Review**, comunicados **OpenAI**, **WilmerHale**) ou **amplie o `02-research.md`** com citação primária da Reuters (URL, data, título) e alinhe o roteiro a ela.  
   - **Segurança física:** reformule “molotov/tiros” para **relatos/indícios** ou cite fonte que o dossiê aceite (ex.: *New Yorker* / BI conforme já calibrado no Agente F), explicitando **o que é confirmado vs. reportado**.

2. **Item 3 — Duração vs. palavras**  
   - Expandir falas até **mínimo 1.400 palavras** (ou recalibrar promessa para vídeo mais curto e ajustar capítulos/metadados).  
   - Corrigir o cabeçalho de produção para refletir a **contagem real**.

3. **Item 10 — Descrição SEO**  
   - Ampliar corpo da descrição para **250–400 palavras**, integrando keyword principal de forma orgânica (3–4 ocorrências).

4. **Itens 22, 28, 30 — Publicação**  
   - Inserir disclosure de imagens ilustrativas / IA generativa na descrição.  
   - Adicionar nota operacional sobre **Altered content** no Studio.  
   - Documentar **Session Architecture**: 2 playlists-alvo, comentário fixo com **pergunta + link de playlist**, plano de end screen e card ~60%.

5. **Itens 12, 1 — Pacote de thumbnail e hashtags**  
   - Completar thumbnail no formato de **7 seções** do checklist.  
   - Incluir linha de **hashtags** (#) coerentes com o tema.

6. **Itens 23, 25, 24, 34 — Roteiro apresentador**  
   - Inserir `[pausa]` / `[ênfase]` nos pontos de virada.  
   - Adicionar **CTAs** de inscrição/comunidade nos pontos exigidos.  
   - Marcar **pattern interrupts** e revisar blocos >45s de fala contínua.

7. **Itens 8, 21**  
   - Inserir **loops abertos** a cada ~300 palavras (após expansão).  
   - Substituir VISUAL genérico por **cena** (ex.: “trecho X do complaint Musk”, “print do post de Jan Leike”, “capa da matéria MIT de mês/ano”).

8. **Item 20**  
   - Registrar no roteiro ou no relatório qual **arquivo** de `canais/marcus-maciel/modelos-de-escrita/` foi lido (ou ler um e ajustar cadência/voz).

---

*Gerado por auditoria manual dos 38 itens conforme `.cursor/agents/yt-qa.md`.*
