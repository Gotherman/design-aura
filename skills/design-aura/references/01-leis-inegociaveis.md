# Os 10 Blocos de Leis Inegociáveis (Design Aura)

Regras objetivas e verificáveis que **reprovam automaticamente (`BLOCK`)** na auditoria de Design, Visual, UI e UX. Nenhum componente, tela ou protótipo pode receber veredito `Approve` enquanto violar qualquer regra destes 10 blocos sem justificativa explícita aprovada no briefing da marca.

---

## Bloco 1 — Proibido Estética "SaaS de IA Genérico" (Direção Visual)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B1-01` | Proibido gradientes roxo/índigo/violeta/neon genéricos como paleta padrão sem justificativa explícita da marca ou do briefing. | `lint_design_aura.py` + revisão da `DESIGN-BIBLE.md` |
| `DA-B1-02` | Proibido glow neon pesado (`box-shadow: 0 0 24px+` saturado), blobs desfocados decorativos, glassmorphism sem função de hierarquia ou bordas brilhantes em todos os elementos. *(Micro-halos sutis `<= 20px` com baixa opacidade em anéis de foco ou badges de score são permitidos.)* | `lint_design_aura.py` + inspeção visual |
| `DA-B1-03` | Proibido usar emojis ou ícones clichês de IA (`✨`, `🚀`, `⚡`, `🛡️`, `🔥`, `💡`, `🎯`) como decoração genérica em títulos, botões, badges ou cards. | `lint_design_aura.py` |
| `DA-B1-04` | Proibido misturar famílias ou estilos de ícones (outline vs solid aleatórios), usar webfonts borradas sem nitidez vetorial ou repetir o mesmo ícone genérico (`ph-bank`, `ph-warning-circle`, `ph-clock`) como muleta visual em toda a tela (`DA-ICON-GENERIC-REPEAT`). Prefira SVGs Duotone/1.75px específicos do domínio (`Tabler`, `Solar Duotone`, `Lucide`, `Heroicons Micro`, `Iconify`) dentro de emblemas com spotlight `.icon-emblem` ou monogramas vetoriais (`.bank-emblem`). | `lint_design_aura.py` + revisão visual |
| `DA-B1-05` | Proibido eyebrows clichês de landing IA (`"FEATURES"`, `"HOW IT WORKS"`, `"WHY CHOOSE US"`) e numeração decorativa (`"01 //"`, `"01 ·"` quando não é passo real). *(Rótulos reais de contexto, data ou módulo como `"Novembro / Dezembro 2026"` ou `"Fila por SLA"` são bem-vindos, mesmo usando classes `.eyebrow`/`.kicker`.)* | `lint_design_aura.py` |
| `DA-B1-06` | Proibido gradiente em texto (`bg-clip-text` / `background-clip: text`), dots/badges `LIVE`/`NEW`/`AI` falsos sem estado real e barrinhas coloridas repetidas em todos os cards/KPIs. *(Borda esquerda sutil em callouts/alertas, blockquotes ou item ativo de menu é permitida.)* | `lint_design_aura.py` |

---

