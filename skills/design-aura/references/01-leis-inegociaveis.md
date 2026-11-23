# Leis da Design Aura, por camada

Este guia lista todas as regras que os scripts verificam. A fonte única é `data/rules.json`: ali ficam a camada de cada regra, o teto de severidade e os orçamentos padrão. Se um número aqui divergir do registro, vale o registro.

## Como ler a severidade

| Severidade | O que significa | Efeito |
|---|---|---|
| **BLOCK** | Falha objetiva que quebra uso, acesso ou confiança | Corrige antes de qualquer entrega |
| **HIGH** | Falha clara, ou sinal forte de interface genérica | Corrige ou registra a exceção com motivo |
| **REVIEW** | Sinal de composição medido por aproximação | Confere na captura; corrige pela causa ou dispensa com motivo |
| **MEDIUM / LOW** | Acabamento | Lista de polimento |

`--strict` falha só com BLOCK ou HIGH. Subagentes construtores entregam com zero BLOCK e listam o resto para o orquestrador.

## Ofício (pode bloquear)

Objetivas e universais. Valem em qualquer projeto, direção ou plataforma. Uma falha aqui é BLOCK ou HIGH e precisa de correção antes da entrega.

| Regra | O que pede | Evidência |
|---|---|---|
| `DA-B3-01` | Texto normal e placeholder com WCAG ≥ 4,5:1 e APCA |Lc| ≥ 60; texto grande e componentes com 3:1 e |Lc| ≥ 45. Sobre gradiente ou imagem, confira na captura. | tokens/runtime |
| `DA-SEMANTIC-HUE-PARITY` | Cada estado mantém a família de matiz nos dois temas: erro vermelho (nunca rosa pastel no Dark), sucesso verde, atenção âmbar. | tokens |
| `DA-B3-03` | Alvos de toque ≥ 44×44 px (iOS, web mobile) e ≥ 48×48 dp (Android) com 8 px entre eles; texto de interface ≥ 12 px, corpo ≥ 14 px. | runtime/código |
| `DA-B9-01` | Todo campo tem label visível, ou aria-label quando é busca ou filtro em barra. Placeholder não substitui label. | runtime/código |
| `DA-B9-02` | Nunca remova o foco sem colocar um anel equivalente (:focus-visible ou :focus-within no contêiner). | código |
| `DA-B10-03` | Imagem com alt adequado (vazio se decorativa) e fallback quando falhar. | runtime/código |
| `DA-B10-IMG` | Nenhuma imagem quebrada na tela entregue. | runtime |
| `DA-DOM-OVERFLOW` | Nenhuma rolagem horizontal da página em nenhuma largura declarada. | runtime |
| `DA-FIXED-OVERLAP` | Conteúdo rolável nunca fica sob barra fixa; reserve o espaço (padding seguro). | runtime |
| `DA-CLIPPED-CONTENT` | Cartão com overflow hidden não pode cortar o próprio conteúdo. | runtime |
| `DA-MOBILE-FLEX-CLIP` | Em coluna flex rolável, filhos com overflow hidden precisam de flex-shrink: 0 (ou use grid com grid-auto-rows: max-content). | runtime/código |
| `DA-NAV-TRUNCATION` | Marca e itens de navegação não podem ser cortados. | runtime |
| `DA-HEADER-HSCROLL` | Barras superiores e seletores não mostram rolagem nem cortam o primeiro ou o último item. | runtime |
| `DA-JS-ERROR` | Zero erro ou exceção de JavaScript, inclusive depois das interações. | runtime |
| `DA-ASSET-404` | Zero recurso local que não carrega. | runtime |
| `DA-AUDIT-COVERAGE` | Toda tela, largura e estado declarados no manifesto têm captura; o que faltar é pendência, não aprovação. | runtime |
| `DA-REACHABLE` | A ação principal está visível e alcançável no estado testado (sem toast, sheet ou overlay por cima). | runtime |
| `DA-B5-01` | Sem Lorem ipsum, John Doe, Acme e similares na tela entregue. | código |
| `DA-B2-08A` | Sem texto de bastidor na tela ("não está nesta amostra", "semente do funil"). | código |
| `DA-A11Y-KEYBOARD` | A jornada principal completa só com teclado, com o foco visível em cada passo. | runtime |

## Sinais de interface genérica (até HIGH)

Marcas fortes de interface gerada sem direção. Corrija ou registre a exceção no próprio arquivo: `<!-- design-aura-allow: DA-B1-01 gradiente oficial da marca -->` (o motivo tem pelo menos 8 caracteres).

