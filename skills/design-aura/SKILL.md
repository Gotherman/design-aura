---
name: design-aura
description: >-
  Diretor de design e engenharia UI/UX de classe mundial para apps Desktop (Electron, Tauri, macOS, Windows), Mobile (iOS HIG/SwiftUI, Android Material 3/Compose, React Native/Expo, Flutter, PWA) e Sistemas Web/SaaS/ERPs/Dashboards. Use sempre que o usuario pedir para planejar, especificar, desenhar, criar, revisar ou remodelar o visual de interfaces e telas já existentes, fluxos, design systems, tokens ou prototipos navegaveis, aplicar anti-AI-slop, garantir alto contraste otico, micro-craft e acessibilidade WCAG/APCA, procurar componentes free/open source que caibam na interface, ou definir animacoes com vida para desktop, iOS e Android. Tambem use para ler um repositorio ou planejamento e transformar isso em uma Biblia Visual de Design com especimes reais, Portao de Telas-Mae, construcao fiel por subagentes (1-3 telas por subagente com auditoria rapida imediata do orquestrador) e vitrine estilo Figma (fluxo.html, preview.html, index.html).
license: MIT
compatibility: >-
  Python 3.9+ (stdlib) e Node.js 20+ com Chromium/Chrome opcional para captura, PDF visual e auditoria DOM real headless.
metadata:
  version: "2.2.1"
  author: "Lucas (Gotherman)"
  display-name: "Design Aura"
---

# Design Aura (`v2.2.1`)

Sistema completo de direção criativa, arquitetura de UI/UX, engenharia visual e orquestração multi-agente para produzir **sistemas web operacionais, apps desktop e aplicativos mobile** com nível de estúdio premiado — zero estética genérica de IA, zero telas casca vazias, contraste irretocável, ergonomia nativa e verificação visual real em cada etapa.

## Ponto de partida universal

Leia o repositório e o planejamento por completo antes de desenhar: concepção, PRD, proposta, rotas, telas, tokens, componentes, logo e o vocabulário real do negócio. Cada projeto ganha um design saído desse material.

1. **Repositório que já tem design e telas.** Dois caminhos claros:
   - **Remodelar o visual (Autópsia Seletiva):** identifique objetivamente o que incomoda/falha nas telas atuais (ex.: contraste fraco, desorganização, visual genérico) e o que precisa sobreviver (rotas, tarefas, dados reais, riqueza funcional). **Regra anti-sabotagem:** remodelar significa *superar em beleza, clareza e densidade útil* o que já existia — **NUNCA** use "remodelar" para proibir cards/superfícies `Z2`, recusar bibliotecas OSS úteis (como ECharts/gráficos/ícones), apagar as cores vivas da marca em bege/marrom morto ou empobrecer telas em tabelas peladas!
   - **Ajuste pontual:** altere só o que foi pedido e preserve o que já funciona.
2. **Planejamento sem telas** (`CONCEPCAO.md`, PRD, requisitos, proposta): extraia domínio, perfis, módulos, fluxos e restrições já decididas.
3. **Ideia do zero:** conduza a especificação enxuta antes de gerar código ou telas.

Regra absoluta: **nunca invente dados de negócio, diferenciais ou métricas.** Demonstração usa dados fictícios verossímeis e completos (`>= 5` registros em listas/tabelas — nunca stubs de 2 linhas com desculpa de "amostra"), mantendo os mesmos valores em todas as telas.

---

## Fluxo End-to-End (5 Etapas com Portões Reais)

```text
FASE 1 (Especificação Enxuta)  → Entrevista curta obrigatória nos pontos críticos em aberto
FASE 2 (Onda 0 · Bíblia Visual) → DESIGN-BIBLE.md + tokens.css + screen-manifest + PDF VISUAL → [PORTÃO 1: Aprovação]
FASE 2.5 (Onda 0.5 · Telas-Mãe) → Design System + 1 Tela-Mãe Desktop + 1 Mobile + PNGs → [PORTÃO 2: Validação Visual]
FASE 3 (Onda 1 + Fast-Audit)   → Subagentes (1–3 telas cada, SEM teto de 8) + Fast-Audit imediato por entrega
FASE 4 (Onda 2 · Vitrine + QA) → build_figma_canvas.py (Hub-and-Spoke) + Auditoria Global + Entrega Acessível
```

