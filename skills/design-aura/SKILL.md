---
name: design-aura
description: >-
  Direção visual e construção de interfaces bonitas, sofisticadas e sem cara de IA para apps mobile
  (iOS, Android, React Native, Flutter, PWA), apps desktop, sistemas web e sites. Use sempre que o
  pedido envolver criar, remodelar, polir ou auditar telas, design system, tokens, paleta, tipografia,
  Bíblia de direção visual, protótipos navegáveis, escolha de componentes open source, motion ou
  verificação visual e funcional, mesmo que o pedido não diga "design".
license: MIT
metadata:
  version: "3.1.0"
  author: "Lucas (Gotherman)"
  display-name: "Design Aura"
---

# Design Aura

Esta skill conduz um projeto da leitura do repositório até telas verificadas: entende o trabalho real, propõe direções visuais, fixa a escolhida numa Bíblia, constrói com subagentes e só entrega o que foi visto e testado.

Três ideias seguram o resto:

1. **Cada projeto ganha a própria cara.** Cor, tipografia, forma, densidade, profundidade e composição saem do projeto e da direção escolhida. A skill oferece método e opções, nunca uma pele pronta. Dois produtos só se parecem se o trabalho deles for parecido.
2. **Ofício é universal, gosto é do projeto.** Contraste, foco, alvos de toque, nada cortado ou encoberto e convenções da plataforma valem sempre e podem bloquear. Sinais de gosto (vazio, empilhamento, eco de selos) só pedem revisão com a captura na mão. A camada de cada regra está em `data/rules.json`.
3. **Ver antes de afirmar.** Aprovação exige a captura do estado que motivou o trabalho, nos temas e larguras declarados, mais o fluxo exercitado. O que não foi visto fica como pendente.

Ferramentas locais: Python 3, Node 20+ e Chromium/Chrome. Nenhuma instalação via npm ou pip.

## Escolha o modo e leia só o necessário

| Modo | Quando | Fases | Leia |
|---|---|---|---|
| **Criar** | Ideia, PRD ou planejamento sem telas | F0 → F5 | 01, 02, 03, 06, 09, 10 + plataforma (04, 05 ou 11) |
| **Remodelar** | Telas existem e o pedido é uma direção nova | F0 → F5 (o "antes" é capturado em F0) | igual a Criar |
| **Polir** | Estrutura e fluxos aprovados; o pedido é visual ou de componentes | F0, atualização da Bíblia, pilotos, F3 no recorte, F4 e F4.5 do escopo | 02 (atualização), 06, 07 |
| **Ajuste pontual** | Uma tela, um estado, um componente | F0, correção, verificação do estado afetado | 07 |
| **Upgrade** | A Bíblia tem selo de versão anterior | F0, deltas na Bíblia, pilotos, verificação | 02, 03 (upgrade), `CHANGELOG.md` |

Plataforma: desktop e sistemas web em [04](references/04-desktop-e-sistemas.md), mobile em [05](references/05-mobile-ios-android.md), sites e páginas em [11](references/11-sites-e-paginas.md). Um produto multiplataforma lê os guias das superfícies que existem. Tokens atravessam as plataformas; navegação, densidade e overlay mudam.

`/designaura` dispara o mesmo processo no projeto aberto.

## O fluxo

```text
F0   Preparação           leitura do projeto, modo, selo, captura do "antes"
F1   Entrevista           uma rodada, só o que muda a entrega
F2A  Estúdio de Direção   2–3 direções sobre o mesmo trecho real        → Portão 1A (escolha)
F2B  Bíblia               decisões, tokens, manifesto, dados de demo    → Portão 1 (aprovação)
F2.5 Telas-Mãe            uma por arquétipo dominante + mobile          → Portão 2 (aprovação)
F3   Construção           subagentes de 1–3 telas, auditoria por entrega
F4   Consolidação         aura_check.py + vitrine
F4.5 QA e crítica         testers por jornada + crítico visual independente
F5   Entrega              veredito por evidência + registro do que o usuário corrigiu
```

### F0 — Preparação (sem perguntas)
Leia o repositório e o planejamento inteiros: concepção, PRD, rotas, telas, tokens, componentes, marca e o vocabulário do negócio. Identifique o modo, as superfícies, a stack e a Bíblia existente com o selo `**Design Aura:** vX.Y.Z`. Em remodelação e polimento, capture agora as telas afetadas (mesmos dados, larguras e temas); essa é a base da comparação final. Em remodelação, as telas atuais servem para extrair tarefas, dados e falhas, não como base de layout.

