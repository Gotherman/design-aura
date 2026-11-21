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

ONDA 0.5 (Orquestrador — Portão das Telas-Mãe / Golden Screens + SHELL-CONTRACT.md)
  ├─ Constrói Design System completo: tokens.css (65/20/10/5 + --chart-1..6) + shell.css (5 camadas de profundidade + sidebar minimizável + .card-brand-hero + .icon-emblem + .chip-sla) + shell.js + libs OSS vendored (zero 404)
  ├─ Gera SHELL-CONTRACT.md (~100 linhas): esqueleto HTML copiável do <head>/sidebar/topbar/mobile-frame + mapa de classes CSS de shell.css + funções de shell.js (evita que cada subagente perca o turno lendo 4.000+ linhas!)
  ├─ Constrói 1 Tela-Mãe Desktop (Lista Limpa → Detalhe Focado ou painel principal + gráfico de estúdio) + 1 Tela-Mãe Mobile (se houver mobile)
  ├─ Audita com lint_design_aura.py + capture_and_audit.mjs e inspeciona PNGs (Dark & Light)
  └─ [PORTÃO 2] Valida as Telas-Mãe com o usuário (se houver ajuste em tokens/cores, re-roda render_design_bible.py --tokens para manter a Bíblia 100% sincronizada antes da Onda 1!)

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

## Template Obrigatório de Briefing de Subagente (`v2.2.0` · Turno Único Turbo)

> **Por que `SHELL-CONTRACT.md` + Escrita Incremental (`v2.2.0`)?**
> Quando cada subagente era obrigado a ler integralmente `DESIGN-BIBLE.md` + `tokens.css` + `shell.css` (`1.500` linhas) + `shell.js` (`450` linhas) + `Tela-Mãe` (`1.700` linhas) = **`4.126` linhas**, 30% dos subagentes estouravam o turno planejando e encerravam sem gravar nenhum HTML; outros gastavam 30+ chamadas tentando improvisar Puppeteer/Playwright. Com o `SHELL-CONTRACT.md` (`~100 linhas`) + a Trava de Escrita Incremental + comando pronto de `capture_and_audit.mjs`, cada subagente conclui seu slice em **1 único turno limpo** com qualidade máxima!

```markdown
### Tarefa: Construir Slice [NOME_DO_MODULO] ([1 a 3] tela(s)) — Projeto [NOME_DO_PROJETO]

Você é um Engenheiro de UI Sênior da Design Aura (`v2.2.0`). Sua entrega deve igualar ou superar o acabamento visual das **Telas-Mãe aprovadas**, seguindo 100% os tokens `65/20/10/5`, a profundidade tátil em 5 camadas e os 10 Blocos.

1. **Leitura Rápida & Direta (MÁXIMO 2 leituras antes de gravar o 1º HTML!):**
   - Leia `<caminho/SHELL-CONTRACT.md>` (`~100 linhas` — já contém `<head>`, esqueleto HTML do shell, sidebar minimizável, classes `.card-brand-hero`, `.panel-z2`, `.well-z0`, `.icon-emblem`, `.chip-sla`, `.chip-status`, `.chip-kv`, `.num`/`.mono` e helpers de `shell.js`).
   - Consulte a Tela-Mãe (`<caminho/tela-mae.html>`) apenas se precisar verificar algum trecho pontual — **NÃO** leia `4.000` linhas em sequência antes de começar a codar!
   - **Fronteira Anti-Clone Estrutural:** herde 100% dos tokens, shell e acabamento, mas construa a arquitetura interna própria de cada tela do slice (ex.: `Lista Limpa → Detalhe Focado` para filas/tabelas, `Combo Chart HUD` para caixa, `Waterfall com conectores` para DRE, `Kanban` para funil, `Inbox 2 colunas + Drawer` para atendimento).

2. **Telas do Seu Slice (1–3 telas, TODAS ricas e com arquitetura própria):**
   - `[id-1]` -> `<caminho/arquivo-1>` (Viewport: `1440x900` | Arquétipo próprio: `<...>` | Widgets OSS & Receitas: `<ex.: Combo Cashflow HUD, BarList, .icon-emblem Duotone, .chip-sla anel SVG>` | Links de saída: `<...>`)
   - `[id-2]` -> `<caminho/arquivo-2>` (...)

3. **Padrão Visual Obrigatório `v2.2.0` (Anti-Slop + Craft):**
   - **Presença da Marca `65/20/10/5`:** use `.card-brand-hero` no card-rei da tela, paleta categórica `--chart-1..6` em gráficos/rankings (nunca 4 barras do mesmo azul) e semânticas puras para risco.
   - **Zero Ícones/Badges Genéricos:** use **`.icon-emblem` com spotlight + SVG Duotone/1.75px específico do domínio** (ou monograma `.bank-emblem` para bancos), **`.chip-sla` com anel SVG circular** para tempos/janelas, **`.chip-status` com halo + ícone vetorial** para estados (ex.: Transbordo) e **`.chip-kv`** para pares Chave|Valor. PROIBIDO repetir `ph-bank` ou `ph-warning-circle` como muleta (`DA-ICON-GENERIC-REPEAT`).
   - **Gráficos de Estúdio:** nunca trave `yAxis: { min: 0 }` em série de saldo com baixa variação (`DA-FLAT-CHART-AXIS`); use escala Y dinâmica ou Combo Barras+Curva + cabeçalho HUD vivo no crosshair + pinos de anotação.
   - **Bento Grid & Tabelas:** proibido buraco interno `> 95px` em cards (`DA-CARD-INTERNAL-VOID`), proibido duplicar a sidebar na topbar do Portal, massa mínima `>= 5` registros reais, números à direita com `.num` (`Geist`/`Inter` tabular-nums) e `.mono` apenas em códigos técnicos.
   - **CSS local liberado:** não edite `tokens.css`, `shell.css` nem `shell.js`; coloque estilos específicos da tela em `<style>` local usando exclusivamente `var(--token)`.

4. **Dados Fictícios Compartilhados (USE EXATAMENTE ESTES VALORES):**
   - Empresa/Sistema: <...> · Perfis: <...> · Métricas/Registros: <...>

5. **REGRA DE ESCRITA INCREMENTAL EM TURNO ÚNICO (OBRIGATÓRIA):**
   - **PROIBIDO** encerrar seu turno apenas com um plano ou após ler arquivos!
   - **Ordem estrita:** (a) Leia `SHELL-CONTRACT.md`; (b) Grave imediatamente o **Arquivo 1 completo** no disco; (c) Grave imediatamente o **Arquivo 2 completo** no disco; (d) Rode o comando único de auditoria abaixo e corrija qualquer `BLOCK`/`HIGH`:
     ```bash
     python3 <skill_dir>/scripts/lint_design_aura.py <arquivo-1> <arquivo-2> --strict && \
     node <skill_dir>/scripts/capture_and_audit.mjs <arquivo-1> <arquivo-2> --out /tmp/audit-<slice> --viewports <desktop|mobile> --themes dark,light --strict
     ```
   - **PROIBIDO** procurar ou tentar instalar Puppeteer, Playwright ou Selenium — o `capture_and_audit.mjs` acima já funciona sem dependências externas!
   - Só responda depois que **todos** os arquivos do slice estiverem gravados no disco e auditados com `0 BLOCK · 0 HIGH`.
```

