# Guia Mobile Nativo & Cross-Platform (iOS HIG · Android M3 · RN · Flutter · PWA)

Um aplicativo mobile falha imediatamente quando parece **um site espremido em tela pequena** ou **um app iOS fantasiado rodando no Android**. A regra central: respeite a física do polegar e as convenções do sistema operacional em que o usuário está segurando o telefone. Cor, tipo, espaço e ícone podem ser os do sistema desktop irmão. Navegação, densidade e overlay, não. O shell largo está no guia [04-desktop-e-sistemas.md](04-desktop-e-sistemas.md).

---

## 1. Ergonomia Universal Mobile (Obrigatória para Todos)

- **Safe Areas & Window Insets**: nenhum controle ou texto crítico invade a status bar, a Dynamic Island, o notch, o home indicator ou o teclado. O conteúdo pode rolar por baixo das barras, edge-to-edge. O que a pessoa precisa tocar fica dentro da área segura.
- **Zona do Polegar (Thumb Zone)**:
  - **Ações primárias e a navegação principal** ficam no terço inferior (Tab Bar, bottom navigation, sheet, botão fixo acima da safe area).
  - **Topo da tela** serve para título, contexto, filtro rápido ou ação secundária de saída/compartilhamento.
- **Uma tarefa principal por tela.** Tabela densa horizontal vira lista agrupada ou cards empilhados, com a hierarquia do registro preservada. O desktop é que fica com a grade. A pessoa aponta a tab bar, a ação e o próximo passo sem caçar. Botões do mesmo peso espalhados pela tela são poluição.
- **Alvos de toque**:
  - **iOS / Web Mobile / PWA**: mínimo absoluto **44×44px** (`44pt`), com pelo menos **8px** entre alvos vizinhos. Se o ícone visual for `20px`, estenda a área clicável via `min-width/min-height: 44px` ou pseudo-elemento invisível.
  - **Android**: mínimo **48×48dp** com pelo menos **8dp** de espaçamento entre alvos vizinhos.
- **Zero scroll aninhado acidental**: não coloque listas longas com scroll interno dentro de uma página que já rola verticalmente sem delimitação explícita. Em Web/PWA mobile, use `100dvh` em vez de `100vh` rígido.
- **Feedback háptico e visual imediato**: todo toque precisa reagir (`active:scale-[0.97]` ou ripple/opacity nativa). Nunca dependa de `:hover` em mobile.

---

## 2. iOS (SwiftUI · UIKit · React Native iOS · Flutter Cupertino)

### Teste de Qualidade iOS
Um usuário fluente de iPhone confiaria neste app na primeira abertura? Os erros clássicos de IA no iOS são barras de navegação web customizadas, botão "Voltar" que quebra o gesto de deslizar na borda esquerda, e cards genéricos empilhados no lugar de listas nativas agrupadas.

### Regras iOS HIG
- **Navegação**:
  - **Tab Bar inferior**: `2 a 5` seções principais (sempre destinos, nunca botões de ação avulsa). Em iOS 18+/26, aproveite a fluidez do sistema sem reinventar pílulas flutuantes quebradas.
  - **Navigation Stack + Edge-Swipe Back**: preserve sempre o gesto de arrastar da borda esquerda para voltar.
  - **Large Titles** nas telas de topo que colapsam para título inline durante a rolagem; telas internas de detalhe começam inline.
- **Tipografia & Dynamic Type**:
  - Use estilos semânticos do sistema (`Large Title`, `Title 1–3`, `Headline`, `Body 17pt`, `Subheadline`, `Footnote`, `Caption 11pt floor`). Nunca trave alturas de linha/caixas que cortam texto quando o usuário aumenta a fonte do iPhone.
  - **SF Pro / SF Compact** para UI; fonte da marca apenas em momentos Display pontuais.
  - **SF Symbols** como família de ícones nativa com peso alinhado à tipografia.