### F1 — Entrevista
Uma rodada em português claro, cada pergunta com uma opção recomendada **derivada deste projeto** e uma frase sobre o efeito na tela. Pergunte só o que ainda muda a entrega:
- o que preservar e o que incomoda (remodelação);
- superfícies e papel do mobile; tema padrão; uso da cor da marca;
- três palavras para como o produto deve parecer e uma para como não pode parecer;
- referências que a pessoa admira ou detesta (links ou prints), se houver;
- densidade (compacta, equilibrada, arejada); idioma e formatos;
- detalhes do domínio (por exemplo, um avião ao enviar): proponha só os prováveis e com plano fechado, e não descarte sem perguntar;
- modelo do orquestrador e dos subagentes, quando o ambiente oferecer escolha.

Se a pessoa disser que não entendeu, pare, explique com um exemplo do produto e confirme antes de seguir. Grave as respostas no Contrato de plataforma da Bíblia; o que você assumir entra marcado como hipótese.

### F2A — Estúdio de Direção
Monte 2 ou 3 direções realmente diferentes (cor e harmonia, tipografia, forma, densidade, profundidade, assinatura, o que cada uma recusa) e renderize todas sobre o mesmo trecho real do produto, em Light e Dark:

```bash
python3 <skill_dir>/scripts/design_intel.py "<domínio e objetivo>" --stack <stack>      # hipóteses de partida
python3 <skill_dir>/scripts/render_direction_board.py direcoes.json --out design/direcao  # direction-board.html + tokens por direção
```

O método de cada eixo está em [06](references/06-sistema-visual.md) e o roteiro do estúdio em [02](references/02-biblia-de-design.md). **Portão 1A:** mostre o board e peça a escolha (uma direção, uma mistura de eixos ou outra rodada). "Segue a recomendada" vale como escolha.

### F2B — Bíblia
Com a direção escolhida:

```bash
python3 <skill_dir>/scripts/discover_oss_components.py --scan <repo-ou-plano> --stack <stack> --platform <plataforma> --mode <modo> [--direction design/direcao/escolhida.json]
python3 <skill_dir>/scripts/generate_tokens.py --seed "<cor>" --accent "<cor>" --depth-style <estilo> --shape <forma> --density <densidade> --emit-json design/tokens.json --out design/ --format all --check-contrast
python3 <skill_dir>/scripts/render_design_bible.py design/DESIGN-BIBLE.md --tokens design/tokens.css --manifest design/screen-manifest.json --check
python3 <skill_dir>/scripts/render_design_bible.py design/DESIGN-BIBLE.md --tokens design/tokens.css --manifest design/screen-manifest.json --out-dir design
```

Use [o template](assets/design-bible-template.md): Parte A para aprovar, Parte B para construir, Parte C para verificar. A Bíblia só chega ao **Portão 1** com `--check` limpo. Entregue o PDF e o resumo; não construa telas antes da aprovação.

### F2.5 — Telas-Mãe
Construa a fundação compartilhada (tokens, `shell.css`, `shell.js`, `SHELL-CONTRACT.md` curto) e uma Tela-Mãe por arquétipo dominante (até três) mais uma mobile, com os estados que importam: populado, aberto ou pós-ação, vazio e erro. Audite e passe o crítico visual antes de mostrar. **Portão 2:** aprovação das capturas. A Tela-Mãe trava a linguagem (tokens, shell, gramática de componentes, acabamento); a estrutura interna de cada outra tela sai da tarefa dela.

### F3 — Construção
Subagentes de 1 a 3 telas, com briefing que traz o mapa de zonas da tela, os dados de `demo-data.json`, o caminho do `SHELL-CONTRACT.md` e da Tela-Mãe, e o comando de verificação. Alvo do subagente: zero BLOCK; HIGH e REVIEW voltam listados para o orquestrador. Audite cada entrega assim que ela chega. Detalhes em [03](references/03-orquestracao-subagentes.md).

### F4 — Consolidação

```bash
python3 <skill_dir>/scripts/build_figma_canvas.py design/screen-manifest.json --tokens design/tokens.css --out design/telas --verify-files
python3 <skill_dir>/scripts/aura_check.py --manifest design/screen-manifest.json --tokens design/tokens.css --bible design/DESIGN-BIBLE.md \
  --shell design/SHELL-CONTRACT.md --project design/telas --out design/audit [--base-url http://127.0.0.1:4188] [--baseline design/audit-antes] --smoke-interact --strict
python3 <skill_dir>/scripts/build_figma_canvas.py design/screen-manifest.json --tokens design/tokens.css --thumbs design/audit/captures --out design/telas --verify-files
```