---

## Modo 3 Oficial — Polimento Cirúrgico sobre Telas Aprovadas (`v2.3.0`)

Quando o usuário já aprovou a arquitetura, fluxos e dados das telas existentes e pede apenas **polimento visual** (cores Dark/Light, profundidade de cards, ícones/emblemas, correções mobile ou vitrine):
1. **NÃO** refaça a Bíblia nem reescreva as telas do zero — preserve 100% do layout, rotas e textos aprovados.
2. **Etapa Piloto (Orquestrador):** atualize primeiro `tokens.json` → `tokens.css` → `shell.css` (incluindo escopo `.on-brand-dark` e `.mob-scroll > * { flex-shrink: 0; }`) + sincronize `DESIGN-BIBLE.md/.pdf` + aplique os novos padrões em **1 Tela-Piloto Desktop + 1 Tela-Piloto Mobile**, audite com `capture_and_audit.mjs --concurrency 4` e **pare para o OK rápido do usuário** nos PNGs piloto.
3. **Propagação Rápida sem Travamento:** como polimento cirúrgico mexe em classes/ícones pontuais (não constrói 800 linhas por tela do zero), prefira **lotes curtos controlados (`2–3` subagentes por vez ou edição em lotes diretos)** em vez de explodir 6 subagentes simultâneos que podem travar aguardando entrada.

## Protocolo Anti-Travamento de Subagentes & Transparência (`v2.3.0`)

- **Verificação de Arranque:** ao disparar subagentes paralelos, prefira ondas de **3 a 4 simultâneos** (em vez de 6–8 cegos de uma vez). Se o harness mostrar subagentes presos em `waiting_for_input` ou sem atividade no disco, encerre os presos e assuma em lotes controlados sem deixar o usuário esperando no escuro.
- **Auditoria Global Sempre Concluída no Turno:** `capture_and_audit.mjs` roda em **paralelo (`--concurrency 4`) com contextos isolados e log de progresso ao vivo** (~25–35s para 46 capturas). **NUNCA** largue a auditoria final em background devolvendo um turno "aguardando auditoria" sem `t3_background_wait` nem conclusão real — aguarde terminar, inspecione os PNGs e entregue o veredito completo com provas visuais.

---

## Reconciliação Final (Onda 2)

Após todos os slices passarem no Fast-Audit individual:
1. Confirme **100% de cobertura** no disco contra `screen-manifest.json` e zero links quebrados.
2. Execute os 3 portões globais em paralelo (`audit_contrast.py`, `lint_design_aura.py`, `capture_and_audit.mjs --manifest --concurrency 4 --strict`).
3. Gere/atualize a vitrine com miniaturas visuais reais da auditoria:
   `build_figma_canvas.py screen-manifest.json --tokens tokens.css --thumbs <dir_audit> --out <dir_telas> --verify-files`
   e valide também a vitrine (`fluxo.html`, `preview.html`, `index.html`) com **0 BLOCK · 0 HIGH** (Dark & Light).
4. Inspecione visualmente os PNGs finais e entregue links acessíveis validados (`HTTP 200`).