---

### Fase 1 — Especificação Enxuta (Linguagem Clara, Sem Jargão e Zero Atropelo)

Antes de paleta, tipografia ou layout, leia o pedido, o repositório e os documentos. Pergunte **em uma única rodada clara**, marcando uma opção **(Recomendada)** em cada pergunta.

**Regras de ouro da entrevista (`v2.2.0`):**
- **Português simples e efeito visual concreto:** NUNCA jogue jargão de design/técnico solto (*"WCAG/APCA"*, *"assinatura contida"*, *"Contrato de Plataforma"*) sem traduzir em 1 frase curta o que o usuário vai **ver e sentir na tela**.
- **Trava Anti-Atropelo em Caso de Dúvida:** se o usuário responder *"não entendi"*, *"como assim?"* ou demonstrar dúvida em qualquer pergunta, **PARE IMEDIATAMENTE** — **NUNCA assuma a opção por conta própria nem gere a Bíblia ainda!** Explique em português direto com exemplo visual do produto e peça a confirmação dele antes de seguir para a Onda 0.

**6 pontos críticos obrigatórios** (nunca assuma silenciosamente se o prompt atual não respondeu):
1. **Em remodelação — o que manter vs o que incomoda:** o que já existe que precisa sobreviver e o que o usuário quer ver drasticamente melhorado.
2. **Tema padrão & Equilíbrio da Cor da Marca (`65/20/10/5`):** qual tema abre por padrão (*Escuro com alternância para Claro* ou *Claro com alternância para Escuro*) e se prefere o **equilíbrio 65/20/10/5 (Recomendado)** — fundo arquitetônico com subtom suave, a cor oficial da empresa presente com personalidade nas zonas principais (*Sidebar, Card-Rei de cada tela e abas ativas*) e acompanhada de cores harmônicas nos gráficos e alertas (nem "tudo azul pesado", nem "preto morto onde a marca sumiu").
3. **Estratégia Anti-Poluição em Telas Densas no Desktop:** **(Recomendado) Lista Limpa → Detalhe Focado na mesma página** (abre em lista espaçosa com KPIs e filtros; ao clicar num item, expande o detalhe completo em tela cheia na mesma página com `← Voltar à lista / Esc` e `‹ Anterior · Próxima ›`), ou painéis em 3 colunas simultâneas (reservado apenas para Chat/Inbox em tempo real).
4. **Superfícies & papel do Mobile:** web desktop, desktop nativo, mobile (iOS / Android / PWA) — e se o mobile será um **app executivo focado** ou as **mesmas rotinas do desktop adaptadas**.
5. **Personalidade Tipográfica & Detalhes do Domínio:** **(Recomendado) Precisão executiva (`Geist` / `Inter` com números monetários tabulares proporcionais + mono só para códigos/CNPJ/atalhos)** e se entra algum detalhe sutil do ofício (com descrição prática).
6. **Modelos de execução (OBRIGATÓRIO):** qual modelo conduz o **Orquestrador** (desenha Bíblia, Telas-Mãe e audita) e qual modelo constrói as demais telas em paralelo nos **subagentes** (`1–3` telas cada). Grave ambos no Contrato de plataforma e obedeça na Fase 3.

Pergunte também, somente se o repositório/pedido ainda não fechou:
7. **Tipo de produto:** `Operate` (sistema de trabalho diário, ERP, operação, backoffice, DevTools), `Read` (editorial/analítico) ou `Persuade` (landing/vitrine).
8. **Quem usa e a decisão de 1 segundo:** perfil principal e a primeira decisão acionável ao abrir o sistema.

**Regra-mãe de superfície:** tokens (cor, tipo, espaço, elevação, ícone) atravessam as superfícies; navegação, densidade, alvo de entrada e overlay mudam por plataforma ([04-desktop-e-sistemas.md](references/04-desktop-e-sistemas.md) e [05-mobile-ios-android.md](references/05-mobile-ios-android.md)).