| Regra | O que pede | Evidência |
|---|---|---|
| `DA-B1-01` | Gradiente roxo, índigo ou neon só entra se for da marca ou do briefing. | código |
| `DA-B1-02` | Sem glow pesado, blobs desfocados ou vidro sem função. Halos sutis em foco e indicadores são permitidos. | código |
| `DA-B1-03` | Emoji não é ícone de interface. | código |
| `DA-B1-05` | Sem eyebrows de landing genérica (FEATURES, HOW IT WORKS) e numeração decorativa. Rótulos reais de contexto são bem-vindos. | código |
| `DA-B1-06A` | Sem gradiente em texto. | código |
| `DA-B1-06B` | Sem a mesma barrinha colorida em todos os cartões. Borda de destaque em alerta, citação ou item ativo é permitida. | código |
| `DA-B1-06C` | Selos LIVE, NEW ou AI só com estado real. | código |
| `DA-B5-02` | Sem frases de IA ("Transforme seu negócio", "Eleve sua experiência"); use verbos e vocabulário do domínio. | código |
| `DA-B6-02A` | Declare as propriedades da transição; nunca transition: all. | código |
| `DA-B6-02B` | Sem escala no hover de cartões grandes. | código |
| `DA-B6-02C` | Sem bounce ou pulse decorativos. | código |
| `DA-B6-02D` | Controles simples respondem em até ~300 ms. | código |
| `DA-B6-04` | Animação infinita só para espera ou sinal real (skeleton, progresso, digitação, gravação, alerta ativo). | código |
| `DA-B9-05` | Campos usam o estilo do design system (borda, raio, padding, foco), não o visual cru do navegador. | código |
| `DA-B2-03` | Texto longo e listas de leitura alinhados à esquerda. | código |

## Acabamento (até MEDIUM)

Detalhes que separam o bom do excelente. Entram na lista de polimento e nunca travam a entrega.

| Regra | O que pede | Evidência |
|---|---|---|
| `DA-B7-01` | Raio interno = raio externo − padding quando o padding é até 24 px. | código/runtime |
| `DA-B7-02` | Espaços da escala do projeto; ajustes ópticos de 2 px dentro de controles são normais. | código |
| `DA-B4-01` | Contraste claro entre título, corpo e metadado; pesos extremos só em display e números de destaque. | código |
| `DA-B4-02` | Números que mudam, valores e colunas numéricas com tabular-nums. | código |
| `DA-B8-03` | Colunas numéricas alinhadas à direita. | código/runtime |
| `DA-B3-02` | Preto e branco puros só com controle de elevação; texto secundário sobre superfície colorida é tingido por ela. | código |
| `DA-B10-04` | Avatares e mídias com object-fit e proporção travada. | código |

## Composição e gosto (REVIEW)

Medidas aproximadas de composição. Saem como REVIEW: abra a captura, confirme e corrija pela causa, ou dispense com o motivo no relatório. Os limites são orçamentos do projeto (Parte B da Bíblia e `project.budgets` no manifesto), com padrões por modo em `data/rules.json`.

