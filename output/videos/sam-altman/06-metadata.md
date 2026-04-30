# Metadados — Sam Altman, OpenAI e o Poder Sobre a AGI

**Slug:** `sam-altman`  
**Duração-alvo:** ~15 minutos (teleprompter)  
**Data:** 2026-04-29  
**Fase:** 5 de 8 (Metadados) · **patch pós-QA (Fase 7)** em 2026-04-29 — descrição template, disclosure imagens, Studio, comentário fixado.

---

## 10 Títulos (≤55 caracteres, 6 fórmulas)

| # | Título | Fórmula | Caracteres |
|---|--------|---------|------------|
| 1 | Sam Altman: Quem Confia na OpenAI? | F1 Mistério | 35 |
| 2 | O Artigo da New Yorker e a Quebra na IA | F1 Mistério | 39 |
| 3 | OpenAI vs Verdade: o Que Sobrou do Caso? | F2 Contraste | 38 |
| 4 | NÃO É FOFOCA: É Poder Sobre a AGI | F3 Urgência | 35 |
| 5 | 18%: O Segredo dos Frameworks de IA | F4 Número | 36 |
| 6 | Casa do CEO da OpenAI Atacada em 2026 | F5 Temporal | 35 |
| 7 | E Se a AGI Dependesse de UMA Pessoa? | F6 Hipótese | 37 |
| 8 | Segurança Não Substitui Confiança na IA | F2 Contraste | 38 |
| 9 | Molotov & IA: Entender Sem Romantizar | F3 Urgência | 35 |
| 10 | Brasil: Por Que a OpenAI IMPORTA PRA NÓS | F1 Mistério | 38 |

---

## Top 3 + Validação VidIQ

### 1. **NÃO É FOFOCA: É Poder Sobre a AGI** (Fórmula 3)

**Por quê:** Converte o ângulo proprietário do manifesto competitivo (não é fofoca de celebridade; é poder institucional sobre AGI) em promessa clara. Diferencia de títulos genéricos de “Sam Altman news”.

**Validação VidIQ (seed `sam altman openai`):** volume 61,4 | competição 100 | overall 30,7 | ~355K buscas/mês — **ceiling_bound** na SERP genérica; este título força *angle lock* (poder/ética) em vez de competir só por nome.

---

### 2. **Sam Altman: Quem Confia na OpenAI?** (Fórmula 1)

**Por quê:** Pergunta direta alinha ao arco emocional (confiança quebrada) e ao gancho de abertura da narrativa.

**Validação VidIQ (seed `sam altman new yorker`):** volume 54,6 | competição 35 | overall 58,7 | ~4,5K buscas/mês — **ângulo editorial** (perfil + consequências) com competição mais baixa que a keyword genérica.

---

### 3. **18%: O Segredo dos Frameworks de IA** (Fórmula 4)

**Por quê:** Número concreto do dossiê (18% disclosure em preprint SaferAI) vira curiosidade sem prometer “hack” vazio; educa e retém quem busca *frameworks* / notícias de IA.

**Validação VidIQ:** `chatgpt news` — volume 64,2 | competição 52 | overall 57,7 | ~20K/mês. `ai ethics` — volume 61,4 | competição 47 | overall 58,0 | ~13K/mês. Cruzamento semântico: **notícia + ética + produto**.

---

## Thumbnail — Master Prompt v2 (blocos técnicos em inglês; headline na imagem em PT-BR)

**Composition:** **C — Objeto Simbólico** (alternância ao último longo do pipeline `agi-em-2027`, que usou C; aqui reforçamos *fratura de confiança* com objeto físico legível em mobile).

**Headline (3 palavras, CAIXA ALTA, intrigue gap):** `CONFIANÇA EM PEDAÇOS`  
*Gap:* a arte mostra confiança “quebrada” visualmente; o título recomendado nega fofoca e fala de **poder sobre AGI** — o espectador precisa clicar para fechar o circuito.

