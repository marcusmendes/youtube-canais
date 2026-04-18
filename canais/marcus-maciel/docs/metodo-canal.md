# Método de Produção — Canal Marcus Maciel
**Versão 2.0 | 18 de abril de 2026**

> Método construído a partir da análise de dados reais de 3 referências
> (Singularidade, Ciência Todo Dia, MrBeast) + diagnóstico dos 12
> primeiros vídeos do canal + integração com VidIQ MCP e prompt v10.
> Cada regra está fundamentada em padrões observados, não em opinião.

---

## Visão Geral

O canal usa o prompt v10 para produção de roteiros — o sistema mais
sofisticado entre os concorrentes mapeados. As melhorias recentes em
títulos (CAPS + contradição) já geraram resultados: Shorts passaram
de 159 views de média para 1.000+. O próximo gargalo é converter
Shorts em views nos longos e gerar os primeiros comentários.

Evolução dos gargalos:

| Gargalo | Status v1.0 (abr/2026) | Status v2.0 (abr/2026) |
|---|---|---|
| **Títulos** descritivos | "Vacina Personalizada" = 43 views | CAPS+contradição = 1.015+ views ✅ Resolvido |
| **Tema repetitivo** (7/7 = IA + câncer) | Algoritmo perdido | Diversificação iniciada (Robótica, Poder/Ética) ⏳ Em progresso |
| **Funil Short → Longo** | 0 conversão | 1.294 Short → 11 Longo ⏳ Melhorou mas precisa escalar |
| **Zero comentários** | 0 em 7 vídeos | 0 em 12 vídeos ❌ Novo foco |
| **Roteiros robóticos** | — | DNA Narrativo (7 Princípios) adicionado ao prompt v10 ⏳ Em progresso |

---

## 0. Pipeline de Produção (Fases V → 0 → P → Roteiro)

O prompt v10 introduziu um pipeline de 4 fases que precedem a escrita do
roteiro. Cada fase usa ferramentas MCP (VidIQ como primária, YouTube como
fallback) e alimenta a próxima.

```
Fase V (Validação) → Fase 0 (Competitiva) → Fase P (Performance) → Roteiro
```

### Fase V — Validação de Tema

Antes de qualquer produção, o tema passa por validação com dados reais.

| Passo | Ação | Ferramenta |
|---|---|---|
| 1 | Pesquisar volume de busca e competição do tema | `vidiq_keyword_research` |
| 2 | Verificar trending no nicho | `vidiq_trending_videos` |
| 3 | Aplicar o teste de 3 perguntas (Seção 1) | Análise IA |

**Critério de corte:** se o volume VidIQ é muito baixo e não há trending,
reconsiderar o tema ou ajustar o ângulo.

### Fase 0 — Análise Competitiva de Roteiros

O prompt v10 faz pesquisa competitiva para **diferenciação de conteúdo**,
não apenas SEO.

| Passo | Ação | Ferramenta (primária → fallback) |
|---|---|---|
| **1. Buscar outliers** | Vídeos com performance desproporcional no tema | `vidiq_outliers` → `videos_searchVideos` |
| **2. Buscar trending** | Vídeos com velocidade de crescimento alta | `vidiq_trending_videos` |
| **3. Selecionar** | 3-5 mais relevantes por views + recência | `vidiq_video_stats` → `videos_getVideo` |
| **4. Extrair** | Transcript de cada vídeo selecionado | `vidiq_video_transcript` → `transcripts_getTranscript` |
| **5. Analisar comentários** | Entender dúvidas e reações do público | `vidiq_video_comments` |
| **6. Cruzar** | Comparar transcripts com fontes científicas | Análise IA |
| **7. Documentar** | Briefing com erros, lacunas e ângulos inexplorados | Análise IA |

### Estrutura do briefing competitivo

Para cada vídeo analisado, registrar:

| Campo | Descrição |
|---|---|
| **Vídeo** | Título, canal, views, data |
| **Erros factuais** | Dados incorretos, simplificações excessivas ou interpretações equivocadas — cruzados com nossas fontes reais |
| **Lacunas** | O que o vídeo não cobriu que nossas fontes permitem cobrir |
| **Padrão estrutural** | Como abre, onde provavelmente perde audiência, como fecha |