- **Cores & Materiais**:
  - Cores semânticas adaptativas (`label`, `secondaryLabel`, `systemBackground`, `secondarySystemGroupedBackground`, `separator`, `tint`).
  - **1 cor de tintagem (`tint`)** conduz as ações interativas.
  - **Liquid Glass e materiais do sistema** ficam nas superfícies que o UIKit/SwiftUI já desenham. Não recrie o vidro em CSS para "parecer iPhone" num WebView ou no Android.
  - **Grouped Inset Lists** (`insetGrouped`) para menus, ajustes e detalhes de registro — muito superiores a inventar card solto sobre card solto.
  - **Sheets (detents `.medium`, `.large`)** para sub-tarefas focadas e dispensáveis por arrasto; `fullScreenCover` apenas para imersão/edição longa com `Cancelar` e `Concluir` claros.
- **Verificação em Simulator**:
  - Testar explicitamente em **Dark Mode** e **Dynamic Type grande**.
  - Captura via `xcrun simctl` / `device_screenshot` do ambiente.

---

## 3. Android (Jetpack Compose · Views · React Native Android · Flutter M3)

### Teste de Qualidade Android
O erro clássico de IA no Android é copiar um iPhone (switches estilo Cupertino, setas centradas sem gesto de volta preditivo, bottom bar idêntica em tablet).

### Regras Material Design 3
- **Navegação Adaptativa por Tamanho**:
  - **Compacto (Celular)**: `NavigationBar` inferior com `3 a 5` destinos. A toolbar flutuante do Material 3 Expressive substitui a barra quando o guia atual da plataforma pede isso. Não empilhe as duas.
  - **Expandido (Tablet / Foldable)**: migre para `NavigationRail` ou `NavigationDrawer` permanente — nunca estique uma barra inferior de celular por 1000px.
  - **Expressive** (forma e movimento mais soltos) cabe em superfície de marca. Em Operate, o scheme padrão e a navegação adaptativa vencem o efeito.
- **Predictive Back & Insets**:
  - Respeite sempre o botão/gesto Back do sistema; nunca prenda o usuário nem bloqueie a animação de retorno preditivo.
  - **Edge-to-Edge**: trate `statusBars`, `navigationBars`, `displayCutout` e `imePadding()` para o teclado nunca cobrir inputs ou botões de envio.
- **Ações & Componentes M3**:
  - **Máximo 1 FAB (Floating Action Button)** por tela para a única ação primária dominante. Nunca empilhe múltiplos FABs.
  - **Snackbars** (com botão de ação/Desfazer quando aplicável) para feedback transitório; `ModalBottomSheet` para seleção/detalhe contextual; `AlertDialog` apenas para decisão bloqueante.
- **Tipografia & Cor M3**:
  - Use `sp` (nunca `px`/`dp` fixo para texto) respeitando a escala M3 (`Display`, `Headline`, `Title`, `Body`, `Label`).
  - Use **Color Roles** (`primary`, `onPrimary`, `surface`, `surfaceContainerLow/High`, `outlineVariant`, `error`) e **Tonal Elevation** — em Dark Mode a elevação muda o tom da superfície, nunca apenas sombra preta.
  - Suporte **Dynamic Color (Material You)** no Android 12+ quando aplicável com fallback fiel da marca.
- **Verificação em Emulador**:
  - Testar `uimode night yes` e `font_scale 1.3` para garantir zero texto truncado ou sobreposto.

---

## 4. Cross-Platform & PWA (React Native / Expo · Flutter · Web Mobile)

