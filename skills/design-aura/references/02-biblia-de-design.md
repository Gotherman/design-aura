# Bíblia de Direção de Design (`DESIGN-BIBLE.md`)

A **Bíblia de Design** é o contrato visual, ergonômico e estrutural criado pelo **Orquestrador na Onda 0** antes de qualquer tela ser construída ou delegada a subagentes. Ela garante que 100% das telas — sejam 3 ou 25, em Desktop, Web e Mobile — pareçam projetadas por uma única diretoria de design.

Use o template copiável em [assets/design-bible-template.md](../assets/design-bible-template.md).

---

## As 12 Seções Obrigatórias da Bíblia

### 1. Diagnóstico & Autópsia (ou Território do Problema)
- **Se houver sistema/app existente**: faça uma autópsia honesta apontando falhas reais (monocromia anestesiada, branco lavado sem contorno, 70% de vazio morto, fluxos passivos, falta de estados).
- **Se for projeto novo**: mapeie os erros típicos do setor que serão terminantemente proibidos desde o dia 1.
- Crave o compromisso de tolerância zero com os **10 Blocos de Leis Inegociáveis**.

### 2. Direção Criativa, Modo de Superfície & Assinatura Única
Classifique a superfície primária do produto:
- **`Operate`** (ERP, SaaS operacional, Fintech, DevTools, App de produtividade): o usuário veio executar trabalho. A estética empresta **apenas 4 coisas**: tipografia, paleta, densidade e **1 assinatura visual (*signature move*)**. Controles e navegação permanecem 100% familiares à plataforma.
- **`Read`** (documentação, relatórios, portal analítico, leitor): foco em medida tipográfica (65–75ch), ritmo vertical e clareza editorial.
- **`Persuade / Experience`** (landing page, vitrine de produto, onboarding de impacto): compromisso expressivo máximo sem sacrificar legibilidade ou velocidade.

Defina **1 assinatura visual concreta** enraizada no domínio (ex.: barra de cobertura financeira estilo *boarding pass*, linha temporal de rota logística, trilho de SLA em tempo real). Se a direção só muda cores, ainda não há assinatura.

### 3. DNA da Marca sem Clichês
Traduza a essência do negócio para **linguagem de UI** sem ilustrações literais ou infantilizadas:
- O que a marca representa no mundo real → como isso vira geometria, superfície, ritmo e nomenclatura.
- Vocabulário oficial do domínio (verbos de ação, rótulos de status, métricas reais).

### 4. Sistema Cromático (Regra 60 · 30 · 10) + Semântica Cirúrgica
- **60% Superfícies & Fundos**: Light Mode com canvas aterrado (nunca branco puro lavado) e Dark Mode com grafite/ardósia profundo de baixa fadiga (nunca `#000000` chapado sem elevação).
- **30% Estrutura & Autoridade**: barras de navegação, textos principais, contornos nítidos (`1.25px`), separadores.
- **10% Ação & Decisão**: cor primária reservada exclusivamente para o CTA dominante, foco e itens ativos.
- **Cores Semânticas**: `success` (esmeralda), `warning` (âmbar), `danger` (carmim/coral), `info` (azul técnico) — sempre em pares `bg-soft + border + fg` validados pelo `audit_contrast.py` em **Light e Dark**.

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
Consulte `scripts/design_intel.py` e registre os primitivos exatos para a stack escolhida (nunca invente componentes frágeis do zero quando existir primitivo acessível consolidado):
- Web/React: Radix / Base UI, shadcn/ui, TanStack Table, cmdk, Vaul, Sonner, Recharts/ECharts, Phosphor/Lucide.
- Desktop (Electron/Tauri): atalhos globais, painéis redimensionáveis, window frames nativos.
- Mobile (SwiftUI / Compose / RN / Flutter): componentes nativos da plataforma, `@gorhom/bottom-sheet`, `FlashList`, `Zeego`, `SF Symbols` / `Material Symbols`.

### 9. Biblioteca de Componentes & Matriz de Estados
Defina regras exatas de:
- Botões (hierarquia: Primário único, Secundário elevado, Ghost, Destrutivo; alinhamento óptico `iconPad = textPad - 2px`; `active:scale-[0.97]`).
- Badges & Pills (somente com estado real; máx. 2 por item de lista).
- Tabelas, Inputs (sempre com `<label>` visível + erro inline + `:focus-visible`), Toasts com **Desfazer**.
- Estados obrigatórios: Loading (skeleton proporcional), Empty (diagnóstico + CTA), Error (causa + retry), Disabled, Foco.

### 10. Arquitetura de Fluxos & Horizontes Temporais
Reestruture a operação do usuário em torno de velocidade cognitiva:
- **Agora (Intervenção Imediata)**: pendências críticas, aprovações, alertas vencidos.
- **Em Rota (Próximos passos / 7 dias)**: fila programada, vencimentos, revisões.
- **Radar / Observabilidade**: indicadores de tendência, saúde de integrações, histórico.
- Mapeie o **fluxo de navegação completo** (entrada → painel central → módulos → mobile/detalhe → volta).

### 11. Mapa Completo de Telas & Dados Fictícios Coerentes
Tabela mestre com **todas** as telas que existem no projeto (`id`, `titulo`, `arquivo/rota`, `plataforma`, `viewport`, `modulo`, `acoes_principais`, `links_saida`) + bloco de **Dados Fictícios Oficiais** (nomes de pessoas, valores, datas, empresas, contagens) que TODOS os subagentes devem usar identicamente para que o sistema pareça vivo e integrado.

### 12. Portões CDO de Aprovação
Critérios objetivos de saída ligados aos 10 Blocos e aos 3 scripts (`audit_contrast.py`, `lint_design_aura.py`, `capture_and_audit.mjs`).

---

## Bíblia Visual Executiva (HTML → PDF Opcional)

Quando o projeto exigir apresentação visual para cliente, diretoria ou handoff de estúdio (como em propostas de sistema):
1. Copie e preencha [assets/biblia-visual-template.html](../assets/biblia-visual-template.html) usando os tokens reais do `tokens.css`.
2. Gere o PDF em A4 paisagem via Chromium headless:
   ```bash
   google-chrome --headless=new --disable-gpu --no-sandbox --print-to-pdf=Biblia-Direcao-Design.pdf --no-pdf-header-footer biblia-visual.html
   ```
3. Inspecione todas as páginas geradas garantindo zero corte de prancha e contraste legível.
