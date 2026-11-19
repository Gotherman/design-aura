# Os 10 Blocos de Leis Inegociáveis (Design Aura)

Regras objetivas e verificáveis que **reprovam automaticamente (`BLOCK`)** na auditoria de Design, Visual, UI e UX. Nenhum componente, tela ou protótipo pode receber veredito `Approve` enquanto violar qualquer regra destes 10 blocos sem justificativa explícita aprovada no briefing da marca.

---

## Bloco 1 — Proibido Estética "SaaS de IA Genérico" (Direção Visual)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B1-01` | Proibido gradientes roxo/índigo/violeta/neon genéricos como paleta padrão sem justificativa explícita da marca ou do briefing. | `lint_design_aura.py` + revisão da `DESIGN-BIBLE.md` |
| `DA-B1-02` | Proibido glow colorido excessivo (`box-shadow: 0 0 24px ...`), blobs desfocados decorativos, glassmorphism sem função de hierarquia ou bordas brilhantes em todos os elementos. | `lint_design_aura.py` + inspeção visual |
| `DA-B1-03` | Proibido usar emojis ou ícones clichês de IA (`✨`, `🚀`, `⚡`, `🛡️`, `🔥`, `💡`, `🎯`) como decoração genérica em títulos, botões, badges ou cards. | `lint_design_aura.py` |
| `DA-B1-04` | Proibido misturar famílias ou estilos de ícones (outline vs solid aleatórios) ou espessuras de traço inconsistentes na mesma interface. Regra: outline como padrão; fill apenas no estado ativo; traço casado com o peso da fonte (`1.5px` para 400, `2px` para 500–600). | Revisão de SVG/ícones |
| `DA-B1-05` | Proibido eyebrows/kickers decorativos em caixa alta com `letter-spacing` largo acima de títulos (`"FEATURES"`, `"PASSPORT"`, `"HOW IT WORKS"`) e numeração decorativa (`"01 //"`, `"01 ·"` quando não é passo real). | `lint_design_aura.py` |
| `DA-B1-06` | Proibido gradiente em texto (`bg-clip-text` / `background-clip: text`), barrinha colorida em apenas um lado de card arredondado (`border-l-4 rounded-xl`) e dots/badges `LIVE`/`NEW`/`AI` estáticos sem binding real de estado. | `lint_design_aura.py` |

---

## Bloco 2 — Hierarquia, Layout e Anti-Cardite (Estrutura)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B2-01` | Proibido "cardite aguda" (colocar tudo dentro de caixas com borda e sombra quando espaço negativo, divisores sutis, lista alinhada ou tabela resolvem melhor) e **proibido card dentro de card**. | `lint_design_aura.py` + inspeção visual |
| `DA-B2-02` | Proibido repetir o template preguiçoso de "3 cards idênticos com ícone em círculo/quadrado colorido + título + 2 linhas" como solução padrão de seção. | Inspeção visual |
| `DA-B2-03` | Proibido centralizar blocos de texto longos ou listas de leitura; alinhamento deve favorecer escaneabilidade pela margem esquerda. | `lint_design_aura.py` |
| `DA-B2-04` | Proibido espaçamento uniforme sem agrupamento lógico (**Lei da Proximidade**): elementos relacionados ficam mais próximos entre si do que de grupos distintos; sempre há mais espaço acima de um título do que abaixo dele. | Inspeção visual + CSS |
| `DA-B2-05` | Proibido múltiplos CTAs primários competindo com o mesmo peso visual na mesma dobra/tela. Cada vista tem no máximo 1 ação primária dominante. | `lint_design_aura.py` + inspeção visual |
| `DA-B2-06` | **Alto Contraste Ótico & Zero Espaços Mortos**: Light Mode usa canvas aterrado com separação clara entre fundo (`Z0/Z1`) e cartões (`Z2`) por contorno nítido (`1.25px`) + sombra dupla sutil — proibido branco lavado onde tudo se mistura. Desktop operacional usa composição de 2 ou 3 zonas sem 60–70% de vazio morto. | Inspeção de `tokens.css` e renders 1440×900 |

---

