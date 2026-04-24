# QA Report — "A IA Mais PERIGOSA do Mundo Ainda Não Existe"

**Canal:** Marcus Maciel | IA & Ciência
**Vídeo:** Longo #9 — Semana 3 de maio 2026
**Attempt:** 2
**Data:** 2026-04-24

---

## Resumo

| Métrica | Valor |
|---|---|
| **Passed** | 29 |
| **Failed** | 0 |
| **Skipped** | 1 |
| **Total** | 30 |

---

## Verificação das Correções do Attempt 1

| # | Correção solicitada | Status | Evidência |
|---|---|---|---|
| 1 | Item 23 — Adicionar `[pausa]` e `[ênfase]` | ✅ Corrigido | 8 marcações `[pausa]` (1s e 2s) distribuídas pelo Hook, B1, B2, B3, CTA Comentário, B4. 4 marcações `[ênfase]` em B1 ("Sobre-humano"), B3 ("a última invenção da humanidade", "terrivelmente eficaz", "Não trinta") e B4 ("poder sem governança"). Supera o mínimo de 5 pausas + 3 ênfases. |
| 2 | Item 26 — Datas por extenso na narração | ✅ Corrigido | Todas as datas convertidas: "dois mil e vinte e três", "dois mil e quatorze", "dois mil e vinte e quatro", "dois mil e vinte e cinco", "dois mil e vinte e seis". Percentuais também: "noventa e nove por cento", "trinta por cento", "cinco por cento", "duzentos e cinquenta por cento". Anos em dígitos mantidos nas linhas VISUAL e seções de fontes (correto). |
| 3 | Item 28 — Nota "Altered content" | ✅ Corrigido | Seção "Nota de Upload — YouTube Studio" adicionada ao final do roteiro com checklist: `[ ] Marcar "Altered or synthetic content"` + motivo. |
| 4 | Item 30 — Session Architecture | ✅ Corrigido | Seção completa "Session Architecture — Longo #9" com: Playlist 1 (IA e o Futuro), Playlist 2 (Para Começar), Comentário fixado com pergunta + link playlist, End-screen (Neuralink), Card aos 60% (~7:48). |

**Nenhum novo problema introduzido pelas correções.** As marcações de pausa/ênfase não quebraram o ritmo respiratório (P3). As datas por extenso fluem naturalmente na narração PT-BR.

---

## Tabela de Resultados

