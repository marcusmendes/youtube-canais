---
name: yt-research
description: >-
  Pesquisa de fontes primárias para vídeo do canal Marcus Maciel |
  IA & Ciência. Usa WebSearch e WebFetch para buscar papers, artigos,
  notícias e dados concretos. Gera dossier estruturado em
  output/videos/{slug}/02-research.md.
---

# Skill — Pesquisa de Fontes Primárias (Fase F)

## Quando usar

- O usuário pede `/yt-research "tema"`
- Dentro do pipeline, após Performance e antes de Competitiva
- Quando qualquer fase precisar de fontes verificáveis

## Ferramentas utilizadas

- **WebSearch** — busca em Google Scholar, Nature, Science, MIT Tech
  Review, IEEE Spectrum, arxiv, PubMed
- **WebFetch** — extrai conteúdo de URLs encontradas para verificação

## Fluxo

1. Decompor tema em 3-5 eixos de pesquisa
2. Para cada eixo, buscar em 3 camadas (papers, divulgação, notícias)
3. Verificar e extrair dados de cada fonte via WebFetch
4. Classificar potencial narrativo de cada dado
5. Identificar lacunas e micro-histórias
6. Gerar dossier estruturado

## Output

Arquivo: `output/videos/{slug-do-tema}/02-research.md`

Seções: Resumo executivo, Eixos de pesquisa (com fontes detalhadas),
Dados de impacto, Micro-histórias potenciais, Lacunas/alertas,
Fontes para descrição SEO.

## Requisitos mínimos

- 8+ fontes verificadas (ideal 12-15)
- 2+ papers peer-reviewed
- 1+ dado "número impossível"
- 1+ caso humano concreto
- Toda fonte preprint sinalizada