## Bloco 2 — Hierarquia, Layout e Anti-Cardite (Estrutura)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B2-01` | **Anti-Cardite ≠ Proibir Cards:** proibido "cardite aguda" (colocar caixas decorativas onde lista/tabela resolve melhor) e **proibido card dentro de card**. Por outro lado, superfícies elevadas `Z2` (cards, painéis, KPIs estruturados, drawers) são **obrigatórias** para dar profundidade e separação visual — é **estritamente proibido** banir cards (`"sem classe card"`) no briefing de subagentes ou achá-los dispensáveis em dashboards/módulos. | `lint_design_aura.py` + `DA-SURFACE-FLAT` + inspeção visual |
| `DA-B2-02` | Proibido repetir o template preguiçoso de "3 cards idênticos com ícone em círculo/quadrado colorido + título + 2 linhas" como solução padrão de seção. | Inspeção visual |
| `DA-B2-03` | Proibido centralizar blocos de texto longos ou listas de leitura; alinhamento deve favorecer escaneabilidade pela margem esquerda. | `lint_design_aura.py` |
| `DA-B2-04` | Proibido espaçamento uniforme sem agrupamento lógico (**Lei da Proximidade**): elementos relacionados ficam mais próximos entre si do que de grupos distintos; sempre há mais espaço acima de um título do que abaixo dele. | Inspeção visual + CSS |
| `DA-B2-05` | Proibido múltiplos CTAs primários competindo com o mesmo peso visual **no mesmo contexto/painel**. Cada vista/modal/drawer tem no máximo 1 ação primária sólida dominante. | `lint_design_aura.py` + inspeção visual |
| `DA-B2-06` | **Alto Contraste Ótico, Zero Espaços Mortos & Zero Buraco em Cards:** Light Mode usa canvas aterrado com separação clara entre fundo (`Z0/Z1`) e cartões (`Z2`) por contorno nítido (`>= 1.22:1` contra `Z2` — `DA-LIGHT-WASHED-OUT`) + sombra física de 3 camadas. Em Desktop operacional, use **Lista Limpa → Detalhe Focado na mesma página** para filas densas ou composição balanceada sem vazio morto (`DA-DEAD-SPACE`), proibido buraco interno `> 95px` em cards de Bento Grid (`DA-CARD-INTERNAL-VOID`) e proibido duplicar a navegação da Sidebar dentro da Topbar do Portal. | `capture_and_audit.mjs` + inspeção 1440×900 |
| `DA-B2-07` | **Anti-poluição e uso humano.** Em poucos segundos a pessoa entende onde está, para onde pode ir, onde clicar e o que pode fazer. Proibido despejar o sistema inteiro numa tela, espalhar botões do mesmo peso, ou posicionar a navegação fora do lugar que a plataforma ensinou. Densidade é permitida quando o trabalho é denso e os grupos estão separados. Proibido esconder a ação principal ou a saída para a tela parecer vazia. | Revisão da tela e do fluxo |
| `DA-B2-08` | **Piso de Substância & Zero Telas Casca (`DA-STUB-SCREEN` / `DA-RAW-LINK-LIST` / `DA-DEAD-SPACE`):** proibidas telas rasas com apenas 1–2 linhas em tabelas operacionais, inspectors laterais quase vazios (ex.: só 1 linha de texto e um buraco branco), copy de desculpa de stub (*"não estão nesta amostra"*, *"semente do funil"*) ou links `<a>` azuis sublinhados crus servindo de lista/menu de aplicativo. | `lint_design_aura.py` (`DA-B2-08A/B`) + `capture_and_audit.mjs` |

---

## Bloco 3 — Contraste, Cor e Acessibilidade (Legibilidade)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B3-01` | Obrigatório respeitar no mínimo **WCAG AA** (`>= 4.5:1` texto normal e placeholders; `>= 3.0:1` texto grande `>= 18pt` / `14pt bold` e componentes UI) e **APCA** (`|Lc| >= 60` corpo, `>= 45` grande/UI). | `audit_contrast.py --strict` + `capture_and_audit.mjs` |
| `DA-B3-02` | Proibido parear `#000000` puro com `#FFFFFF` puro sem controle de elevação de superfície, ou textos cinza lavados em Dark Mode. *(Cartões `#FFFFFF` elevados em `Z2` sobre canvas aterrado `Z1` no Light Mode são recomendados!)* Em superfícies coloridas, matize o texto secundário pela cor do fundo, nunca cinza genérico. | `audit_contrast.py` + `lint_design_aura.py` |
| `DA-B3-03` | Proibido áreas de toque/clique menores que **44×44px** em interfaces mobile/iOS (e **48×48dp** com 8dp de respiro em Android), com texto de corpo mínimo de **14px** (e rótulos técnicos `>= 11–12px`; `< 10px` bloqueia; ícones `<i>` internos ficam isentos). | `capture_and_audit.mjs` + `lint_design_aura.py` |
| `DA-B3-04` | **Vitalidade Cromática da Marca:** proibido degradar/escurecer uma cor vibrante da marca até virar marrom, bege sujo ou cinza apagado apenas para forçar texto branco no botão. Quando a cor vibrante (ex.: laranja, âmbar, verde-lima) tem luminância alta, use texto escuro calibrado (`#101822` / `#140804`) sobre o acento vivo ou variante deep saturada, mantendo WCAG AA `>= 4.5:1`. | `audit_contrast.py` + inspeção da Prancha Visual |
| `DA-B3-05` | **Equilíbrio Cromático `65 / 20 / 10 / 5` (Dark & Light Ancorado pela Marca):** em Dark Mode, proibido saturar todos os planos `Z0–Z4` no mesmo matiz da primária (`S > 36%` → `DA-DARK-MONOCHROME`) **E** proibido apagar a marca para cinza morto. No **Light Mode (`Brand-Anchored Light Mode`)**, proibido deixar Sidebar, Login, Canvas e todos os Cards em branco/cinza pálido sem divisão: use **Âncora Forte da Marca (`--surface-brand-dark`, ex.: Marinho `#0E294B → #163E70`)** na Sidebar/Painel de Login/Card-Rei + **variações de cor clara estrutural (`--surface-tint-soft: #E6F0FD`)** em cabeçalhos de cards, `<thead>` e `.icon-emblem` + `border-subtle >= 1.22:1` contra `Z2` (`DA-LIGHT-WASHED-OUT`) + sombras tintadas pela marca + paleta 6 cores (`--chart-1..6`). | `audit_contrast.py` + inspeção da Prancha Visual |

