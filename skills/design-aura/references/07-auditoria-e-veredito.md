# Auditoria, QA Visual Real & Formato de Veredito

Nenhuma entrega da **Design Aura** é considerada pronta por "leitura de código". Aprovação exige **portões automáticos verdes + evidência renderizada real** nos viewports alvo (Desktop e Mobile, Light e Dark).

---

## Modos de Auditoria

| Modo | Quando usar | Cobertura | Limite de Achados no Resumo |
|---|---|---|---|
| **`fast-slice`** (novo `v2.0`) | **Obrigatório imediatamente após CADA entrega de subagente na Onda 1** | `lint_design_aura.py` + `capture_and_audit.mjs` nas 1–3 telas do slice + comparação visual direta dos PNGs contra a **Tela-Mãe aprovada** | Todos os `BLOCK`/`HIGH` + desvios estéticos (corrige/redespacha NA HORA) |
| **`quick`** | Revisão rápida de um componente ou ajuste focal | Fluxo principal e estados de maior tráfego; reporta `BLOCK`, `HIGH` e `MEDIUM` | Até `5` principais (correções mecânicas vão todas na tabela) |
| **`full`** (padrão Onda 2) | Entrega completa pós-construção de todos os slices | Todos os **10 Blocos** + **Piso de Substância `v2.0`** + Vitrine (`fluxo.html`, `preview.html`, `index.html`) em `desktop` (`1440×900`), `tablet` (`768×1024`) e `mobile` (`390×844`) em **Dark e Light** | Até `15` achados estruturais agrupados |

---

## Pipeline de Verificação Obrigatório (Onda 2)

Use os passos aplicáveis ao escopo. Em ajuste localizado, cubra a tela, o estado e os contratos afetados.

### Passo 1 — Contraste Matemático, Paridade Semântica & Profundidade (`audit_contrast.py` v2.4.0)
```bash
python3 <skill_dir>/scripts/audit_contrast.py tokens.css --strict
```
Valida WCAG AA (`>= 4.5:1` / `>= 3.0:1`), APCA (`|Lc| >= 60` / `>= 45`) incluindo superfícies semânticas (`--{role}-text` sobre `--{role}-surface`), **Paridade Semântica Light/Dark (`DA-SEMANTIC-HUE-PARITY` — bloqueia erro rosa pastel no Dark!)**, **Anti-Monobloco Cinza (`DA-DARK-FLAT-MONOLITH`)** e **Light Mode Nítido (`DA-LIGHT-WASHED-OUT`: `border-subtle >= 1.85:1`, `Z1/Z2 >= 1.18:1`)**.

### Passo 2 — Linter dos 10 Blocos + Anti-Jargão & Anti-Eco (`lint_design_aura.py` v2.4.0)
```bash
python3 <skill_dir>/scripts/lint_design_aura.py <caminho-do-projeto> --strict
```
Varre HTML/CSS/JS/TS/TSX/Vue/Svelte/Swift/Kotlin/Dart contra os 10 Blocos + `DA-TECH-JARGON-UI` (bloqueia jargão técnico vazado ao trabalhador) e `DA-BADGE-ECHO` (selos-eco repetidos).

### Passo 3 — Renderização Real + Auditoria DOM, SPA & Pós-Clique (`capture_and_audit.mjs` v2.4.0 · Paralelo)
```bash
node <skill_dir>/scripts/capture_and_audit.mjs --manifest screen-manifest.json [--base-url http://127.0.0.1:4188] --out <dir_audit> --viewports desktop,mobile --themes dark,light --concurrency 4 --smoke-interact --strict
```
Suporta **HTML estático E rotas SPA React/Vite/Next (`"route"` + `--base-url`)**, audita automaticamente `entrega.html` (whitelist `.da-hub`), `fluxo.html`, `preview.html` e `index.html`, estende `DA-B3-01` a emblemas/monogramas (`div`/`span`), e checa em runtime:
- Overflow horizontal (`DA-DOM-OVERFLOW`), imagens quebradas/sem `alt`, alvos mobile `< 44×44px`, corpo `< 12px`, inputs sem label (`DA-B9-01`), contraste real WCAG AA inclusive em emblemas (`DA-B3-01`), raios beliscados (`DA-B7-01`), scroll aninhado e números desalinhados (`DA-B8-03`)
- Erros de console/exceções JS (`DA-JS-ERROR`) e assets locais HTTP 404 (`DA-ASSET-404`)
- **Piso de Craft & Anti-Poluição (`v2.4.0`):** `DA-BADGE-ECHO`, `DA-MOBILE-HERO-BLOAT` (hero/alertas mobile `<= 38%`), `DA-HEADER-STACK-BLOAT` (máx. 2 barras topo desktop `<= 210px`), `DA-TAB-OVERFLOW` (máx. 6 abas irmãs), `DA-DEAD-SPACE`, `DA-CARD-INTERNAL-VOID`, `DA-STUB-SCREEN`, `DA-RAW-LINK-LIST`, `DA-FIXED-OVERLAP`, `DA-CLIPPED-CONTENT`, `DA-MOBILE-FLEX-CLIP`, `DA-NAV-TRUNCATION`, `DA-HEADER-HSCROLL`, `DA-SERIF-OPERATE`, `DA-SURFACE-FLAT` e **smoke pós-clique (`--smoke-interact` / `clickSelector`)** validando o estado aberto do Resize In-Place!
- **Miniaturas na Galeria (`index.html`):** re-execute `build_figma_canvas.py screen-manifest.json --tokens tokens.css --thumbs <dir_audit> --out <dir_telas> --verify-files`.