O briefing final deve conter:

1. **Top 3 erros/simplificações** mais comuns entre os concorrentes (com a correção baseada em nossas fontes)
2. **Top 3 ângulos que nenhum concorrente explorou** (nossa oportunidade de diferenciação)
3. **Padrão estrutural dominante a evitar** (ex: "todos abrem com histórico do telescópio")

### Fase P — Análise de Performance do Vídeo Anterior

Executada automaticamente pelo prompt v10 antes de cada roteiro. Usa os
dados do vídeo mais recente para calibrar o próximo.

| Passo | Ação | Ferramenta (primária → fallback) |
|---|---|---|
| 1 | Identificar o canal e último vídeo | `vidiq_user_channels` → `channels_getMyChannel` |
| 2 | Obter stats do último vídeo | `vidiq_video_stats` → `analytics_getVideoAnalytics` |
| 3 | Tendências do canal (últimos 28d) | `vidiq_channel_performance_trends` |
| 4 | Gerar diagnóstico: o que funcionou, o que ajustar | Análise IA |

**Nota sobre delay da API:** Para vídeos publicados há < 3 dias, usar
stats em tempo real. Para analytics detalhados, usar o penúltimo vídeo
(que já tem dados processados).

### Regras de uso das fases

- **Foco em gaps, não em cópia** — O briefing existe para identificar o que falta, não o que funciona. Nossa estrutura narrativa já está definida no método e no prompt v10
- **Sempre ancorado em fontes** — Cada erro identificado deve ter a fonte real que o contradiz. Cada lacuna deve ter a fonte real que permite preenchê-la
- **Alimentar o prompt** — O briefing entra como campo variável no prompt v10. O roteiro deve referenciar pelo menos 1 correção explícita e 1 ângulo diferenciador
- **Reutilizar para tags** — Os vídeos encontrados na Fase 0 servem como base para a pesquisa competitiva de tags (evitando busca duplicada)
- **Modelos de escrita** — Antes de iniciar o roteiro, consultar os arquivos em `modelos-de-escrita/` para calibrar o tom narrativo

---

## 1. Escolha do Tema

### Regra de ouro: nunca repetir o sub-tema em vídeos consecutivos

O Singularidade nunca repetiu tema em 20 vídeos. Ciência Todo Dia nunca
repete em 20 consecutivos. O canal já começou a diversificar (Robótica,
Poder/Ética com Sam Altman), mas a maioria dos vídeos ainda é IA +
saúde. O algoritmo precisa de mais sinais temáticos diversos.

### Matriz de Temas

O eixo do canal é **"IA + Ciência + Futuro da Humanidade"**. Dentro desse eixo, há pelo menos 8 sub-nichos com alta demanda e baixa oferta em PT-BR:

| Sub-nicho | Potencial de busca | Exemplo de vídeo | Referência |
|---|---|---|---|
| IA + Espaço/Astronomia | Alto | "A IA Encontrou Algo Estranho nas Fotos do James Webb" | Singularidade: 107K views com "Universo Observável" |
| IA + Física/Cosmologia | Alto | "A IA Resolveu em 3 Dias o que Físicos Não Conseguiram em 50 Anos" | Singularidade: top 4 vídeos são todos de física |
| IA + Medicina/Saúde | Médio | "IA vs Médico: Quem Encontra o Câncer Primeiro?" | Seu melhor Short (312 views) é deste tema |
| IA + Robótica | Médio | "O Robô que Aprendeu a Operar Sozinho" | Já explorado (vídeos 7, 11, 12) — rotacionar |
| IA + Filosofia/Existencial | Alto | "A IA Tem CONSCIÊNCIA? O Que a Ciência Diz de Verdade" | CTD: "O Livre Arbítrio não EXISTE?" = 1.9M views |
| IA + Energia/Clima | Médio | "A IA Descobriu Como Gerar Energia INFINITA?" | Pouca competição em PT-BR |
| IA + Poder/Ética | Alto | "Sam Altman Controla Nosso Futuro — Podemos Confiar Nele?" | Vídeo extra produzido (Sam Altman / New Yorker) |
| IA + Computação Quântica | Médio | "Computador Quântico + IA: O Que Acontece Quando Dois Monstros Se Encontram?" | Singularidade: 912 views com tema quântico (título fraco) |
| IA + História/Arqueologia | Baixo-Médio | "A IA Leu Uma Pedra de 3.000 Anos que Ninguém Conseguia Decifrar" | Oceano azul — quase ninguém faz isso em PT-BR |

