# Orquestração de Subagentes (`v2.0` · Sem Teto de Subagentes · Fast-Audit por Entrega)

O Orquestrador é o **Diretor de Design e Arquiteto-Chefe**. Subagentes são **especialistas de execução paralela** que constroem slices enxutos sobre uma fundação visual já validada (**Telas-Mãe**).

**Regra de ouro (`v2.0`):** **não existe teto artificial de 8 subagentes.** O que garante acabamento de estúdio é o **limite rígido de telas por subagente (`1–3` telas)** e a **Auditoria Rápida Imediata pelo Orquestrador (Fast-Audit)** assim que cada subagente entrega seu resultado.

---

## O Padrão em 4 Etapas com Fast-Audit Contínuo

```text
ONDA 0 (Orquestrador — Bíblia Visual + Contrato)
  ├─ Fase 1: lê repo/docs e faz entrevista curta obrigatória nos pontos críticos (incl. modelos)
  ├─ Grava Contrato de plataforma no topo da DESIGN-BIBLE.md
  ├─ Roda design_intel.py + discover_oss_components.py (bibliotecas reais: ECharts, Lucide/Phosphor, SortableJS, etc.)
  ├─ Compila tokens.json → tokens.css e trava Portão 0 (audit_contrast.py --strict)
  ├─ Fecha screen-manifest.json consolidado (alvo 12–24 telas profundas; acima de 24 exige justificativa)
  ├─ Gera DESIGN-BIBLE.html/.pdf VISUAL com --tokens tokens.css (pranchas Light/Dark renderizadas!)
  └─ [PORTÃO 1] PARA e aguarda aprovação explícita da Bíblia Visual

ONDA 0.5 (Orquestrador — Portão das Telas-Mãe / Golden Screens)
  ├─ Constrói Design System completo: tokens.css + shell.css + shell.js + libs OSS vendored/carregadas (zero 404)
  ├─ Constrói 1 Tela-Mãe Desktop (a mais rica/densa do sistema) + 1 Tela-Mãe Mobile (se houver mobile)
  ├─ Audita com lint_design_aura.py + capture_and_audit.mjs e inspeciona PNGs (Dark & Light)
  └─ [PORTÃO 2] Valida as Telas-Mãe com o usuário antes de escalar para os subagentes
     (pule a pausa apenas se o usuário autorizou construir tudo direto sem parar nas Telas-Mãe)

ONDA 1 + FAST-AUDIT LOOP (Subagentes — 1 a 3 telas cada · SEM teto de 8)
  ├─ Cada subagente nasce com o modelo gravado no Contrato de plataforma
  ├─ Orquestrador dispara em lotes paralelos (ex.: 4–6 simultâneos) até cobrir 100% das telas num único processo
  ├─ Cada subagente recebe Briefing Rico + caminho das Telas-Mãe como régua visual + permissão para CSS local via var(--token)
  └─ [FAST-AUDIT IMEDIATO POR SUBAGENTE — OBRIGATÓRIO]:
     Assim que CADA subagente entrega suas 1–3 telas, o Orquestrador IMEDIATAMENTE:
       1. Roda lint_design_aura.py <arquivos-do-slice> --strict
       2. Roda capture_and_audit.mjs <arquivos-do-slice> --out <audit>/slices/<id> --themes dark,light --strict
       3. Abre os PNGs e compara diretamente com a Tela-Mãe aprovada (substância, vazio, cor, hierarquia)
       4. Se reprovar (técnico OU estético): corrige na hora ou redespacha feedback cirúrgico ao subagente ANTES de integrar!

ONDA 2 (Consolidação + Vitrine Figma + Auditoria Global + Entrega Acessível)
  ├─ Orquestrador verifica 100% de cobertura no disco e zero links quebrados
  ├─ Roda build_figma_canvas.py --verify-files (fluxo.html Hub-and-Spoke, preview.html, index.html)
  ├─ Roda os 3 portões globais (audit_contrast.py, lint_design_aura.py, capture_and_audit.mjs --manifest incl. vitrine)
  └─ Inspeciona PNGs finais (inclusive fluxo.html) e entrega com preview aberto ou link acessível HTTP 200
```