### Passo 3.5 — QA Interativo E2E por Subagentes Testers (Fase 4.5 · Onda 3 · `v2.4.0`)
```bash
node <skill_dir>/scripts/run_workflow_probe.mjs --scenario <qa-jornada.json> --out <dir_qa> [--base-url http://127.0.0.1:4188] --strict
```
Subagentes Testers Read-Only percorrem cada jornada real clicando nos controles, testando fluxos positivos/negativos/estados vazios e alternância Dark/Light. O Orquestrador tria as falhas reais, gera o Plano de Correção, lança subagentes corretivos e confirma via re-teste direcionado (máx. 2 ciclos).

### Cobertura declarada e estado pós-interação

- Use `screens[].viewports` para declarar dimensões por tela, por exemplo `["desktop", "1920x1080"]` ou `["mobile", "mobile-360x800"]`. Use `project.vitrineViewports` quando a vitrine também precisar de cobertura mobile. O manifesto prevalece sobre o padrão da linha de comando para essas entradas. Entradas antigas mantêm os padrões.
- Use `clickSelector` com `afterClickSelector` para verificar o estado aberto no smoke. Quando for necessário preparar dados ou navegar antes do clique, use uma jornada E2E para esse estado. Consulte dimensões e estados no JSON. Uma rota ou estado declarado sem evidência aparece como lacuna.
- No probe, `viewport` aceita os mesmos tamanhos. Use `{"action":"assertReachable","selector":"#aprovar"}` com um overlay ativo para checar o controle na área visível. Para um gráfico em base conhecida, use `{"action":"assertText","selector":"[data-day-total]","equals":"12"}` depois de trocar o dia. Um clique isolado demonstra a ação; a assertiva demonstra o resultado.
- Marque o contêiner amplo com `data-da-workspace` quando o vazio externo do conteúdo dentro dele importar. Em formulários e leitura, preserve a medida do conteúdo. Confirme em captura se o vazio indicado prejudica o uso.

### Passo 4 — Inspeção Visual Comparativa contra a Tela-Mãe (Batch Review)
Abra e analise os PNGs gerados em `<dir_audit>` e `<dir_qa>` (incluindo `entrega-desktop-dark.png`, `fluxo-desktop-dark.png` e os PNGs pós-clique `-interact.png`) — **zero erros automáticos NÃO basta se a tela estiver feia**:
1. **Paridade Visual sem Clonagem Estrutural & Zero Monobloco Cinza/Branco:** a cor da marca vive nos cabeçalhos, seleções e profundidade em Dark & Light, e a paridade semântica está impecável (vermelho = falha, verde = sucesso, âmbar = alerta, zero rosa)?
2. **Fluxo Humano & Resize In-Place:** dá para usar sem "estudar a tela"? A fila limpa abre conferência focada sem duplicar dados nem empilhar barras?
3. **Alinhamento, Badges & Mobile:** zero selo-eco, zero jargão técnico, hero mobile compacto e zero corte sob tab bar?
4. **Vitrine Unificada (`entrega.html`):** link único operando com `Mapa Figma · App ao Vivo · Preview · Galeria · Bíblia + PDF + Tema` sem erros JS?

