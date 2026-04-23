---
name: yt-validation
description: >-
  Validação de tema/keyword para vídeo do canal Marcus Maciel | IA
  & Ciência. Fase V avulsa. Use quando o usuário invocar
  /yt-validation com uma keyword.
---

# YT Validation — Validação de Tema Avulsa

## Quando usar

O usuário invoca `/yt-validation "keyword"` (ex: `/yt-validation "computação quântica"`).

## Workflow

Lance o subagent **`/yt-validation`** passando a keyword fornecida.

O subagent usa `vidiq_keyword_research` para avaliar volume,
competition e overall, aplica o Checklist de Ouro, e retorna o
veredicto: approved, low_demand ou rejected.

Após conclusão, apresente: dados da keyword, alternativas, checklist
de ouro e veredicto.