---

## Bloco 4 — Tipografia Intencional (Leitura e Ritmo)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B4-01` | Obrigatório contraste tipográfico claro entre título, subtítulo, corpo e metadados (escala, peso e `line-height`), com medida de leitura confortável (`65–75ch`). Peso `800` é bem-vindo em Display/KPIs; evite `900`/`font-black` gratuito em textos corridos. | `lint_design_aura.py` + inspeção |
| `DA-B4-02` | Obrigatório `font-variant-numeric: tabular-nums` (`tabular-nums`) em todos os números dinâmicos, preços, contadores, timers e colunas numéricas de tabela. | `lint_design_aura.py` + inspeção |
| `DA-B4-03` | Obrigatório `text-wrap: balance` em títulos curtos (≤6 linhas) e `text-wrap: pretty` em parágrafos/descrições, além de `-webkit-font-smoothing: antialiased` no root. Todo texto dinâmico deve prever quebra limpa ou `text-overflow: ellipsis` sem estourar containers. | `capture_and_audit.mjs` + CSS |
| `DA-B4-04` | **Tipografia Adequada ao Modo `Operate` (`DA-SERIF-OPERATE`):** em sistemas operacionais, ERPs e dashboards (`Operate`), proibido usar fontes serifadas editoriais (`Source Serif`, `Georgia`, `Palatino`, `Times`, `Merriweather`, `Playfair`) em títulos ou corpo sem autorização explícita do usuário. Prefira sans-serif de precisão suíça (`Geist`, `Inter`, `IBM Plex Sans`). | `lint_design_aura.py` + `capture_and_audit.mjs` |
| `DA-B4-05` | **Números Monetários Proporcionais Tabulares vs Mono Técnico:** valores financeiros grandes (`R$ 1.248.920,50`), KPIs e tabelas usam a **sans-serif principal** com `font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1` (classe `.num`, sem buracos largos de monoespaçada). Reserve `--font-mono` (`Geist Mono` / `JetBrains Mono`) estritamente para códigos técnicos (CNPJ, linha digitável, IDs, protocolo, `<kbd>`). | Revisão CSS + inspeção visual |

---

## Bloco 5 — Conteúdo Real e Zero Copy de Template (Microcopy)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B5-01` | Proibido usar `"Lorem ipsum"`, `"John Doe"`, `"Jane Doe"`, `"Acme Corp"` ou placeholders genéricos em telas entregues. | `lint_design_aura.py` |
| `DA-B5-02` | Proibido microcopy clichê de IA (`"Transforme seu negócio"`, `"Eleve sua experiência"`, `"Solução definitiva"`, `"Potencializado por IA"`, `"Revolucione sua rotina"`, `"Unlock your potential"`). O texto deve usar verbos concretos e vocabulário do domínio real. | `lint_design_aura.py` |
| `DA-B5-03` | Proibido subtítulos-eco que apenas repetem o título (*"Contas a pagar — Gerencie suas contas"*), *botsplaining* (`"Clique no botão abaixo para..."`), notas de dev vazadas e **copy de referência externa vazada para a UI** (`DA-REF-COPY-LEAK`, ex.: `"estilo Linear"`, `"estilo TOTVS"`). *(Subtítulos com dados reais e contagem como `"140 editais abertos · 17 encerram em 7 dias"` são ótimos.)* | `lint_design_aura.py` + revisão textual |

---