---

## Tabela de Dimensionamento por Profundidade (Qualidade > Compressão)

| Tipo de Tela no Slice | Telas por Subagente | Por quê |
|---|---|---|
| **Cockpit ultra-denso (3 zonas, gráfico ECharts, fila + documento + inspector, chat + IA)** | **`1` tela dedicada** | Exige foco total em widgets reais, massa de dados completa (`>= 6` registros) e micro-interações. |
| **Telas operacionais padrão ou Mobile ricas (tabelas com filtros, funil, detalhes, bottom sheets)** | **`2` a `3` telas** | Equilíbrio ótimo de contexto para manter 100% de paridade visual com a Tela-Mãe sem virar stub. |
| **Telas auxiliares simples (login/acesso, perfil, preferências)** | **máx. `3` telas** | Evita desperdício sem nunca empilhar 6–7 páginas no mesmo subagente. |

**Sem teto de 8 subagentes:** um sistema com 18 telas ricas pode usar **7 a 10 subagentes** (`1–3` telas cada), executados em lotes paralelos (ex.: Lote A com 5 subagentes → Fast-Audit de cada entrega → Lote B com os restantes → Fast-Audit), realizando **100% das telas num processo só** com acabamento impecável.

**Disciplina contra fragmentação:** não invente 40 arquivos HTML rasos de 2 KB quando **14 a 22 telas profundas** (usando abas, filtros, drawers e bottom sheets reais) resolvem o produto com muito mais qualidade. Acima de 24 telas, justifique explicitamente na Bíblia e peça aprovação do usuário.

---

## Protocolo Obrigatório de Fast-Audit pelo Orquestrador (Por Entrega de Subagente)

Nenhum slice de subagente é considerado "pronto" apenas porque o subagente disse que terminou. Assim que o subagente retorna:

1. **Verificação Automática Rápida (~15–30s):**
   ```bash
   python3 <skill_dir>/scripts/lint_design_aura.py <arquivos-do-slice> --strict
   node <skill_dir>/scripts/capture_and_audit.mjs <arquivos-do-slice> --out <dir_audit>/slices/<slice_id> --viewports <desktop|mobile> --themes dark,light --strict
   ```
2. **Inspeção Visual Comparativa contra a Tela-Mãe (~15s):**
   Abra os screenshots gerados do slice e cheque 6 perguntas objetivas:
   - **Paridade visual (sem clonagem estrutural):** parece feito pela mesma diretoria de design da Tela-Mãe (mesmos tokens, componentes e acabamento), **mas com layout interno e fluxo próprios da tarefa daquela tela** (não forçou o miolo da Tela-Mãe numa tela de natureza diferente, como Configurações, Funil ou Perfil)?
   - **Zero vazio morto (`DA-DEAD-SPACE`):** a viewport desktop está equilibrada (sem buracos vazios de 60–75% nem inspector de 1 linha)?
   - **Substância real (`DA-STUB-SCREEN`):** há `>= 5` registros realistas, widgets/gráficos combinados, badges semânticos e ícones coerentes?
   - **Zero regressões proibidas:** sem links `<a>` azuis sublinhados crus, sem serifa editorial em `Operate`, sem texto cortado sob barra fixa mobile, sem `404` em scripts/CSS?
   - **Interatividade real:** filtros, abas, seleção de linha que atualiza o inspector, modal/sheet e toast funcionam de verdade?
   - **Aderência ao arquétipo do módulo:** a organização da tela segue a lógica real do trabalho (ex.: Kanban em funil, Master-Detail em catálogo, Formulário agrupado em configurações, Cockpit 3 zonas em triagem)?
