# Design Aura (`design-aura` · `v2.5.0`)

Skill de direção de design, arquitetura de informação, engenharia UI/UX e **QA interativo E2E** para **Apps Desktop**, **Apps Mobile** (iOS HIG / SwiftUI, Android Material 3 / Jetpack Compose, React Native / Expo, Flutter, PWA) e **Sistemas Complexos** (HTML estático ou SPA **React / Vite / Next.js**, SaaS, ERPs, Dashboards Operacionais).

Transforma um repositório existente, um planejamento (`CONCEPCAO.md`/PRD) ou uma ideia do zero (ou executa **Polimento Cirúrgico** sobre telas já aprovadas) em:
1. **Especificação Enxuta Zero-Treinamento** (fluxos humanos de 3–4 passos, documentos reais do trabalho, trava anti-atropelo quando o usuário tem dúvida e zero jargão técnico na interface do trabalhador).
2. **Coerência Cromática & Paridade Semântica Light/Dark (`v2.4.0`)** — acaba com o **monobloco cinza** no Dark e o **tudo-branco** no Light trazendo a família de cores da marca para dentro do workspace (`--surface-brand-header`, `--rim-highlight`, sombras Dark/Light calibradas e superfícies semânticas prontas `--{role}-surface/border/text`), garantindo **vermelho real = erro** nos dois modos (bloqueia erro rosa pastel via `DA-SEMANTIC-HUE-PARITY`), **verde esmeralda = sucesso**, **âmbar = atenção** e `border-subtle >= 1.85:1` / `Z1/Z2 >= 1.18:1` no Light.
3. **Bíblia Visual Autossuficiente & Catálogo Studio** (`DESIGN-BIBLE.md` com Orçamentos de Composição, **Resize In-Place `Fila Limpa → Conferência Focada`**, `DESIGN-BIBLE.pdf` com prancha squircle 6px + barra de decisão tátil + alertas/toasts, e `discover_oss_components.py --scan` sobre `16 Categorias Canônicas`).
4. **Portão das Telas-Mãe (`Onda 0.5`) + Construção por Subagentes com Fast-Audit (`Onda 1`)** (`1–3` telas/subagente, sem teto de 8, `SHELL-CONTRACT.md` enxuto + auditoria imediata a cada entrega).
5. **Vitrine Unificada em Link Único + SPA Dual-Engine (`Onda 2 · Fase 4 Obrigatória`)** (`entrega.html` unificando `Mapa Figma · App ao Vivo · Preview Guiado · Galeria · Bíblia Visual + PDF + Tema` em 3 canais + `serve_entrega.mjs` em 1 única porta `0.0.0.0:4188` servindo `/design/*` + SPA `dist/*`).
6. **Auditoria Paralela Real em Chromium + Pós-Clique (`--concurrency 4 --smoke-interact`)** (`DA-SEMANTIC-HUE-PARITY`, `DA-DARK-FLAT-MONOLITH`, `DA-LIGHT-WASHED-OUT >= 1.85:1`, `DA-TECH-JARGON-UI`, `DA-BADGE-ECHO`, `DA-MOBILE-HERO-BLOAT`, `DA-HEADER-STACK-BLOAT`, `DA-TAB-OVERFLOW`, `DA-B3-01` estendido a emblemas/badges, whitelist `entrega.html`/`.da-hub`, suporte nativo `--base-url` + `"route"` para SPAs).
7. **Fase 4.5 — QA Interativo E2E por Subagentes Testers (`Onda 3 · v2.4.0`)** — Subagentes Testers **Read-Only** fatiados por jornada clicam nos fluxos reais via `scripts/run_workflow_probe.mjs` (zero dependência npm), reportam falhas reais (`P0/P1/P2` + PNGs) ao Orquestrador, que faz triagem de causa raiz, cria o Plano de Correção, lança subagentes corretivos e valida com re-teste direcionado (trava anti-loop: máx. 2 ciclos).


Na v2.5.0, a cobertura pode ser declarada por tela e estado. O probe verifica ações encobertas e valores exatos após interação. O fechamento combina a inspeção dos pilotos, a evidência do build entregue e a verificação de sincronia entre tokens e contratos. Receitas externas entram nos guias existentes conforme a necessidade da entrega.

---

## Os 10 Blocos de Leis Inegociáveis

