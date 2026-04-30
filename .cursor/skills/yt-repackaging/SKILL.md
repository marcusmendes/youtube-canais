---
name: yt-repackaging
description: >-
  Repackaging de vídeo underperforming do canal Marcus Maciel | IA
  & Ciência. Diagnostica armadilhas e delega a geração do novo pacote
  ao agente `yt-metadata` (single source of truth para regras de
  embalagem). Use quando o usuário invocar /yt-repackaging com um
  video ID.
---

# YT Repackaging — Otimização de Vídeo

## Quando usar

O usuário invoca `/yt-repackaging VIDEO_ID` (ex: `/yt-repackaging daK_7PofxMU`).

## Workflow

1. Lance o subagent **`/yt-repackaging`** passando:
   - O `VIDEO_ID` fornecido pelo usuário
   - O handle do canal: `@MarcusMacielIAeCiencia`
   - Instrução para salvar output em `output/repackaging/{video_id}_{timestamp}.md`

2. O subagent `yt-repackaging` irá:
   - Carregar inputs do disco (`output/videos/{slug}/01..04` e
     `06-metadata.md` se existirem)
   - Coletar métricas reais via `analytics_*`, `reporting_*` e VidIQ
   - **Diagnosticar** o pacote v1 (armadilha do título, anti-padrões
     da thumbnail, lacunas da descrição, problemas de tags)
   - Escrever **rationale** (hipótese, mudança proposta, efeito
     esperado, mudança a isolar nesta iteração)
   - Montar **briefing de repackaging** em markdown
   - **Delegar ao subagent `yt-metadata`** (modo repackaging),
     passando o briefing como input no lugar dos arquivos
     `01..04` do pipeline
   - Receber o pacote v2 do `yt-metadata` (10 títulos + Top 3,
     thumbnail prompt 7 seções, descrição SEO completa, tags em
     cluster, post comunidade, comentário fixado)
   - Consolidar Diagnóstico + Rationale + Briefing + Pacote v2 +
     Versionamento + Plano de Iteração no output final
   - Salvar o resultado

3. Após conclusão, apresente ao usuário:
   - Resumo do diagnóstico
   - Mudança a isolar nesta iteração (título / thumbnail / ambos)
   - Top 3 títulos do pacote v2
   - Caminho do arquivo salvo

## Notas

- A memória do canal (baseline, última thumbnail) é injetada pelo
  hook `sessionStart`
- O `yt-repackaging` NÃO escreve o pacote por conta própria — ele
  diagnostica e delega ao `yt-metadata`. Isso garante alinhamento
  com o padrão de embalagem do canal (single source of truth).
- O `yt-metadata` valida todas as tags com `vidiq_keyword_research`
  antes de publicar a tabela final
