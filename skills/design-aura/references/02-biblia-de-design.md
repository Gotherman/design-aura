# Bíblia de Direção de Design (`DESIGN-BIBLE.md`)

A **Bíblia de Design** é o contrato visual, ergonômico e estrutural criado pelo **Orquestrador na Onda 0** antes de qualquer tela ser construída ou delegada a subagentes. Ela garante que 100% das telas — sejam 3 ou 25, em Desktop, Web e Mobile — pareçam projetadas por uma única diretoria de design.

Use o template copiável em [assets/design-bible-template.md](../assets/design-bible-template.md).

O primeiro bloco do arquivo, antes das 12 seções, é o **Contrato de plataforma**: trabalho (remodelar com autópsia seletiva, completar ou criar), tipo de produto, superfícies, qual é a principal, papel do mobile, stack, tema, uso das cores da marca (com vitalidade cromática), detalhes do domínio aprovados, modelo do Orquestrador, modelo dos subagentes, como o trabalho se organiza e **adaptações do molde ao vocabulário e fluxo do projeto**. Também lista as hipóteses que não foram confirmadas. Cor, tipo e tela só começam depois desse bloco.

**Regra anti-sabotagem:** adaptar o molde ao domínio **nunca** significa descartar engenharia UI de alto nível (superfícies `Z2`, cockpits de 3 zonas quando o trabalho pede triagem+documento+telemetria, gráficos OSS reais como ECharts, badges semânticos, ícones coerentes ou tipografia sans-serif moderna em `Operate`).

---

## As 12 Seções Obrigatórias da Bíblia

### 1. Diagnóstico & Autópsia (ou Território do Problema)
- **Se houver sistema/app existente**: faça uma autópsia honesta apontando falhas reais (monocromia anestesiada, branco lavado sem contorno, 70% de vazio morto, fluxos passivos, falta de estados).
- **Se for projeto novo**: mapeie os erros típicos do setor que serão terminantemente proibidos desde o dia 1.
- Crave o compromisso de tolerância zero com os **10 Blocos de Leis Inegociáveis**.

### 2. Direção Criativa, Modo de Superfície & Assinatura Única
Classifique a superfície primária do produto:
- **`Operate`** (ERP, SaaS operacional, Fintech, DevTools, App de produtividade): o usuário veio executar trabalho. A estética empresta **apenas 4 coisas**: tipografia, paleta, densidade e **1 assinatura visual (*signature move*)**. Controles e navegação permanecem familiares à plataforma. A composição da área de trabalho segue o fluxo real do projeto, não um cockpit genérico.
- **Multiplataforma:** a Bíblia repete os tokens e descreve um shell por plataforma. Não existe um layout único que só muda de largura.
- **`Read`** (documentação, relatórios, portal analítico, leitor): foco em medida tipográfica (65–75ch), ritmo vertical e clareza editorial.
- **`Persuade / Experience`** (landing page, vitrine de produto, onboarding de impacto): compromisso expressivo máximo sem sacrificar legibilidade ou velocidade.

Os detalhes visuais do domínio só entram se a Fase 1 aprovou, cada um com plano fechado: ação, aparição, formato, duração, reduced motion e onde não entra. O Orquestrador tem liberdade para criar o que foi aprovado. Não troca isso por cenário de fundo nem por um efeito em cada tela. Se nada foi aprovado, a identidade fica no vocabulário, na hierarquia e nos dados reais.

### 3. DNA da Marca sem Clichês
Traduza a essência do negócio para **linguagem de UI**. Um avião, um carimbo ou outro objeto do ofício só entra no momento aprovado, nunca como papel de parede:
- O que a marca representa no mundo real → como isso vira geometria, superfície, ritmo e nomenclatura.
- Vocabulário oficial do domínio (verbos de ação, rótulos de status, métricas reais).

