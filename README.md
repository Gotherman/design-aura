# Design Aura (`design-aura` · `v2.3.0`)

Skill de direção de design, arquitetura de informação e engenharia UI/UX para **Apps Desktop**, **Apps Mobile** (iOS HIG / SwiftUI, Android Material 3 / Jetpack Compose, React Native / Expo, Flutter, PWA) e **Sistemas Complexos** (SaaS, ERPs, Dashboards Operacionais).

Transforma um repositório existente, um planejamento (`CONCEPCAO.md`/PRD) ou uma ideia do zero (ou executa **Polimento Cirúrgico** sobre telas já aprovadas) em:
1. **Especificação Enxuta sem Jargão** (autópsia seletiva + entrevista curta obrigatória em português direto com trava anti-atropelo quando o usuário tem dúvida).
2. **Mapeamento Categórico Automático de Componentes OSS (`16 Categorias Canônicas`)** (`discover_oss_components.py --scan <repo>` sobre `106+` registries/bibliotecas permissivas + `ui_elements_recipes.json` cobrindo gráficos de estúdio, `BarList`/`Tracker`, SVGs Duotone, emblemas `.icon-emblem`, chips `.chip-sla` com anel SVG, Kanban, calendários, máscaras e micro-interações).
3. **Bíblia Visual de Design** (`DESIGN-BIBLE.md` + `tokens.json`/`tokens.css` em equilíbrio cromático **`65/20/10/5`** com âncora institucional `--surface-brand-dark` em Dark & Light, escopo automático `.on-brand-dark`, **Brand-Anchored Light Mode** com `--surface-tint-soft`, `--chart-1..6` + `DESIGN-BIBLE.pdf` com pranchas visuais reais e sincronia automática de hexes).
4. **Portão das Telas-Mãe + `SHELL-CONTRACT.md` (Onda 0.5) & Modo Polimento Cirúrgico** (Design System com profundidade tátil em 5 camadas, Sidebar minimizável `248px ↔ 68px` anti-truncamento, padrão **Lista Limpa → Detalhe Focado na mesma página**, blindagem mobile contra corte por flex-shrink, `SHELL-CONTRACT.md` enxuto + 1 Tela-Mãe Desktop + 1 Tela-Mãe Mobile validadas visualmente antes de escalar).
5. **Construção Turbo por Subagentes + Anti-Travamento & Fast-Audit Imediato** (`1–3` telas por subagente, **sem teto de 8**, ondas controladas com fallback transparente + auditoria rápida automática e visual do Orquestrador a cada entrega).
6. **Vitrine Interativa Estilo Figma `v2.3.0`** (`fluxo.html` sincronizado com `tokens.css` em Dark/Light com `0` erros de contraste e Hub-and-Spoke fiel às seções, `preview.html` com seletor de jornadas sem scrollbar horizontal + bezel mobile `clip-path`, e `index.html` galeria `⌘K` com miniaturas visuais Dark/Light via `--thumbs`).
7. **Auditoria Paralela Real em Chromium (`--concurrency 4` com contextos isolados e log ao vivo) + 10 Blocos** (`DA-NAV-TRUNCATION`, `DA-HEADER-HSCROLL`, `DA-BRAND-DARK-SCOPE`, `DA-REF-COPY-LEAK`, `DA-CLIPPED-CONTENT`, `DA-MOBILE-FLEX-CLIP`, `DA-DARK-MONOCHROME`, `DA-LIGHT-WASHED-OUT`, `DA-ICON-GENERIC-REPEAT`, `DA-FLAT-CHART-AXIS`, `DA-CARD-INTERNAL-VOID`, `DA-DEAD-SPACE`, `DA-STUB-SCREEN`, `DA-RAW-LINK-LIST`, `DA-FIXED-OVERLAP`, `DA-SERIF-OPERATE`, `DA-SURFACE-FLAT` e `DA-ASSET-404`).

---

## Os 10 Blocos de Leis Inegociáveis

1. **Zero Estética "SaaS de IA Genérico"**: proibido gradientes roxo/índigo/neon gratuitos, glow/glassmorphism sem hierarquia, emojis clichês (`✨🚀⚡🛡️`) como ícones, mistura de outline/solid, eyebrows decorativos, numeração `01 //`, gradiente em texto, barrinha lateral em card e dots/badges `LIVE` falsos.
2. **Hierarquia, Layout & Anti-Cardite**: proibido "cardite aguda" e card dentro de card; proibido repetir "3 cards idênticos de ícone em círculo + título + 2 linhas"; proibido centralizar texto longo; respeitar Lei da Proximidade; 1 CTA primário dominante por dobra; Alto Contraste Ótico com 5 planos `Z0→Z4` e zero espaços mortos em desktop.
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
| `generate_tokens.py` | Python 3 stdlib | Compila `tokens.json` em CSS, Tailwind v4, TypeScript, Swift, Kotlin e Dart |
| `audit_contrast.py` | Python 3 stdlib | Validador WCAG 2.1 + APCA-W3 sobre `tokens.css`, `tokens.json` ou pares avulsos |
| `lint_design_aura.py` | Python 3 stdlib | Linter determinístico dos 10 Blocos de Leis Inegociáveis e AI tells |
| `build_figma_canvas.py` | Python 3 stdlib | Gera `fluxo.html` (Canvas Figma), `preview.html` (Player guiado) e `index.html` (Galeria `⌘K`) |
| `capture_and_audit.mjs` | Node 20+ + Chromium | Captura screenshots multi-viewport (Dark/Light) e audita DOM/contraste/touch-targets via CDP |

---

## Créditos e Inspirações Open-Source

Esta skill integra conceitos e boas práticas de engenharia de design inspirados em:
- [`felipebasurto/unslop-ui`](https://github.com/felipebasurto/unslop-ui) (MIT)
- [`jakubkrehel/make-interfaces-feel-better`](https://github.com/jakubkrehel/make-interfaces-feel-better) (MIT)
- [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) (Apache 2.0)
- [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT)
- [`uizze/uizze`](https://github.com/uizze/uizze) (MIT / Apache 2.0)
