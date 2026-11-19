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

1. Leia e siga a skill **design-aura** inteira (o `SKILL.md` instalado ao lado deste, em `design-aura`). Ela e o processo completo (`v2.2.1`). Este comando dispara o fluxo.
2. Inspecione o projeto aberto antes de perguntar qualquer coisa: repositorio, planejamento (`CONCEPCAO.md`, PRD, proposta), rotas, telas existentes, tokens, marca e componentes.
3. Se ja houver telas ou um visual feito, o trabalho e **remodelar com autopsia seletiva**. Diga isso numa frase. Identifique objetivamente o que falha nas telas atuais e o que funciona no fluxo do produto. **Nunca** use "remodelar" como pretexto para proibir cards/superficies `Z2`, graficos interativos OSS, icones vetoriais Duotone, cores vivas da marca ou densidade operacional real.
4. Se nao houver tela nenhuma, o trabalho e criar do zero a partir do planejamento ou da ideia.
5. **Entrevista curta obrigatoria em portugues claro, sem jargao (nunca pule silenciosamente nem atropele duvidas):** em uma unica rodada objetiva com opcao recomendada e traducao pratica de 1 linha em cada pergunta, cubra:
   - Em remodelacao: o que mais incomoda nas telas atuais vs o que preservar;
   - Tema principal & equilibrio cromatico `65/20/10/5` (marca presente com personalidade nas 3 Zonas + cores harmonicas nos graficos, evitando tanto "tudo azul" quanto "carvao morto");
   - Estrategia anti-poluicao em telas densas desktop (*Lista Limpa -> Detalhe Focado na mesma pagina* como recomendado);
   - Papel do Mobile (app executivo focado vs mesmas rotinas do desktop);
   - Tipografia executiva (`Geist`/`Inter` com numeros tabulares proporcionais + mono so em codigos) e detalhes sutis do dominio;
   - **Modelo do Orquestrador e modelo dos subagentes construtores** (obrigatorio confirmar).
   - **Trava Anti-Atropelo:** se o usuario responder *"nao entendi"* ou *"como assim?"* em qualquer pergunta, **PARE, explique em portugues simples com exemplos praticos e confirme antes de gerar a Biblia!**
6. Na Onda 0, rode `discover_oss_components.py --scan <caminho-do-projeto>` para mapear automaticamente as **16 Categorias Canonicas de UI/UX** (bibliotecas OSS + receitas de graficos/micro-componentes + curadoria de icones anti-generico), grave o **Contrato de plataforma**, feche `DESIGN-BIBLE.md`, compile `tokens.css` (`audit_contrast.py --strict` verde, com `--chart-1..6`, sem `DA-DARK-MONOCHROME` nem `DA-LIGHT-WASHED-OUT`), feche `screen-manifest.json` e gere `DESIGN-BIBLE.pdf` **visual** (`render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css`). **Pare para aprovacao da Biblia.**
7. Apos aprovacao da Biblia, execute a **Onda 0.5 (Telas-Mae + `SHELL-CONTRACT.md`)**: construa o Design System (`tokens.css`, `shell.css` com profundidade de 5 camadas, sidebar minimizavel, `.card-brand-hero`, `.icon-emblem`, `.chip-sla` com anel SVG, `shell.js`), o resumo `SHELL-CONTRACT.md` (~100 linhas) e **1 Tela-Mae Desktop + 1 Tela-Mae Mobile**, audite com Chromium e valide o padrao visual antes de disparar os subagentes da Onda 1 (`1–3` telas por subagente, escrita incremental em turno unico + **Fast-Audit imediato do Orquestrador**).
