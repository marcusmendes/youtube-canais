---
name: yt-qa
description: >-
  Revisão de qualidade (38 itens) para vídeo do canal Marcus Maciel
  | IA & Ciência. Valida roteiro e metadados. Use quando o usuário
  invocar /yt-qa.
---

# YT QA — Checklist de Validação Avulso

## Quando usar

O usuário invoca `/yt-qa` após ter metadados e roteiro gerados.

## Workflow

Lance o subagent **`/yt-qa`** passando:
- Os metadados completos (títulos, thumbnail, descrição, tags)
- O roteiro completo

O subagent executa os 38 itens da checklist (incluindo Intrigue Gap,
Session Architecture, compliance médico e narrativa/storytelling) e
retorna o veredicto.

Após conclusão, apresente:
- Resumo (passed/failed/total)
- Veredicto (approved, needs_fix, approved_with_warnings)
- Itens que falharam com detalhes
- Instruções de correção se aplicável