Grave tudo no **Contrato de plataforma**, no topo da `DESIGN-BIBLE.md`.

---

### Fase 2 — Bíblia Visual de Design (Onda 0 · Orquestrador)

Antes de construir ou delegar qualquer tela, o Orquestrador cria o **Contrato Único de Verdade**:

1. **Pesquisa determinística + Mapeamento Categórico Automático de Componentes OSS (`16 Categorias Canônicas`)**:
   ```bash
   python3 <skill_dir>/scripts/design_intel.py "<domínio e objetivo>" --platform <desktop|mobile|system|all> --stack <stack> --format markdown
   python3 <skill_dir>/scripts/discover_oss_components.py --scan <caminho-do-repositorio-ou-plano> --stack <stack> --platform <desktop|mobile|system|ios|android> --mode <operate|read|persuade>
   ```
   *(Para consultas pontuais ou pesquisa ao vivo no GitHub/npm, use também `discover_oss_components.py --need "<interação>" [--online]` ou `--category <id>`.)*
   - O `--scan` lê o repositório/planejamento, identifica automaticamente quais das **16 Categorias Canônicas de UI/UX** o projeto precisa (`charts-telemetry-financial`, `icons-emblems-avatars`, `badges-chips-timers-status`, `kpi-metrics-sparklines`, `data-tables-lists-progressive`, `kanban-drag-drop-workflows`, `forms-inputs-pickers-upload`, `calendar-gantt-timelines`, `inbox-chat-omnichannel-ai`, etc.) e devolve **bibliotecas permissivas (`MIT`/`Apache-2.0`/`ISC`) + Receitas de Micro-Componentes de Estúdio + Curadoria de Ícones Específicos do Domínio** prontos para a Seção 8 da Bíblia!
   - **Adapte o vocabulário e o fluxo do molde ao domínio real** — nunca descarte componentes OSS sofisticados (TradingView Lightweight Charts / ECharts Combo com HUD vivo, Tremor BarList & Tracker, Tabler/Solar Duotone SVGs, SortableJS, IMask, AutoAnimate, tinykeys, FullCalendar, Floating UI).

2. **Ler as referências obrigatórias do escopo**:
   - Sempre: [01-leis-inegociaveis.md](references/01-leis-inegociaveis.md) e [02-biblia-de-design.md](references/02-biblia-de-design.md).
   - Desktop / Sistemas / ERPs: [04-desktop-e-sistemas.md](references/04-desktop-e-sistemas.md).
   - Mobile iOS / Android / Cross-platform: [05-mobile-ios-android.md](references/05-mobile-ios-android.md).
   - Micro-craft e Motion: [06-micro-craft-e-motion.md](references/06-micro-craft-e-motion.md) e [10-motion-anti-slop.md](references/10-motion-anti-slop.md).
   - Componentes free/OSS: [09-pesquisa-componentes-oss.md](references/09-pesquisa-componentes-oss.md).

3. **Gerar os artefatos fundacionais (nesta ordem)**:
   - **`tokens.json` → `tokens.css`**: modele com base em [assets/tokens.example.json](assets/tokens.example.json) e valide:
     ```bash
     python3 <skill_dir>/scripts/generate_tokens.py tokens.json --out tokens.css --format all --check-contrast
     python3 <skill_dir>/scripts/audit_contrast.py tokens.css --strict
     ```
     **Portão 0**: não avance se `audit_contrast.py --strict` falhar. Preserve a saturação viva da cor de ação da marca (`DA-B3-04`: se a cor viva precisa de texto escuro `#101822` para bater WCAG >= 4.5:1, use texto escuro em vez de transformar laranja em marrom morto!).
   - **`screen-manifest.json`** ([08-canvas-figma-manifest.md](references/08-canvas-figma-manifest.md)):
     - **Disciplina de escopo (Qualidade > Fragmentação):** consolide rotinas relacionadas via abas, filtros, drawers e sheets reais dentro de **12 a 24 telas profundas e ricas** em vez de estilhaçar o produto em 40 páginas vazias de 2 KB. Acima de 24 telas exige justificativa concreta na Bíblia e aprovação explícita do usuário.
     - Inclua seções, `startScreenId`, arestas com `tier: "primary" | "secondary"` (para o mapa Figma ficar limpo) e jornadas reais ponta a ponta.
   - **`DESIGN-BIBLE.md` + `DESIGN-BIBLE.html` + `DESIGN-BIBLE.pdf` (BÍBLIA VISUAL):**
     Use [assets/design-bible-template.md](assets/design-bible-template.md) incluindo anatomia executável de CSS (seção 8.1) e piso de riqueza/widgets por tela, e renderize **com `--tokens tokens.css`** para incluir pranchas visuais reais no PDF:
     ```bash
     python3 <skill_dir>/scripts/render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css --out-dir .
     ```
     O PDF agora mostra **pranchas visuais renderizadas** (Light & Dark `Z0`–`Z4`, swatches reais, tipografia, botões, badges semânticos e card `Z2`) — o usuário nunca mais aprova no escuro.

