# Guia de Sistemas Web, SaaS, ERPs & Apps Desktop

Interfaces desktop e sistemas operacionais existem para **velocidade de leitura, precisão na tomada de decisão e baixa fadiga em jornadas longas**. A estética nunca pode atrasar ou fantasiar o trabalho diário.

Tokens de cor, tipo, espaço, elevação e ícone são os mesmos do app mobile irmão. A estrutura não é. Sidebar, master-detail e command palette existem porque há cursor, teclado e largura. Não estique uma tab bar de celular até sobrar um miolo vazio, e não entregue esta densidade numa tela de 390px: lá a tabela vira lista, como na seção 6 e no guia mobile.

---

## 1. Filosofia `Operate` (Sistemas e Ferramentas de Trabalho)

Em sistemas operacionais (ERPs, CRMs, portais financeiros, painéis de SRE, IDEs e ferramentas B2B):
- **O tema empresta apenas 4 elementos**: Tipografia, Paleta, Densidade e **1 Assinatura Visual** ligada ao domínio.
- **Nunca fantasie os controles**: botões, selects, abas, tabelas ordenáveis, filtros e menus mantêm comportamento 100% padrão e previsível. Nunca transforme uma tabela financeira em "papel pautado" nem um painel web em "terminal retrô com moldura falsa" só por estilo.
- **Hierarquia pela ordem real do trabalho**: leia no planejamento e no repositório o que a pessoa decide primeiro, o que compara ao lado e o que só consulta. Os nomes das zonas saem dessa língua. "Agora / Em Rota / Radar" é um exemplo de operação logística, não a estrutura padrão.
- **Uma tela, um uso.** Se a pessoa não aponta a navegação, a ação principal e o próximo passo sem varrer a tela inteira, a tela está poluída. Separe em outra tela, agrupe, ou rebaixe o botão a secundário. Não esconda o caminho para o resultado parecer limpo.

---

## 2. Arquitetura de Composição Desktop (Anti-Poluição & Zero Espaços Mortos)

O erro clássico de sistemas web/desktop tem dois polos opostos: **(1) deixar 60–70% do painel direito vazio** ou **(2) espremer 3 colunas permanentes em telas cheias de números criando poluição visual**. Escolha o arquétipo pela lógica real da tarefa de cada tela:

### A. Revelação Progressiva por Resize In-Place: `Fila Limpa → Conferência & Aprovação Focada` (Arquétipo #1 · `v2.4.0`)
Ideal para **Filas de Pendências, Conferência/Aprovação Operacional, Contas a Pagar/Receber, Radar de Editais, Certidões e Contratos** — acaba de vez com o vício de jogar lista + 8 abas + resumo duplicado + documento + botões tudo ao mesmo tempo na tela:
1. **Estado 1 — Fila Limpa (`100%` da área útil):** topo enxuto com **no máximo 2 barras horizontais (`<= 210px`, `DA-HEADER-STACK-BLOAT`)**, **máx. 4–5 abas primárias + dropdown `"Mais status"` (`DA-TAB-OVERFLOW`)** e lista/tabela respirável em `.panel-z2` com hover nítido (`inset 3px 0 0 var(--primary)`). Sem selos-eco repetindo o óbvio em cada linha (`DA-BADGE-ECHO`).
2. **Estado 2 — Clique na Pendência → Resize Suave na Mesma Área (`180ms`):** a fila recolhe para um trilho compacto lateral (ou alterna com `← Voltar à fila [Esc]` e `‹ Anterior · Próxima ›`), abrindo uma **Tela de Conferência & Aprovação** simples, direta e objetiva em **3 blocos únicos**:
   - **Bloco 1 (Identificação — Single Source of Truth):** quem, unidade/posto, data e motivo aparecem **1 única vez** (nunca duplicados em 2 cards diferentes!).
   - **Bloco 2 (Evidência / Documento Real do Trabalho):** cartão comparativo tátil (`Antes → Proposto`) com faixa superior em `--surface-brand-header` + justificativa do solicitante, sem nenhum jargão de infraestrutura (`DA-TECH-JARGON-UI`).
   - **Bloco 3 (Rodapé Estrutural `flex-shrink: 0`):** container em `display: flex; flex-direction: column` com corpo rolável (`flex: 1; overflow-y: auto`) + **Tactile Decision Bar** estrutural fixa na base (`Aprovar` em `--success` esmeralda + branco, `Devolver` secundário, `Indeferir` em vermelho real `--danger` — **nunca flutuando sobre texto, nunca rosa e nunca misturado com controles de demo!**).

