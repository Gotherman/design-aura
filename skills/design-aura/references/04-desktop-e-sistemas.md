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

### A. Revelação Progressiva Anti-Poluição: `Lista Limpa → Detalhe Focado na Mesma Página` (Arquétipo #1 para Filas & Tabelas Densas)
Ideal para **Contas a Pagar, Contas a Receber, Radar de Editais, Cofre de Certidões, Pedidos e Contratos**:
1. **Estado 1 — Visão Geral Limpa (largura total):** faixa executiva de KPIs (com `.card-brand-hero` no indicador principal) + barra de busca e filtros em poço `.well-z0` + tabela respirável e escaneável em `.panel-z2` com hover de elevação (`inset 3px 0 0 var(--primary)`).
2. **Estado 2 — Detalhe Focado Inline na Mesma Página (ao clicar em qualquer linha ou abrir `?item=id`):** a lista dá lugar suavemente (`180ms`) à ficha completa do registro em largura total com:
   - Barra fixa superior: **`← Voltar à lista` (`Esc`)**, contador (`Item 1 de 8`) e navegação **`‹ Anterior · Próxima ›`**;
   - Documento completo (com picote técnico se for fatura/edital) + simulação de cobertura bancária/risco + 1 CTA dominante com **Toast Desfazer**.

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

## 5. Equilíbrio Cromático `65 / 20 / 10 / 5` & Modo Claro Ancorado pela Marca (`v2.2.1`)

- **Modo Claro Ancorado pela Marca (`Brand-Anchored Light Mode` — PROIBIDO "Tudo Branco/Cinza Lavado" · `DA-LIGHT-WASHED-OUT`):**
  Um Modo Claro onde Sidebar, Topbar, Canvas, Login e todos os Cards são brancos ou cinza-pálido perde completamente o senso de divisão, profundidade e identidade! Use **variações da cor forte e da cor clara da marca**:
  1. **Âncora Forte da Marca (`--surface-brand-dark`, ex.: Marinho `#0E294B → #163E70` com texto `#F8FAFC`):** aplique na **Sidebar Desktop no Light Mode** (ou no **Painel Institucional do Login Split-Screen**) e no **Card-Rei `.card-brand-hero`** de cada tela (ex.: Saldo Consolidado / Cabeçalho Mobile) — criando divisão arquitetônica imediata entre a Navegação/Hero ricos em cor e a Área de Trabalho clara!
  2. **Variações de Azul/Cor Clara Estrutural (`--surface-tint-soft: #E6F0FD`, `--border-tint: #B5CEF0`):** aplique nos **cabeçalhos internos de cards compostos (`.panel-head`)**, nos **`<thead>` das tabelas**, nos **berços de ícone (`.icon-emblem`)** e nos **controles ativos** — substituindo cinza-morto por tintagem harmônica da marca.
  3. **Canvas, Poços e Sombras Tintadas pela Marca:** `Z0 #CFDCEB` · `Z1 #E1EAF4` · `Z2 #FFFFFF` com borda nítida `#B0C2D9` (`>= 1.22:1` contra `Z2`), chanfro branco `inset 0 1px 0 #FFFFFF` e sombra física tintada com a cor profunda da marca (`rgba(14, 41, 75, 0.11)`).
- **Dark Mode com Subtom Arquitetônico & Âncora de Marca Viva (`DA-DARK-MONOCHROME`):** evite tanto a **massa azul 50%-saturada** quanto o **carvão morto sem marca**. Use base `Z0–Z3` em Obsidiana com subtom sutil da marca (`S = 18%–26%`, ex.: `#080C12 → #0E131D → #141C29 → #1B2637`) e expresse a cor oficial da empresa com clareza em **3 Zonas Fixas**:
  1. Bloco de identidade na Sidebar/Header (`.sidebar-brand-card` em `--surface-brand-dark: #0D2442 → #163966` com fio especular superior `rgba(110,181,255,0.22)`) + item ativo (`18% --primary` + filete `3px --accent`);
  2. **Card-Rei (`.card-brand-hero`)** no topo de cada tela com gradiente azul-marinho institucional (`--surface-brand-dark-2 → --surface-brand-dark`) + borda luminosa (mantendo personalidade da marca tanto no Dark quanto no Light!);
  3. Controles selecionados (`.subtab.is-active`, `.seg-btn.is-active`) + paleta categórica harmônica de 6 cores (`--chart-1..6`).
- **Escopo Automático `.on-brand-dark` (`DA-BRAND-DARK-SCOPE`):** toda superfície escura da marca (`.sidebar`, `.auth-brand-pane`, `.card-brand-hero`) DEVE redeclarar localmente `--text-strong`, `--text-body`, `--text-muted` e `--border-subtle` para tons claros de alto contraste — impedindo que texto escuro do Light Mode vaze sobre fundo marinho.

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