4. **Portão 1 — Pare para aprovação da Bíblia Visual:**
   Entregue `DESIGN-BIBLE.pdf`, `DESIGN-BIBLE.md` e `tokens.css` com resumo curto (superfícies, paleta/tipografia, bibliotecas OSS com gráficos/interações, lista consolidada de telas e modelos escolhidos). **Não construa as telas nem chame subagentes até aprovação explícita.**

---

### Fase 2.5 — Portão das Telas-Mãe (`Golden Screens` · Onda 0.5 · Orquestrador)

Imediatamente após a aprovação da Bíblia, **ANTES** de disparar os subagentes construtores em paralelo:

1. O Orquestrador constrói a fundação real completa:
   - `tokens.css` + `shell.css` + `shell.js` (Design System rico: equilíbrio cromático `65/20/10/5` com 3 Zonas de Presença da Marca e `--chart-1..6`, profundidade tátil de 5 camadas, **Sidebar Desktop minimizável `232px ↔ 68px` com `«` e `[` em `localStorage`**, zero duplicação de navegação na Topbar, `.card-brand-hero`, `.icon-emblem` com spotlight, `.chip-sla` com anel SVG circular, `.chip-status` com halo, `.chip-kv`, modais/drawers/sheets, `⌘K`, toast com Desfazer, Light nítido & Dark com subtom sutil e bibliotecas OSS vendored com zero 404).
   - **`SHELL-CONTRACT.md` (`~100 linhas`, OBRIGATÓRIO em `v2.2.0`):** resumo executável do `<head>`, esqueleto HTML do shell, catálogo de classes CSS de `shell.css` e helpers de `shell.js` para que cada subagente comece a gravar telas no passo 2 sem perder o turno lendo `4.000+ linhas`!
   - **1 Tela-Mãe Desktop** (usando o padrão **Lista Limpa → Detalhe Focado na Mesma Página** quando for fila/tabela densa + gráfico/telemetria de estúdio com HUD vivo, `>= 5` registros reais e interações completas).
   - **1 Tela-Mãe Mobile** (se o projeto possui mobile: navegação nativa no terço inferior, `.card-brand-hero`, `.icon-emblem` específicos do domínio, safe areas, zero texto cortado sob a bottom bar e bottom sheet interativo).
2. O Orquestrador audita as Telas-Mãe imediatamente:
   ```bash
   python3 <skill_dir>/scripts/lint_design_aura.py <telas-mae> --strict
   node <skill_dir>/scripts/capture_and_audit.mjs <telas-mae> --out <dir_audit_golden> --viewports desktop,mobile --themes dark,light --strict
   ```
   Se houver ajustes após a revisão do usuário no Portão 2, atualize `tokens.css`, `shell.css`, `SHELL-CONTRACT.md` e re-execute `render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css` (sincronizando automaticamente as tabelas da Bíblia) antes de disparar os subagentes!