3. **Decisão imediata:**
   - **Passou nos 6 pontos + 0 BLOCK/HIGH:** slice aceito e integrado.
   - **Ajuste pequeno (1–2 CSS/copy):** o próprio Orquestrador corrige na hora e revalida.
   - **Slice raso, feio ou fora do padrão:** o Orquestrador **reprova e redespacha** com lista cirúrgica do que faltou (citando a Tela-Mãe e os achados exatos) antes de seguir para a vitrine!

---

## Isolamento de Contexto & Briefing Rico

### O que SEMPRE passar para cada subagente construtor:
1. **Caminho exato das Telas-Mãe aprovadas** (ex.: `design/telas/desktop-pagar.html` e `design/telas/mobile-hoje.html`) deixando explícita a fronteira: **herdar 100% da linguagem visual, shell, componentes `Z2` e padrão de acabamento — mas NUNCA copiar o layout interno ou fluxo de trabalho da Tela-Mãe** quando o módulo tem outra natureza (ex.: Funil Kanban, Configurações/Perfil em seções de formulário, Editais Master-Detail, Atendimento Inbox).
2. **Caminho exato de saída** das `1–3` telas do slice + recorte do `screen-manifest.json` (ID, título, plataforma, viewport, **arquétipo estrutural próprio de cada tela**, links de entrada e links de saída reais).
3. **Referência direta aos artefatos travados:** `DESIGN-BIBLE.md`, `tokens.css`, `shell.css`, `shell.js` e os caminhos exatos das bibliotecas OSS da seção 8 (ex.: `vendor/echarts.min.js`, `vendor/sortable.min.js`).
4. **Anatomia funcional e widgets obrigatórios de cada tela do slice:** o que vai em cada zona (fila, documento, gráfico/telemetria, inspector, bottom sheet), massa mínima realista (`>= 5` registros) e interações que precisam responder ao clique.
5. **Dados Fictícios Compartilhados:** mesmos números, nomes, datas e alertas usados nas demais telas.
6. **Liberdade controlada de CSS local:** o subagente **não edita** `tokens.css` nem `shell.css` compartilhados, mas **PODE e DEVE** adicionar `<style>` ou folha CSS local da sua tela usando **exclusivamente** `var(--token)` do `tokens.css` para construir layouts ricos (3 zonas, grids de KPIs, timelines, cards `Z2`, painéis de gráfico).

### O que NUNCA colocar no briefing de um subagente:
- **NUNCA** escreva `"sem classe card"`, `"proibido usar cards"` ou `"faça só 2 linhas porque o resto não está na amostra"`.
- **NUNCA** proíba estilos locais necessários para a riqueza da tela (a camisa de força de "só use classes prontas de um shell.css mínimo" produz páginas peladas).
- **NUNCA** deixe dois subagentes editarem o mesmo arquivo compartilhado (`tokens.css`, `shell.css`, `shell.js`, `index.html`, `fluxo.html`).
- **NUNCA** entregue 5–7 telas num único subagente.

---

## Template Obrigatório de Briefing de Subagente (`v2.0`)