| Regra | O que pede | Evidência |
|---|---|---|
| `DA-DEAD-SPACE` | Vazio grande na área de trabalho: confirme se é respiro da direção ou falta de estrutura. Orçamento: `deadSpaceReviewPct`. | runtime |
| `DA-STUB-SCREEN` | Tela com pouco conteúdo real: confirme se é uma tela curta legítima (formulário, login) ou uma casca. | runtime |
| `DA-B2-08B` | Tabela operacional com 1–2 linhas: use dados de demo completos. | código |
| `DA-SURFACE-FLAT` | Planos sem nenhuma pista de separação (degrau, borda ou sombra). | runtime |
| `DA-CARD-INTERNAL-VOID` | Buraco vertical dentro de cartão, comum com space-between em grades de alturas diferentes. Orçamento: `cardVoidPx`. | runtime |
| `DA-BADGE-ECHO` | O mesmo selo repetido em todos os itens de uma aba que já filtra esse estado. | runtime/código |
| `DA-HEADER-STACK-BLOAT` | Barras demais empilhadas antes do primeiro dado. Orçamento: `headerMaxBars/headerMaxPx`. | runtime |
| `DA-TAB-OVERFLOW` | Abas irmãs demais numa linha; agrupe as secundárias. Orçamento: `maxSiblingTabs`. | runtime |
| `DA-MOBILE-HERO-BLOAT` | Topo mobile empurrando a lista de trabalho para fora da dobra. Orçamento: `mobileTopMaxPct/mobileTopMaxPx`. | runtime |
| `DA-RAW-LINK-LIST` | Links crus sublinhados servindo de menu ou lista de app. | runtime |
| `DA-SERIF-OPERATE` | Serifa editorial em tela operacional: vale se a direção escolheu e registrou. | runtime |
| `DA-B4-04` | Serifa editorial em tela operacional: vale se a direção escolheu e registrou. | código |
| `DA-B2-01` | Caixa dentro de caixa com o mesmo peso. Faixa recuada, bloco de evidência ou painel com função própria organizam. | código |
| `DA-ICON-GENERIC-REPEAT` | O mesmo ícone genérico repetido como muleta; use o vocabulário do domínio. | código |
| `DA-FLAT-CHART-AXIS` | Eixo travado em zero numa série de pouca variação vira linha reta; ajuste a escala ou combine barras e linha. | código |
| `DA-B7-03` | No Dark, elevação vem de luminosidade e borda, não só de sombra preta. | código |
| `DA-TECH-JARGON-UI` | Termo técnico na tela de quem não é técnico. Em ferramentas de desenvolvimento ele é o vocabulário certo. | código |
| `DA-REF-COPY-LEAK` | Texto copiado de uma referência externa. | código |
| `DA-BRAND-DARK-SCOPE` | Superfície escura da marca no tema claro precisa redeclarar os tokens de texto claros. | código |
| `DA-B5-03` | Subtítulo que repete o título e explicação do óbvio. | código |
| `DA-B10-02` | Rolagem dentro de rolagem sem um painel fixo que justifique. | código/runtime |
| `DA-DARK-FLAT-MONOLITH` | Planos escuros sem degrau visível para o estilo de profundidade escolhido. | tokens |
| `DA-DARK-MONOCHROME` | Neutros escuros tingidos demais pela marca, virando massa monocromática. | tokens |
| `DA-LIGHT-WASHED-OUT` | Tema claro sem separação de planos para o estilo de profundidade escolhido. | tokens |
| `DA-B3-04` | Cor viva da marca escurecida até perder a vida para caber texto branco; use texto escuro sobre o tom vivo. | tokens |
| `DA-DUPLICATE-TEXT` | O mesmo dado em várias regiões da vista; cada dado aparece uma vez. Orçamento: `duplicateTextMin`. | runtime |
| `DA-ALIGN-EDGES` | Muitas linhas de alinhamento à esquerda; a grade está dispersa. Orçamento: `alignEdgesMax`. | runtime |
| `DA-PERF-BUDGET` | Peso, requisições ou fontes acima do orçamento do projeto. | runtime |
| `DA-REDUCED-MOTION` | Animação infinita que continua com prefers-reduced-motion. | runtime |

## Princípios que nenhum script mede

- **Uso humano.** Em poucos segundos a pessoa sabe onde está, para onde pode ir, o que pode fazer e qual é o próximo passo. Densidade é permitida quando o trabalho é denso e os grupos estão separados. Esconder a ação principal para a tela parecer limpa também é erro.
- **Proximidade.** O espaço dentro de um grupo é menor que o espaço entre grupos; há mais espaço acima de um título do que abaixo dele.
- **Uma ação primária por contexto.** Vários botões de mesmo peso no mesmo olhar são poluição.
- **Estados completos.** Carregando, vazio com próxima ação, erro com recuperação, sucesso com desfazer quando a ação é reversível.
- **Destrutivo com cuidado.** Confirmação que diz a consequência ou desfazer imediato; nunca modal sobre modal.
- **Cor com significado.** Cores semânticas só onde há estado real; o estado nunca depende só da cor (ícone ou texto junto).
- **Plataforma primeiro.** iOS segue o HIG, Android o Material 3, desktop tem teclado, foco e menus de contexto. Tokens atravessam as plataformas; navegação, densidade e overlay mudam.
- **Dados verdadeiros.** Nunca invente métricas, clientes, depoimentos ou diferenciais. Demonstração usa dados fictícios verossímeis e iguais em todas as telas.

## Como uma regra nova entra

1. Explica uma falha reproduzível, vista em mais de um projeto ou demonstrável numa fixture.
2. Ganha uma fixture boa (não pode disparar) e uma ruim (tem de disparar) em `tests/fixtures/`.
3. Recebe camada e, se for heurística, um orçamento ajustável por projeto.
4. Substitui texto existente em vez de somar. Preferências de um único projeto ficam na Bíblia daquele projeto.