3. **Portão 2 — Validação rápida do padrão visual:**
   Mostre os PNGs (ou link preview) das 2 Telas-Mãe ao usuário para confirmar que o visual real bate 100% com a expectativa (pule esta pausa apenas se o usuário já pediu explicitamente *"aprovado, construa tudo direto sem parar nas telas-mãe"*).
   - **Fronteira rígida — o que a Tela-Mãe trava vs o que NUNCA se copia:**
     - **HERDA 100% (DNA Visual & Sistema):** tokens (`Z0–Z4`, paleta, bordas, sombras, Dark/Light), tipografia, escala `4/8px`, raios concêntricos, shell externo (barra superior, sidebar/rail, dock mobile, `⌘K`, ícones), gramática de componentes (botões, badges, inputs, cards `Z2`, drawers/sheets, toasts) e **régua de acabamento**.
     - **NUNCA COPIA (Arquitetura Interna & Lógica da Tela):** o layout interno, o número de zonas e o fluxo de trabalho pertencem **exclusivamente à tarefa daquela tela**. Exemplo: se a Tela-Mãe é um cockpit de 3 zonas (Financeiro), o Funil continua Kanban de colunas arrastáveis, Editais continua tabela + inspector, Atendimento continua Inbox + chat + ficha, Configurações/Perfil usa seções de formulário focadas, e Login usa split-screen limpo. **Clonar a estrutura interna da Tela-Mãe para telas de outra natureza reprova no Fast-Audit.**

---

### Fase 3 — Orquestração Sem Teto Artificial + Fast-Audit Loop (Onda 1)

Consulte [03-orquestracao-subagentes.md](references/03-orquestracao-subagentes.md) para fatiamento, briefing rico e auditoria imediata:

- **Sem limite rígido de 8 subagentes!** O que governa a qualidade é o **limite estrito de telas por subagente**:
  - **Tela ultra-densa / cockpit 3 zonas** (com gráficos, filas, chat ou inspector rico): **`1` tela dedicada por subagente**.
  - **Telas operacionais padrão ou mobile ricas**: **máximo `2–3` telas por subagente**.
  - **Telas auxiliares leves** (acesso, perfil, preferências): **máximo `3` telas por subagente**.
  - Dispare quantos subagentes forem necessários para cobrir **100% das telas num único processo**, agrupando em lotes paralelos (ex.: 4–6 simultâneos conforme a capacidade do ambiente) usando **exatamente o modelo gravado no Contrato de plataforma**.
- **Briefing Rico com `SHELL-CONTRACT.md` & Protocolo de Turno Único (`v2.2.0`):**
  - Passe a cada subagente: seu slice exato (`1–3` telas), o caminho do **`SHELL-CONTRACT.md` (~100 linhas)** + a Tela-Mãe como referência visual, os widgets/gráficos OSS e receitas de micro-componentes das categorias daquela tela (`.card-brand-hero`, `.icon-emblem`, `.chip-sla`, Combo HUD Chart, BarList, Tracker), os dados fictícios compartilhados (`>= 5` registros) e o **comando único de auto-auditoria** (`lint_design_aura.py` + `capture_and_audit.mjs`).
  - **Trava de Escrita Incremental em Turno Único:** instrua o subagente a gravar a Tela 1 imediatamente no disco, depois a Tela 2, e só então rodar a validação — **proibido** ler `4.000+` linhas antes de escrever, encerrar o turno apenas com plano ou tentar instalar Puppeteer/Playwright.
  - **Proibido** escrever `"sem classe card"` ou engessar o subagente impedindo estilos locais da tela: o subagente **pode** escrever `<style>` ou CSS local da sua tela usando **exclusivamente** `var(--token)` do `tokens.css`.
- **OBRIGATÓRIO — Fast-Audit Imediato pelo Orquestrador a cada Entrega de Subagente:**
  - Assim que **cada** subagente concluir seu slice (`1–3` telas), o Orquestrador **não acumula erros para o final**: ele audita aquele slice **imediatamente**:
    1. Executa `lint_design_aura.py <arquivos-do-slice> --strict`.
    2. Executa `capture_and_audit.mjs <arquivos-do-slice> --out <dir_audit>/slices/<id> --themes dark,light --strict`.
    3. Abre os PNGs do slice e compara diretamente contra a **Tela-Mãe aprovada** (substância visual, zero vazio morto `DA-DEAD-SPACE`, zero casca rasa `DA-STUB-SCREEN`, zero recorte por barra fixa `DA-FIXED-OVERLAP`, interatividade real e fidelidade cromática).
    4. **Se falhar em qualquer critério técnico OU estético:** o Orquestrador corrige na hora (se for pontual) ou devolve feedback cirúrgico imediato ao subagente para refazer aquele slice **antes** da consolidação final!

