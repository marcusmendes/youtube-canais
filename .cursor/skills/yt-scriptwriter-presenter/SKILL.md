---
name: yt-scriptwriter-presenter
description: >-
  Roteiro para Marcus falar em câmera (teleprompter), sem ElevenLabs.
  Mesmo DNA narrativo que /yt-scriptwriter. Use quando o usuário
  invocar /yt-scriptwriter-presenter com um tema.
---

# YT Scriptwriter Presenter — Roteiro em Câmera

## Quando usar

O usuário invoca `/yt-scriptwriter-presenter "tema"` quando o vídeo
será gravado com **Marcus em A-roll** (e B-roll quando indicado), e
**não** com narração sintetizada pela ElevenLabs.

Para **voz-over + ElevenLabs**, use `/yt-scriptwriter` (agente
separado).

## Workflow

Lance o subagent **`/yt-scriptwriter-presenter`** passando:

- O tema fornecido (e o `slug` da pasta `output/videos/{slug}/` se
  estiver no pipeline)
- Contexto adicional se disponível (Fase N, metadados, dossier,
  Performance, Competitiva)

O subagent gera o pacote de roteiro no formato **teleprompter**:
marcadores `[A-ROLL]` / `[B-ROLL]`, `VISUAL:` **não genérico**,
`[pausa]` / `[ênfase]`, blocos **B1–B4** explícitos (com **Bloco 4 denso e conclusivo**, sem pressa), **CTAs** nas
posições da Fase Q, contagem real de palavras faladas (**mínimo 1.500**
para longos, sem teto rígido para garantir respiro narrativo), **Auditoria 30s**, mapa de loops (~250–400 palavras),
linha do **modelo de escrita** lido, mapeamento **claim → fonte** do
`02-research.md` (somente veículos do índice do dossiê).

Salva em `output/videos/{slug}/07-script-presenter.md` (pipeline) ou
exibe na conversa (avulso). **Nome canônico:** `07-script-presenter.md`
(evitar `07-scriptwriter-presenter.md`).

Após conclusão, apresente o roteiro completo ao usuário.
