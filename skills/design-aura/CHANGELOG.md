# Histórico da Design Aura

Use este arquivo no modo Upgrade: compare o selo da Bíblia do projeto com a versão atual e aplique os deltas que se aplicam.

## 3.2.0 — Consumo e sites, Estúdio multi-superfície, tokens nativos completos, estados e acessibilidade ampliada
- **Setores de consumo e sites + anti-convergência:** `data/domains.json` ganhou 12 setores de consumo e site (`ecommerce-moda-varejo`, `restaurante-delivery`, `hospedagem-turismo-consumidor`, `fitness-bem-estar`, `beleza-estetica`, `esporte-aventura-aulas`, `midia-editorial`, `portfolio-agencia`, `eventos-ingressos`, `institucional-ong`, `imobiliaria-vitrine`, `comunidade-social-app`). `design_intel.py` aplica corte de relevância (`min_ratio`) ignorando termos genéricos (briefings fora dos setores voltam sem preset forçado), e sementes iniciais de `saude-clinica` (sálvia + terracota) e `juridico-contratos` (tinta + carmim) foram promovidas para evitar convergência em azul.
- **Estúdio de Direção multi-superfície e eixo de motion:** `render_direction_board.py` passa a renderizar modelos reais de **sistema, app mobile e site** em cada direção, além do eixo `motion` (`none`, `subtle`, `expressive`), propagado para `color_engine.py` e `generate_tokens.py`.
- **Tokens nativos completos + DTCG + `forced-colors`:** `generate_tokens.py` emite `DesignTokens.swift` (`Adaptive`, `Radius`, `Space`, `Size`, `Animation.timingCurve`, `Elevation`, `designAura`), `DesignTokens.kt` (`lightColorScheme`/`darkColorScheme`, `AuraShapes`, `CubicBezierEasing`, `TouchMin = 48.dp`), `design_tokens.dart` (`ColorScheme`, `Cubic`, `BoxShadow`, `ThemeData`), `tokens.dtcg.json` com sombras e curvas cúbicas, e bloco `@media (forced-colors: active)` no `tokens.css`.
- **Estados declarados, ação primária, zoom 200% e cores forçadas:** `capture_and_audit.mjs` captura cada estado declarado no `screen-manifest.json` (`tela@vazio`, `tela@erro`, `tela@aberto` via `query`/`hash`/`file`/`route`/`click` + `after`), confere a alcançabilidade da `primaryAction` (`DA-REACHABLE`), isenta estados vazios/erro/carregando de sinais de tela rasa/vazio, e executa 1× por tela os novos checks **`DA-ZOOM-REFLOW`** (zoom 200% / 720px CSS) e **`DA-FORCED-COLORS`** (contorno de controles em alto contraste do sistema).
- **Licenças do catálogo revisadas:** remoção de `@theatre/studio` (AGPL-3.0) do comando padrão, ressalvas explícitas (Preline, BlockNote, Theatre) e redução das entradas "a conferir" para <= 20.
- **Histórico de auditorias e script de release:** `aura_check.py --log <arquivo.jsonl>` grava o histórico de regras por rodada; novo `tools/release.py` (`--check` / `--sync`) valida paridade de selos de versão, instala em todas as pastas configuradas sem cache residual e gera `dist/design-aura-vX.Y.Z.{zip,skill}`.

## 3.1.1 — Correções da auditoria da 3.1.0
- **Leitura do projeto:** o scanner lê primeiro o planejamento, depois o código e as telas do produto, e por último no máximo 10 artefatos de design de rodadas anteriores. Pastas `audit-*`, `qa-*` e capturas ficam fora; marcação, CSS e nomes de classe são descartados. Antes, numa remodelação, ele lia os relatórios de auditoria antigos e nunca chegava a `src/`.
- **Necessidades:** as 18 mais fortes recebem candidatos e as demais saem em "Também detectadas" (`--max-needs`). Palavras-chave ambíguas corrigidas ("agente", "bot", "aria", "fonte", "tema", "erro", "status", "rastreio").
- **Um motor por família:** quando uma peça cobre duas ou mais necessidades de gráficos, tabelas, agenda ou overlays, ela vira a primeira opção de todas.
- **Base de componentes:** categorias derivadas das necessidades (`--category` acha tudo), comando de instalação em todas as peças adotáveis e `installs` por stack (nomes conferidos no npm e no pub.dev). Licenças conferidas ao vivo em 220 entradas, com `stale` para repositórios parados; Swapy virou armadilha (GPL-3.0); Paper Shaders e HeroUI Native confirmados como Apache-2.0. Saiu o campo `license_ok` gravado, que contradizia o calculado. Textos com acentuação.
- **Estúdio → tokens → componentes:** o board grava `direcao-N.json`, e `generate_tokens.py --direction` e `discover_oss_components.py --direction` leem esse arquivo. Antes, o SKILL.md pedia um `escolhida.json` que nenhum script gerava, e passar o arquivo de tokens travava a busca.
- **Motor de cor:** marca preta, branca ou cinza vira tinta (sem matiz inventada nos neutros e sem `#000000` cru). Marca clara mantém o preenchimento com texto escuro, e o traço usa `--primary-strong`. Novo `--focus-ring` (3:1). A semente aceita `rgb()`, `hsl()`, `oklch()` e nomes CSS, com erro claro. A densidade agora muda a escala de espaço, `--control-h`, `--row-h` e o texto base, e o board mostra a diferença.
- **Bíblia:** o template ganhou a seção de profundidade que o `--check` exigia, e o `--check` passa a recusar seção vazia (antes, só títulos passavam). Os valores de exemplo dos orçamentos seguem `rules.json`.
- **`aura_check.py`:** portão que não rodou aparece como pendente e falha o `--strict`, salvo com `--partial`. O relatório da captura anterior é apagado antes de cada rodada.
- **Contraste em tempo real:** compõe fundos translúcidos, lê cores em `oklch`/`color()` e as paradas de gradiente. Texto que reprova só na parada extrema vira REVIEW, e logotipo fica isento. Nas telas reais testadas, os emblemas em gradiente deixaram de dar HIGH falso, e chips translúcidos abaixo de 4,5:1 passaram a ser pegos.
- **Corpus de calibração:** painel denso com gradientes e selos translúcidos, tela mobile e um caso ruim de texto claro sobre gradiente claro.
- Chrome, Chromium ou Edge encontrados também no Windows e no cache do Playwright. Página 404 não gera mais sinais de composição. `assertReachable` falha como `DA-REACHABLE`. Guia 10 com acentuação.