### B. Inbox 2 Colunas + Drawer de Contexto Sob Demanda (Atendimento / Chat / Mensageria)
Ideal para atendimento omnichannel (WhatsApp/Site), tickets em tempo real e simuladores:
1. **Coluna Esquerda (`300–340px`):** fila priorizada por SLA (`.chip-sla` com anel SVG circular) + seleção por teclado (`↑`/`↓`).
2. **Coluna Principal (`1fr`):** conversa viva + cabeçalho com janela SLA + notas internas + compositor; o **contexto de contrato/cliente abre num Drawer lateral sob demanda** em vez de espremer a conversa o tempo todo.

### C. Cockpit 3 Zonas / Master-Detail / Kanban / Bento Executivo (Sob Medida por Módulo)
- **Kanban:** poços `.well-z0` por etapa com soma financeira ao vivo + barra de progresso de habilitação nos cards + `SortableJS` + setas `<` `>` para teclado.
- **Bento Grid Executivo (Portal):** **PROIBIDO buraco vazio interno (`> 95px`, `DA-CARD-INTERNAL-VOID`)** causado por `justify-content: space-between` / `margin-top: auto` quando dois cards na mesma linha têm alturas diferentes! Equilibre a densidade interna (ex.: linha de destaque/próximo prazo no miolo) ou empilhe o conteúdo com `gap` constante.
- **Workbench / Split-Pane Redimensionável:** para IDEs, clientes de dados e ferramentas técnicas (`Split.js` / `Dockview` / `react-resizable-panels`).

---

## 3. Tabelas Densas de Alta Legibilidade

- **Alinhamento rígido**: textos e identificadores à esquerda; datas em formato curto uniforme (`18 Nov` ou `18/11/26`); **números, valores monetários, percentuais e contagens sempre à direita com `tabular-nums`**.
- **Controle de badges**: no máximo 1–2 tags/pills semânticas por linha. Evite arco-íris de pílulas competindo pelo olhar.
- **Cabeçalho fixo (`sticky`)** quando a tabela rola, barra de ações em lote flutuante quando >= 1 linha estiver selecionada.
- **Ações por linha**: mantenha no máximo 1 ação rápida visível no hover/foco e o restante em menu contextual (`...` ou clique direito).
- **Ordenação e filtros visíveis**: chip/pílula ativa sempre indica o filtro aplicado e mostra o botão rápido de limpar.

---

## 4. Ergonomia de Apps Desktop (Electron, Tauri, macOS, Windows)

Se o projeto compila para janela desktop nativa (Electron, Tauri, SwiftUI macOS, WinUI 3):

### Anatomia de Janela
- **Titlebar integrada e arrastável (`-webkit-app-region: drag`)**: botões, inputs, buscas e controles dentro da titlebar DEVEM ter `-webkit-app-region: no-drag`.
- **Respeito ao OS host**:
  - **macOS**: reserve `76–84px` à esquerda na titlebar para os *traffic lights* (fechar/minimizar/zoom); use `⌘` para atalhos (`⌘K`, `⌘,`, `⌘W`). Material vítreo (Liquid Glass) fica a cargo do sistema nas superfícies nativas. Não simule esse vidro num ERP web nem no Android.
  - **Windows / Linux**: reserve espaço à direita para minimizar/maximizar/fechar com altura confortável (`>= 32–40px`); use `Ctrl` nos atalhos.
- **Estado `window-unfocused`**: atenue sutilmente a barra de título/seleção ativa quando a janela perder foco do SO (detalhe clássico de app nativo).

### Produtividade por Teclado & Command Palette (`⌘K`)
- **Command Palette (`⌘K` / `Ctrl+K`)** obrigatório em sistemas com >= 5 módulos ou ações recorrentes: busca instantânea de telas, registros e ações rápidas, totalmente operável por `↑`/`↓`/`Enter`/`Esc`.
- **Atalhos descobertos**: exiba `<kbd>` discreto nos tooltips ou menus (`G` depois `P` para Portal, `/` para buscar, `Esc` para fechar drawer/modal).
- **Menus contextuais e estado persistente**: salve tema, largura de sidebar e filtros recentes em `localStorage` ou store do app desktop.
- **Hover, foco e tooltip** existem porque há cursor. Tooltip explica o atalho ou o dado truncado. Não esconda a ação principal só no hover.
- **Overlay certo para o peso da tarefa**: menu de contexto no clique direito, popover ancorado no controle que abriu, dialog central só para confirmação destrutiva ou fluxo que precisa bloquear. Tarefa secundária longa vai para inspector ou sheet, não para um modal no meio da tabela.