### Regra de rotação

Para os próximos 10 vídeos, seguir esta distribuição:

- **Máximo de 2 vídeos por sub-nicho** a cada 10 vídeos
- **Nunca 2 consecutivos** no mesmo sub-nicho
- **Começar pelos sub-nichos de maior potencial**: Espaço, Física, Filosofia (são os que geraram mais views nos concorrentes)
- **Intercalar temas "grandes perguntas"** com temas "descoberta concreta"

### Teste de tema: Fase V + 3 perguntas antes de produzir

Antes de iniciar qualquer vídeo, o tema deve passar pela **Fase V**
(validação com `vidiq_keyword_research` + `vidiq_trending_videos`) e
pelas 3 perguntas abaixo:

1. **"Alguém sem formação técnica se importa com isso?"** Se a resposta for "só especialistas", o tema precisa de um ângulo mais universal. "Vacina mRNA personalizada" → "E Se Existisse Uma Vacina Feita SÓ Para Você?"
2. **"Consigo explicar a premissa em 1 frase de <10 palavras?"** Se não, o tema é complexo demais ou o ângulo está errado. "IA detecta câncer de mama com acurácia de 94.5% em estudo com 80.000 mulheres" → "A IA Viu o Que Nenhum Médico Conseguiu"
3. **"Esse tema toca na identidade ou no medo do espectador?"** Temas que funcionam tocam em algo que o espectador sente: medo de ficar obsoleto, medo da morte, fascínio pelo desconhecido, desejo de entender o universo. "Vacina personalizada" é informativo. "E Se a IA Curar o CÂNCER Antes dos Médicos?" toca no medo.

---

## 2. Construção do Título

### O título é 80% do sucesso do vídeo

Com 0-10 inscritos, o canal depende 100% de busca e sugestões. Ambos dependem de CTR (click-through rate). CTR depende de título + thumbnail. O título é a alavanca mais fácil de melhorar imediatamente.

### Checklist do título (verificar TODOS antes de publicar)

- [ ] **<10 palavras** (MrBeast nunca passa de 10)
- [ ] **Zero jargão** (CTD nunca usa jargão no título — o jargão vai na descrição)
- [ ] **1-2 palavras em CAPS** (CTD: "É possível CURAR a MORTE?", nunca tudo em caps, nunca sem caps)
- [ ] **Tom conversacional** (deve soar como algo que você diria numa conversa, não como manchete de jornal)
- [ ] **Contém pergunta, contradição ou conflito** (Singularidade: "Por Que Existe Um Limite Para o Que Podemos Ver?" > "O Universo Observável e Seus Limites")
- [ ] **Premissa de filme, não resultado** (MrBeast: conta uma história que precisa ser resolvida, não anuncia o final)
- [ ] **Número concreto quando possível** ("80.000 Mamografias em 1 Minuto" > "IA Detecta Câncer")

### 6 fórmulas de título testadas (usar como ponto de partida)

| # | Fórmula | Exemplo para o canal | Fonte |
|---|---|---|---|
| 1 | **Pergunta existencial** | "A IA Pode CURAR a Morte?" | Singularidade + CTD |
| 2 | **X vs Y** | "IA vs Médico: Quem Detecta CÂNCER Primeiro?" | MrBeast |
| 3 | **Contradição/Negação** | "A IA NÃO Vai Substituir Médicos... Vai Algo PIOR" | CTD |
| 4 | **Número impossível** | "A IA Analisou 80.000 Exames em UMA Hora" | MrBeast + dados |
| 5 | **Descoberta + consequência** | "A IA Encontrou ALGO que Nenhum Cientista Esperava" | Singularidade |
| 6 | **E se...** | "E Se a IA Descobrir VIDA Fora da Terra?" | Singularidade |

