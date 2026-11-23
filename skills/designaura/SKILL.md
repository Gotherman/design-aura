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

1. Leia e siga a skill **design-aura** inteira (o `SKILL.md` instalado ao lado deste, em `design-aura`). Ela e o processo completo (`v2.4.1`). Este comando dispara o fluxo.
2. Inspecione o projeto aberto antes de perguntar qualquer coisa: repositorio, planejamento (`CONCEPCAO.md`, PRD, proposta), rotas (HTML ou SPA React/Vite/Next), telas existentes, tokens, marca e componentes.
3. Se ja houver telas ou um visual feito, o trabalho e **remodelar com autopsia seletiva**. Diga isso numa frase. Identifique objetivamente o que falha nas telas atuais e o que funciona no fluxo do produto. **Nunca** use "remodelar" como pretexto para proibir cards/superficies `Z2`, graficos interativos OSS, icones vetoriais Duotone, cores vivas da marca ou densidade operacional real.
4. Se nao houver tela nenhuma, o trabalho e criar do zero a partir do planejamento ou da ideia.
5. **Entrevista curta obrigatoria em portugues claro, sem jargao (nunca pule silenciosamente nem atropele duvidas):** em uma unica rodada objetiva com opcao recomendada e traducao pratica de 1 linha em cada pergunta, cubra:
   - Em remodelacao: o que mais incomoda nas telas atuais vs o que preservar;
   - Tema principal, **marca presente dentro do workspace** (fim do monobloco cinza no Dark e do tudo-branco no Light) e **paridade semantica** (vermelho real = falha nos dois temas, nunca rosa; verde esmeralda = sucesso; ambar = atencao);
   - **Fluxo zero-treinamento & Resize In-Place** para telas densas (*Fila Limpa -> clique abre Conferencia Focada na mesma area*, max. 2 barras no topo, zero duplicacao e zero jargao tecnico);
   - Papel do Mobile (app executivo/operacional focado com hero <= 38% da tela vs rotinas adaptadas);
   - Tipografia executiva (`Geist`/`Inter` com numeros tabulares proporcionais + mono so em codigos) e detalhes sutis do dominio;
   - **Modelo do Orquestrador e modelo dos subagentes construtores/testers** (obrigatorio confirmar).
   - **Trava Anti-Atropelo:** se o usuario responder *"nao entendi"* ou *"como assim?"* em qualquer pergunta, **PARE, explique em portugues simples com exemplos praticos e confirme antes de gerar a Biblia!**
6. Na Onda 0, rode `discover_oss_components.py --scan <caminho-do-projeto>`, grave o **Contrato de plataforma** + **Orcamentos de Composicao & Anti-Poluicao** na `DESIGN-BIBLE.md` (autossuficiente), compile `tokens.css` (`generate_tokens.py` + `audit_contrast.py --strict` verde, sem `DA-SEMANTIC-HUE-PARITY`, `DA-DARK-FLAT-MONOLITH` nem `DA-LIGHT-WASHED-OUT`), feche `screen-manifest.json` e gere `DESIGN-BIBLE.pdf` **visual** (`render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css`). **Pare para aprovacao da Biblia.**
7. Apos aprovacao da Biblia, execute a **Onda 0.5 (Telas-Mae + `SHELL-CONTRACT.md`)**, construa as telas na **Onda 1** (`1–3` telas/subagente + Fast-Audit imediato), execute a **Fase 4 obrigatoria** (`entrega.html` + `fluxo.html` + `preview.html` + `index.html` + auditoria global com `--smoke-interact`), e finalize na **Fase 4.5 (Onda 3 · Subagentes Testers E2E Read-Only com `run_workflow_probe.mjs` -> Triagem & Plano do Orquestrador -> Fixers -> Re-teste, max. 2 ciclos)** entregando em **1 link unico via `serve_entrega.mjs`**.
