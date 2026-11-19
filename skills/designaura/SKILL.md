---
name: designaura
description: >-
  Comando /designaura. Use somente quando o usuario digitar /designaura,
  "rode /designaura" ou "rode a skill design aura" para comecar o processo
  no projeto aberto. Nao use sozinho em pedidos genericos de design.
disable-model-invocation: true
---

# /designaura

O usuario acabou de pedir para comecar a Design Aura neste chat. Nao pergunte se deve comecar. Comece.

1. Leia e siga a skill **design-aura** inteira (o `SKILL.md` instalado ao lado deste, em `design-aura`). Ela e o processo completo (`v2.0.0`). Este comando dispara o fluxo.
2. Inspecione o projeto aberto antes de perguntar qualquer coisa: repositorio, planejamento (`CONCEPCAO.md`, PRD, proposta), rotas, telas existentes, tokens, marca e componentes.
3. Se ja houver telas ou um visual feito, o trabalho e **remodelar com autopsia seletiva**. Diga isso numa frase. Identifique objetivamente o que falha nas telas atuais e o que funciona no fluxo do produto. **Nunca** use "remodelar" como pretexto para proibir cards/superficies `Z2`, graficos interativos OSS, icones consistentes, cores vivas da marca ou densidade operacional real.
4. Se nao houver tela nenhuma, o trabalho e criar do zero a partir do planejamento ou da ideia.
5. **Entrevista curta obrigatoria (nunca pule silenciosamente):** em uma unica rodada objetiva com opcao recomendada em cada linha, pergunte os pontos criticos que ainda nao foram respondidos no prompt atual:
   - Em remodelacao: o que mais incomoda nas telas atuais vs o que preservar;
   - Tema principal (Dark-first, Light-first ou ambos);
   - Papel do Mobile (se houver: app focado/executivo dedicado ou mesmas rotinas do desktop adaptadas);
   - Detalhes visuais do dominio (com proposta concreta e recomendada);
   - **Modelo do Orquestrador e modelo dos subagentes construtores** (obrigatorio confirmar).
6. Grave o **Contrato de plataforma**, feche a `DESIGN-BIBLE.md`, compile `tokens.css` (`audit_contrast.py --strict` verde), feche `screen-manifest.json` (preferindo 12–24 telas profundas em vez de cascas vazias) e gere `DESIGN-BIBLE.pdf` **visual** (`render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css`). Entregue os caminhos e **pare para aprovacao da Biblia**.
7. Apos aprovacao da Biblia, execute a **Onda 0.5 (Telas-Mae)**: construa o Design System + **1 Tela-Mae Desktop + 1 Tela-Mae Mobile**, audite com Chromium e valide o padrao visual antes de disparar os subagentes da Onda 1 (limitados a **1–3 telas por subagente**, sem teto artificial de 8 subagentes, com **Fast-Audit imediato do Orquestrador** a cada entrega).
