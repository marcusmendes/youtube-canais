---
name: yt-metadata
description: >-
  Geração de metadados (títulos, thumbnail, descrição, tags) para
  vídeo do canal Marcus Maciel | IA & Ciência. Use quando o
  usuário invocar /yt-metadata com um tema.
---

# YT Metadata — Metadados Avulso

## Quando usar

O usuário invoca `/yt-metadata "tema"` (ex: `/yt-metadata "IA na cirurgia robótica"`).

## Workflow

Lance o subagent **`/yt-metadata`** passando:
- O tema fornecido
- Contexto adicional se disponível (resultados de Performance,
  Competitiva, Validação)

O subagent gera o pacote completo: 10 títulos (6 fórmulas), thumbnail
(Master Prompt v2 **e** tabela **7 seções** checklist QA), descrição SEO
**250–400 palavras** com disclosure de IA, tags com volume, **hashtags
em linha dedicada**, post comunidade, comentário fixo com **URL de
playlist**, seção **Session Architecture (Fase S)** e nota de conteúdo
alterado no Studio quando couber.

Após conclusão, apresente os metadados completos ao usuário.
