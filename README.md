# Design Aura (`design-aura` · `v3.1.1`)

Skill de direção visual e construção de interfaces bonitas, sofisticadas e sem cara de IA para **apps mobile** (iOS, Android, React Native/Expo, Flutter, PWA), **apps desktop** (Electron, Tauri, nativo), **sistemas web** (SaaS, ERPs, painéis; HTML estático ou SPA React/Vite/Next) e **sites**.

## O que ela faz

1. **Lê o projeto** (repositório, planejamento, rotas, marca) e escolhe o modo: criar, remodelar, polir, ajuste pontual ou upgrade.
2. **Entrevista curta** com recomendações derivadas do próprio projeto.
3. **Estúdio de Direção**: 2–3 direções diferentes (cor, tipografia, forma, densidade, profundidade) renderizadas sobre o mesmo trecho real do produto, em Light e Dark, para a pessoa escolher.
4. **Bíblia de direção visual** em três partes (aprovar, construir, verificar), com tokens gerados por um motor de cor OKLCH, orçamentos de composição, diagramas de zona e componentes com caminho e licença. Só avança com a checagem de completude limpa.
5. **Telas-Mãe** por arquétipo e **construção por subagentes** (1–3 telas cada) com auditoria a cada entrega.
6. **Verificação por evidência**: contraste WCAG + APCA, linter, auditoria no navegador em várias larguras e temas, jornadas clicadas (inclusive só por teclado), crítico visual independente e comparação antes/depois.
7. **Vitrine em link único** (`entrega.html`: mapa estilo Figma, app ao vivo, preview guiado, galeria, Bíblia).

## Princípios

- **Cada projeto ganha a própria cara.** A skill dá método e opções, não uma pele pronta.
- **Ofício é universal, gosto é do projeto.** Regras objetivas podem bloquear; sinais de composição pedem revisão com a captura. Cada regra tem uma camada em `data/rules.json`.
- **Ver antes de afirmar.** O que não foi visto fica pendente.

## Componentes open source

Base pré-categorizada em `skills/design-aura/data/catalog/`: 23 categorias, 110 necessidades e cerca de 360 entradas (kits, primitivos, gráficos, tabelas, agenda, editores, mobile, ícones, fontes, motion, efeitos, seções de site, ferramentas de cor e galerias de referência), cada uma com stack, plataforma, modo, estilo, acabamento, comando de instalação por stack, situação de licença e data da última conferência ao vivo (cerca de 220 entradas conferidas no GitHub e no npm; as demais são referências e galerias). Um projeto usa várias bibliotecas: uma peça por necessidade, um motor por família (gráficos, tabelas, agenda, overlays), todas re-tematizadas pelos tokens.

## Instalação

No T3 Code, digite `/designaura` no chat do projeto.

```bash
npx skills add Gotherman/design-aura -g
```

Instalação manual: copie `skills/design-aura` (e `skills/designaura` para o comando) para a pasta de skills do agente:
- Claude Code: `~/.claude/skills/`
- Codex: `~/.codex/skills/`
- Agentes universais / T3 Code: `~/.agents/skills/`
- Gemini / Antigravity: `~/.gemini/config/skills/`

## Scripts (`skills/design-aura/scripts/`)

| Script | Função |
|---|---|
| `design_intel.py` | Hipóteses do setor: sementes de cor, tipografia por personalidade, arquétipos, erros comuns |
| `discover_oss_components.py` | Busca na base de componentes por necessidade, stack, plataforma, modo e direção (`--online` para GitHub/npm) |
| `render_direction_board.py` | Estúdio de Direção |
| `generate_tokens.py` + `color_engine.py` | Tokens por semente OKLCH; CSS, Tailwind v4, TS, Swift, Kotlin, Dart e DTCG |
| `render_design_bible.py` | Bíblia em HTML/PDF, checagem de completude, diagramas de zona, sincronia |
| `aura_check.py` | Todos os portões num comando |
| `audit_contrast.py` | WCAG + APCA, paridade semântica, separação de planos por estilo de profundidade |
| `lint_design_aura.py` | Linter estático por camada |
| `capture_and_audit.mjs` | Captura e auditoria no Chromium (larguras, temas, pós-clique, peso, movimento, linha de base) |
| `run_workflow_probe.mjs` | Jornadas E2E (cliques, teclado real, reduced motion, assertivas) |
| `build_figma_canvas.py` + `serve_entrega.mjs` | Vitrine e servidor de link único |
| `refresh_catalog.py` | Licença e atividade da base de componentes (`--mark-checked` grava a data e marca peças paradas) |

Requisitos: Python 3, Node 20+ e Chromium/Chrome. Sem npm install nem pip install.

## Testes

```bash
python3 skills/design-aura/tests/test_design_aura.py
```

Inclui o corpus de calibração (`tests/fixtures/good` e `bad`): telas boas não podem bloquear e telas ruins precisam ser pegas.

## Créditos e inspirações

[`felipebasurto/unslop-ui`](https://github.com/felipebasurto/unslop-ui), [`jakubkrehel/make-interfaces-feel-better`](https://github.com/jakubkrehel/make-interfaces-feel-better), [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable), [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), [`uizze/uizze`](https://github.com/uizze/uizze), skills de Emil Kowalski e Meng To, Stageshow, OpenDesign, Solid Glass, Radix Colors e o ecossistema OKLCH da Evil Martians.
