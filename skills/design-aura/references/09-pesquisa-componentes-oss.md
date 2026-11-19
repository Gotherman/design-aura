# Pesquisa Categorizada de Componentes Free/OSS & Elementos Gerais de UI/UX (`v2.2.0`)

A interface nao fica sofisticada porque entrou um componente famoso. Fica sofisticada quando o **catalogo le o projeto real, identifica categoricamente cada elemento necessario e entrega a biblioteca permissiva + a receita de micro-componente e iconografia certa** — tudo re-tematizado pelos tokens da Biblia.

## 0. Mapeamento Categorico Automatico do Projeto (`16 Categorias Canonicas`)

Na Fase 2, **antes** de fechar a Secao 8 da `DESIGN-BIBLE.md`, rode o scanner categorico no repositorio ou arquivo de planejamento:

```bash
python3 <skill_dir>/scripts/discover_oss_components.py \
  --scan <caminho-do-repositorio-ou-plano> \
  --stack <html|react|vue|svelte|rn|flutter|ios|android> \
  --platform <system|desktop|mobile|all> --mode <operate|read|persuade>
```

Em menos de 1 segundo, o script le o planejamento, rotas e arquivos de dados do projeto, ativa automaticamente as categorias relevantes entre as **16 Categorias Canonicas** (`data/ui_elements_recipes.json`) e devolve:
1. **Bibliotecas e registries permissivos (`MIT / Apache-2.0 / BSD / ISC`)** ja filtrados para a stack (`106+` entradas em `registries_oss.json` + `71+` em `components_oss.json`);
2. **Receitas Visuais & Micro-Componentes de Estudio** obrigatorios de cada categoria (`.icon-emblem` spotlight, `.chip-sla` com anel SVG, `.chip-status` com halo, `.chip-kv`, `.card-brand-hero`, `Combo Cashflow HUD`, `Stepped Waterfall DRE`, `BarList`, `Tracker 30 blocos`, `CategoryBar`, `Lista Limpa -> Detalhe Focado`);
3. **Curadoria de Icones especificos da categoria** (eliminando icones genericos repetidos);
4. **Tabela pronta para a Secao 8 da `DESIGN-BIBLE.md`**.

Para listar todas as 16 categorias ou consultar uma especifica / buscar no GitHub e npm:
```bash
python3 <skill_dir>/scripts/discover_oss_components.py --list-categories
python3 <skill_dir>/scripts/discover_oss_components.py --category charts-telemetry-financial --stack html
python3 <skill_dir>/scripts/discover_oss_components.py --need "grafico de fluxo de caixa com crosshair" --stack html [--online]
```

### As 16 Categorias Canonicas de Elementos Gerais de UI/UX
1. `shell-navigation` — Sidebar minimizavel, Topbar, `Cmd+K` (`ninja-keys`, `cmdk`, `tinykeys`, `coss ui`, `shadcn/ui`)
2. `icons-emblems-avatars` — SVGs Duotone/1.75px (`Solar Icons Duotone`, `Tabler Icons`, `Lucide`, `Heroicons Micro`, `Radix Icons`, `Iconify`, `Remix Icon`, `Iconoir`, `MingCute`, `SVGL`, `Boring Avatars`) + `.icon-emblem` e `.bank-emblem`
3. `badges-chips-timers-status` — `.chip-sla` com anel SVG circular, `.chip-status` com halo duplo + glifo vetorial, `.chip-kv` bipartido
4. `kpi-metrics-sparklines` — `Tremor Raw` (`BarList`, `Tracker`, `CategoryBar`), `NumberFlow`, `CountUp.js`, Sparklines
5. `charts-telemetry-financial` — `TradingView Lightweight Charts`, `Apache ECharts` (Combo HUD + Waterfall + Sankey), `ApexCharts.js`, `EvilCharts`, `shadcn/ui Charts`, `Observable Plot`, `uPlot`, `Frappe Charts`, `visx`
6. `data-tables-lists-progressive` — `Lista Limpa -> Detalhe Focado`, `Tabulator`, `TanStack Table/Virtual`, `AG Grid Community`, `Grid.js`, `Dice UI`
7. `kanban-drag-drop-workflows` — `SortableJS`, `Atlassian Pragmatic drag and drop`, `@dnd-kit`, `Kibo UI Kanban`
8. `forms-inputs-pickers-upload` — `IMask.js` (CNPJ/CPF/R$/boleto), `Flatpickr`, `Tom Select`, `Uppy`, `FilePond`, `coss ui`, `React Day Picker`, `React Aria`
9. `calendar-gantt-timelines` — `FullCalendar Core (MIT)`, `Frappe Gantt`, `Schedule-X`, `Kibo UI Gantt & Calendar`
10. `inbox-chat-omnichannel-ai` — `Prompt Kit`, `assistant-ui`, `Kibo UI AI Chat`, `Tiptap`, `Quill`
11. `overlays-drawers-sheets-toasts` — `Floating UI`, `Vaul`, `Sonner`, `Notyf`, `Driver.js`, `Base UI`, `@gorhom/bottom-sheet`
12. `documents-tickets-ledgers-import` — `PDF.js`, `PapaParse`, picote tecnico e linha digitavel copiavel
13. `auth-onboarding-governance-settings` — `input-otp`, split-screen auth, seletor de perfis, governanca
14. `desktop-native-workbenches` — `Dockview`, `Split.js`, `react-resizable-panels`, `Tauri v2`, `Electron`
15. `mobile-native-pwa-touch` — `SwiftUI`, `Jetpack Compose M3`, `Flutter M3`, `Konsta UI`, `FlashList`, `Zeego`, `Burnt`
16. `motion-microinteractions-feedback` — `AutoAnimate`, `Motion`, `NumberFlow`, `Open Props`

