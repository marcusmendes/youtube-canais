---
name: yt-calendar
description: >-
  Geração de cronograma mensal de conteúdo para o canal. Pesquisa
  trending, outliers e keywords para gerar temas validados com
  rotação de sub-nichos, Shorts e metas. Use quando o usuário
  invocar /yt-calendar.
---

# YT Calendar — Cronograma Mensal

## Quando usar

O usuário invoca `/yt-calendar "mês ano"`.

Exemplos:
- `/yt-calendar "junho 2026"`
- `/yt-calendar "julho 2026" foco em IA + medicina`
- `/yt-calendar "agosto 2026" 5 longos, 3 shorts por semana`

## Workflow

Lance o subagent **`yt-calendar`** passando como contexto:
- O mês/ano solicitado
- Quantidade de vídeos longos (default: 4)
- Shorts por semana (default: 2)
- Foco temático ou exclusões (se informados)

O subagent executa 5 fases automaticamente:
1. **Fase 1 — Contexto:** últimos uploads, memória do canal,
   calendários anteriores
2. **Fase 2 — Descoberta:** outliers, trending, keywords,
   comentários, breakout channels
3. **Fase 3 — Geração:** 10-15 candidatos com scores
4. **Fase 4 — Filtragem:** rotação de sub-nichos, arco narrativo,
   Checklist de Ouro
5. **Fase 5 — Montagem:** cronograma completo com datas reais,
   Shorts, títulos, fontes e metas

Após conclusão, apresente ao usuário:
- A visão geral do mês (grade visual)
- A rotação de sub-nichos com arco narrativo
- O detalhamento de cada semana (tema + títulos + escalonamento)
- A grade de Shorts
- As metas do mês
- O link para o arquivo salvo em `output/calendar/`

## Integração com pipeline

Cada tema aprovado no cronograma pode ser executado com:
```
/yt-pipeline "tema da semana N"
```

Ou executar fases individuais:
```
/yt-validation "keyword do tema"
/yt-competitive "tema"
/yt-scriptwriter (com tema + fontes do cronograma)
```