## Bloco 6 — UX Completa e Interação com Propósito (Funcionalidade)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B6-01` | Proibido entregar apenas o "caminho feliz": fluxos e componentes devem prever estados reais aplicáveis (`loading/skeleton`, `empty state` com próxima ação, `error` com recuperação, `sucesso` com feedback). | Revisão de componentes/telas |
| `DA-B6-02` | Proibido `transition: all` / `transition-all`, `hover:scale-105` em todo card, `animate-bounce`/`animate-pulse` decorativo ou transições `> 300ms` em controles simples. Interações devem usar **CSS transitions interrompíveis** em propriedades específicas, saída mais rápida que a entrada, `active:scale-[0.97]` tátil em botões e respeito obrigatório a `prefers-reduced-motion`. | `lint_design_aura.py` + CSS |
| `DA-B6-04` | Animação infinita só para estados reais de espera ou sinal ativo (skeleton, spinner, progresso, indicador de digitação `typing`, gravação ou alerta SLA crítico). Página, card e componente animam quando a mudança de estado precisa ser percebida. Ver [10-motion-anti-slop.md](10-motion-anti-slop.md). | `lint_design_aura.py` + revisão |
| `DA-B6-03` | Proibido esconder ações críticas ou navegação essencial atrás de padrões confusos por estética minimalista. Superfícies do browser (`::selection`, `caret-color`, scrollbars, `text-underline-offset`) devem ser tematizadas pela paleta. | Inspeção CSS + navegador |

---

## Bloco 7 — Precisão Geométrica e Sistema (Acabamento Visual)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B7-01` | **Concentricidade obrigatória**: proibido raios idênticos em elementos aninhados com padding `<= 24px`. Fórmula: `Raio Interno = Raio Externo - Padding` (ou `Externo = Interno + Padding`). | `lint_design_aura.py` + inspeção CSS |
| `DA-B7-02` | Preferir a escala baseada em **4px / 8px** (`4, 8, 12, 16, 20, 24, 32, 40, 48, 64px`), permitindo ajustes ópticos curtos (`2, 6, 7, 9, 10, 11, 14px`) dentro de controles/ícones. Magic numbers arbitrários maiores (`13, 15, 17, 19, 21, 23px`) geram alerta `MEDIUM` (polimento, não bloqueio). | `lint_design_aura.py` (`MEDIUM`) |
| `DA-B7-03` | **Profundidade Tátil em 5 Camadas (`Z0→Z4`):** proibido usar sombra preta chapada como único recurso de elevação em Dark Mode ou cards chapados 2D. Cards `Z2` combinam luminosidade progressiva + **chanfro óptico duplo (`inset 0 1px 0` + borda `1px` + sombra de 3 camadas)**, painéis compostos usam **anatomia interna em 2 planos (`Header/Footer Z3 + Miolo Z2 + Poços Z0`)**, ícones vivem em **emblemas spotlight `.icon-emblem`** e badges de tempo/status usam **`.chip-sla` (anel SVG circular) / `.chip-status` (halo duplo + glifo vetorial) / `.chip-kv`**. | `lint_design_aura.py` + `tokens.css` + inspeção visual |

---

## Bloco 8 — Semântica e Higiene de Dados (Dashboards e Listas)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B8-01` | Proibido usar cores semânticas (vermelho/carmim, verde/esmeralda, âmbar/alerta) como decoração sem significado funcional real no domínio. | Revisão visual |
| `DA-B8-02` | Proibido poluir listas e tabelas com excesso de badges/pills coloridas competindo entre si. | Revisão visual |
| `DA-B8-03` | **Higiene de Tabelas & Gráficos de Estúdio (`DA-FLAT-CHART-AXIS`):** proibido alinhar colunas numéricas à esquerda em tabelas (sempre à direita + `.num` tabular) ou entregar gráficos "tutorial" (1 linha reta no topo com paredão azul morto até o zero — use escala Y dinâmica ou **Combo Barras Entrada/Saída + Curva + HUD Vivo de Crosshair + Pinos de Evento**; Waterfall DRE sempre com conectores tracejados, `%` e paleta multi-cor `--chart-1..6`; rankings em **`BarList`**; SLAs em **`Tracker`**). Proibido nomear tipo de gráfico no título. | `lint_design_aura.py` + revisão visual |

---