### Processo: gerar 10, validar com dados, escolher 1

Para cada vídeo:
1. Gere 10 títulos usando as 6 fórmulas acima (o prompt v10 já faz isso)
2. Aplique o checklist em cada um
3. Valide os 3 melhores com `vidiq_keyword_research` (volume, competição)
4. Elimine os que falham em qualquer item
5. Dos restantes, escolha o que você mais gostaria de clicar se visse no feed

### Status no prompt v10 ✅

As 6 fórmulas de título já foram integradas ao prompt v10, substituindo
os templates de manchete ("CONFIRMADO:", "REVELADO:"). A validação com
VidIQ keyword research também já está no pipeline.

---

## 3. Estrutura Narrativa

### Narrativa: escalonamento + DNA Narrativo

O prompt v10 combina a estrutura de 4 blocos escalados com o **DNA
Narrativo** — 7 princípios de escrita que humanizam o roteiro:

1. **História primeiro** — abrir com cenário humano, não com dado
2. **Transições invisíveis** — sem "vamos agora", "a próxima questão"
3. **Ritmo respiratório** — alternar parágrafos longos com frases curtas
4. **Metáfora antes de conceito** — concretizar antes de abstrair
5. **Espectador participante** — perguntas reais, não retóricas
6. **Contra-argumento honesto** — apresentar o melhor argumento contrário
7. **Conclusão como crescendo** — encerrar com emoção, não resumo

Referência completa: `modelos-de-escrita/` + seção VOZ E TOM do prompt v10.

### Escalonamento: a técnica que separa 5 views de 5M views

Todo vídeo do MrBeast que passou de 200M views e todo vídeo do Singularidade que passou de 10K views usa a mesma estrutura:

**A tensão AUMENTA a cada bloco. Nunca diminui. Nunca estabiliza.**

```
Bloco 1: [Fácil / Conhecido]     → "A IA acertou um diagnóstico simples"
Bloco 2: [Difícil / Surpresa]    → "Agora com casos que médicos erraram"
Bloco 3: [Impossível / Virada]   → "A IA encontrou algo que ninguém viu"
Bloco 4: [Consequência / Futuro] → "O que acontece quando isso escala?"
```

### Aplicação prática: template de 4 blocos escalados

| Bloco | Função | Duração | O que acontece |
|---|---|---|---|
| **Bloco 1** | Âncora | 2-3 min | Apresenta o cenário de forma acessível. O espectador pensa "ok, entendo" |
| **Bloco 2** | Escalada | 3-4 min | Introduz o dado ou caso que contradiz o senso comum. O espectador pensa "espera, isso é real?" |
| **Bloco 3** | Clímax | 3-4 min | O dado mais impactante do vídeo. O "número impossível". O espectador pensa "isso muda tudo" |
| **Bloco 4** | Implicação | 2-3 min | O que isso significa para o futuro. Conexão emocional. O espectador pensa "preciso contar isso pra alguém" |

O prompt v10 aplica escalonamento entre blocos + os 7 princípios do DNA
Narrativo dentro de cada bloco.

### Duração alvo

| Formato | Duração alvo | Fundamentação |
|---|---|---|
| **Vídeo longo** | 13-17 minutos | CTD: longos de 1M+ views = 13-17 min. Singularidade: sweet spot = 26-32 min, mas para canal novo sem base, 13-17 min é mais seguro para retenção |
| **Short** | 45-60 segundos | Seus Shorts de ~1 min performam bem. Manter |

O prompt v10 já mira 13-17 min nos longos.

---

## 4. Cadência de Publicação

### Cadência atual: 1 longo/semana + 2-3 Shorts/semana

A fase inicial de 7 vídeos em 2 semanas era insustentável. A cadência
estabilizou em 1 longo por sábado + 2-3 Shorts durante a semana.