---

### Fase 4 — Vitrine Estilo Figma (Hub-and-Spoke) + Auditoria Global + Entrega Acessível (Onda 2)

1. **Reconciliação de cobertura 100% + Vitrine Estilo Figma** ([08-canvas-figma-manifest.md](references/08-canvas-figma-manifest.md)):
   ```bash
   python3 <skill_dir>/scripts/build_figma_canvas.py screen-manifest.json --tokens tokens.css --out <dir_telas> --verify-files
   ```
   Entrega automaticamente:
   - `fluxo.html`: canvas estúdio Figma **Dark-first** com layout panorâmico **Hub-and-Spoke** (Acesso → `★ Tela Inicial` em destaque → raias horizontais Desktop à direita → faixa dedicada Mobile embaixo), higiene automática de arestas (`Setas: Principais` vs `Todas (E)`), botões rápidos `★ Início` e `Mobile`, filtros com contagem, previews ao vivo em iframe, inspetor e minimapa.
   - `preview.html`: player guiado de uso real por jornada/persona com enquadramento automático mobile/desktop.
   - `index.html`: galeria filtrável por módulo com busca instantânea `⌘K` / `Ctrl+K`.

2. **Executar os 3 portões globais de auditoria** ([07-auditoria-e-veredito.md](references/07-auditoria-e-veredito.md)):
   ```bash
   python3 <skill_dir>/scripts/audit_contrast.py tokens.css --strict
   python3 <skill_dir>/scripts/lint_design_aura.py <dir_projeto> --strict
   node <skill_dir>/scripts/capture_and_audit.mjs --manifest screen-manifest.json --out <dir_audit> --viewports desktop,mobile --themes dark,light --strict
   ```
   *(Em `v2.2.1`, `--manifest` audita automaticamente também `fluxo.html` aguardando todos os iframes `.is-loaded`, `preview.html` com bezel mobile `clip-path` anti-vazamento e `index.html`, além de checar `DA-JS-ERROR`, `DA-ASSET-404`, `DA-CLIPPED-CONTENT`, `DA-MOBILE-FLEX-CLIP`, `DA-DEAD-SPACE`, `DA-CARD-INTERNAL-VOID`, `DA-STUB-SCREEN`, `DA-RAW-LINK-LIST`, `DA-FIXED-OVERLAP`, `DA-SERIF-OPERATE` e `DA-SURFACE-FLAT`; e `audit_contrast.py` + `lint_design_aura.py` checam também `DA-DARK-MONOCHROME`, `DA-LIGHT-WASHED-OUT`, `DA-ICON-GENERIC-REPEAT`, `DA-FLAT-CHART-AXIS` e `DA-MOBILE-FLEX-CLIP`.)*

3. **Inspeção visual final & Entrega real em ambiente local ou remoto**:
   - Inspecione os PNGs finais (inclusive `fluxo.html`, `preview.html`, `index.html`). Só encerre com veredito **`Approve`** (`0 BLOCK`, `0 HIGH` e qualidade estética validada).
   - **Regra de entrega acessível:** se estiver em sandbox/servidor remoto onde o navegador do usuário não alcança `localhost`, **nunca** entregue apenas caminhos locais ou `http://localhost:...` sem alternativa funcional — abra a vitrine na ferramenta de preview do ambiente (quando disponível) ou informe um link público/acessível verificado com `HTTP 200`, além dos caminhos dos arquivos.

---

## Os 10 Blocos de Leis Inegociáveis (Resumo Executivo `v2.0`)

Qualquer violação abaixo **reprova automaticamente** (`BLOCK` / `HIGH`). Detalhes completos em [01-leis-inegociaveis.md](references/01-leis-inegociaveis.md):