### 4. Sistema Cromático `65 / 20 / 10 / 5` (Presença da Marca "Estou Aqui!" + Harmonia Multi-Cor)
- **65% Base Arquitetônica com Subtom Sutil (Nem Massa Monocromática, Nem Carvão Morto):**
  - **Dark Mode:** planos `Z0–Z3` em Obsidiana com subtom calibrado da marca (`S = 18%–26%`, ex.: `#080C12 → #0E131D → #141C29 → #1B2637`). Proibido saturar tudo no mesmo azul (`S > 36%` → `DA-DARK-MONOCHROME`) e proibido cinza puro sem identidade.
  - **Light Mode:** Porcelana/Alabastro aterrado (`Z0 #DCE3EC`, `Z1 #E6ECF3`, `Z2 #FFFFFF`, `Z3 #F3F6FA`) com **bordas nítidas** (`border-subtle >= 1.22:1` contra `Z2`, ex.: `#B4C1D1` e `#7A8CA3` → `DA-LIGHT-WASHED-OUT`).
- **20% Presença Estrutural da Marca (3 Zonas Fixas Obrigatórias):**
  1. **Identidade na Navegação:** cabeçalho institucional da Sidebar/Mobile (`.sidebar-brand-card`) + item ativo com cápsula `18% --primary` e filete `3px --accent`;
  2. **Card-Rei de cada Tela (`.card-brand-hero`):** gradiente direcional `135deg` com `20% --primary → --surface-z2` + borda `35% --primary` + chanfro especular;
  3. **Controles Ativos:** `.subtab.is-active`, `.seg-btn.is-active` e foco de tabela na cor primária.
- **10% Acento Complementar + Paleta Categórica Harmônica de 6 Cores (`--chart-1` a `--chart-6`):**
  - Acento quente/contrastante da marca no CTA Primário único + **6 tokens categóricos harmônicos em OKLCH** (`--chart-1` Azul Marca, `--chart-2` Teal/Oceano, `--chart-3` Índigo, `--chart-4` Laranja/Âmbar, `--chart-5` Esmeralda, `--chart-6` Coral/Rosa) para gráficos, barras de composição e setores nunca ficarem monocromáticos.
- **5% Cores Semânticas Puras:** `success` (esmeralda), `warning` (âmbar), `danger` (carmim/coral), `info` (azul técnico) — validados por `audit_contrast.py --strict` em **Light e Dark**.

### 5. Sistema de Profundidade & 5 Planos (`Z0 → Z4`)
Documente explicitamente os 5 planos físicos da interface nos dois temas:
- **`Z0` Poço / Recesso**: inputs em repouso, trilhos de tabs segmentadas, wells de tabelas.
- **`Z1` Canvas Base**: fundo geral do app/sistema onde os grupos respiram.
- **`Z2` Superfície Elevada (Cards / Painéis)**: Light Mode com contorno nítido + sombra-como-borda em 3 camadas; Dark Mode com luminosidade +8–12% sobre `Z1` + borda luminosa sutil superior.
- **`Z3` Superfície Flutuante**: popovers, dropdowns, command palette (`⌘K`), barras fixas de ação.
- **`Z4` Modal / Drawer / Sheet**: diálogos críticos, gavetas de detalhe, bottom sheets nativos.

### 6. Tipografia (Display · UI · Números Tabulares vs Mono Técnico)
- **Display & UI (`Operate`):** prefira sans-serif de precisão executiva (**`Geist`** ou **`Inter`**, ou **`IBM Plex Sans`**; `SF Pro` em iOS/macOS, `Roboto` em Android, `Segoe UI Variable` em Windows), com tracking `-0.02em` a `-0.03em` em headings, `text-wrap: balance/pretty` e `-webkit-font-smoothing: antialiased`.
- **Valores Financeiros & KPIs (`.num`):** usam a **própria sans-serif principal com `font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1`** (alinhamento perfeito em colunas sem os buracos largos da monoespaçada).
- **Mono Técnico (`.mono` — `Geist Mono` / `JetBrains Mono`):** restrito exclusivamente a códigos técnicos (CNPJ, linha digitável, IDs, protocolos, hashes, `<kbd> ⌘K`).