`--online` consulta a API publica do GitHub e o registry do npm e so devolve licenca **MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause ou ISC**. Sem rede, o modo offline basta.

## 1. Comece pela interacao

Escreva a necessidade como verbo, nao como "componente bonito":

- comparar muitos registros e editar uma celula
- escolher um intervalo de datas com teclado
- dividir a janela desktop em paineis persistentes
- abrir um sheet arrastavel com o polegar
- mostrar uma lista de milhares de linhas sem perder o scroll

Se a frase servir para qualquer produto, ela ainda nao e uma necessidade.

## 2. O que cada fonte e

| Tipo | Exemplos no catalogo | O que fazer |
|---|---|---|
| Registry copiavel, licenca permissiva | shadcn/ui, coss ui (ex-Origin UI), Kibo UI, Dice UI, HyperUI | Copiar, re-tematizar, assumir a manutencao |
| Dependencia mantida | Base UI, React Aria, TanStack Table, cmdk, Dockview, Mantine, gluestack, Tamagui, Forui | Instalar se o peso couber. Nao embrulhar um segundo kit por cima |
| Primitivo da plataforma | SwiftUI, Material 3 | Preferir ao kit web portado. Nao e pacote para colar |
| Galeria de referencia | Mobbin, Refero, Godly, Page Flows, Screenlane, Banani, Component Gallery, 21st.dev | Estudar fluxo e hierarquia. Nao ha codigo com licenca unica |
| Guia oficial e anatomia | Apple HIG, Material 3, Fluent 2, APG, Primer, Polaris, Geist, Laws of UX, Inclusive Components | Consultar a estrutura canonica. Nao instalar a pele visual, salvo se o produto ja vive naquela plataforma |
| Armadilha de licenca | Aceternity UI, React Bits (MIT + Commons Clause), Tailwind Plus | Pode ser bonito e ainda assim nao entrar como open source |

Sites renomados entram nesta skill em dois grupos, de proposito. Mobbin, Refero, Godly, Page Flows e Screenlane ensinam composicao de produto real. HyperUI, Kibo, Dice, coss ui, Magic UI e Cult UI entregam codigo. Misturar os dois grupos e como copiar um print e chamar de componente.

Codigo visivel no browser nao e open source. Preview publico de biblioteca paga tambem nao.

## 3. Filtro pelo modo de superficie

- **Operate** (cockpit, ERP, despacho, backoffice): o script corta pecas `flashy` (glow, marquee, spotlight, partículas). Densidade e estado vencem efeito.
- **Read** (leitura, historico, relatorio): movimento curto de troca de contexto e permitido. Loop decorativo nao.
- **Persuade** (landing, convite, empty de primeiro uso): um gesto de impacto pode entrar, se for o signature move da Biblia e nao a personalidade de toda tela.

## 4. Portao de 8 pontos

Antes de registrar na Biblia, cada candidato responde:

1. **Adequacao.** Resolve a interacao escrita no passo 1?
2. **Stack.** Funciona na versao real do projeto?
3. **Acessibilidade.** Teclado, foco e nome acessivel estao no comportamento, nao so no README?
4. **Adaptacao.** Cor, raio, tipo e icone saem dos tokens, ou a peca traz a paleta dela?
5. **Estados.** Tem loading, vazio, erro, disabled e foco, ou so a demo feliz?
6. **Manutencao.** Ha dono, issues tratadas e uma API estavel? Commit antigo nao e abandono automatico.
7. **Peso.** Quantas dependencias entram para um detalhe que o projeto ja sabe fazer?
8. **Licenca.** O arquivo `LICENSE` do commit copiado e permissivo? Commons Clause, licenca propria e "free para olhar" reprovam.

Declare o uso com uma palavra: **Referencia**, **Dependencia** ou **Codigo copiado via registry**.

## 5. Anti-Frankenstein

Uma tela que junta o card do Magic UI, o input do HeroUI e a tabela do Mantine sem re-tema e uma colcha. Escolha um primitivo de comportamento e pinte com a Biblia.

