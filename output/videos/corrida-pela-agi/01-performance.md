# Diagnóstico de Performance — Fase P

**Canal:** Marcus Maciel | IA & Ciência (`@MarcusMacielIAeCiencia`)
**Data do diagnóstico:** 2026-04-24
**Período de análise:** últimos 90 dias (2026-01-24 a 2026-04-24)

---

## 1. Último Vídeo Publicado

| Campo | Valor |
|---|---|
| **Título** | A Neuralink Fez um Mudo FALAR com o Pensamento |
| **ID** | `1ZB4WSkCQgQ` |
| **Tipo** | Longo (9 min 5 s) |
| **Data de publicação** | 21/04/2026 às 17:00 (BRT) |
| **Dias desde publicação** | 3 dias |
| **Views (VidIQ)** | 83 |
| **Views (Analytics, 3 dias)** | 8 (delay da API — dados parciais) |
| **Likes** | 6 |
| **Comentários** | 0 |
| **Inscritos ganhos** | 1 |
| **Like ratio** | 7,2% (6 likes / 83 views) |
| **Retenção média (Analytics)** | 38,72% (~3 min 31 s de 9:05) |
| **Avg view duration (Analytics)** | 211 s (~3 min 31 s) |

### Último Short publicado

| Campo | Valor |
|---|---|
| **Título** | Um CHIP Ouviu o Que Ele Pensava. E Falou Por Ele |
| **ID** | `fs64BTP07ps` |
| **Data** | 23/04/2026 |

---

## 2. Diagnóstico Geral

### Baseline do canal (últimos 90 dias)

| Métrica | Total (90d) | Média por vídeo longo (4 vídeos) |
|---|---|---|
| Views totais | 4.923 | ~1.231 |
| Minutos assistidos | 1.345 | ~336 min |
| Avg view duration | 30 s (canal todo, inclui Shorts) | — |
| Likes | 92 | ~23 |
| Comentários | 0 | 0 |
| Inscritos ganhos | 9 | ~2,3 |
| **Total de inscritos** | **6** | — |
| **Total de vídeos** | **11** (4 longos + 7 Shorts) | — |

### Comparação: vídeos longos (analytics por vídeo, período recente)

| Vídeo | Views | Min. assistidos | Avg duration (s) | Retenção % | Likes | Subs |
|---|---|---|---|---|---|---|
| **Neuralink (último)** | 83* / 8† | 28† | 211† | 38,72%† | 6* / 2† | 1† |
| Cirurgião Robô | 32* / 25† | 75† | 181† | 24,82%† | 2* / 2† | 0† |
| IA Reduziu Câncer 50% | 8* / 6† | 1† | 19† | 2,88%† | 0 | 0 |
| IA vs Médicos | —** / 4† | 10† | 157† | 30,87%† | 0 | 0 |

> \* VidIQ (tempo real) · † YouTube Analytics (delay 2-3 dias, dados parciais) · ** Erro no fetch

### Comparação: Shorts (analytics, período recente)

| Short | Views | Avg dur (s) | Retenção % | Likes | Subs |
|---|---|---|---|---|---|
| O ROBÔ Errou na Cirurgia | 2.740 | 19 | 62,28% | 42 | 3 |
| Esse ROBÔ Aprendeu a Operar | 1.300 | 19 | 61,71% | 36 | 3 |
| 29% dos CÂNCERES São Invisíveis | 317 | 15 | 24,87% | 4 | 0 |
| Essa PINTINHA Era Câncer | 154 | 16 | 23,03% | 2 | 0 |
| Seu DNA Custava 3 BILHÕES | 141 | 21 | 32,72% | 0 | 0 |
| ChatGPT Criou Uma VACINA | 46 | 7 | 12,15% | 0 | 0 |

### O que FUNCIONOU

1. **Título com gatilho emocional forte** — "Fez um Mudo FALAR com o Pensamento" gera curiosity gap poderoso. O vídeo da Neuralink tem 83 views em 3 dias, o melhor desempenho em views/dia de todos os longos do canal (27,7 views/dia vs 3,2/dia do Cirurgião Robô em 10 dias).
2. **Retenção 38,72% é a MELHOR do canal em vídeos longos** — supera o Cirurgião Robô (24,82%) e IA vs Médicos (30,87%). Com 3 min 31 s de avg duration em 9:05, indica que o hook e a primeira metade funcionaram.
3. **Like ratio de 7,2%** — significativamente acima do Cirurgião Robô (6,25%) e muito acima dos outros dois longos (0%). Indica que quem assistiu, engajou.
4. **Duração mais enxuta (9:05)** — o vídeo mais curto dos 4 longos, e com a melhor retenção. Correlação clara entre brevidade e engajamento.

### O que FALHOU

