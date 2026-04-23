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

O subagent gera o pacote completo: 10 títulos (6 fórmulas),
thumbnail prompt, descrição SEO, tags com volume, hashtags e post
comunidade.

Após conclusão, apresente os metadados completos ao usuário.