- Uma familia de icones.
- Os raios concentricos da secao 7.
- As cores semanticas da secao 5, nao as da demo.
- O motion do guia [10-motion-anti-slop.md](10-motion-anti-slop.md), nao o stagger da landing de origem.

Se todos os candidatos levarem ao mesmo dashboard generico, procure outro padrao de interacao (tabela em vez de cards, timeline em vez de feed). Nao responda so trocando a cor.

## 6. Como registrar

Na secao 8 da Biblia, uma linha por peca de fato usada:

| Papel | Fonte | Licenca | Uso | O que foi aproveitado |
|---|---|---|---|---|
| Tabela densa | TanStack Table | MIT | Dependencia | Ordenacao e colunas fixas; visual proprio |
| Sheet mobile | @gorhom/bottom-sheet | MIT | Dependencia | Gesto e detents; cor da superficie Z4 |
| Landing hero | Godly | n/a | Referencia | So a ordem da prova; nenhum codigo |

Nao escreva "a mais atual" ou "a mais bonita" sem a comparacao que sustenta a frase.

## 7. Onde olhar anatomia, sem copiar a pele

Abra o guia da plataforma antes de inventar navegacao. O catalogo `registries_oss.json` devolve estas fontes na secao de referencia, nunca como dependencia.

- **Nativo:** [Apple HIG](https://developer.apple.com/design/human-interface-guidelines) (iOS, iPadOS, macOS), [Material 3](https://m3.material.io) (Android, tablet, dobravel), [Fluent 2](https://fluent2.microsoft.design) (Windows e desktop denso).
- **Shell de produto web:** [Primer](https://primer.style) para densidade, [Polaris](https://polaris.shopify.com) para admin, [Geist](https://vercel.com/geist) para tipo e dark mode. Estudar o shell. Instalar so quando o app ja e Shopify ou GitHub, ou quando a equipe adotou aquele sistema de proposito.
- **Comportamento:** [Base UI](https://base-ui.com), [React Aria](https://react-spectrum.adobe.com/react-aria) e o [APG](https://www.w3.org/WAI/ARIA/apg) para teclado, foco e nome acessivel. [Inclusive Components](https://inclusive-components.design) e [Laws of UX](https://lawsofux.com) para a decisao, nao para um componente pronto.
- **Telas e movimento reais:** Mobbin, [Banani](https://banani.co/references) e [60fps.design](https://60fps.design). Banani e galeria gratuita: nao exporte o HTML que a IA deles gera. 60fps ensina microinteracao; o que entrar no produto ainda passa pelo guia 10. Pixlpin mistura campanha, poster e motion: serve para persuasao, nao para a estrutura de um sistema.

Liquid Glass e Material 3 Expressive sao a linguagem atual das plataformas nativas. No app Apple ou Android, use o que o sistema desenha. No web operacional, nao simule o vidro nem a toolbar expressiva por cima de uma sidebar.

## 8. Produtos reais para estudar, nao para clonar

`data/study_references.json` guarda uma curadoria curta de apps, paineis e galerias com acabamento alto. A busca devolve isso em **referencia**. Nunca como dependencia e nunca como pele do projeto.

O que entrou, e como usar:

- **SaaS e paineis** (Cal.com, Dub, Plane, Umami, PostHog, Grafana, Metabase): olhar shell, densidade e um fluxo parecido com a tarefa. A estrutura continua saindo do trabalho deste projeto.
- **Desktop** (Zed, Penpot, AppFlowy, Yaak, LocalSend, NetNewsWire): olhar janela, atalho e coluna. Nao porte a janela do Mac para a web.
- **Mobile** (Bluesky, Ice Cubes, Breezy, Signal, Bitwarden, Organic Maps): olhar polegar, gesto e o sistema certo. Ice Cubes nao vira a cara de um ERP.
- **Landing, preco e paywall** (Tailark, Lapa, Saaspo, PaywallScreens, Stripe Checkout): so quando a tarefa e convencer ou cobrar. Uma peca, re-tematizada.
- **Recortes** (Navbar Gallery, Dark.design, CallToInspiration, Siteinspire): estudar um pedaco. Nao montar a tela como colagem.

O que ficou de fora de proposito:

- **Aceternity UI e React Bits** continuam no portao de licenca. Nao sao MIT livre para copiar.
- **Templates de dashboard** (shadcn-admin e starters parecidos) ensinam chrome generico. Usar um deles como base repete a mesma cara em todo cliente.
- **AGPL e GPL** (Cal.com, Plane, Grafana, Signal, Zed) servem para ler. Copiar o codigo para o repositorio do cliente exige a licenca, e a skill nao faz isso sozinha.

Uma referencia por necessidade. Se a tela seguinte precisa de outra, busque de novo. Tres produtos misturados na mesma tela viram colcha.