1. **Zero comentários** — nenhum dos 4 vídeos longos do canal tem comentários. Padrão sistêmico que precisa de intervenção urgente.
2. **Views absolutas ainda muito baixas** — 83 views em 3 dias. Mesmo sendo o melhor do canal, o YouTube não está distribuindo o conteúdo. Isso sugere problemas de impressões/CTR, não de conteúdo.
3. **Inscritos ganhos = 1** — taxa de conversão views→sub de 1,2%, que é razoável, mas o volume é irrelevante.
4. **VPH (views per hour) decrescente** — o video_stats retornou vazio (dados não processados pelo VidIQ para canal pequeno), mas pelo padrão de performance_trends, a curva de views do canal é muito flat: mediana de 3 views em 24h, 5 em 48h.

### Comparação com top performers

Os **top performers do canal são os Shorts**, não os longos. O Short "O ROBÔ Errou na Cirurgia" (2.740 views, 62,28% retenção, 42 likes) supera TODOS os longos em views absolutas por uma ordem de magnitude. Isso confirma que:
- O algoritmo do YouTube distribui muito mais os Shorts deste canal
- Os longos dependem quase exclusivamente de busca orgânica e tráfego direto

---

## 3. Análise de Retenção

> **Nota:** A retention curve (audienceWatchRatio por elapsedVideoTimeRatio) retornou vazia da API — o vídeo tem apenas 3 dias e dados insuficientes para granularidade por timestamp. Usamos a retenção média como proxy.

### Proxy: Retenção média 38,72% (avg duration: 3:31 de 9:05)

Com base na estrutura do roteiro (capítulos declarados na descrição):

| Timestamp estimado | Capítulo | Retenção estimada | Análise |
|---|---|---|---|
| 00:00 – 01:30 | Introdução | ~80-100% | Hook forte — o título já é o hook |
| 01:30 – 03:25 | Ensaio clínico VOICE | ~55-65% | Drop normal pós-hook (~30s) |
| 03:25 – 05:00 | Bradford Smith | ~40-50% | História humana — provável ponto de sustentação |
| 05:00 – 06:30 | IA decodifica a fala | ~30-38% | Bloco técnico — provável drop |
| 06:30 – 08:00 | Stanford e Paradromics | ~25-30% | Competição — menos emocional |
| 08:00 – 08:45 | Futuro + Conclusão | ~20-25% | Apenas quem ficou até aqui |

### 3 Maiores Drops Estimados

| Drop | Timestamp estimado | Causa provável |
|---|---|---|
| **1** | ~00:30 – 01:30 | Transição do hook para contexto clínico. Se a promessa do título ("fez um mudo falar") não é recompensada rapidamente com o momento exato, o espectador sai. |
| **2** | ~05:00 – 06:00 | Bloco "Como a IA decodifica a fala" — explicação técnica sobre redes neurais e fonemas. Se não tem dado contraintuitivo ou visual impactante, perde. |
| **3** | ~06:30 – 07:30 | Bloco "Stanford e Paradromics" — competição entre empresas pode parecer desconectado da promessa emocional do título. |

---

## 4. Pontos Críticos Universais

| Ponto | Timestamp | O que indica | Avaliação |
|---|---|---|---|
| **1ª decisão** | ~30s | Hook entregou a promessa? | **Provavelmente OK** — retenção média de 38,72% sugere que o hook manteve boa parte da audiência inicial. Para confirmar, precisamos da curva real. |
| **2ª decisão** | ~2 min | Primeiro payoff funcionou? | **Incerto** — o payoff emocional (Bradford Smith) só vem em 03:25. Se há 2 min de contexto técnico antes, pode haver drop. |
| **Ponto de fadiga** | ~4:30 (50% de 9:05) | Virada narrativa? | **Provável queda** — 4:30 cai no meio do bloco "Bradford Smith" → "IA decodifica a fala", que é transição de história humana para técnica. |

---

## 5. Lições do Último Vídeo

### ERRO A NÃO REPETIR

1. **Primeiro payoff emocional demora 3:25** — em um vídeo de 9 min, o espectador precisa do primeiro payoff antes de 2 min. Bradford Smith (a história humana mais impactante) deveria abrir o vídeo, não aparecer no terço médio. O hook promete "fez um mudo falar", mas o momento exato em que isso acontece pode não estar nos primeiros 90 segundos.
2. **Zero CTA de comentário** — nenhum momento do vídeo pede opinião ao espectador. Resultado: zero comentários em TODOS os vídeos longos. Isso é um padrão sistêmico grave que prejudica o sinal de engajamento para o algoritmo.

### ACERTO A MANTER

1. **Duração enxuta (9:05)** — o vídeo mais curto do canal e com a melhor retenção. Manter vídeos entre 8-10 min para o estágio atual do canal. Não inflar duração artificialmente.
2. **Título com dado humano concreto** — "Fez um Mudo FALAR" é tangível e emocional. Melhor título do canal até agora.

---

## 6. Calibrações para o Próximo Roteiro

1. **FRONT-LOAD a história humana** — O caso mais emocional e concreto do vídeo (o equivalente de "Bradford Smith") deve abrir o roteiro, nos primeiros 60 segundos. O contexto técnico vem DEPOIS do payoff emocional, não antes.

