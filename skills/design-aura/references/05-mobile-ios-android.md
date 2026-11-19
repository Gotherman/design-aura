# Guia Mobile Nativo & Cross-Platform (iOS HIG · Android M3 · RN · Flutter · PWA)

Um aplicativo mobile falha imediatamente quando parece **um site espremido em tela pequena** ou **um app iOS fantasiado rodando no Android**. A regra central: respeite a física do polegar e as convenções do sistema operacional em que o usuário está segurando o telefone.

---

## 1. Ergonomia Universal Mobile (Obrigatória para Todos)

- **Safe Areas & Window Insets**: nenhum elemento interativo ou texto crítico pode invadir o notch, a Dynamic Island, a barra de status, o Home Indicator ou a área coberta pelo teclado virtual (IME).
- **Zona do Polegar (Thumb Zone)**:
  - **Ações primárias frequentes** ficam na metade inferior (Tab Bar / Bottom Sheet / botão fixo acima da safe-area inferior).
  - **Topo da tela** serve para título, contexto, filtro rápido ou ação secundária de saída/compartilhamento.
- **Alvos de toque**:
  - **iOS / Web Mobile / PWA**: mínimo absoluto **44×44px** (`44pt`). Se o ícone visual for `20px`, estenda a área clicável via `min-width/min-height: 44px` ou pseudo-elemento invisível.
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
  - **Compacto (Celular)**: `NavigationBar` inferior com `3 a 5` destinos.
  - **Expandido (Tablet / Foldable)**: migre para `NavigationRail` ou `NavigationDrawer` permanente — nunca estique uma barra inferior de celular por 1000px.
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