| # | Verificação | Status | Detalhe |
|---|---|---|---|
| 1 | Metadados completos | `pass` | 10 títulos (6 fórmulas) + Top 3 com justificativa + thumbnail (7 seções) + post comunidade (143 palavras) + 3 hashtags + 12 tags (todas com volume > 0) + descrição SEO (338 palavras). Tudo presente. |
| 2 | Títulos validados | `pass` | Todos ≤55 chars (máx 52), ≤10 palavras (máx 10), zero jargão (sem "AGI" ou "superinteligência" nos títulos), 1 CAPS cada, tom conversacional. |
| 3 | Contagem de palavras | `pass` | ~1.766 palavras (narração). Dentro do intervalo 1.400-2.000. |
| 4 | Seções presentes | `pass` | Hook (0-3s) + Contexto (3-15s) + Bloco 1 (Âncora) + Bloco 2 (Escalada) + Bloco 3 (Clímax) + Bloco 4 (Implicação) + CTA Comentário + CTA Final. Mapa de Open Loops + Auditoria de Retenção + Checklist DNA Narrativo + Fontes Citadas. |
| 5 | Escalonamento progressivo | `pass` | Âncora (O que é AGI) → Escalada (Corrida OpenAI/DeepMind/Anthropic/China) → Clímax (Bostrom, explosão de inteligência, alinhamento) → Implicação (Russell, terceira via, governança). Transições invisíveis: "A distância entre o que temos... é um abismo" (B1→B2), "Mas existe uma terceira via" (B3→B4). |
| 6 | VISUAL em todos os blocos | `pass` | Cada seção narrativa possui marcação `VISUAL:` com descrição específica. Hook (1), Contexto (1), Bloco 1 (3), Bloco 2 (4), Bloco 3 (4), Bloco 4 (3), CTA Final (2). Total: 18 direções visuais. |
| 7 | Camada Visual Permanente | `pass` | Paleta consistente: azul escuro #0A1628 + azul elétrico #00A3FF em todo o roteiro. Estilo fotorrealista/cinematográfico mantido. Atmosfera documental sombria coerente com a thumbnail (que usa #6D0000 vermelho — diferenciação deliberada). |
| 8 | Loops de retenção | `pass` | 7 open loops mapeados. 4 loops nos primeiros 60s (loops 1-4). Nenhum loop aberto > 5 min. Densidade: ~1 loop a cada 250 palavras. Dentro do critério (≥1 a cada 250-400 palavras). |
| 9 | Credibilidade científica | `pass` | Zero especulação como fato. Fontes com ano: Bostrom (2014/2024), DeepMind Morris et al. (2023/2025), Russell (2019/2026), Bengio (2025), Anthropic (2026), Katja Grace et al. (2024), OpenAI Blog. Correção explícita do p(doom) 30%→5% com citação do survey real. |
| 10 | Descrição SEO | `pass` | 338 palavras (intervalo 250-400). Hook na linha 1, keyword "IA"/"inteligência artificial"/"AGI" 4x, timestamps, fontes, CTA de inscrição com link, 3 hashtags. |
| 11 | Post comunidade | `pass` | 143 palavras (≤150). 4 partes: abertura com dado impossível ("Existe uma probabilidade real..."), expansão com tensão + dado numérico (5%-30%), CTA ("O vídeo sai sábado"), pergunta para comentários. 1 emoji (≤2). |
| 12 | Thumbnail completa | `pass` | 7 seções: Identity Anchor, Composition B (Visual Protagonista), Presenter (N/A), Paleta Emocional (Documental Sombria), Text Overlay (0 palavras), Style Close, Anti-Padrões. Composição B alternada com vídeo anterior. |
| 13 | Sub-nicho diferente | `pass` | Último vídeo: IA + Corpo/Neuralink. Este vídeo: IA + Futuro/AGI. Sub-nichos diferentes. |
| 14 | Função do Short | `skip` | Este é um vídeo longo. Short companion não faz parte deste pipeline de QA. |
| 15 | Fase P executada | `pass` | Diagnóstico completo em `01-performance.md`. 4 calibrações incorporadas: (1) front-load dado existencial nos primeiros 60s; (2) CTA de comentário antes do payoff principal (entre B2 e B3); (3) pattern interrupts em blocos técnicos (lâmpada, corrida nuclear, avião 5%, 3,8 bilhões de anos); (4) duração ≤2.000 palavras (1.766). |
| 16 | Fase 0 executada | `pass` | 5 concorrentes analisados (≥3). ≥1 correção: p(doom) 30%→5% (Erro 3 da competitiva). ≥1 ângulo inédito: corrida geopolítica EUA/China + framework DeepMind Levels + paradigma de Russell. Todos incorporados no roteiro. |
| 17 | Validação de tema | `pass` | Keyword "agi" validada com overall 67.6, volume 258.971/mês. 5 keywords validadas, todas com overall ≥50. |
| 18 | DNA Narrativo — 8 Princípios | `pass` | **P1** História primeiro: narrativa contínua sem rótulos. **P2** Transições invisíveis: "A distância... é um abismo" (B1→B2), "Mas a corrida não é só entre empresas americanas" (B2 interno), "Mas existe uma terceira via" (B3→B4). **P3** Ritmo respiratório: frases curtas ("É outra coisa", "Ela não seria má", "Um ciclo") alternadas com longas (≥25 palavras). **P4** Metáfora antes de conceito: lâmpada→IA estreita, colega→AGI, espelho infinito→auto-aprimoramento, avião 5%→risco. **P5** Espectador como participante: "nós estamos entre o Nível 1 e o Nível 2", "estamos presos". **P6** Contra-argumento honesto: correção p(doom), "Desligar não funciona", "LLMs tropeçam". **P7** Conclusão como crescendo: doom/utopia → terceira via → poder sem governança → CTA. **P8** Fator de agência: IA incerta que "pediria para ser desligada", CTA "você confiaria?" |
| 19 | Revisão anti-IA | `pass` | Nenhuma frase-molde detectada. Bridges não se repetem — cada transição usa mecanismo diferente: abismo, "mas a corrida não é só", "mas existe uma terceira via", "então estamos presos". Linguagem natural e específica. |
| 20 | Modelo de escrita consultado | `pass` | Modelos `IA+Futuro-01.md` e `IA+Futuro-02.md` consultados. Roteiro reflete: (1) fluidez narrativa sem interrupções didáticas; (2) metáforas concretas (lâmpada, colega, espelho infinito); (3) alternância dados/narrativa; (4) escalada progressiva de complexidade. |
| 21 | Especificidade visual | `pass` | Nenhum VISUAL genérico. Todos incluem composição específica, objetos concretos, paleta com hexadecimais (#0A1628, #00A3FF), referências de câmera/lente, atmosfera descrita. Exemplos: "linhas de código refletidas em pupilas humanas", "espelho infinito de cérebros digitais", "barra de progresso quase completa (98%)". |
| 22 | Disclosure IA | `pass` | "Imagens ilustrativas geradas por inteligência artificial." presente na descrição SEO (metadados). |
| 23 | Teste de voz alta | `pass` | **Corrigido no attempt 2.** 8 marcações `[pausa]` distribuídas: Hook (2×), B1 (1×), B2 (1×), B3 (2×), CTA Comentário (1×), B4 (1×). 4 marcações `[ênfase]` em pontos de impacto: B1 ("Sobre-humano"), B3 ("a última invenção da humanidade", "terrivelmente eficaz", "Não trinta"), B4 ("poder sem governança"). Marcações nos pontos de maior impacto emocional sem quebrar o ritmo respiratório. |
| 24 | Camada de Retenção | `pass` | Auditoria 30s completa: hook entrega dado existencial em ≤3s, primeiro VISUAL específico, ≥1 dado numérico nos primeiros 15s ("oitenta quilômetros", "três empresas"), loop aberto sem resolver. 5 pattern interrupts: lâmpada (B1), corrida nuclear (B2), avião 5% (B3), 3,8 bilhões de anos (B3), "quem decide?" (B4). 7 open loops mapeados. |
| 25 | CTAs na narração | `pass` | CTA 1 (engajamento): entre B2 e B3 — "Me diz nos comentários: você confiaria numa IA que decide sozinha?" antes do payoff Bostrom. CTA 2 (inscrição): CTA Final — "Se inscreve no canal". CTA 3 (próximo vídeo): últimos 10s — gancho sobre "IA que toma decisões que nenhum humano consegue entender". |
| 26 | Voice-over + tradução | `pass` | **Corrigido no attempt 2.** Todas as datas escritas por extenso na narração: "dois mil e vinte e três", "dois mil e quatorze", "dois mil e vinte e quatro", "dois mil e vinte e cinco", "dois mil e vinte e seis". Percentuais por extenso: "noventa e nove por cento", "trinta por cento", "cinco por cento", "duzentos e cinquenta por cento". Dígitos mantidos nas linhas VISUAL e seções de metadata (correto). Sem contrações inadequadas. |
| 27 | Manifesto de Diferenciação | `pass` | Presente no Bloco 4, parágrafo 5: "Este vídeo é o único que estou vendo, neste momento, que mapeia a corrida pela superinteligência como uma disputa geopolítica real, com um framework concreto de níveis para situar onde estamos, e que propõe o paradigma de Russell como alternativa ao binário apocalipse ou paraíso." Parafraseado — não copiado literalmente. |
| 28 | Label "Altered content" | `pass` | **Corrigido no attempt 2.** Seção "Nota de Upload — YouTube Studio" presente no final do roteiro com checklist: `[ ] Marcar "Altered or synthetic content" nas configurações avançadas do vídeo` + motivo ("todas as imagens são geradas por IA"). |
| 29 | Stress Test título ↔ thumbnail (Intrigue Gap) | `pass` | Título "A IA Mais PERIGOSA do Mundo Ainda Não Existe" afirma resultado (algo perigoso está vindo). Thumbnail mostra instante ANTES: sala de servidores com terminal a 98%, luz vermelha. Validação: "Se apago o título, a thumbnail gera a pergunta 'O que está sendo carregado nesse terminal?'. Só o título responde." Gap temporal correto, sem redundância. |
| 30 | Session Architecture (FASE S) | `pass` | **Corrigido no attempt 2.** Seção completa no roteiro: Playlist 1 ("IA e o Futuro: AGI, Superinteligência e o Que Vem Depois"), Playlist 2 ("Para Começar"), Comentário fixado com pergunta provocativa + link playlist, End-screen para Neuralink (melhor performance), Card aos 60% (~7:48) para Longo #extra ou Cirurgião Robô. |

---

## Veredicto

### `approved` ✅

**0 falhas no attempt 2.** Todas as 5 correções do attempt 1 foram aplicadas corretamente. Nenhum novo problema introduzido. Roteiro e metadados estão prontos para produção.

---

## Notas

### Correções Verificadas

As 4 correções solicitadas (itens 23, 26, 28, 30) foram todas aplicadas com qualidade:

1. **Item 23** — Marcações de pausa/ênfase bem distribuídas e posicionadas nos momentos de maior impacto emocional, sem prejudicar o ritmo respiratório (P3 do DNA Narrativo).
2. **Item 26** — Datas e percentuais convertidos por extenso apenas no texto narrado, mantendo dígitos nas linhas VISUAL e seções técnicas. Leitura natural em PT-BR.
3. **Item 28** — Nota de upload clara e acionável com checkbox para o YouTube Studio.
4. **Item 30** — Session Architecture completa com playlists, comentário fixado, end-screen e card — todos com justificativa estratégica.

### Pontos Fortes do Material

- **Credibilidade científica exemplar:** 7 fontes reais com ano, incluindo correção explícita do p(doom) 30%→5% (Katja Grace et al., 2024).
- **Diferenciação clara:** Único vídeo no nicho que combina framework DeepMind Levels + geopolítica EUA/China + paradigma de Russell.
- **Retenção engenheirada:** 4 loops nos primeiros 60s, 5 pattern interrupts, CTA de comentário antes do payoff principal.
- **Intrigue Gap validado:** Título e thumbnail criam gap temporal sem redundância.

---

*QA concluída. Attempt 2: 29 pass, 0 fail, 1 skip. Roteiro aprovado para produção.*