### 7. Escala Espacial (4/8px) & Raios Concêntricos
- Defina os tokens permitidos (`4, 8, 12, 16, 20, 24, 32, 40, 48, 64` + `2, 6, 10, 14` apenas internos de controles).
- Documente os pares de **raios concêntricos** usados no sistema (ex.: container `20px` + padding `8px` → filho `12px`; card `16px` + padding `8px` → botão/item interno `8px`).

### 8. Arsenal Open-Source de Elite & Mapeamento Categórico (`16 Categorias Canônicas`)
Rode **`scripts/discover_oss_components.py --scan <caminho-do-repositorio-ou-plano> --stack <stack> --platform <platform> --mode <mode>`** na Fase 2. Ele analisa o projeto automaticamente, ativa as categorias exatas entre as **16 Categorias Canônicas de UI/UX** (`ui_elements_recipes.json`) e entrega **bibliotecas permissivas (`MIT`/`Apache-2.0`/`ISC`) + Receitas de Micro-Componentes (`.icon-emblem`, `.chip-sla`, `.chip-status`, `BarList`, `Tracker`, `Combo HUD Chart`) + Curadoria de Ícones Específicos** prontos para esta seção!

Registre só o que for usado. Cada linha traz categoria, licença, uso e caminho completo (URL/comando/vendor local).

- **Gráficos & Telemetria:** TradingView Lightweight Charts, Apache ECharts (Combo HUD + Waterfall com conectores), ApexCharts.js, Tremor Raw (`BarList`, `Tracker`, `CategoryBar`), EvilCharts, Observable Plot, uPlot, Frappe Charts.
- **Ícones Vetoriais & Emblemas:** Tabler Icons (`5700+` SVGs `1.75px`), Solar Icons Duotone (`4800+` SVGs 2 camadas), Lucide, Heroicons Micro (`16px` p/ chips), Radix Icons (`15px`), Iconify (`<iconify-icon>`), SVGL.
- **Tabelas, Kanban, Formulários, Calendário & Chat:** Tabulator, TanStack Table, AG Grid Community, SortableJS, Atlassian Pragmatic DnD, coss ui, shadcn/ui, Kibo UI, Dice UI, IMask.js, Flatpickr, Tom Select, Uppy, FullCalendar Core, Frappe Gantt, Prompt Kit, Tiptap, Floating UI, AutoAnimate, tinykeys, Vaul, Konsta UI.
- **Mobile Nativo:** SwiftUI, Jetpack Compose Material 3, Flutter M3, `@gorhom/bottom-sheet`, FlashList, Zeego, Burnt.
- **Galerias (referência de fluxo, nunca copiar código):** Mobbin, Refero, Godly, Page Flows, Screenlane, Banani.

*Nota de sincronia (`v2.2.0`): sempre que atualizar `tokens.css` após a Onda 0.5, re-execute `render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css --out-dir .` — o script sincroniza automaticamente os hexes das tabelas do Markdown contra o `tokens.css` atual!*

### 9. Biblioteca de Componentes & Matriz de Estados
Defina regras exatas de:
- Botões (hierarquia: Primário único, Secundário elevado, Ghost, Destrutivo; alinhamento óptico `iconPad = textPad - 2px`; `active:scale-[0.97]`).
- Badges & Pills (somente com estado real; máx. 2 por item de lista).
- Tabelas, Inputs (sempre com `<label>` visível + erro inline + `:focus-visible`), Toasts com **Desfazer**.
- Estados obrigatórios: Loading (skeleton proporcional), Empty (diagnóstico + CTA), Error (causa + retry), Disabled, Foco.
- Motion: preencha o contrato do guia [10-motion-anti-slop.md](10-motion-anti-slop.md). Diga o que anima, o que fica quieto, e as durações de desktop, iOS e Android separadas. Uma curva CSS não serve para as três.

