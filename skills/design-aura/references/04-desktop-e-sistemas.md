# Sistemas web, SaaS, ERPs e apps desktop

Sistemas de trabalho existem para leitura rápida, decisão precisa e pouca fadiga ao longo do dia. A estética serve a isso. Tokens de cor, tipo, espaço e elevação são os mesmos do app mobile irmão; a estrutura não. Sidebar, master-detail e paleta de comandos existem porque há cursor, teclado e largura.

## 1. Modo Operate

- A direção empresta quatro coisas ao sistema: paleta, tipografia, densidade e uma assinatura. Controles e navegação continuam familiares.
- Não fantasie controles: tabelas, filtros, menus e abas mantêm o comportamento padrão. Nada de "papel pautado" ou "terminal retrô" por estilo.
- A hierarquia segue a ordem real do trabalho: o que a pessoa decide primeiro, o que compara ao lado, o que só consulta. Os nomes das zonas vêm do vocabulário do projeto.
- Uma tela, um uso. Se a pessoa não aponta a navegação, a ação principal e o próximo passo sem varrer a tela, separe, agrupe ou rebaixe. Não esconda o caminho para a tela parecer limpa.

## 2. Escada de revelação

Antes de pôr um bloco na tela, decida em que degrau ele mora:

1. **Na linha** — dado que a pessoa usa para decidir agora (valor, prazo, estado).
2. **Popover ou tooltip** — explicação ou detalhe curto sob demanda.
3. **Drawer ou sheet** — contexto secundário que não pede foco total.
4. **Detalhe na mesma área** — o item vira o centro do trabalho (resize in-place).
5. **Página própria** — tarefa longa, compartilhável por link.

Quanto mais um dado é usado para decidir, mais perto da linha ele fica. O resto desce na escada.

## 3. Arquétipos

Escolha pela tarefa de cada tela; a Tela-Mãe não impõe arquétipo às outras. Os padrões visuais de cada problema estão em `data/recipes.json`.

| Arquétipo | Quando | Estrutura |
|---|---|---|
| **Lista → detalhe na mesma área** | Fila de conferência ou aprovação decidida item a item | A lista ocupa a área; ao abrir, recolhe para um trilho e o detalhe assume, com Voltar (Esc), anterior e próximo, identificação uma vez só, evidência do item e um rodapé estrutural com a ação primária |
| **Master-detail** | Consulta frequente com comparação | Painéis redimensionáveis; o detalhe guarda a seleção |
| **Inbox** | Conversas e tickets com prazo | Fila de 300–340 px + conversa; contexto do cliente em drawer, fixo só acima de ~1400 px |
| **Kanban** | Etapas com volume e valor | Colunas recuadas com contagem e soma; cartões curtos; mover também pelo teclado |
| **Painel** | Visão geral para decidir o dia | Blocos pela urgência do negócio; KPI só quando leva a uma ação |
| **Formulário em seções** | Configurações, cadastros longos | Navegação secundária + seções focadas, largura de leitura |
| **Workbench** | Ferramentas técnicas e de criação | Painéis acopláveis, árvore, editor, painel inferior |

Larguras fixas das zonas precisam caber na largura mínima declarada (`minWidth` no manifesto; `render_design_bible.py --check` confere). Abaixo dela, uma zona vira drawer.

## 4. Tabelas densas

- Texto e identificadores à esquerda; números, moeda, percentuais e contagens à direita com `tabular-nums`; datas num formato curto único.
- No máximo um ou dois selos por linha, só para exceções. Não repita o estado que a aba já filtra.
- Cabeçalho fixo quando a tabela rola; barra de ações em lote quando há seleção.
- Uma ação rápida visível no hover ou foco; o resto no menu de contexto.
- Filtros ativos visíveis em chips com botão de limpar.

## 5. Shell por largura

| Largura | Shell |
|---|---|
| `≥ 1024 px` | Sidebar recolhível (largura expandida e recolhida definidas na Bíblia; o nome da marca cabe inteiro) + topbar enxuta com contexto do módulo, busca/paleta, tema e conta |
| `768–1023 px` | Rail com tooltips ou drawer; lista + detalhe ou painel focado |
| `< 768 px` | Drawer ou barra inferior de 4–5 destinos; uma tarefa por tela; tabela vira lista |

- A topbar não repete os módulos da sidebar. No módulo, mostra as sub-abas dele; no início, período ou visão.
- `100dvh` e `env(safe-area-inset-*)`; landmarks reais (`header`, `nav`, `main`, `aside`); um `h1` por tela; tudo operável por teclado.

## 6. Apps desktop (Electron, Tauri, nativo)

- Barra de título integrada e arrastável; controles dentro dela com `no-drag`.
- macOS: espaço para os botões de janela à esquerda, atalhos com ⌘, materiais do sistema só onde o sistema desenha. Windows/Linux: controles à direita, atalhos com Ctrl, Mica e Acrylic são do sistema (Fluent).
- Atenue a seleção ativa quando a janela perde o foco.
- Paleta de comandos (⌘K/Ctrl+K) em sistemas com cinco ou mais módulos ou ações recorrentes, operável por setas, Enter e Esc. Atalhos aparecem em `<kbd>` nos menus e tooltips.
- Overlay pelo peso da tarefa: menu de contexto no clique direito, popover ancorado no controle, diálogo central só para confirmação destrutiva ou fluxo que precisa bloquear.
- Persista tema, largura da sidebar e filtros recentes.

## 7. Gráficos de produto

Antes de escolher o gráfico, escreva na Bíblia a pergunta que ele responde, a métrica, a unidade, o denominador, a escala, o estado vazio e a interação.

- Série com pouca variação não começa em zero: ajuste a escala ou combine barras de entrada e saída com a linha do acumulado.
- Mostre o valor sob o cursor num cabeçalho do cartão e torne a leitura principal acessível sem hover.
- Cascatas com conectores, cor por função e sinal negativo só nas deduções.
- Rankings como lista com barra proporcional; saúde ao longo do tempo como faixa de blocos; composição como barra segmentada.
- O título diz o que o gráfico mostra, não o tipo de gráfico.
- Depois de trocar dia, série ou filtro, confira o número exibido contra um dado conhecido (o probe tem `assertText`).

Peças de gráfico, tabela e área de trabalho: `discover_oss_components.py --category charts` (ou `data-tables`, `desktop-workbench`).