1. **Zero Estética "SaaS de IA Genérico"**: proibido gradientes roxo/índigo/neon gratuitos, glow/glass decorativo, emojis clichês (`✨🚀⚡🛡️`) como ícones, mistura de outline/solid, eyebrows decorativos, numeração `01 //`, gradiente em texto, barrinha lateral em card arredondado e dots/badges `LIVE` falsos.
2. **Hierarquia, Superfícies `Z2` & Piso de Substância (Anti-Cardite ≠ Proibir Cards)**: proibido *card dentro de card* e *3 cards vazios de landing*, mas **obrigatório** usar superfícies `Z2` elevadas com contorno/profundidade real. **Proibido** banir cards (`"sem classe card"`), entregar telas casca rasas (`DA-STUB-SCREEN`), deixar `> 45%` de vazio morto ou inspector de 1 linha (`DA-DEAD-SPACE`) ou usar links `<a>` azuis sublinhados crus em listas/menus (`DA-RAW-LINK-LIST`).
3. **Contraste, Vitalidade Cromática & Acessibilidade**: WCAG AA `>= 4.5:1` normal / `>= 3:1` grande, APCA `|Lc| >= 60`; proibido `#000000`/`#FFFFFF` crus ou apagar a cor viva da marca em marrom/bege morto (`DA-B3-04`: prefira texto escuro sobre acento vivo quando necessário); touch targets `>= 44×44px` (mobile/iOS) e `>= 48×48dp` (Android); corpo `>= 14px`.
4. **Tipografia Intencional (`Operate` sem Serifa Editorial)**: escala/peso nítidos; `tabular-nums` obrigatório em dados/tabelas; `text-wrap: balance/pretty`; `-webkit-font-smoothing: antialiased`; **proibido** usar fontes serifadas editoriais (`Source Serif`, `Georgia`, `Palatino`, `Times`) em sistemas operacionais `Operate` sem pedido explícito (`DA-B4-04` / `DA-SERIF-OPERATE`).
5. **Conteúdo Real & Zero Copy de Template ou Dev-Leak**: proibido *Lorem ipsum*, clichês de IA, *botsplaining* e textos vazados de desenvolvimento (*"não estão nesta amostra"*, *"semente do funil"* — `DA-B2-08A`).
6. **UX Completa & Motion com Propósito**: estados reais (loading/skeleton, empty, error+retry, sucesso+Desfazer); animações comunicam estado com curvas próprias por plataforma ([10-motion-anti-slop.md](references/10-motion-anti-slop.md)); proibido `transition-all`, `hover:scale-105` em todo card e loops gratuitos.
7. **Precisão Geométrica & Sistema**: raios concêntricos (`Interno = Externo - Padding`); escala 4/8px sem *magic numbers*; profundidade em Dark Mode por luminosidade progressiva `Z0→Z4` + contorno sutil; alinhamento óptico de ícones.
8. **Semântica & Higiene de Dados**: cores semânticas com significado real; máx. 2 selos por linha; números alinhados à direita; gráficos proporcionais reais (ECharts/SVG) sem nomear tipo de gráfico no título.
9. **Formulários, Estados & Interação**: `<label>` visível obrigatório; `:focus-visible` preservado; `<textarea>`/inputs estilizados pelo design system (`DA-B9-05`); proibido modal sobre modal e ação destrutiva sem confirmação ou Desfazer.
10. **Ergonomia Nativa Mobile, Desktop & Zero Recorte Fixo**: iOS HIG e Android Material 3 reais; Desktop (`⌘K`, atalhos, master-detail/cockpit); zero scroll aninhado acidental; `object-fit: cover`; **zero conteúdo cortado sob barra fixa inferior/superior** (`DA-FIXED-OVERLAP` / `DA-B10-06`).

---

## Modos Rápidos de Uso