**Title (top bar, ≤40 chars, NO headline repeat):** `SAM ALTMAN / OPENAI`

**Palette:** fundo frio (#0A0E14); acento vermelho (#E63946) na palavra **CONFIANÇA** ou na fissura do objeto; demais palavras do headline em off-white (#F8F9FA).

**Layout:**  
- **Zona superior (15%):** barra escura com “SAM ALTMAN / OPENAI” em sans bold pequeno.  
- **Zona central (55%):** revista genérica estilizada (não reproduz capa real) com manchete borrada + **rachadura** diagonal; ou **troféu de vidro** rachado com reflexo do logo da OpenAI *estilizado* (fair use / paródia visual, não asset oficial).  
- **Zona inferior (30%):** headline `CONFIANÇA EM PEDAÇOS` em caixa alta; **CONFIANÇA** em vermelho (#E11D2E), **EM PEDAÇOS** em branco com contorno escuro (regra Master Prompt v2).

**Marcus:** canto inferior direito, expressão séria, olhar para câmera, leve desvio do centro do headline para não competir com o objeto.

**Lighting:** key light 45°, sombra curta; rim light fria separando do fundo.

**Anti-patterns:** sem foto de capa real do *New Yorker*; sem sangue; sem “clickbait” de crime como entretenimento; sem prometer “prova” que o vídeo não sustenta.

---

## Thumbnail — Tabela de QA (7 seções)

| Seção | Check | Status |
|-------|-------|--------|
| 1. Composição | C — objeto simbólico (confiança quebrada); não repete rosto-only do último metadata longo quando possível alternar | OK |
| 2. Headline | 3 palavras em PT-BR (`CONFIANÇA EM PEDAÇOS`); Intrigue Gap com título (poder/AGI vs confiança visual) | OK |
| 3. Title top | ≤40 chars; não repete headline; “SAM ALTMAN / OPENAI” | OK |
| 4. Paleta | Fundo frio + vermelho cirúrgico + off-white | OK |
| 5. Headline mobile | 3 palavras PT; legível em ~10% da tela | OK |
| 6. Marcus | Presença humana, canto, não cobre objeto central | OK |
| 7. Anti-patterns | Sem capa real; sem crime glamourizado; sem falso “exposed” | OK |

---

## Descrição (YouTube) — template SEO + `02-research.md`

Sam Altman e a **OpenAI** estão no olho de um furacão que mistura **ChatGPT**, promessa de **AGI**, violência real em São Francisco e uma crise de **confiança** que não é “fofoca de celebridade” — é **poder institucional**.

Neste episódio em câmera (~15 min), eu separo **notícia verificável** de rumor, conecto a linha do tempo de abril de **2026** ao que muda para **regulação**, **SUS**, **judiciário** e **trabalho no Brasil**, e mostro por que um **preprint** independente colocou a **mediana de disclosure** dos frameworks de segurança em **dezoito por cento** — com o rótulo honesto de **preprint**.

🔬 **NESTE VÍDEO VOCÊ VAI VER:**  
0:00 **OpenAI + confiança** — o gancho que o feed mistura com meme  
1:30 **Sam Altman** e São Francisco: o que a polícia pública **disse** (e o que **não** provou)  
4:00 **Frameworks de IA** e o silêncio custoso dos provedores  
6:45 **OpenAI** em fratura pública: *New Yorker*, *Verge* e *TechCrunch* na mesma mesa  
9:30 **Segurança** não substitui confiança — e crime não vira entretenimento  
12:00 **Brasil**: consumo rápido de **ChatGPT**, marco regulatório lento  
14:00 Próximo passo: como **você** entra na história sem virar refém de headline

▶️ **ASSISTA TAMBÉM:**  
• Você Deixaria um ROBÔ Morar Na Sua Casa? (último longo do canal) → https://www.youtube.com/watch?v=rVUdHTnKkNQ

📚 **FONTES E ESTUDOS CITADOS** (mesmas URLs canônicas do `02-research.md`; leia o original em cada link):  
• https://www.newyorker.com/magazine/2026/04/13/sam-altman-may-control-our-future-can-he-be-trusted  
• https://techcrunch.com/2026/04/11/sam-altman-responds-to-incendiary-new-yorker-article-after-attack-on-his-home  
• https://sfstandard.com/2026/04/16/duo-accused-shooting-sam-altman-s-home-freed-charges-filed/  
• https://www.theverge.com/ai-artificial-intelligence/907421/sam-altman-is-unconstrained-by-truth  
• https://www.theverge.com/2024/5/17/24159095/openai-jan-leike-superalignment-sam-altman-ai-safety  
• https://www.theverge.com/2024/5/28/24166370/jan-leike-openai-anthropic-ai-safety-research  
• https://www.reuters.com/technology/sam-altman-return-openai-ceo-2023-11-22/  
• https://www.reuters.com/legal/elon-musk-openai-head-court-spar-over-nonprofit-conversion-2025-02-04/  
• https://www.theverge.com/ai-artificial-intelligence/920191/elon-musk-sam-altman-trial-day-one  
• https://www.npr.org/2024/03/01/1235159084/elon-musk-suit-chatgpt-sam-altman-greg-brockman  
• https://fortune.com/2026/04/14/sam-altman-openai-ceo-attacked-molotov-cocktail-gunshots-san-francisco-anti-ai-data-centers-tech/  
• https://arxiv.org/abs/2512.01166 (preprint SaferAI — metodologia e limitações no próprio PDF)  
• https://link.springer.com/article/10.1007/s43681-024-00653-w (*AI and Ethics*)  
• https://www.sciencedirect.com/science/article/pii/S0963868724000672 (*Journal of Strategic Information Systems*)

Imagens ilustrativas geradas por inteligência artificial.

**Disclosure (texto/roteiro):** roteiro estruturado com apoio de ferramentas de IA; revisão editorial e fact-check contra as fontes listadas são minhas responsabilidades.

🔔 **INSCREVA-SE** para acompanhar ciência, poder e futuro da IA no canal:  
https://www.youtube.com/@MarcusMacielIAeCiencia?sub_confirmation=1

Créditos de imagens/vídeos: Marcus Maciel | IA & Ciência — https://www.youtube.com/@MarcusMacielIAeCiencia

#SamAltman #OpenAI #ChatGPT #AGI #ÉticaEmIA #InteligênciaArtificial #Brasil #NewYorker #TechNews #IA

---

## Tags (copiar para o YouTube)

```
sam altman, openai, chatgpt, agi, ai ethics, openai news, sam altman new yorker, tech news, inteligência artificial, ética ia, brasil ia, governança ia, frameworks ia, disclosure modelos, new yorker openai, segurança openai, marcus maciel
```

---

## Capítulos (curiosity-driven)

```
0:00 A Confiança Que Vende (& o Que Ela Esconde)
1:30 Do Futebol ao Hospital (& Por Que Isso É AGI)
4:00 Frameworks Brilhantes (& o Silêncio Custoso)
6:45 OpenAI: Fratura em Público (& Resposta Oficial)
9:30 Segurança Não É Confiança (& Crime Não É Resposta)
12:00 Brasil: Consumo Rápido (& Marco Lento)
14:00 Próximo Episódio (& Como Você Entra Nessa História)
```

---

## Post para a Comunidade (aba Community)

**Título corto:** Poder, confiança e AGI — sem fofoca barata.

**Corpo (4 partes):**  
1. **Abertura:** O mesmo fio virou meme, crime e “prova” no Twitter — em minutos.  
2. **Expansão:** Neste longo eu amarro **abril/2026** a fontes, explico por que **dezoito por cento** (mediana em **preprint**) importa mais que lista de números sem trilha, e traduzo para **Brasil**.  
3. **CTA:** Assiste até o bloco da **SFPD** antes de compartilhar thread com “causa certa”.  
4. **Engajamento:** Qual dos três o Brasil mais ignora hoje: **transparência**, **segurança** ou **concentração de poder**? Comenta no vídeo.

---

## Comentário Fixado (copy-paste)

Confiança em quem controla **AGI** não nasce de headline — nasce de **auditoria**, de **polícia pública** e de **preprint** lido com método.  
**Pergunta:** que critério *mensurável* você exigiria de um provedor antes de chamar o framework de segurança dele de “prestável de contas” para fora da empresa — além do discurso de marketing?  
Playlist (salve para rever a série): https://www.youtube.com/@MarcusMacielIAeCiencia/playlists  

*(Quando existir playlist dedicada “Ética & Poder na IA”, substitua pela URL `playlist?list=...` específica e mantenha este comentário atualizado.)*

---

## Session Architecture (descoberta + continuidade)

| Playlist | Função | URL |
|----------|--------|-----|
| **Ética, Poder & Instituições (IA)** | Episódios longos sobre quem decide, o que é público, o que é marketing e onde o Brasil entra | https://www.youtube.com/@MarcusMacielIAeCiencia/playlists |
| **Mapas Rápidos de IA (série)** | Compilado de vídeos “um conceito por episódio” para binge educativo | https://www.youtube.com/@MarcusMacielIAeCiencia/playlists |

**YouTube Studio — conteúdo alterado / IA generativa:** no upload, marcar explicitamente quando houver **imagem ou vídeo gerados ou alterados por IA** (thumbnail, B-roll, *re-enactment*), conforme as opções atuais da plataforma para transparência com o espectador.

**End screen:** com **menos de 15** vídeos públicos no canal, usar placeholder até métricas estáveis: `[PREENCHER após Fase Y — thumbnail do vídeo de maior CTR na playlist “Ética, Poder & Instituições”]`. Com **15 ou mais** vídeos, aplicar a regra do canal (maior CTR da playlist-alvo).

**Card ~60%** da duração (~9 min em vídeo de ~15 min): `[PREENCHER — vídeo de maior watch time na playlist “Ética, Poder & Instituições”]`.

**Crédito de canal (rodapé da descrição):** já incluído no bloco **Descrição** acima; repetir no Studio se o editor de descrição não preservar o trecho final.

---

## Notas de implementação

- **Título recomendado para upload:** `NÃO É FOFOCA: É Poder Sobre a AGI` (Top 1) *ou* `Sam Altman: Quem Confia na OpenAI?` (Top 2) — A/B mental: Top 1 para *angle lock*; Top 2 para busca editorial “new yorker”.
- **CTR-risk:** evitar thumb que pareça “crime channel”; manter tom **The Verge / NPR** (contexto) não **tabloid**.
- **Analytics canal (90d, top por views):** vídeos com melhor *average view percentage* recente incluem IDs `7OIQoBQHBJo` (~62% AVP), `yzDxS5HP0_4` (~62%) — reforçar padrão de **pergunta + promessa clara nos primeiros 30s** alinhado a esses performers.

---

## Checklist final (Fase 5)

- [x] 10 títulos / 6 fórmulas / ≤55 caracteres  
- [x] Top 3 + métricas VidIQ (seeds documentadas)  
- [x] Thumbnail Master Prompt v2 + tabela QA 7 seções  
- [x] Descrição 250–400 palavras + FONTES só do `02-research.md` + disclosure  
- [x] Hashtags linha dedicada  
- [x] Post Community + comentário fixado com URL de playlist  
- [x] Session Architecture (2 playlists + Studio + end screen + card)  
- [x] Crédito de canal no bloco Descrição  

**Status:** metadados **revalidados pós-QA** — próximo: `FINAL.md` após gravação/publicação (ou fechar Fase 8 conforme pipeline).
