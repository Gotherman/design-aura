# Auditoria, QA Visual Real & Formato de Veredito

Nenhuma entrega da **Design Aura** é considerada pronta por "leitura de código". Aprovação exige **portões automáticos verdes + evidência renderizada real** nos viewports alvo (Desktop e Mobile, Light e Dark).

---

## Modos de Auditoria

| Modo | Quando usar | Cobertura | Limite de Achados no Resumo |
|---|---|---|---|
| **`quick`** | Revisão rápida de um componente ou ajuste focal | Fluxo principal e estados de maior tráfego; reporta `BLOCK`, `HIGH` e `MEDIUM` | Até `5` principais (correções mecânicas vão todas na tabela) |
| **`full`** (padrão Onda 2) | Entrega completa de sistema, app ou pós-construção dos subagentes | Todos os **10 Blocos** + **5 Categorias de Micro-Craft** em `desktop` (`1440×900`), `tablet` (`768×1024`) e `mobile` (`390×844`) em **Dark e Light** | Até `15` achados estruturais agrupados |

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

### Passo 3 — Renderização Real + Auditoria DOM (`capture_and_audit.mjs`)
```bash
node <skill_dir>/scripts/capture_and_audit.mjs <arquivos-ou-urls> --out <dir_audit> --viewports desktop,tablet,mobile --themes dark,light --strict
```
Abre Chromium headless real via CDP, captura PNGs de cada viewport × tema e inspeciona em runtime:
- Overflow horizontal (`scrollWidth > clientWidth`)
- Imagens quebradas ou sem `alt`
- Controles mobile `< 44×44px`
- Corpo de texto `< 14px`
- Inputs com placeholder sem label acessível
- Contraste real computado no navegador
- Erros de console e exceções JavaScript

*(Para apps nativos iOS/Android compilados: capture diretamente pelo Simulator via `device_screenshot` / `xcrun simctl io booted screenshot` em Dark Mode + Dynamic Type grande, ou Emulator Android com `uimode night yes` + `font_scale 1.3`. Nunca aprove app nativo apenas olhando simulação web.)*

### Passo 4 — Inspeção Visual das Imagens (Batch Review)
Abra e analise os PNGs gerados em `<dir_audit>` (sem fazer uma viagem separada por regra — analise todas as categorias de uma vez):
1. **Hierarquia & Anti-Cardite**: a ação principal salta aos olhos em 1 segundo? Há espaço morto? Há cardite/card-dentro-de-card?
2. **Alto Contraste Ótico**: os planos `Z0→Z4` separam claramente sem clarão branco no Light nem borrão escuro no Dark?
3. **Alinhamento & Densidade**: números à direita, sem quebra feia de texto, sem badges brigando?
4. **Fidelidade à Bíblia**: a assinatura visual do domínio aparece com coerência entre todas as telas?

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
