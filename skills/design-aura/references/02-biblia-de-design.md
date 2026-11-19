# Bíblia de Direção de Design (`DESIGN-BIBLE.md`)

A **Bíblia de Design** é o contrato visual, ergonômico e estrutural criado pelo **Orquestrador na Onda 0** antes de qualquer tela ser construída ou delegada a subagentes. Ela garante que 100% das telas — sejam 3 ou 25, em Desktop, Web e Mobile — pareçam projetadas por uma única diretoria de design.

Use o template copiável em [assets/design-bible-template.md](../assets/design-bible-template.md).

O primeiro bloco do arquivo, antes das 12 seções, é o **Contrato de plataforma**: trabalho (remodelar, completar ou criar), tipo de produto, superfícies, qual é a principal, stack, tema, uso das cores da marca, sinal do domínio, modelo do Orquestrador, modelo dos subagentes, como o trabalho se organiza e o que o projeto recusa do molde do catálogo. Também lista as hipóteses que não foram confirmadas. Cor, tipo e tela só começam depois desse bloco. Um subagente que não leu o contrato não escolhe shell nem recupera a cara antiga numa remodelação.

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

### 4. Sistema Cromático (Regra 60 · 30 · 10) + Semântica Cirúrgica
- **60% Superfícies & Fundos**: Light Mode com canvas aterrado (nunca branco puro lavado) e Dark Mode com grafite/ardósia profundo de baixa fadiga (nunca `#000000` chapado sem elevação).
- **30% Estrutura & Autoridade**: barras de navegação, textos principais, contornos nítidos (`1.25px`), separadores.
- **10% Ação & Decisão**: cor primária reservada exclusivamente para o CTA dominante, foco e itens ativos.
- **Cores Semânticas**: `success` (esmeralda), `warning` (âmbar), `danger` (carmim/coral), `info` (azul técnico) — sempre em pares `bg-soft + border + fg` validados pelo `audit_contrast.py` em **Light e Dark**.
- **Cores da marca, quando a Fase 1 autorizou:** elas ocupam os 10% de ação e podem tintar a estrutura. Os 60% de superfície e os neutros de texto continuam uma família própria, com contraste real. Sucesso, alerta, erro e informação não são o azul da marca clareado e escurecido. Paleta de uma cor só é falha, não fidelidade.

### 5. Sistema de Profundidade & 5 Planos (`Z0 → Z4`)
Documente explicitamente os 5 planos físicos da interface nos dois temas:
- **`Z0` Poço / Recesso**: inputs em repouso, trilhos de tabs segmentadas, wells de tabelas.
- **`Z1` Canvas Base**: fundo geral do app/sistema onde os grupos respiram.
- **`Z2` Superfície Elevada (Cards / Painéis)**: Light Mode com contorno nítido + sombra-como-borda em 3 camadas; Dark Mode com luminosidade +8–12% sobre `Z1` + borda luminosa sutil superior.
- **`Z3` Superfície Flutuante**: popovers, dropdowns, command palette (`⌘K`), barras fixas de ação.
- **`Z4` Modal / Drawer / Sheet**: diálogos críticos, gavetas de detalhe, bottom sheets nativos.

### 6. Tipografia (Display · UI · Telemetria)
- **Display**: fonte com presença para títulos e métricas hero (tracking fechado `-0.02em` a `-0.03em`, `text-wrap: balance`).
- **UI / Corpo**: máxima legibilidade em densidades médias/altas (`>= 14px`, `text-wrap: pretty`, `-webkit-font-smoothing: antialiased`).
- **Mono / Telemetria**: códigos, IDs, valores financeiros e timers com `font-variant-numeric: tabular-nums`.
- **Nativo**: especifique quando usar `SF Pro` (iOS/macOS), `Roboto` (Android) ou `Segoe UI Variable` (Windows).

### 7. Escala Espacial (4/8px) & Raios Concêntricos
- Defina os tokens permitidos (`4, 8, 12, 16, 20, 24, 32, 40, 48, 64` + `2, 6, 10, 14` apenas internos de controles).
- Documente os pares de **raios concêntricos** usados no sistema (ex.: container `20px` + padding `8px` → filho `12px`; card `16px` + padding `8px` → botão/item interno `8px`).

### 8. Arsenal Open-Source de Elite
Rode `scripts/discover_oss_components.py` com a interação real, a stack e o modo de superfície. O procedimento e a diferença entre registry, galeria e licença própria estão em [09-pesquisa-componentes-oss.md](09-pesquisa-componentes-oss.md).

Registre só o que for usado. Cada linha traz licença, uso e caminho completo: URL, comando de instalação e o arquivo no projeto depois de copiado. Sem caminho, a peça não entra na Bíblia.

- Web/React: shadcn/ui, coss ui, Kibo UI, Dice UI, Base UI, TanStack Table, cmdk.
- Desktop: Dockview ou `react-resizable-panels`, mais o frame nativo da janela.
- Mobile: SwiftUI e Material 3 primeiro; depois React Native Reusables, gluestack, `@gorhom/bottom-sheet`, FlashList, Forui ou `shadcn_ui` conforme a stack.
- Galerias (Mobbin, Refero, Godly, Page Flows, Screenlane) entram como referência de fluxo, nunca como código.

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

## O papel da Bíblia

A Bíblia é um documento só, em duas faces do mesmo texto:

- **`DESIGN-BIBLE.md`** é o que o subagente executa. Títulos, tabelas e caminhos ficam literais.
- **`DESIGN-BIBLE.html` e `DESIGN-BIBLE.pdf`** são o papel para leitura humana. Não há número máximo de páginas. O conteúdo manda. Seção longa continua na página seguinte. Nada fica escondido por altura fixa.

```bash
python3 <skill_dir>/scripts/render_design_bible.py DESIGN-BIBLE.md --out-dir .
```

O PDF sai em A4 retrato, com margem, título que não fica órfão e tabela que não parte no meio. Se não houver Chromium, o HTML já imprime do mesmo jeito.

A seção 8 lista cada componente, card ou elemento escolhido fora do projeto, com licença, uso e **caminho**: URL, comando de instalação e o arquivo no repositório depois de copiado. Sem essa linha, o subagente não adota a peça.

As pranchas de [assets/biblia-visual-template.html](../assets/biblia-visual-template.html) são um resumo de uma página por tema, opcional e fácil de cortar. Elas não substituem este papel.