## Bloco 9 — Formulários, Estados e Acessibilidade de Interação

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B9-01` | Proibido usar `placeholder` como substituto de `<label>` visível (ou `aria-label` quando controle de busca/filtro em barra). | `lint_design_aura.py` + `capture_and_audit.mjs` |
| `DA-B9-02` | Proibido remover `:focus-visible` (`outline: none` / `outline-none`) sem fornecer anel de foco acessível equivalente (`:focus-visible` ou `:focus-within` no container pai em barras de busca/composers compostos). | `lint_design_aura.py` |
| `DA-B9-03` | Obrigatório prever estados reais (`hover`, `active`, `disabled`, `focus`, `invalid`) com mensagens de erro junto ao campo que dizem o que aconteceu e como corrigir. | Revisão de fluxo |
| `DA-B9-04` | Proibido empilhar modais (modal sobre modal) ou executar ações destrutivas sem confirmação explícita ou mecanismo imediato de **Desfazer (Undo)**. | Revisão de fluxo |
| `DA-B9-05` | Proibido deixar `<textarea>`, `<select>` ou `<input>` com visual cru do navegador sem classe/estilização do design system (borda, padding, raio e `:focus-visible`). | `lint_design_aura.py` + inspeção visual |

---

## Bloco 10 — Ergonomia Nativa Mobile, Desktop & Mídia

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B10-01` | Proibido ignorar Safe Areas (notch, Dynamic Island, home indicator, IME/window insets) ou posicionar ações primárias mobile fora da zona natural do polegar (thumb zone). iOS respeita HIG (Tab Bar 2–5 seções, edge-swipe back vivo, Large Titles); Android respeita Material 3 (Nav Bar/Rail adaptativo, Predictive Back vivo, máx 1 FAB). | `05-mobile-ios-android.md` + `capture_and_audit.mjs` |
| `DA-B10-02` | Proibido criar áreas de scroll aninhado (scroll interno dentro de página rolável) sem justificativa estrita de layout (ex.: painel lateral fixo em cockpit desktop `h-dvh`). Evitar `100vh` rígido em mobile (usar `100dvh` + `env(safe-area-inset-*)`). | `lint_design_aura.py` + `capture_and_audit.mjs` |
| `DA-B10-03` | Proibido exibir imagens/avatares sem preservação de proporção (`object-fit: cover` / `object-cover`), sem `alt` adequado ou sem estado de fallback (iniciais/ícone) em caso de falha. | `lint_design_aura.py` + `capture_and_audit.mjs` |
| `DA-B10-05` | Proibido espremer o shell desktop no mobile ou esticar o shell mobile no desktop. Web: sidebar a partir de `1024px`, rail ou drawer entre `768` e `1023px`, drawer ou bottom nav abaixo de `768px`. Tabela densa vira lista no mobile. Tokens continuam os mesmos. | Revisão contra `04` e `05` |
| `DA-B10-06` | **Zero Recorte por Barras Fixas, Zero Corte Interno de Cards & Encaixe Limpo de Mockup (`DA-FIXED-OVERLAP` / `DA-CLIPPED-CONTENT` / `DA-MOBILE-FLEX-CLIP`):** conteúdo rolável em mobile ou desktop nunca pode ficar cortado sob barra inferior fixa (`padding-bottom` seguro), **PROIBIDO** cards `overflow: hidden` sendo esmagados dentro de containers flex-column sem `flex-shrink: 0` (ou `display: grid; grid-auto-rows: max-content`), e molduras/mockups mobile devem usar `overflow: hidden; clip-path: inset(0 round 32px); isolation: isolate` para impedir cantos quadrados vazando fora do bezel. | `capture_and_audit.mjs` + `lint_design_aura.py` |
| `DA-B10-07` | **Zero Marca/Nav Truncada, Zero Header com Scrollbar & Escopo `.on-brand-dark` (`DA-NAV-TRUNCATION` / `DA-HEADER-HSCROLL` / `DA-BRAND-DARK-SCOPE`):** nome de marca na Sidebar e itens de navegação não podem ser cortados horizontalmente, topbars/seletores em desktop (`1440px`) não podem vazar com scrollbar horizontal, e superfícies escuras da marca no Modo Claro (`.sidebar`, `.auth-brand-pane`, `.card-brand-hero`) devem redeclarar localmente `--text-strong`/`--text-muted` claros. | `capture_and_audit.mjs` + `lint_design_aura.py` |

---

## Matriz Rápida de Detecção

| Verificador | Cobertura Principal |
|---|---|
| **`audit_contrast.py`** | Bloco 3 (`DA-B3-01`, `DA-B3-02`) em Light e Dark via WCAG 2.1 + APCA-W3 |
| **`lint_design_aura.py`** | Blocos 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 via análise estática de markup/CSS/TSX/Swift/Kotlin/Dart |
| **`capture_and_audit.mjs`** | Blocos 2, 3, 4, 6, 9, 10 em runtime real no Chromium (1440×900, 768×1024, 390×844, Dark & Light) |
| **Auditor Subagente (Onda 2)** | Regras semânticas e composicionais (anti-cardite, Lei da Proximidade, estados completos, fidelidade à Bíblia, ergonomia nativa) |