### Cadência recomendada

| Conteúdo | Frequência | Dia sugerido |
|---|---|---|
| **1 vídeo longo** | Por semana | Sábado (maior audiência BR) |
| **2-3 Shorts** | Por semana | Terça + Quinta (+ Quarta em semanas de tema quente) |

**Total: 1 longo + 2-3 Shorts por semana = ~13 publicações/mês**

O tempo por longo deve incluir o pipeline completo:
1. **Fase V**: validação do tema com VidIQ (15 min)
2. **Fase 0**: análise competitiva com transcripts e comentários (1 hora)
3. **Fase P**: diagnóstico do vídeo anterior (15 min)
4. **Título**: 10 opções + validação `vidiq_keyword_research` (30 min)
5. **Roteiro**: geração com prompt v10 + revisão DNA Narrativo (2-3 horas)
6. **Thumbnail**: 2-3 variações (1 hora)
7. **SEO**: tags com VidIQ + descrição otimizada + legendas (30 min)

---

## 5. Funil Short → Longo

### Evolução do funil

Os Shorts evoluíram de 159 views de média para 1.000+ após a aplicação
de títulos CAPS + contradição. A conversão Short → Longo ainda é baixa
(1.294 Short → 11 Longo), mas já existe. O próximo passo é sistematizar.

### O funil de 3 passos

```
[Short teaser] → [Short standalone] → [Vídeo longo]
     ↓                    ↓                   ↓
  Cria demanda      Gera views/subs      Monetização + autoridade
```

### Estrutura do ciclo de conteúdo

Para cada vídeo longo, produzir 4 Shorts que formam um funil:

| Short | Timing | Função | Estrutura |
|---|---|---|---|
| **Short 1** (Teaser) | 3 dias ANTES do longo | Criar demanda | Dado mais impactante do vídeo + "vídeo completo em breve" |
| **Short 2** (Standalone) | 1 dia ANTES do longo | Gerar views independentes | Caso ou dado secundário do tema, funciona sozinho |
| **Short 3** (Lançamento) | Mesmo dia do longo | Converter para o longo | Pergunta que só o vídeo longo responde + CTA direto |
| **Short 4** (Reprise) | 3-5 dias DEPOIS do longo | Capturar audiência tardia | Clip do momento mais impactante do longo |

### CTAs nos Shorts

Cada Short deve ter CTA específico, nunca genérico:

- **Genérico (não usar):** "Se inscreva no canal"
- **Específico (usar):** "No vídeo completo, eu mostro o dado que mudou tudo. Link no perfil."

### Títulos de Short: mesmas regras dos longos

Aplicar o mesmo checklist da Seção 2. Os Shorts com melhor performance no canal ("IA detectou cânceres que médicos não viram" = 312 views) já seguem o padrão de conflito humano.

---

## 6. Métricas e Metas

### Métricas que importam nesta fase

O canal tem <10 inscritos. Não faz sentido medir subscribers/mês ainda. As métricas que importam agora são as que o algoritmo usa para decidir se distribui o vídeo:

| Métrica | Meta | Como medir | Por que importa |
|---|---|---|---|
| **CTR (Click-through rate)** | >5% | YouTube Studio → Analytics | Se <5%, título/thumbnail não estão funcionando |
| **Retenção média** | >40% (longos), >70% (Shorts) | YouTube Studio → Retenção | Se <40%, a narrativa perde o espectador |
| **Like ratio** | >3% | Likes / Views | Benchmark: Singularidade = 3.5%, CTD = 5-10% |
| **Views por vídeo (longos)** | >200 até vídeo 15 | YouTube Studio | Se atingir, o canal está sendo distribuído |
| **Views por Short** | >1.000 até Short 20 | YouTube Studio | Shorts são o motor de crescimento (meta ajustada — já atingida) |

### Metas progressivas (primeiros 3 meses)