1. **Zero Estética "SaaS de IA Genérico"**: proibido gradientes roxo/índigo/neon gratuitos, glow/glassmorphism sem hierarquia, emojis clichês (`✨🚀⚡🛡️`) como ícones, mistura de outline/solid, eyebrows decorativos, numeração `01 //`, gradiente em texto, barrinha lateral em card e dots/badges `LIVE` falsos.
2. **Hierarquia, Layout & Anti-Cardite**: reprove caixas redundantes que competem pela atenção; proibido repetir "3 cards idênticos de ícone em círculo + título + 2 linhas"; proibido centralizar texto longo; respeitar Lei da Proximidade; 1 CTA primário dominante por dobra; Alto Contraste Ótico com 5 planos `Z0→Z4` com distribuição adequada à tarefa em desktop.
3. **Contraste, Cor & Acessibilidade**: WCAG AA ≥ 4.5:1 (normal/placeholder) e ≥ 3:1 (grande/UI), APCA `|Lc| >= 60` corpo; proibido `#000000`/`#FFFFFF` puros sem elevação controlada ou cinzas lavados em dark mode; touch targets ≥ 44×44px (mobile/iOS) e ≥ 48×48dp (Android); corpo ≥ 14px.
4. **Tipografia Intencional**: contraste claro de escala/peso/line-height; `tabular-nums` em dados dinâmicos, preços e tabelas; `text-wrap: balance` em títulos curtos e `pretty` em parágrafos; proteção contra overflow/truncamento.
5. **Conteúdo Real & Zero Copy de Template**: proibido *Lorem ipsum*, *John Doe*, *Acme Corp*; proibido clichês ("Transforme seu negócio", "Eleve sua experiência", "Solução definitiva", "Potencializado por IA"); zero subtítulos redundantes e zero *botsplaining*.
6. **UX Completa & Motion com Propósito**: estados loading/skeleton, empty, error+recuperação e sucesso. Página, card e componente animam quando a mudança precisa ser sentida; desktop, iOS e Android têm curvas próprias. Proibido `transition-all`, `hover:scale-105` em todo card, bounce e loop que não seja espera.
7. **Precisão Geométrica & Sistema**: raios concêntricos (`Raio Interno = Raio Externo - Padding`); escala estrita 4/8px sem magic numbers; profundidade em Dark Mode por luminosidade de superfície; alinhamento óptico de ícones.
8. **Semântica & Higiene de Dados**: cores semânticas apenas com significado real; sem excesso de badges competindo em listas/tabelas; colunas numéricas alinhadas à direita; gráficos proporcionais sem título de tipo de gráfico nem instruções de leitura.
9. **Formulários, Estados & Interação**: proibido placeholder substituindo `<label>`; proibido remover `:focus-visible` sem substituto equivalente; estados `hover`/`active`/`disabled`/`focus`/`invalid` + mensagens orientando correção; proibido modal sobre modal e ações destrutivas sem confirmação ou Desfazer.
10. **Ergonomia Nativa Mobile, Desktop & Mídia**: tokens iguais entre plataformas, shell diferente. iOS HIG e Android Material 3 nativos (safe areas, insets, navigation bar/rail, predictive back, thumb zone); desktop (`⌘K`, atalhos, cockpit); web com sidebar, rail ou bottom nav conforme a largura; proibido scroll aninhado sem justificativa; `object-fit: cover` e fallback em mídias.

---

## Instalação

No T3 Code, no chat do projeto, digite `/designaura`. Se o repositório já tem telas, a skill começa a remodelação sem perguntar se deve começar.

### Via CLI `skills` (com acesso ao repo privado)
```bash
npx skills add Gotherman/design-aura -g
```

### Instalação Manual (Global nos Agentes)
Copie a pasta `skills/design-aura` para o diretório de skills do seu agente:
- **Universal / Antigravity / T3 Code**: `~/.agents/skills/design-aura` ou `~/.gemini/config/skills/design-aura`
- **Claude Code**: `~/.claude/skills/design-aura`
- **Codex**: `~/.codex/skills/design-aura`

---

## Scripts Inclusos (`skills/design-aura/scripts/`)

| Script | Runtime | Função |
|---|---|---|
| `design_intel.py` | Python 3 stdlib | Motor offline BM25 para pesquisa de domínio, paletas, tipografia, padrões e bibliotecas OSS |
| `discover_oss_components.py` | Python 3 stdlib | Casa uma interação com registries free/OSS, galerias de referência e a API do GitHub/npm (`--online`) |
| `generate_tokens.py` | Python 3 stdlib | Compila `tokens.json` em CSS, Tailwind v4, TypeScript, Swift, Kotlin e Dart com superfícies semânticas e sombras/rims Dark & Light |
| `audit_contrast.py` | Python 3 stdlib | Validador WCAG 2.1 + APCA-W3 + `DA-SEMANTIC-HUE-PARITY` + `DA-DARK-FLAT-MONOLITH` + `DA-LIGHT-WASHED-OUT >= 1.85:1` |
| `lint_design_aura.py` | Python 3 stdlib | Linter determinístico dos 10 Blocos + `DA-TECH-JARGON-UI` + `DA-BADGE-ECHO` |
| `build_figma_canvas.py` | Python 3 stdlib | Gera `entrega.html` (Hub link único), `fluxo.html` (Canvas Figma), `preview.html` e `index.html` (HTML e SPA `"route"`) |
| `serve_entrega.mjs` | Node 20+ (zero dep) | Servidor HTTP de porta única (`0.0.0.0:4188`) combinando `/`, `/design/*` e SPA `/app/*` (`dist/*`) |
| `capture_and_audit.mjs` | Node 20+ + Chromium | Captura paralela (HTML + SPA `--base-url`), auditoria DOM/contraste/emblemas/anti-poluição e smoke pós-clique (`--smoke-interact`) |
| `run_workflow_probe.mjs` | Node 20+ + Chromium | Motor CDP interativo E2E para Subagentes Testers (Fase 4.5) clicarem nos fluxos reais, validarem assertivas/layout e salvarem PNGs |

---

## Créditos e Inspirações Open-Source

Esta skill integra conceitos e boas práticas de engenharia de design inspirados em:
- [`felipebasurto/unslop-ui`](https://github.com/felipebasurto/unslop-ui) (MIT)
- [`jakubkrehel/make-interfaces-feel-better`](https://github.com/jakubkrehel/make-interfaces-feel-better) (MIT)
- [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) (Apache 2.0)
- [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT)
- [`uizze/uizze`](https://github.com/uizze/uizze) (MIT / Apache 2.0)