## Bloco 3 — Contraste, Cor e Acessibilidade (Legibilidade)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B3-01` | Obrigatório respeitar no mínimo **WCAG AA** (`>= 4.5:1` texto normal e placeholders; `>= 3.0:1` texto grande `>= 18pt` / `14pt bold` e componentes UI) e **APCA** (`|Lc| >= 60` corpo, `>= 45` grande/UI). | `audit_contrast.py --strict` + `capture_and_audit.mjs` |
| `DA-B3-02` | Proibido usar preto puro (`#000000`) com branco puro (`#FFFFFF`) sem controle de elevação de superfície, ou textos cinza lavados que prejudicam a leitura em Dark Mode. Em superfícies coloridas, matizar o texto secundário pela cor do fundo/frente, nunca cinza genérico. | `audit_contrast.py` + `lint_design_aura.py` |
| `DA-B3-03` | Proibido áreas de toque/clique menores que **44×44px** em interfaces mobile/iOS (e **48×48dp** com 8dp de respiro em Android), com texto de corpo mínimo de **14px** (ideal 15–16px web, 17pt iOS). | `capture_and_audit.mjs` + `lint_design_aura.py` |

---

## Bloco 4 — Tipografia Intencional (Leitura e Ritmo)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B4-01` | Obrigatório contraste tipográfico claro entre título, subtítulo, corpo e metadados (escala, peso e `line-height`), com medida de leitura confortável (`65–75ch`). Proibido peso `800`/`900` gratuito em textos corridos ou UI comum. | `lint_design_aura.py` + inspeção |
| `DA-B4-02` | Obrigatório `font-variant-numeric: tabular-nums` (`tabular-nums`) em todos os números dinâmicos, preços, contadores, timers e colunas numéricas de tabela. | `lint_design_aura.py` + inspeção |
| `DA-B4-03` | Obrigatório `text-wrap: balance` em títulos curtos (≤6 linhas) e `text-wrap: pretty` em parágrafos/descrições, além de `-webkit-font-smoothing: antialiased` no root. Todo texto dinâmico deve prever quebra limpa ou `text-overflow: ellipsis` sem estourar containers. | `capture_and_audit.mjs` + CSS |

---

## Bloco 5 — Conteúdo Real e Zero Copy de Template (Microcopy)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B5-01` | Proibido usar `"Lorem ipsum"`, `"John Doe"`, `"Jane Doe"`, `"Acme Corp"` ou placeholders genéricos em telas entregues. | `lint_design_aura.py` |
| `DA-B5-02` | Proibido microcopy clichê de IA (`"Transforme seu negócio"`, `"Eleve sua experiência"`, `"Solução definitiva"`, `"Potencializado por IA"`, `"Revolucione sua rotina"`, `"Unlock your potential"`). O texto deve usar verbos concretos e vocabulário do domínio real. | `lint_design_aura.py` |
| `DA-B5-03` | Proibido subtítulos reflexos que repetem o título, *botsplaining* (`"Clique no botão abaixo para..."`), notas de design vazadas (`"(atualiza em tempo real)"`) e correntes de status inchadas (`"12 itens · Sincronizado · v2.1"`). CTAs dizem exatamente o que fazem. | `lint_design_aura.py` + revisão textual |

---

## Bloco 6 — UX Completa e Interação com Propósito (Funcionalidade)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B6-01` | Proibido entregar apenas o "caminho feliz": fluxos e componentes devem prever estados reais aplicáveis (`loading/skeleton`, `empty state` com próxima ação, `error` com recuperação, `sucesso` com feedback). | Revisão de componentes/telas |
| `DA-B6-02` | Proibido `transition: all` / `transition-all`, `hover:scale-105` em todo card, `animate-bounce`/`animate-pulse` decorativo ou transições `> 300ms` em controles simples. Interações devem usar **CSS transitions interrompíveis** em propriedades específicas, saída mais rápida/suave que a entrada, `active:scale-[0.97]` tátil em botões e respeito obrigatório a `prefers-reduced-motion`. | `lint_design_aura.py` + CSS |
| `DA-B6-03` | Proibido esconder ações críticas ou navegação essencial atrás de padrões confusos por estética minimalista. Superfícies do browser (`::selection`, `caret-color`, scrollbars, `text-underline-offset`) devem ser tematizadas pela paleta. | Inspeção CSS + navegador |

---

