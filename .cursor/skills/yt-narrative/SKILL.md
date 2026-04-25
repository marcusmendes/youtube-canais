---
name: yt-narrative
description: >-
  Arquitetura narrativa (Fase N) — converte output analítico de
  P+T+A em storytelling acionável: protagonista, espinha dorsal,
  arco emocional, beat map, cenas, micro-histórias e anti-clichês.
---

# /yt-narrative

Executa a Fase N do pipeline: arquitetura narrativa pré-roteiro.

## Uso

```
/yt-narrative <briefing ou referência ao output P+T+A>
```

## Exemplo

```
/yt-narrative @output/videos/corrida-pela-agi/
```

O subagent `yt-narrative` lê os outputs de performance, validação
e análise competitiva, e gera a arquitetura narrativa com 8 passos:

1. Protagonista (quem o viewer acompanha)
2. Espinha dorsal (3 atos)
3. Arco emocional (mapa emoção por bloco de 2 min)
4. Cenas (lugar, personagem, conflito, revelação)
5. Micro-histórias humanas (2-4 pessoas reais)
6. Motivos visuais recorrentes (2-3)
7. Pares setup/payoff (loops abertos da Fase A)
8. Anti-clichês do nicho (5 com substitutos)

Output salvo em `output/videos/{slug}/04-narrative.md`.

O roteirista (`/yt-scriptwriter`) usa este output como fundação
para escrever o roteiro como HISTÓRIA, não como ensaio.
