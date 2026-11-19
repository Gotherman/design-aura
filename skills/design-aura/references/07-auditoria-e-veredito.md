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

Execute nesta ordem exata e **nunca pule etapas**:

### Passo 1 — Contraste Matemático (`audit_contrast.py`)
```bash
python3 <skill_dir>/scripts/audit_contrast.py tokens.css --strict
```
Valida WCAG AA (`>= 4.5:1` / `>= 3.0:1`) e APCA (`|Lc| >= 60` / `>= 45`) em **Light e Dark**, detecta `#000000`/`#FFFFFF` crus e cinzas lavados.

### Passo 2 — Linter dos 10 Blocos (`lint_design_aura.py`)
```bash
python3 <skill_dir>/scripts/lint_design_aura.py <caminho-do-projeto> --strict
```
Varre todos os arquivos HTML/CSS/JS/TS/TSX/Vue/Svelte/Swift/Kotlin/Dart contra as regras determinísticas dos Blocos 1 a 10 (AI tells, copy clichê, `transition-all`, magic numbers, inputs sem label, falta de `tabular-nums`, foco removido, etc.).

### Passo 3 — Renderização Real + Auditoria DOM & Craft (`capture_and_audit.mjs` v2.0)
```bash
node <skill_dir>/scripts/capture_and_audit.mjs --manifest screen-manifest.json --out <dir_audit> --viewports desktop,mobile --themes dark,light --strict
```
Abre Chromium headless real via CDP, audita automaticamente as telas **e a vitrine (`fluxo.html`, `preview.html`, `index.html`)**, captura PNGs de cada viewport × tema e inspeciona em runtime:
- Overflow horizontal (`DA-DOM-OVERFLOW`), imagens quebradas/sem `alt`, alvos mobile `< 44×44px`, corpo `< 12px`, inputs sem label (`DA-B9-01`), contraste real WCAG AA (`DA-B3-01`), raios beliscados (`DA-B7-01`), scroll aninhado e números desalinhados (`DA-B8-03`)
- Erros de console/exceções JS com stack completo (`DA-JS-ERROR`) e assets/scripts locais com HTTP 404 (`DA-ASSET-404`)
- **Piso de Craft & Composição (`v2.0`):**
  - `DA-DEAD-SPACE`: detecta vazio morto em desktop (`1440×900`) e inspectors/painéis laterais quase vazios (ex.: apenas 1 linha de dado)
  - `DA-STUB-SCREEN`: bloqueia/alerta tabelas operacionais rasas (`1–2` linhas) e telas casca com `< 4` elementos úteis
  - `DA-RAW-LINK-LIST`: detecta links `<a>` azuis sublinhados crus em listas/tabelas/menus de app
  - `DA-FIXED-OVERLAP`: bloqueia conteúdo cortado ou escondido sob barra fixa inferior/superior mesmo no fim da rolagem
  - `DA-SERIF-OPERATE`: detecta tipografia serifada editorial indevida em telas operacionais `Operate`
  - `DA-SURFACE-FLAT`: detecta falta de separação visual entre canvas `Z1` e painéis/cards `Z2`

### Passo 4 — Inspeção Visual Comparativa contra a Tela-Mãe (Batch Review)
Abra e analise os PNGs gerados em `<dir_audit>` (incluindo `fluxo-desktop-dark.png`) — **zero erros automáticos NÃO basta se a tela estiver feia**:
1. **Paridade Visual sem Clonagem Estrutural & Zero Telas Casca**: cada tela usa a mesma linguagem visual e nível de acabamento da Tela-Mãe aprovada, **mas respeitando a organização interna natural do seu módulo** (ex.: Kanban em funil, formulário agrupado em configurações/perfil, inbox em atendimento — nunca cópia cega das zonas da Tela-Mãe), com dados completos, widgets OSS vivos e sem vazio morto?
2. **Alto Contraste Ótico & Vitalidade Cromática**: os planos `Z0→Z4` separam com nitidez sem clarão branco no Light nem borrão escuro no Dark? A cor da marca continua viva (sem virar marrom/bege apagado)?
3. **Alinhamento, Badges & Densidade**: números à direita, ícones consistentes, sem links azuis crus, sem badges brigando e sem texto cortado sob a barra mobile?
4. **Vitrine Estilo Figma**: `fluxo.html` está panorâmico (Hub-and-Spoke), legível (sem torre vertical a 25% de zoom e sem macarronada de setas) e com zero erro JS?

### Passo 5 — Regra de Entrega Acessível (Local ou Sandbox Remoto)
Antes de encerrar, verifique como o usuário vai abrir o protótipo:
- Se estiver em ambiente remoto/cloud onde o navegador do usuário não alcança `localhost`, **nunca** entregue apenas caminhos locais ou `http://localhost:...` — abra no preview integrado do ambiente (quando disponível) ou forneça uma URL acessível verificada com `HTTP 200` junto dos caminhos no repositório.

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
1. **Verification Receipt**: liste os comandos exatos executados após a última edição, quantos PNGs/viewports foram inspecionados e os resultados observados. Qualquer item não executado deve aparecer explicitamente como **Not verified**.
2. **Verdict**:
   - **`Block`**: se restar qualquer achado `BLOCK` ou `HIGH`, ou falha de renderização.
   - **`Needs changes`**: se restarem apenas `MEDIUM` ou `LOW` acionáveis.
   - **`Approve`**: apenas quando `0` achados `BLOCK`/`HIGH` permanecerem e todos os portões aplicáveis tiverem passado após a última edição.