## 3.1.0 — Catálogo vivo e verificação ampliada
- Base de componentes pré-categorizada em `data/catalog/` (24 categorias, mais de 110 necessidades, cerca de 360 entradas) com stacks, plataformas, modos, estilo, licença e acabamento. Um projeto usa várias bibliotecas: uma peça por necessidade, todas re-tematizadas.
- `discover_oss_components.py` detecta necessidades com radical e sinônimos PT/EN, devolve até três candidatos por necessidade de qualquer biblioteca, ajusta o ranking à direção (`--direction`, `--shape`, `--density`, `--motion`, `--skin`) e avalia necessidades de site no modo Persuade.
- `refresh_catalog.py` confere licença, arquivamento e atividade no GitHub e no npm e gera um diff para revisão.
- Licenças corrigidas: ApexCharts ≥ 5 (licença dupla com limite de receita), Remix Icon (licença própria), Solar (CC BY 4.0, atribuição), Iconify (motor MIT, conjuntos com licença própria), Lightweight Charts (atribuição). Novas armadilhas: tldraw, Shepherd.js, Intro.js.
- Probe de jornadas: teclado real (`key`, `tabTo`, `assertFocused`) e `setReducedMotion`.
- Auditor: dado duplicado, alinhamento disperso, peso da página, movimento com `prefers-reduced-motion` e comparação com a linha de base (`--baseline`).

## 3.0.0 — Direção
- Estúdio de Direção (F2A): 2–3 direções sobre o mesmo trecho real, em Light e Dark (`render_direction_board.py`), antes da Bíblia (Portão 1A).
- Motor de cor OKLCH (`color_engine.py`, `generate_tokens.py --seed`): escalas de 12 degraus, neutros tingidos pela marca, semânticas com família fixa e energia da marca, sólidos ajustados para WCAG + APCA, gráficos com checagem de daltonismo. Exportação DTCG 2025.10.
- Quatro estilos de profundidade (linha fina, suave, tonal, tátil), três linguagens de forma e três densidades.
- Bíblia em três partes (aprovar, construir, verificar) com `render_design_bible.py --check` e diagramas de zona gerados do manifesto.
- Crítico visual independente na F4.5.
- Guia novo de sites e páginas (`11-sites-e-paginas.md`); guia 06 passa a ser o sistema visual completo.
- Tipografia por personalidade (38 pares); domínios sugerem sementes de cor com motivo em vez de paletas fixas.

## 2.6.0 — Consolidação
- Registro único de regras (`data/rules.json`) com quatro camadas: ofício (pode bloquear), sinal de IA genérica (até HIGH), acabamento (até MEDIUM) e composição (REVIEW). Heurísticas nunca bloqueiam.
- Orçamentos de composição por projeto (`project.budgets`), com padrões por modo.
- Corpus de calibração em `tests/fixtures/good` e `bad`.
- `aura_check.py`: todos os portões num comando.
- SKILL.md vira roteiro; selos de versão e maiúsculas saem do corpo das instruções; receitas visuais deixam de ser obrigatórias e viram padrões por problema (`data/recipes.json`).
- Removidos valores e vocabulário de projetos específicos da skill (agora em `examples/`).

## 2.5.1 — Higiene
- Commit da 2.5.0, instalações sincronizadas e contradições numéricas unificadas (sidebar, abas, topo mobile, escala de espaço, registros de demo, número de telas).

## 2.5.0
- Cobertura por tela e largura, verificação de ação alcançável e de valor exato após interação, sincronia Bíblia/shell/CSS.

## 2.4.x
- Paridade semântica Light/Dark, presença da marca no workspace, resize in-place, vitrine em link único, suporte a SPA, testers E2E (Fase 4.5), atualização da Bíblia em polimento, modo Upgrade com selo de versão.

## 2.0–2.3
- Bíblia visual em PDF, Telas-Mãe, subagentes de 1–3 telas com auditoria por entrega, canvas estilo Figma, auditoria paralela.

## 1.x
- Primeira versão, descoberta de componentes, motion por plataforma, comando `/designaura`, parada para aprovação da Bíblia.