## Bloco 7 — Precisão Geométrica e Sistema (Acabamento Visual)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B7-01` | **Concentricidade obrigatória**: proibido raios idênticos em elementos aninhados com padding `<= 24px`. Fórmula: `Raio Interno = Raio Externo - Padding` (ou `Externo = Interno + Padding`). | `lint_design_aura.py` + inspeção CSS |
| `DA-B7-02` | Proibido *magic numbers* arbitrários (`7px`, `11px`, `13px`, `15px`, `17px`, `19px`) fora da escala estrita baseada em **4px / 8px** (exceção: `2px`, `6px`, `10px`, `14px` dentro de controles compactos ou ajuste óptico `-2px` no lado do ícone de um botão). | `lint_design_aura.py` |
| `DA-B7-03` | Proibido sombras pretas chapadas como único recurso de profundidade em Dark Mode: a hierarquia `Z0→Z4` em Dark Mode deve evoluir por **luminosidade progressiva de superfície + contorno nítido** (`1px–1.25px`). Em Light Mode, preferir sombra-como-borda em 3 camadas. | `lint_design_aura.py` + `tokens.css` |

---

## Bloco 8 — Semântica e Higiene de Dados (Dashboards e Listas)

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B8-01` | Proibido usar cores semânticas (vermelho/carmim, verde/esmeralda, âmbar/alerta) como decoração sem significado funcional real no domínio. | Revisão visual |
| `DA-B8-02` | Proibido poluir listas e tabelas com excesso de badges/pills coloridas competindo entre si. | Revisão visual |
| `DA-B8-03` | Proibido alinhar colunas numéricas à esquerda em tabelas (sempre à direita + `tabular-nums`) ou exibir barras/gráficos fora de proporção real. Em gráficos: proibido nomear o tipo do gráfico no título, proibido legenda de instrução de leitura, proibido redundância e preferir rótulo direto quando `<= 4` séries. | `lint_design_aura.py` + revisão visual |

---

## Bloco 9 — Formulários, Estados e Acessibilidade de Interação

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B9-01` | Proibido usar `placeholder` como substituto de `<label>` visível (ou `aria-label` quando controle de busca/filtro em barra). | `lint_design_aura.py` + `capture_and_audit.mjs` |
| `DA-B9-02` | Proibido remover `:focus-visible` (`outline: none` / `outline-none`) sem fornecer anel de foco acessível equivalente (`2px+`, contraste >= 3:1). | `lint_design_aura.py` |
| `DA-B9-03` | Obrigatório prever estados reais (`hover`, `active`, `disabled`, `focus`, `invalid`) com mensagens de erro junto ao campo que dizem o que aconteceu e como corrigir. | Revisão de fluxo |
| `DA-B9-04` | Proibido empilhar modais (modal sobre modal) ou executar ações destrutivas sem confirmação explícita ou mecanismo imediato de **Desfazer (Undo)**. | Revisão de fluxo |

---

## Bloco 10 — Ergonomia Nativa Mobile, Desktop & Mídia

| ID | Regra Inegociável | Como verificar |
|---|---|---|
| `DA-B10-01` | Proibido ignorar Safe Areas (notch, Dynamic Island, home indicator, IME/window insets) ou posicionar ações primárias mobile fora da zona natural do polegar (thumb zone). iOS respeita HIG (Tab Bar 2–5 seções, edge-swipe back vivo, Large Titles); Android respeita Material 3 (Nav Bar/Rail adaptativo, Predictive Back vivo, máx 1 FAB). | `05-mobile-ios-android.md` + `capture_and_audit.mjs` |
| `DA-B10-02` | Proibido criar áreas de scroll aninhado (scroll interno dentro de página rolável) sem justificativa estrita de layout (ex.: painel lateral fixo em cockpit desktop `h-dvh`). Evitar `100vh` rígido em mobile (usar `100dvh` + `env(safe-area-inset-*)`). | `lint_design_aura.py` + `capture_and_audit.mjs` |
| `DA-B10-03` | Proibido exibir imagens/avatares sem preservação de proporção (`object-fit: cover` / `object-cover`), sem `alt` adequado ou sem estado de fallback (iniciais/ícone) em caso de falha. | `lint_design_aura.py` + `capture_and_audit.mjs` |

---

## Matriz Rápida de Detecção

| Verificador | Cobertura Principal |
|---|---|
| **`audit_contrast.py`** | Bloco 3 (`DA-B3-01`, `DA-B3-02`) em Light e Dark via WCAG 2.1 + APCA-W3 |
| **`lint_design_aura.py`** | Blocos 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 via análise estática de markup/CSS/TSX/Swift/Kotlin/Dart |
| **`capture_and_audit.mjs`** | Blocos 2, 3, 4, 6, 9, 10 em runtime real no Chromium (1440×900, 768×1024, 390×844, Dark & Light) |
| **Auditor Subagente (Onda 2)** | Regras semânticas e composicionais (anti-cardite, Lei da Proximidade, estados completos, fidelidade à Bíblia, ergonomia nativa) |