---

## 5. Coerência Cromática (Fim do Monobloco Cinza/Branco) & Paridade Semântica Light/Dark (`v2.4.0`)

- **Fim do Monobloco Cinza no Dark Mode (`DA-DARK-FLAT-MONOLITH`):** **PROIBIDO** deixar uma Sidebar azul rica ao lado de um paredão cinza chapado sem identidade, sem profundidade e sem separação de conteúdos!
  1. **Traga a família de azuis profundos/fortes da marca (da própria Sidebar) para dentro do workspace:** use `--surface-brand-header` (ex.: `#112C54`) nos cabeçalhos de painéis de conferência/documentos, `--surface-brand-panel` (`#0E2240`) em cartões de destaque, `--primary` (`#2563EB` com `#FFFFFF`) nas abas ativas e na seleção da fila, e `--rim-highlight` (`inset 0 1px 0 rgba(148,197,255,0.12)`) + sombras calibradas Dark (`--shadow-z1..z3`) para criar **profundidade real entre planos `Z0 → Z4`** (`Z2/Z1 >= 1.08:1`, `border-subtle/Z2 >= 1.25:1`).
  2. **Preto e cinza contidos:** entram apenas em detalhes de apoio e recessos discretos, nunca como bloco monocromático morto.
- **Modo Claro Ancorado pela Marca (`DA-LIGHT-WASHED-OUT >= 1.85:1`):**
  1. **Âncora Forte (`--surface-brand-dark: #0C254A → #143A70`)** na Sidebar, Painel Institucional e Card-Rei;
  2. **Variações de Azul Claro Estrutural (`--surface-brand-header: #E3EEFC`, `--surface-tint-soft: #E6F0FD`, `--border-tint: #9DBCE6`)** nos cabeçalhos de painel, `<thead>` e berços de ícone;
  3. **Profundidade física nítida:** `Z0 #C6D6EA` · `Z1 #D9E5F3` (`>= 1.18:1` vs `Z2 #FFFFFF`) · `border-subtle #93ABC7` (`>= 1.85:1`, ideal `2.0–2.4:1` contra `Z2`) + sombras tintadas pela marca.
- **Paridade Semântica Rígida Light ↔ Dark (`DA-SEMANTIC-HUE-PARITY`):** cada cor semântica mantém a **mesma família de cor nos dois temas** (usando tokens separados para sólido `--{role}` + `--on-{role}` e para badge/texto `--{role}-surface` / `--{role}-border` / `--{role}-text`):
  - **Erro / Falha / Indeferir:** **Vermelho real** nos dois modos (`#B91C1C` / `#DC2626` sólido + `#FFFFFF`; `--danger-text: #FF6E6E` no Dark) — **NUNCA rosa pastel (`#FDA4AF`)**!
  - **Sucesso / Aprovar:** **Verde esmeralda real** nos dois modos (`#15803D` sólido + `#FFFFFF`; `--success-text: #4ADE80`) — **NUNCA verde-água neon com letra preta**!
  - **Atenção / Pendente:** **Âmbar real** (`#B45309` / `#F59E0B`);
  - **Ativo / Marca:** **Azul oficial da marca** (`#14427A` / `#2563EB` com `#FFFFFF`) — **NUNCA ciano-elétrico destoando da Sidebar**!
- **Escopo Automático `.on-brand-dark` (`DA-BRAND-DARK-SCOPE`):** toda superfície escura da marca redeclara localmente `--text-strong`, `--text-body` e `--text-muted` claros.

---

## 6. Shell Web que Muda de Forma (Sidebar Minimizável + Zero Truncamento de Marca)

O mesmo produto web não tem um layout só. Tem um shell por largura, com os mesmos tokens:

| Largura | Shell | O que cabe |
|---|---|---|
| Desktop, `>= 1024px` | **Sidebar esquerda minimizável (`248px ↔ 68px` rail)** com botão `«`/`»` + atalho `[` persistido em `localStorage` + Topbar enxuta (`56px`) | Breadcrumb + **Sub-abas internas do módulo atual** + `⌘K` + Tema + Conta |
| Tablet, `768–1023px` | Sidebar recolhe automaticamente para rail `68px` com tooltips | Lista + detalhe ou painel focado |
| Mobile web, `< 768px` | Drawer ou Tab Bar inferior fixa de `4–5` destinos (`height: 68px`, `padding-bottom >= 96px`) | Uma tarefa. Tabela densa vira lista com `.icon-emblem` |