### 10. Arquitetura de Fluxos, tirada do trabalho real
A organização da tela repete a organização do trabalho que o planejamento e o repositório descrevem: a ordem das decisões, o que fica visível junto, o que é fila, o que é documento, o que é consulta.

Nomeie as zonas com a língua do projeto. "Agora / Em Rota / Radar" só vale quando o negócio de fato separa o dia assim. Uma agência de viagens pode organizar por reserva, embarque e pós-viagem. Um caixa pode organizar por vencido, a compensar e conciliado. Copiar o horizonte de outro projeto é molde, não leitura.

Antes de acrescentar um bloco, um botão ou um item de navegação, a tela ainda precisa responder a quatro perguntas: onde estou, para onde posso ir, o que posso fazer aqui, qual é o próximo passo. O que não serve a uma delas sai da tela ou vai para uma tela seguinte. A navegação usa poucos destinos, com o nome da tarefa, no lugar que a plataforma ensinou (tab bar, sidebar, rail). Vários botões primários no mesmo olhar são poluição, não atalho.

Mapeie o **fluxo de navegação completo**. Cada tela alcança a próxima e volta para onde o usuário estava. Uma jornada válida: inicial, tela específica, volta à inicial, outra específica, volta. Lista, detalhe e confirmação seguem o mesmo vai-e-volta. A vitrine em [08-canvas-figma-manifest.md](08-canvas-figma-manifest.md) desenha essas arestas. Tela solta, sem ida nem volta, não entra.

### 11. Mapa Completo de Telas & Dados Fictícios Coerentes
Tabela mestre com **todas** as telas que o produto precisa (`id`, `titulo`, `arquivo/rota`, `plataforma`, `viewport`, `modulo`, `acoes_principais`, `links_saida`), não só as que o planejamento listou. Perfil, configurações, sessão, notificação e automação entram quando alguém precisa governar conta, preferência ou rotina. Um sistema com logins e automações tem essas telas mesmo se o documento esqueceu. Um quiosque sem conta não ganha perfil para completar o mapa. Ao lado de cada tela extra, escreva o fato que a exigiu.

Inclua o bloco de **Dados Fictícios Oficiais** (nomes, valores, datas, empresas, contagens) alinhado ao planejamento. Todos os subagentes usam os mesmos valores.

### 12. Portões CDO de Aprovação
Critérios objetivos de saída ligados aos 10 Blocos e aos 3 scripts (`audit_contrast.py`, `lint_design_aura.py`, `capture_and_audit.mjs`).

---

## O papel da Bíblia (Bíblia Visual `v2.0`)

A Bíblia é um documento só, em duas faces, **com pranchas visuais reais renderizadas a partir de `tokens.css`**:

- **`DESIGN-BIBLE.md`** é o contrato literal que os subagentes executam (incluindo seção 8.1 de anatomia CSS e piso de riqueza/widgets por tela).
- **`DESIGN-BIBLE.html` e `DESIGN-BIBLE.pdf`** renderizam automaticamente **Pranchas Visuais de Espécimes** (Dark & Light `Z0–Z4`, swatches reais, tipografia, botões, badges semânticos e card `Z2`) antes das seções textuais — sem limite artificial de páginas e sem corte. O usuário enxerga o visual real antes de aprovar.

```bash
python3 <skill_dir>/scripts/render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css --out-dir .
```

Após a aprovação da Bíblia e construção das **Telas-Mãe (Onda 0.5)**, você pode re-gerar o PDF incorporando também as capturas reais das Telas-Mãe:

```bash
python3 <skill_dir>/scripts/render_design_bible.py DESIGN-BIBLE.md --tokens tokens.css --golden-desktop audit/desktop-mae-dark.png --golden-mobile audit/mobile-mae-dark.png --out-dir .
```

O PDF sai em A4 retrato com fundo limpo neutro, tipografia moderna de estúdio (sem viés de papel bege/serifa) e blocos ` ```html-specimen ` renderizados ao vivo quando presentes no Markdown.