2. **Inserir CTA de comentário antes do payoff mais forte** — entre 5:00-6:00, logo antes da revelação mais surpreendente do vídeo, pausar e perguntar: "Me diz nos comentários: você confiaria numa IA para [X]?". O payoff que vem logo depois serve como recompensa por ficar.

3. **Pattern interrupt no bloco técnico** — se houver explicação técnica > 90 segundos, inserir um "Para ter ideia…" com comparação do cotidiano. Exemplo: em vez de explicar redes neurais, dizer "Imagine que 1.024 microfones captam sua voz, mas cada um ouve uma nota diferente. A IA junta tudo numa frase."

4. **Manter duração ≤ 10 min** — A correlação entre duração mais curta e melhor retenção é clara nos dados. Não expandir artificialmente. Se o conteúdo precisa de mais, dividir em 2 vídeos.

---

## 7. Session Architecture — Checklist

| Item | Status | Detalhe |
|---|---|---|
| Vídeo adicionado a 2 playlists temáticas? | ✅ | Está em **"🧠 IA e o Cérebro: Neuralink e Interface Cérebro-Computador"** (3 itens) e **"📚 Para Começar"** (5 itens) |
| Comentário fixado com pergunta provocativa + link para playlist? | ❌ | **Zero comentários** no vídeo. Não há comentário fixado. |
| End-screen apontando para vídeo da mesma playlist? | ⚠️ | Não verificável via API, mas o canal tem poucos vídeos — garantir que o end-screen aponte para "Seu Próximo Cirurgião Pode Ser um ROBÔ" (mesmo tema de IA + corpo humano). |
| Card aos 60% com vídeo de maior watch time? | ⚠️ | Não verificável via API. Deve apontar aos ~5:30 para o vídeo do Cirurgião Robô (75 min assistidos, maior watch time entre longos). |
| Short companion publicado? | ✅ | "Um CHIP Ouviu o Que Ele Pensava. E Falou Por Ele" (`fs64BTP07ps`) publicado em 23/04. |

### Ações Pendentes

1. **URGENTE — Adicionar comentário fixado** no vídeo da Neuralink:
   > "Se a Neuralink pudesse ler seus pensamentos agora, qual seria a primeira coisa que você 'falaria'? 🧠 Assista toda a série sobre IA e o cérebro: [link da playlist]"
2. **Verificar end-screen** — confirmar que aponta para vídeo da playlist "IA e o Cérebro" ou "Para Começar".
3. **Verificar card** — inserir card aos ~5:30 apontando para "Seu Próximo Cirurgião Pode Ser um ROBÔ".

---

## 8. Alerta

| Flag | Status | Detalhe |
|---|---|---|
| `low_retention` | ❌ Não ativo | Retenção média = 38,72% (acima do limiar de 20%) |
| `zero_comments` | 🚨 **ATIVO** | TODOS os 4 vídeos longos do canal têm 0 comentários. Padrão sistêmico grave. |
| `low_views` | ⚠️ Alerta | 83 views em 3 dias. Melhor do canal, mas insuficiente para tração algorítmica. O canal está em fase de cold start — views dependem de Shorts para gerar awareness e busca orgânica para longos. |
| `sub_conversion` | ⚠️ Alerta | 6 inscritos totais em 11 vídeos. Taxa de conversão extremamente baixa. Necessita de CTA de inscrição mais agressivo e estratégico nos vídeos. |

### Performance Trends — Curva típica do canal

Com base no `channel_performance_trends`:

| Horas desde publicação | Mediana de views | P70 | Max |
|---|---|---|---|
| 1h | 0 | 0 | 1 |
| 4h | 1 | 1 | 4 |
| 8h | 1 | 4,2 | 9 |
| 16h | 3 | 5,6 | 11 |
| 24h | 3 | 6,5 | 20 |
| 48h | 5 | 12,4 | 43 |
| 72h | 8 | 24,3 | 117 |

O vídeo da Neuralink com 83 views em 72h está **acima do max histórico do canal (117 views)** se considerarmos o total VidIQ, mas os dados de analytics (8 views) indicam que o VidIQ está contando views totais (inclusive de antes do período). De qualquer forma, o vídeo está performando **no topo ou acima do range típico** do canal.

---

## Resumo Executivo

O vídeo **"A Neuralink Fez um Mudo FALAR com o Pensamento"** é o **melhor vídeo longo do canal** em:
- ✅ Views/dia (27,7/dia vs 3,2/dia do segundo melhor)
- ✅ Retenção (38,72% vs 24,82%)
- ✅ Like ratio (7,2%)
- ✅ Avg view duration (3:31)

Os problemas são **sistêmicos do canal**, não deste vídeo especificamente:
- 🚨 Zero comentários em todos os longos
- ⚠️ Volume de views muito baixo (cold start)
- ⚠️ Conversão de inscritos negligenciável
- ⚠️ Sem comentário fixado

**Prioridade #1 para o próximo vídeo:** inserir CTA de comentário antes do payoff principal + front-load a história humana nos primeiros 60 segundos.