```markdown
### Tarefa: Construir Slice [NOME_DO_MODULO] ([1 a 3] tela(s)) — Projeto [NOME_DO_PROJETO]

Você é um Engenheiro de UI Sênior da Design Aura. Sua entrega deve igualar ou superar o acabamento visual e funcional das **Telas-Mãe aprovadas**, seguindo 100% a Bíblia de Design e os 10 Blocos de Leis Inegociáveis.

1. **Fundação & Régua Visual (LEITURA OBRIGATÓRIA antes de codar):**
   - Tela(s)-Mãe aprovada(s): `<caminho/tela-mae-desktop.html>` / `<caminho/tela-mae-mobile.html>`
     - **O QUE HERDAR DA TELA-MÃE:** tokens (`Z0–Z4`, paleta, contraste, Dark/Light), tipografia, espaçamento `4/8px`, shell externo, gramática de botões/badges/cards/inputs/toasts e **nível de acabamento**.
     - **O QUE NÃO COPIAR DA TELA-MÃE:** o layout interno, o número de colunas/zonas ou o fluxo de trabalho! Construa a organização interna que faz sentido natural para a tarefa deste módulo (ex.: Kanban para funil, Master-Detail para lista/catálogo, Formulário em seções agrupadas para configurações/perfil, Inbox+Chat para atendimento, Cockpit 3 zonas para triagem).
   - `DESIGN-BIBLE.md` (Contrato de plataforma, planos Z0–Z4, tipografia, seção 8 de libs OSS e seção 8.1)
   - `tokens.css`, `shell.css` e `shell.js` (não edite estes arquivos compartilhados; crie estilos específicos da sua tela em `<style>` local usando exclusivamente `var(--token)`).

2. **Telas do Seu Slice (1–3 telas, TODAS ricas e com arquitetura própria):**
   - `[id-1]` -> `<caminho/arquivo-1>` (Viewport: `1440x900` | Arquétipo próprio desta tela: `<ex: Kanban 5 colunas + drawer lateral OU Configurações em 2 colunas de seções agrupadas>` | Links de saída: `<arquivos-destino>`)
   - `[id-2]` -> `<caminho/arquivo-2>` (...)

3. **Widgets OSS & Interatividade Obrigatória:**
   - Bibliotecas disponíveis no projeto: `<ex.: vendor/echarts.min.js, ícones SVG consistentes, bottom sheet>`
   - Massa realista mínima: `>= 5` registros concretos em tabelas/listas (proibido stub de 1–2 linhas ou texto de desculpa).
   - Interações reais: filtros funcionais, seleção de item atualizando o inspector completo (nunca 1 linha só), busca/tabs, modal/drawer/sheet com fechar por `Esc` e toast com Desfazer.

4. **Dados Fictícios Compartilhados (USE EXATAMENTE ESTES VALORES):**
   - Empresa/Sistema: <...>
   - Perfis/Usuários: <...>
   - Métricas/Alertas integrados: <...>

5. **Os 10 Blocos & Regras Anti-Regressão (`v2.0`):**
   - Suporte completo a `data-theme="dark"` e `data-theme="light"` via variáveis de `tokens.css`.
   - Use superfícies elevadas `Z2` nítidas (proibido card-dentro-de-card, mas obrigatório ter hierarquia real de painéis/cards `Z2`).
   - Proibido vazio morto em desktop (`DA-DEAD-SPACE`), proibido links `<a>` azuis sublinhados crus em listas/menus (`DA-RAW-LINK-LIST`), proibido fonte serifada editorial em sistema `Operate` (`DA-SERIF-OPERATE`), proibido texto cortado por barra fixa mobile (`DA-FIXED-OVERLAP`).
   - `tabular-nums` + alinhamento à direita em números de tabela, `<label>` visível em inputs, `<textarea>` estilizado, `:focus-visible`, touch target `>= 44px` em mobile, zero `transition-all`, zero emojis clichês.

6. **Validação Local Obrigatória antes de Responder:**
   - Rode `python3 <skill_dir>/scripts/lint_design_aura.py <seus-arquivos> --strict` e corrija qualquer falha `BLOCK`/`HIGH`.
   - Responda listando: arquivos criados, widgets/interações implementadas, links conectados e resultado do linter. (O Orquestrador rodará Fast-Audit visual em Chromium imediatamente após sua entrega.)
```

---

## Reconciliação Final (Onda 2)

Após todos os slices passarem no Fast-Audit individual:
1. Confirme **100% de cobertura** no disco contra `screen-manifest.json` e zero links quebrados.
2. Gere a vitrine com `build_figma_canvas.py screen-manifest.json --tokens tokens.css --out <dir_telas> --verify-files`.
3. Execute os 3 portões globais (`audit_contrast.py`, `lint_design_aura.py`, `capture_and_audit.mjs --manifest` que agora audita também `fluxo.html`, `preview.html` e `index.html`).
4. Inspecione visualmente os PNGs finais e entregue links acessíveis validados (`HTTP 200`).
