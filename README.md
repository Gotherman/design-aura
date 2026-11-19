# Design Aura (`design-aura`)

Skill de direção de design, arquitetura de informação e engenharia UI/UX para **Apps Desktop**, **Apps Mobile** (iOS HIG / SwiftUI, Android Material 3 / Jetpack Compose, React Native / Expo, Flutter, PWA) e **Sistemas Complexos** (SaaS, ERPs, Dashboards Operacionais).

Transforma um repositório existente, um planejamento (`CONCEPCAO.md`/PRD) ou uma ideia do zero em:
1. **Especificação Enxuta** (apenas o essencial que altera decisões de produto e design).
2. **Bíblia de Direção de Design** (`DESIGN-BIBLE.md` + `tokens.json` + `tokens.css` validado em WCAG/APCA + Bíblia Visual HTML/PDF opcional).
3. **Construção Fiel Orquestrada** (Onda 0 Orquestrador → Onda 1 até 7 subagentes construtores → Onda 2 Auditor Visual, **teto rígido de 8 subagentes**).
4. **Vitrine Interativa Estilo Figma** (`fluxo.html` canvas infinito com setas Bézier e previews ao vivo, `preview.html` player guiado de uso real e `index.html` galeria com `⌘K`).
5. **Auditoria Objetiva dos 10 Blocos de Leis Inegociáveis** (contraste WCAG/APCA, linter estático anti-slop e inspeção DOM real em Chromium headless).

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
10. **Ergonomia Nativa Mobile, Desktop & Mídia**: iOS HIG e Android Material 3 nativos (safe areas, insets, navigation bar/rail, predictive back, thumb zone); desktop (`⌘K`, atalhos, cockpit); proibido scroll aninhado sem justificativa; `object-fit: cover` e fallback em mídias.

---

## Instalação

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