| Stack | Como manter fidelidade nativa sem duplicar trabalho |
|---|---|
| **React Native / Expo** | Use menus nativos (`Zeego`), sheets com gestos físicos (`@gorhom/bottom-sheet`), listas virtualizadas (`FlashList`), animações na UI thread (`react-native-reanimated`) e `react-native-safe-area-context`. Adapte `Header` e ícones por `Platform.OS` (`SF Symbols` / `Material Symbols`). |
| **Flutter** | Use `ThemeData(useMaterial3: true)` com `ColorScheme` em roles reais; adote widgets `.adaptive` (`Switch.adaptive`, diálogos adaptativos) e respeite `MediaQuery.padding` / `SafeArea` + `NavigationBar` vs `NavigationRail` via `LayoutBuilder`. |
| **Mobile Web / PWA / Showcase iPhone** | Aplique `env(safe-area-inset-top/bottom)`, `100dvh`, `touch-action: manipulation` (remove delay de 300ms), `overscroll-behavior: contain` em sheets, `-webkit-tap-highlight-color: transparent` com feedback próprio `active:scale-[0.97]` e simulação limpa de Bottom Sheet (ex.: `Vaul`) com fechar por arrasto e `Esc`. |

---

## 5. Orçamento de Topo Mobile & Primeira Dobra (`DA-MOBILE-HERO-BLOAT` · `v2.4.0`)

Em apps operacionais mobile (`390×844`), a pessoa abriu o celular para **agir na lista de trabalho** (escolas, entregas, pendências), não para ler dois banners gigantes antes de rolar:
- **Teto rígido de topo (`<= 38%` / `<= 320px`):** o conjunto **Header + Hero/Resumo + Aviso da Mesa** nunca pode consumir mais de `38%` da altura útil da viewport.
- **Lista acionável acima da dobra:** o primeiro item real da lista principal precisa aparecer claramente visível sem obrigar rolagem (`y < 480px`), com alertas secundários condensados em 1 linha expansível ou dispensável (`Entendi`).
- **Zero selo-eco em listas estreitas (`DA-BADGE-ECHO`):** nunca repita o mesmo selo genérico (ex.: `8× PWA Mobile`) roubando largura e truncando nomes de pessoas ou unidades.

---

## 6. Blindagem contra Corte de Dados e Vazamento de Mockup Mobile (`DA-CLIPPED-CONTENT` & `DA-MOBILE-FLEX-CLIP`)

Dois erros técnicos clássicos destroem protótipos mobile quando abertos no desktop (`preview.html` ou visualização em moldura de aparelho):

1. **PROIBIDO esmagamento de cards por `flex-shrink: 1` (`DA-MOBILE-FLEX-CLIP`):**
   - Em containers roláveis verticais (`.mob-scroll`, `.sheet-panel`, `main` mobile), se você usar `display: flex; flex-direction: column; overflow-y: auto;` e colocar cards filhos com `overflow: hidden` (para arredondar bordas), o Flexbox do navegador **encolhe todos os cards verticalmente para caberem sem scroll**, cortando números e textos pela metade!
   - **Solução obrigatória (escolha uma):**
     ```css
     /* Opção A (recomendada): grid auto-rows nunca esmaga filhos */
     .mob-scroll {
       flex: 1;
       overflow-y: auto;
       display: grid;
       grid-auto-rows: max-content;
       align-content: start;
       gap: var(--space-4);
     }

     /* Opção B: se usar flex-column, trave flex-shrink: 0 em TODOS os filhos diretos */
     .mob-scroll > * {
       flex-shrink: 0;
     }
     ```
2. **PROIBIDO canto quadrado vazando fora do bezel arredondado do mockup:**
   - No Chromium, um cabeçalho `position: sticky` com `backdrop-filter: blur(...)` dentro de um container arredondado (`border-radius: 40px`) ou de um `<iframe>` pelado vaza cantos de 90° por cima da borda curva!
   - **Solução obrigatória:** aplique no container `.mob-device` (desktop showcase) e no wrapper `.pv-frame-wrap.is-mobile` do iframe:
     ```css
     .mob-device, .pv-frame-wrap.is-mobile {
       overflow: hidden;
       border-radius: 40px;
       clip-path: inset(0 round 32px);
       isolation: isolate;
       transform: translateZ(0);
     }
     ```
   - E valide sempre no Chromium com `capture_and_audit.mjs` (que bloqueia automaticamente via `DA-CLIPPED-CONTENT` e `DA-MOBILE-FLEX-CLIP`).