Em SPA, rode o build antes de auditar. A vitrine (`entrega.html`, `fluxo.html`, `preview.html`, `index.html`) e o servidor de link único estão em [08](references/08-canvas-figma-manifest.md).

### F4.5 — QA funcional e crítica visual
Testers somente leitura percorrem as jornadas com `run_workflow_probe.mjs`, incluindo um trecho só por teclado e casos extremos de dados. Um crítico visual com contexto limpo compara as capturas com a Parte A da Bíblia usando a rubrica de [07](references/07-auditoria-e-veredito.md). O orquestrador tria pela causa, corrige ou despacha correções e pede reteste. No máximo dois ciclos; o que restar vira pendência explícita.

### F5 — Entrega e aprendizado
Veredito: **aprovado**, **requer correção** ou **pendente de verificação**, conforme a evidência. Entregue um link verificado. Registre na Bíblia (histórico) cada correção pedida pelo usuário, com motivo e escopo. Uma correção só vira regra da skill depois de reproduzida em outro projeto ou numa fixture de calibração.

## Leis em uma página

As leis completas, com a camada de cada uma, estão em [01](references/01-leis-inegociaveis.md). Em resumo:
- **Ofício (pode bloquear):** contraste WCAG AA + APCA; mesma família de cor por estado nos dois temas (erro vermelho, sucesso verde, atenção âmbar); label visível; foco visível; alvos de 44 px (iOS/web) e 48 dp (Android); nada cortado, encoberto ou com rolagem horizontal; sem erro de JS ou 404; texto real, sem Lorem ipsum.
- **Sinais de IA genérica (corrige ou justifica):** gradiente roxo como paleta padrão, glow e vidro decorativos, emoji como ícone, eyebrow clichê, gradiente em texto, microcopy de IA, `transition: all`, animação infinita sem espera real.
- **Acabamento (polimento):** raios concêntricos, escala de espaço, números tabulares e alinhados à direita.
- **Composição (revisão com captura):** vazio grande, telas rasas, eco de selos, barras empilhadas, abas demais, topo mobile alto, dado duplicado, alinhamento disperso. Os limites são orçamentos do projeto, definidos na Bíblia.

Nunca invente dados de negócio, diferenciais ou métricas. Dados de demonstração são fictícios e verossímeis, iguais em todas as telas.

## Componentes open source

A base em `data/catalog/` é ampla e pré-categorizada (24 categorias, mais de 110 necessidades, cerca de 360 peças, referências e armadilhas de licença). Um projeto pode usar várias bibliotecas: escolha **uma peça por necessidade**, re-tematize tudo pelos tokens e mantenha uma família de ícones e um sistema de motion. Licença conferida na versão fixada, registrada na Bíblia. Método em [09](references/09-pesquisa-componentes-oss.md).

## Mapa

- `references/01` leis por camada · `02` Bíblia e Estúdio de Direção · `03` orquestração, testers e crítico · `04` desktop e sistemas · `05` mobile · `06` sistema visual (cor, tipo, espaço, profundidade, anti-poluição, conteúdo, ícones, acabamento) · `07` auditoria e veredito · `08` vitrine e manifesto · `09` componentes · `10` motion · `11` sites e páginas.
- `scripts/`: `design_intel.py` (hipóteses) · `discover_oss_components.py` (base de componentes) · `render_direction_board.py` (Estúdio de Direção) · `generate_tokens.py` + `color_engine.py` (tokens por semente OKLCH, CSS, Tailwind, TS, Swift, Kotlin, Dart, DTCG) · `render_design_bible.py` (Bíblia, completude, zonas, sincronia) · `aura_check.py` (todos os portões) · `audit_contrast.py` · `lint_design_aura.py` · `capture_and_audit.mjs` · `run_workflow_probe.mjs` · `build_figma_canvas.py` · `serve_entrega.mjs` · `refresh_catalog.py` (licenças e atividade da base) · `rules_registry.py`.
- `data/`: `rules.json` (regras e orçamentos), `taxonomy.json` + `catalog/` (componentes), `recipes.json` (padrões por problema), `patterns.json`, `domains.json`, `typography.json`.
- `assets/`: template da Bíblia, exemplo de direções, manifesto e tokens. `examples/`: estudos de caso e o estilo tátil completo.