| Pedido | Ação | Referência |
|---|---|---|
| **`/designaura`** | Autópsia seletiva + Fase 1 curta obrigatória → Bíblia Visual PDF → Telas-Mãe → Subagentes (1–3 telas) + Fast-Audit → Vitrine Figma | [designaura/SKILL.md](../designaura/SKILL.md) |
| **`biblia`** | Rodar Fase 1 + Fase 2 e gerar `DESIGN-BIBLE.md/.pdf` visual, `tokens.json/css` e `screen-manifest.json` | [02-biblia-de-design.md](references/02-biblia-de-design.md) |
| **`construir`** | Validar Telas-Mãe (Onda 0.5), fatiar 1–3 telas/subagente sem teto de 8 com Fast-Audit imediato e gerar vitrine | [03-orquestracao-subagentes.md](references/03-orquestracao-subagentes.md) |
| **`auditar`** | Rodar `audit_contrast.py`, `lint_design_aura.py` e `capture_and_audit.mjs` (incluindo vitrine e craft checks) | [07-auditoria-e-veredito.md](references/07-auditoria-e-veredito.md) |
| **`polir`** | Aplicar micro-craft, remoção de vazios/AI tells e correções de auditoria em lote, depois revalidar | [06-micro-craft-e-motion.md](references/06-micro-craft-e-motion.md) |
| **`canvas`** | Gerar/reorganizar `fluxo.html`, `preview.html` e `index.html` em Hub-and-Spoke (`--relayout` se preciso) | [08-canvas-figma-manifest.md](references/08-canvas-figma-manifest.md) |

---

## Mapa de Referências e Scripts

- `references/01-leis-inegociaveis.md` — Os 10 Blocos completos + regras `v2.0` de substância, vitalidade cromática, tipografia `Operate` e zero recorte fixo.
- `references/02-biblia-de-design.md` — As 12 seções da Bíblia Visual + espécimes reais no PDF.
- `references/03-orquestracao-subagentes.md` — Orquestração sem teto de 8 subagentes, 1–3 telas por subagente, Onda 0.5 (Telas-Mãe) e Fast-Audit Loop imediato.
- `references/04-desktop-e-sistemas.md` — Cockpit 3 zonas, master-detail, shell por largura, alto contraste ótico.
- `references/05-mobile-ios-android.md` — iOS HIG, Android Material 3, thumb zone, safe areas, PWA.
- `references/06-micro-craft-e-motion.md` — Raios concêntricos, alinhamento óptico, sombras, tipografia e motion.
- `references/07-auditoria-e-veredito.md` — Fast-Audit por subagente + Auditoria Global + formato de Veredito + entrega remota.
- `references/08-canvas-figma-manifest.md` — `screen-manifest.json`, layout Hub-and-Spoke e higiene de arestas `primary`/`secondary`.
- `references/09-pesquisa-componentes-oss.md` — Curadoria de componentes OSS free com licenças seguras.
- `references/10-motion-anti-slop.md` — Curvas de motion separadas para Desktop, iOS e Android.
- `scripts/render_design_bible.py` — Gera `DESIGN-BIBLE.html` e `DESIGN-BIBLE.pdf` com pranchas visuais reais a partir de `tokens.css`.
- `scripts/design_intel.py` — Pesquisa offline BM25 sobre domínios, tipografia, padrões e OSS.
- `scripts/discover_oss_components.py` — Caça componentes OSS por necessidade/stack/plataforma (`--online` GitHub/npm).
- `scripts/generate_tokens.py` — Compila `tokens.json` em CSS, Tailwind v4, TS, Swift, Kotlin e Dart.
- `scripts/audit_contrast.py` — Validador WCAG 2.1 + APCA em Light & Dark.
- `scripts/lint_design_aura.py` — Linter determinístico dos 10 Blocos + anti-stub/anti-serif/anti-dev-leak.
- `scripts/build_figma_canvas.py` — Gerador da vitrine `fluxo.html` (Hub-and-Spoke) + `preview.html` + `index.html`.
- `scripts/capture_and_audit.mjs` — Captura multi-viewport e auditoria DOM real (incluindo vitrine, `DA-DEAD-SPACE`, `DA-STUB-SCREEN`, `DA-FIXED-OVERLAP`, `DA-RAW-LINK-LIST`, `DA-SERIF-OPERATE`, `DA-SURFACE-FLAT`, `DA-ASSET-404`).