- **Regra Anti-Truncamento de Marca e Navegação (`DA-NAV-TRUNCATION` & `DA-HEADER-HSCROLL`):** a largura expandida da Sidebar (`>= 244px–256px`) e o cabeçalho `.sidebar-brand` devem acomodar o nome da empresa **inteiro sem cortar letras** ao lado do botão `«` (prefira nome curto em `.brand-name` + contexto em `.brand-sub`). Topbars e seletores horizontais em desktop (`1440px`) nunca podem exibir scrollbar horizontal ou cortar o primeiro/último botão.
- **Regra Anti-Duplicação na Topbar:** NUNCA repita os mesmos módulos globais da Sidebar esquerda dentro da Topbar da tela inicial/Portal! Na tela de módulo, a Topbar mostra as **sub-abas internas** daquele módulo; no Portal, mostra seletor de período/visão ou atalhos rápidos.
- Altura de tela: `100dvh` ou `svh`, com `env(safe-area-inset-*)`.
- Landmarks reais: `header`, `nav`, `main`, `aside`. Um `h1` por tela, headings sem pular nível e operação 100% por teclado.

---

## 7. Gráficos de Estúdio & Micro-Componentes Analíticos OSS (`v2.3.0`)

Antes de escolher o componente, descreva na Bíblia a pergunta, a métrica, sua unidade e denominador, a escala, o estado zero e a interação necessária. Explicite quando um comparativo tem escala própria por linha ou quando o vazio mostra outra métrica. Verifique o número com dados conhecidos após trocar dia, série ou filtro. Disponibilize a leitura relevante também sem hover.

Nunca entregue gráficos "tutorial" (1 linha quase reta no topo com paredão monocromático até o zero):
1. **Fluxo de Caixa / Séries Financeiras (`TradingView Lightweight Charts` / `Apache ECharts` / `ApexCharts`):**
   - **Escala Y Dinâmica Calibrada (`DA-FLAT-CHART-AXIS`):** nunca trave `min: 0` numa série que varia entre `3,2M` e `3,5M`; ajuste `min` à faixa real ou combine **Combo Barras Diárias (`+Entradas` / `-Saídas`) + Curva Suave de Saldo Acumulado**;
   - **HUD Vivo no Cabeçalho do Card:** ao mover o mouse no gráfico (`updateAxisPointer` / `crosshairMove`), atualize no topo do card a Data em foco, Saldo exato (`.num`), Entradas/Saídas e Delta `%` vs piso operacional;
   - **Anotações Reais:** pinos `markPoint` nos dias críticos (maior saída / maior entrada) + `markLine`/`markArea` para o piso/meta.
2. **Cascata Financeira (`Waterfall DRE`):**
   - Use **paleta categórica multi-cor (`--chart-1` a `--chart-6`)** por função (Receita, Custos/Repasses, Estrutura, Tributos, Resultado Líquido) — nunca 4 barras do mesmo azul — com **linhas conectoras tracejadas** entre degraus e badge de `% da receita` no topo de cada barra.
   - **Higiene de Sinais:** apenas barras de dedução/saída levam prefixo `–` (ex.: `– R$ 283,0k`); barras de **Receita inicial** e **Subtotal / Resultado Líquido positivo** NUNCA levam sinal negativo!
3. **Micro-Componentes Analíticos Estilo Tremor Raw (para acabar com cards "só texto"):**
   - **`BarList`:** listas de ranking/setor com barra horizontal translúcida proporcional ao valor por trás do rótulo;
   - **`Tracker` (24–45 blocos):** faixa de blocos semânticos para SLA, saúde de integrações ou validade de certidões com tooltip por bloco;
   - **`CategoryBar`:** barra segmentada multi-cor (`--chart-1..5`) sincronizada no hover com os sub-cards abaixo;
   - **`Sparklines`:** mini-tendência de 7 dias dentro de cards de banco/KPI.

Geist, Primer, Polaris, TradingView e Tremor servem de referência técnica. A busca automática categorizada está em [09-pesquisa-componentes-oss.md](09-pesquisa-componentes-oss.md).