| Período | Meta principal | Meta secundária |
|---|---|---|
| **Mês 1** (vídeos 8-11) | >200 views/longo, >1K views/Short | 1 comentário por vídeo |
| **Mês 2** (vídeos 12-15) | >500 views/longo, >2K views/Short | 50 inscritos |
| **Mês 3** (vídeos 16-19) | >1K views/longo, >5K views/Short | 200 inscritos, 1 vídeo >5K views |

Metas de Shorts ajustadas para cima — a aplicação de CAPS + contradição
já levou os Shorts para 1.000+ views.

### Revisão mensal

No final de cada mês, verificar:

1. **Qual vídeo performou melhor?** Analisar por que (tema? título? Short teaser?)
2. **Qual vídeo performou pior?** Analisar por que (tema repetido? título descritivo? sem Short de apoio?)
3. **CTR está acima de 5%?** Se não, o problema é título/thumbnail
4. **Retenção está acima de 40%?** Se não, o problema é narrativa/escalonamento
5. **Shorts estão convertendo?** Comparar views do Short teaser com views do longo correspondente

---

## 7. Evolução do Prompt: v8 → v9 → v10

| Área | v8 (original) | v9 (intermediário) | v10 (atual) |
|---|---|---|---|
| **Títulos** | Manchete ("CONFIRMADO:") | 6 fórmulas + checklist | + Validação com `vidiq_keyword_research` |
| **Duração** | 12-15 min | 13-17 min | 13-17 min |
| **Escalonamento** | Não explícito | Blocos escalados | + Scaffold invisível |
| **Análise competitiva** | Não existia | Fase 0 (MCP YouTube) | Fase 0 (VidIQ primário + YouTube fallback) |
| **Performance** | Não existia | Fase P (MCP YouTube) | Fase P (VidIQ primário + YouTube fallback) |
| **Validação de tema** | Não existia | Não existia | Fase V (`vidiq_keyword_research` + `vidiq_trending`) |
| **Humanização** | Básica | Anti-IA + Assimetria | DNA Narrativo (7 Princípios) + Modelos de escrita |
| **Tags/SEO** | Manual | Competitiva | `vidiq_keyword_research` (volume, competição, score) |
| **CTA** | Genérico | Específico | Crescendo emocional + CTA específico |

Todas as recomendações da v1.0 deste método foram implementadas.

---

## Resumo Executivo: Os 14 Mandamentos

0. **Validar tema com dados antes de produzir** (Fase V: `vidiq_keyword_research` + trending)
1. **Analisar concorrentes antes de escrever** (Fase 0: outliers, transcripts, comentários, lacunas)
2. **Analisar performance do vídeo anterior** (Fase P: o que funcionou, o que ajustar)
3. **Nunca repetir sub-tema em vídeos consecutivos**
4. **Título = premissa de filme em <10 palavras, com 1-2 CAPS cirúrgicos**
5. **Validar títulos com `vidiq_keyword_research`** (volume + competição)
6. **Teste de tema: 3 perguntas antes de produzir**
7. **Escalonamento progressivo entre blocos (tensão sempre sobe)**
8. **Aplicar os 7 Princípios do DNA Narrativo em cada roteiro**
9. **Consultar modelos de escrita antes de gerar o roteiro**
10. **1 longo por semana + 2-3 Shorts por semana**
11. **CTA específico, nunca genérico. Encerramento como crescendo emocional**
12. **13-17 min nos longos, 45-60s nos Shorts**
13. **Like ratio >3%, CTR >5%, Retenção >40%**

---

## Próximo Passo

Seguir o [Cronograma de Maio 2026](cronograma-maio-2026.md) usando o
prompt v10. Pipeline para cada vídeo:

1. **Fase V** — validar tema com VidIQ
2. **Fase 0** — análise competitiva (outliers, transcripts, comentários)
3. **Fase P** — performance do vídeo anterior
4. **Consultar modelos de escrita** (`modelos-de-escrita/`)
5. **Gerar roteiro** com prompt v10 (inclui títulos, tags, SEO, script)
6. **Revisar DNA Narrativo** — checklist de 20 itens do prompt v10
7. **Produzir 2-3 Shorts** da semana
8. **Publicar e medir** com métricas da Seção 6