Compare o antes e o depois no mesmo tema, largura, dados e estado quando houver uma base anterior válida. Abra capturas da área usada e, quando a questão envolver ritmo ou vazios abaixo da dobra, também da página ou região rolável inteira. Para dados críticos pequenos ou sobre fundos compostos, inspecione a leitura no tamanho real. Classifique achados pela evidência disponível (código, comportamento renderizado ou revisão visual) e agrupe sintomas pela causa. Trate adornos repetidos pela função, como um separador visual que torna uma fila escaneável. [Impeccable](https://impeccable.style/slop/) · [Auditoria de Meng To](https://github.com/MengTo/skills/blob/main/agent-skills/ui/audit-ai-design-slop/SKILL.md)

### Passo 5 — Regra de Entrega Unificada em 1 Porta / 1 Link (`serve_entrega.mjs`)
Suba o servidor unificado de porta única (`0.0.0.0:4188`) combinando `/design/*` + SPA `dist/*`:
```bash
node <skill_dir>/scripts/serve_entrega.mjs --design-dir <dir_design> [--app-dir <dir_dist>] --port 4188
```
Se estiver em ambiente remoto/cloud onde o navegador do usuário não alcança `localhost`, abra no preview integrado do ambiente ou forneça URL acessível verificada com `HTTP 200` (via túnel HTTPS quando necessário), sempre em **1 único link** apontando para `entrega.html`.

Informe quais artefatos a URL oferece e se a hospedagem depende da sessão. Depois de publicar, confirme que a rota renderiza a tela esperada e que cada download responde com seu conteúdo real. O fallback de SPA pode responder com HTML no lugar de um arquivo.

*(Opcional: se o usuário tiver conectado o MCP Uizze com token válido, `find_ui_references` e `get_ui_flow` podem servir para comparar soluções de referência em telas problemáticas — sempre distinguindo claramente o que foi inspecionado do que foi inferido.)*

---

## Formato Obrigatório do Relatório de Auditoria

### 1. Escopo e Cobertura (`Scope and Coverage`)
Informe o modo (`quick`/`full`), stack, viewports e temas efetivamente testados. Nunca implique que uma tela ou tema não testado passou:

| Categoria | Evidência Inspecionada | Resultado |
|---|---|---|
| Contraste & Cor (Bloco 3) | `audit_contrast.py` em `tokens.css` + DOM Dark/Light | `Clear` / `N achados` / `Not reviewed` |
| Anti-AI-Slop & Copy (Blocos 1, 5) | `lint_design_aura.py` em `N` arquivos | `...` |
| Hierarquia & Layout (Blocos 2, 8) | Screenshots `1440x900` e `390x844` | `...` |
| Micro-Craft & Motion (Blocos 4, 6, 7) | CSS/tokens + linter + inspeção visual | `...` |
| Interação & Ergonomia (Blocos 9, 10) | DOM runtime audit + checks mobile/desktop | `...` |

### 2. Achados (`Findings`)
Agrupe por Bloco/Princípio. **Obrigatório usar exatamente as 5 colunas abaixo** (consolidando ocorrências idênticas na mesma linha):

| Severity | Location | Before | After | Why |
|---|---|---|---|---|
| `BLOCK` | `src/Acesso.html:48` | `<input placeholder="E-mail">` | `<label for="email">E-mail</label><input id="email" ...>` | Viola `DA-B9-01`: placeholder não substitui label visível |

Severidades válidas:
- **`BLOCK`**: viola qualquer um dos **10 Blocos de Leis Inegociáveis**, gera erro JS, quebra layout/overflow ou falha WCAG AA. **Impede aprovação.**
- **`HIGH`**: prejudica seriamente usabilidade, legibilidade ou ergonomia nativa.
- **`MEDIUM`**: inconsistência notável de espaçamento, alinhamento ou estado secundário.
- **`LOW`**: polimento fino opcional (aparece apenas no modo `full`).

### 3. Considerado mas Rejeitado (`Considered but Rejected`)
Liste `1–3` (quick) ou `2–5` (full) candidatos reais avaliados durante a auditoria e mantidos intactos intencionalmente:

| Location | Candidate | Rejected because |
|---|---|---|
| `desktop-caixa.html:112` | Aumentar sombra dos cards | A elevação atual segue `Z2` da `DESIGN-BIBLE.md`; alterar isoladamente quebra a consistência dos 5 planos |

### 4. Verificação & Veredito (`Verification and Verdict`)
1. **Registro de verificação.** Identifique o build testado, as telas, dimensões, temas e estados que foram abertos, os comandos, os artefatos e o resultado visual. Confira a aprovação ou a autorização para seguir direto no piloto quando pertinente. Reconcilie Bíblia, shell, manifesto e interface. Use `render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css --check-sync --shell SHELL-CONTRACT.md` para verificar tabelas e declarações explícitas no shell, como `border-subtle` Light `#86A2C7`. Acrescente `--compare-css caminho/tokens.css` para cada cópia compilada que deve ser idêntica. Confira na revisão as rotas atuais, as escolhas em prosa, o histórico e o estado dos portões.
2. **Veredito:** `Requer correção` quando a evidência comprovar um problema acionável dentro do escopo. `Pendente de verificação` quando faltar evidência exigida. `Aprovado` quando o QA funcional e a inspeção visual aplicáveis estiverem concluídos no build final, com o contrato coerente.
