---
name: yt-repackaging
description: >-
  Repackaging de vídeo underperforming do canal Marcus Maciel | IA
  & Ciência. Diagnostica e propõe novos título, thumbnail, descrição
  e tags. Use quando o usuário invocar /yt-repackaging com um video ID.
---

# YT Repackaging — Otimização de Vídeo

## Quando usar

O usuário invoca `/yt-repackaging VIDEO_ID` (ex: `/yt-repackaging daK_7PofxMU`).

## Workflow

1. Lance o subagent **`/yt-repackaging`** passando:
   - O `VIDEO_ID` fornecido pelo usuário
   - O handle do canal: `@MarcusMacielIAeCiencia`
   - Instrução para salvar output em `output/repackaging/{video_id}_{timestamp}.md`

2. O subagent irá:
   - Buscar dados do vídeo via VidIQ e YouTube
   - Comparar com baseline do canal
   - Diagnosticar problemas no título, thumbnail, descrição e tags
   - Gerar propostas completas de repackaging
   - Salvar o resultado

3. Após conclusão, apresente ao usuário:
   - Resumo do diagnóstico
   - Títulos propostos (top 3)
   - Prompt da thumbnail
   - Caminho do arquivo salvo

## Notas

- A memória do canal (baseline, última thumbnail) é injetada pelo
  hook `sessionStart`
- O subagent valida todas as tags com `vidiq_keyword_research`
