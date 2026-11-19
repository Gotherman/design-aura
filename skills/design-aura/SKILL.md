---
name: design-aura
description: >-
  Diretor de design e engenharia UI/UX de classe mundial para apps Desktop (Electron, Tauri, macOS, Windows), Mobile (iOS HIG/SwiftUI, Android Material 3/Compose, React Native/Expo, Flutter, PWA) e Sistemas Web/SaaS/ERPs/Dashboards. Use sempre que o usuario pedir para planejar, especificar, desenhar, criar, revisar ou remodelar o visual de interfaces e telas já existentes, fluxos, design systems, tokens ou prototipos navegaveis, aplicar anti-AI-slop, garantir alto contraste otico, micro-craft e acessibilidade WCAG/APCA, procurar componentes free/open source que caibam na interface, ou definir animacoes com vida para desktop, iOS e Android. Tambem use para ler um repositorio ou planejamento e transformar isso em uma Biblia de Design propria daquele projeto, com construcao fiel orquestrada por ate 8 subagentes e vitrine estilo Figma (fluxo.html, preview.html, index.html).
license: MIT
compatibility: >-
  Python 3.9+ (stdlib) e Node.js 20+ com Chromium/Chrome opcional para captura e auditoria visual headless.
metadata:
  version: "1.1.10"
  author: "Lucas (Gotherman)"
  display-name: "Design Aura"
---

# Design Aura

Sistema completo de direção criativa, arquitetura de UI/UX, engenharia visual e orquestração multi-agente para produzir **sistemas web operacionais, apps desktop e aplicativos mobile** com nível de estúdio premiado — zero estética genérica de IA, contraste irretocável, ergonomia nativa e verificação visual real.

## Ponto de partida universal

Leia o repositório e o planejamento por completo antes de desenhar: concepção, PRD, proposta, rotas, telas, tokens, componentes, logo e o vocabulário real do negócio. Cada projeto ganha um design saído desse material. Uma agência de viagens e um caixa de banco não compartilham a mesma pele.

1. **Repositório que já tem design e telas.** Dois caminhos, e eles não se misturam:
   - **Remodelar o visual:** o pedido, e principalmente `/designaura`, já diz que as telas atuais não servem. Leia-as só para extrair tarefas, dados e o que falhou. Não baseie layout, navegação, botões nem composição nelas. Mantenha rotas, tarefas e dados reais. A estrutura nova sai do fluxo de trabalho do projeto e das regras da skill.
   - **Ajuste pontual:** altere só o que foi pedido e preserve o que já funciona.
2. **Planejamento sem telas** (`CONCEPCAO.md`, PRD, requisitos, proposta): extraia domínio, perfis, módulos, fluxos e restrições já decididas.
3. **Ideia do zero:** conduza a especificação enxuta antes de gerar código ou telas.

Regra absoluta: **nunca invente dados de negócio, diferenciais ou métricas.** Demonstração usa dados fictícios coerentes com o que o planejamento descreve, e os mesmos valores em todas as telas.

---

## Fluxo End-to-End (4 Fases · 3 Ondas)

### Fase 1 — Especificação Enxuta
Antes de paleta, tipografia ou layout, leia o pedido, o repositório e os documentos. Pergunte só o que ainda muda o shell, a stack ou a Bíblia. Não há teto: se faltam seis decisões, pergunte as seis de uma vez. Se falta uma, pergunte uma. Não pergunte gosto, nome de fonte nem o que o pedido já respondeu. Em cada pergunta, marque uma opção recomendada.

Pule a linha inteira quando a resposta já existe:

1. **Trabalho:** remodelar o visual do que já existe, completar em cima do que há, ou criar do zero.
2. **Tipo de produto:** sistema de trabalho diário (ERP, operação, backoffice), SaaS, app, ou uma combinação. Isso escolhe `Operate`, `Read` ou `Persuade`.
3. **Superfícies:** web, desktop nativo, mobile, ou quais juntas. Se houver mais de uma, qual é a principal.
4. **Mobile, só se essa superfície existir:** iOS, Android ou os dois. Entrega nativa (SwiftUI e/ou Compose), compartilhada (React Native/Expo ou Flutter) ou PWA.
5. **Desktop nativo, só se existir:** macOS, Windows ou os dois. Electron, Tauri ou nativo do sistema.
6. **Web, só se existir:** só o desktop largo, ou também o mobile web.
7. **Quem usa e a tarefa de um segundo:** o perfil e a decisão que a tela principal precisa resolver.
8. **Tema:** light-first, dark-first, ou os dois obrigatórios.
9. **Cores da marca:** usar a paleta oficial como base? Recomendado **sim** quando logo ou paleta existem. Se a resposta for sim, a cor da marca conduz a ação e pode tintar a estrutura. Fundos, neutros e cores semânticas não são variações da mesma tinta. Interface monocromática reprova.
10. **Sinal do domínio:** o planejamento traz um fato visual. Exemplo: a Brasitur é agência de turismo e viagens, o que sustenta céu, rota e horizonte. Pergunte se esse fato vira um sinal no visual. Recomendado **sim** quando cabe num gesto só. Recomendado **não** quando viraria ilustração repetida. Sem o sim, não desenhe avião, nuvem nem paisagem. Com o sim, um sinal contido. Vários, não.

**Regra-mãe, antes de qualquer layout:** tokens (cor, tipo, espaçamento, elevação, ícone) atravessam as superfícies. Navegação, densidade, alvo de entrada e overlay mudam. Espremer um desktop em colunas estreitas, ou esticar um celular até sobrar vazio, reprova. O shell de cada uma está em [04-desktop-e-sistemas.md](references/04-desktop-e-sistemas.md) e [05-mobile-ios-android.md](references/05-mobile-ios-android.md).

**A estrutura visual sai do trabalho deste projeto**, lido no planejamento e no repositório: quem faz o quê, em que ordem, o que fica aberto ao mesmo tempo e como a pessoa volta. Dois projetos só ficam parecidos se esses fatos forem parecidos. Parecer com o exemplo da skill, com o primeiro arquétipo da lista ou com a ficha do catálogo não é decisão.

**Anti-poluição.** Cada tela responde, sem esforço, a quatro perguntas: onde estou, para onde posso ir, o que posso fazer aqui, qual é o próximo passo. Informação junta, botão competindo com botão e navegação sem nome claro reprovam. Densidade de trabalho é bem-vinda quando está agrupada. Esconder a ação principal para "limpar" a tela também reprova.

Grave as respostas no **Contrato de plataforma**, no topo da `DESIGN-BIBLE.md`, antes de cor e de tela. O que você assumiu entra marcado como hipótese.

Se o pedido já fechou todas as linhas, não abra entrevista: escreva o contrato com o que foi dito e avance.

---

### Fase 2 — Modelagem da Bíblia de Design (Onda 0 · Orquestrador)
Antes de delegar ou codar qualquer tela, o Orquestrador cria o **Contrato Único de Verdade**:

1. **Pesquisa de inteligência de design (offline, determinística)**:
   ```bash
   python3 <skill_dir>/scripts/design_intel.py "<domínio e objetivo>" --platform <desktop|mobile|system|all> --stack <stack> --format markdown
   ```
   A saída é hipótese. Paleta, arquétipo e assinatura do catálogo só entram na Bíblia se combinam com o fluxo de trabalho já lido. Antes de travar, escreva no contrato o que este projeto recusa do molde: outro arquétipo quando a tarefa não for fila mais documento mais telemetria, outra organização do tempo quando "Agora / Em Rota / Radar" não for a língua do negócio, outra paleta quando a marca não for a cor da ficha.
   *(Opcional: se o servidor MCP Uizze estiver conectado e houver dúvida concreta de composição/fluxo, consulte-o como evidência complementar; nunca dependa dele.)*

   Para cada interação que o projeto realmente precisa (tabela editável, sheet, command palette, gantt), rode o caçador antes de escolher biblioteca:

   ```bash
   python3 <skill_dir>/scripts/discover_oss_components.py --need "<interação>" --stack <stack> --platform <desktop|mobile|system|ios|android> --mode <operate|read|persuade>
   ```

   Use `--online` quando houver rede. Galerias (Mobbin, Refero, Godly, Page Flows) são referência visual. Código só entra com licença MIT, Apache-2.0, BSD ou ISC, re-tematizado pela Bíblia. O contrato de animação (o que pode mover, e a diferença entre desktop, iOS e Android) fica no guia 10 e na seção 9 da Bíblia.

2. **Ler as referências obrigatórias do escopo**:
   - Sempre: [01-leis-inegociaveis.md](references/01-leis-inegociaveis.md) e [02-biblia-de-design.md](references/02-biblia-de-design.md).
   - Desktop / Sistemas / ERPs: [04-desktop-e-sistemas.md](references/04-desktop-e-sistemas.md).
   - Mobile iOS / Android / Cross-platform: [05-mobile-ios-android.md](references/05-mobile-ios-android.md).
   - Micro-craft e Motion: [06-micro-craft-e-motion.md](references/06-micro-craft-e-motion.md) e [10-motion-anti-slop.md](references/10-motion-anti-slop.md).
   - Componentes free/OSS: [09-pesquisa-componentes-oss.md](references/09-pesquisa-componentes-oss.md).

3. **Gerar os 4 artefatos fundacionais (nesta ordem)**:
   - **`DESIGN-BIBLE.md`** (use [assets/design-bible-template.md](assets/design-bible-template.md)): comece pelo Contrato de plataforma. Depois diagnóstico, modo de superfície, assinatura, cor, tipo, espaço, arsenal com caminho de cada componente, motion, estados, fluxo do trabalho e mapa de telas. Em seguida gere o papel, sem limite de páginas:
     ```bash
     python3 <skill_dir>/scripts/render_design_bible.py DESIGN-BIBLE.md --out-dir .
     ```
     O Markdown é a cópia que o subagente executa. O HTML e o PDF são a mesma Bíblia para leitura. A seção 8 traz URL, comando e caminho de arquivo de cada peça open source adotada.
   - **`tokens.json` → `tokens.css`**: modele com base em [assets/tokens.example.json](assets/tokens.example.json) e compile:
     ```bash
     python3 <skill_dir>/scripts/generate_tokens.py tokens.json --out tokens.css --format all --check-contrast
     python3 <skill_dir>/scripts/audit_contrast.py tokens.css --strict
     ```
     **Portão 0**: não avance com `tokens.css` se `audit_contrast.py --strict` falhar.
   - **Shell / Primitivos compartilhados**: header/sidebar/dock, tema switcher (`data-theme`), tipografia base, botões, badges, tabelas, drawers/sheets e toast com Desfazer.
   - **`screen-manifest.json`** (contrato em [08-canvas-figma-manifest.md](references/08-canvas-figma-manifest.md)): liste **100% das telas necessárias**, inclusive perfil e configurações quando o produto tem conta, sessão, preferência ou automação para governar, mesmo que o planejamento tenha esquecido. Inclua seções, viewports, arestas de ida e volta e jornadas que atravessam o fluxo de verdade (inicial, específica, volta, outra específica).
   - As pranchas de [assets/biblia-visual-template.html](assets/biblia-visual-template.html) são resumo opcional. Não substituem o PDF da Bíblia.

4. **Pare para aprovação.** Entregue o caminho de `DESIGN-BIBLE.pdf` e de `DESIGN-BIBLE.md`, com um resumo curto: superfícies, o que foi recusado do molde, a assinatura e a lista de telas. Não construa shell, telas nem vitrine. Não chame subagente construtor. A Fase 3 só começa quando a pessoa aprovar com clareza ("aprovado", "pode construir", "segue"). Se pedir ajuste, revise a Bíblia, gere o PDF de novo e pare outra vez.

---

### Fase 3 — Orquestração & Construção Fiel (Onda 1 · Máximo 8 Subagentes)

Só depois da aprovação da Bíblia.
Consulte [03-orquestracao-subagentes.md](references/03-orquestracao-subagentes.md) para dimensionar e delegar sem drift visual:

- **Limite rígido:** **nunca ultrapasse 8 subagentes** no projeto (ideal: `1` a `7` construtores em paralelo + `1` auditor visual na Onda 2).
- **Dimensionamento:**
  - `1–3` telas ou ajuste pontual: faça diretamente (0 subagentes) ou use no máximo 1–2.
  - `4–10` telas: fatiar em `2–4` subagentes por módulo/plataforma + `1` auditor.
  - `11–24+` telas multi-plataforma: até `7` subagentes construtores agrupados por módulo/camada + `1` auditor = **8 no total**.
- **Regra de isolamento de contexto:** passe a cada subagente **apenas**:
  1. Seu slice exato do `screen-manifest.json` (IDs, nomes de arquivo/rota, links de entrada e saída).
  2. Os trechos aplicáveis de `DESIGN-BIBLE.md` + caminho para `tokens.css` / shell compartilhado.
  3. O resumo dos **10 Blocos de Leis Inegociáveis**.
  4. Os dados fictícios compartilhados entre telas para zero divergência de números, nomes ou status.
- **Reconciliação antes da Vitrine:** confira no disco que **100% das telas do `screen-manifest.json`** foram criadas e que nenhum link inter-módulo aponta para rota inexistente.

---

### Fase 4 — Vitrine Estilo Figma + Auditoria Automática & Visual Real (Onda 2)
1. **Gerar a vitrine interativa estilo Figma** ([08-canvas-figma-manifest.md](references/08-canvas-figma-manifest.md)):
   ```bash
   python3 <skill_dir>/scripts/build_figma_canvas.py screen-manifest.json --tokens tokens.css --out <dir_telas> --verify-files
   ```
   Entrega automaticamente:
   - `fluxo.html`: canvas infinito estilo Figma (pan, zoom, seções por módulo/plataforma, previews ao vivo em iframe, setas Bézier clicáveis, modo isolar conexões, inspetor de saltos, minimapa e preview modal).
   - `preview.html`: player guiado de uso real por jornada/persona com detecção automática de navegação dentro das telas e dock recolhível.
   - `index.html`: galeria de telas filtrável por módulo com busca instantânea `⌘K` / `Ctrl+K`.

2. **Executar os 3 portões objetivos de auditoria** ([07-auditoria-e-veredito.md](references/07-auditoria-e-veredito.md)):
   ```bash
   python3 <skill_dir>/scripts/audit_contrast.py tokens.css --strict
   python3 <skill_dir>/scripts/lint_design_aura.py <dir_projeto> --strict
   node <skill_dir>/scripts/capture_and_audit.mjs --manifest screen-manifest.json --out <dir_audit> --viewports desktop,mobile --themes dark,light --strict
   ```

3. **Inspeção visual real e fechamento**:
   - Abra os screenshots gerados em `<dir_audit>` (1440×900 e 390×844, Dark e Light) para inspecionar alinhamento, espaçamento, legibilidade, ausência de espaços mortos e fidelidade à Bíblia.
   - Corrija todos os itens `BLOCK` e `HIGH` em lote, re-execute os validadores e só entregue com veredito **`Approve`**.

---

## Os 10 Blocos de Leis Inegociáveis (Resumo Executivo)

Qualquer violação abaixo **reprova automaticamente** na auditoria (`BLOCK`). Detalhes completos e regras automatizadas em [01-leis-inegociaveis.md](references/01-leis-inegociaveis.md):

1. **Zero Estética "SaaS de IA Genérico"**: proibido gradientes roxo/índigo/neon gratuitos, glow/glass decorativo, emojis clichês (`✨🚀⚡🛡️`) como ícones, mistura de estilos/traços de ícones, eyebrows decorativos, numeração `01 //`, gradiente em texto, barrinha lateral em card e dots/badges `LIVE` sem estado real.
2. **Hierarquia, Layout & Anti-Cardite**: proibido "cardite aguda" e card dentro de card; proibido repetir "3 cards iguais de ícone em círculo + título + 2 linhas"; proibido centralizar textos longos/listas; respeitar Lei da Proximidade; 1 CTA primário dominante por dobra; navegação nomeada e no lugar da plataforma; a tela responde onde estou, para onde vou e o que posso fazer; Alto Contraste Ótico com 5 planos `Z0→Z4` e zero espaços mortos em desktop.
3. **Contraste, Cor & Acessibilidade**: WCAG AA mínimo `4.5:1` (texto normal/placeholder) e `3:1` (grande/UI), APCA `|Lc| >= 60` corpo; proibido `#000000`/`#FFFFFF` puros sem elevação controlada ou cinzas lavados em dark mode; touch targets `>= 44×44px` (mobile/iOS) e `>= 48×48dp` (Android); corpo `>= 14px`.
4. **Tipografia Intencional**: contraste claro de escala/peso; `tabular-nums` obrigatório em dados dinâmicos, preços, tabelas e timers; `text-wrap: balance` em títulos curtos e `pretty` em parágrafos; `-webkit-font-smoothing: antialiased` no root; proteção real contra overflow/truncamento.
5. **Conteúdo Real & Zero Copy de Template**: proibido *Lorem ipsum*, *John Doe*, *Acme Corp*; proibido clichês ("Transforme seu negócio", "Eleve sua experiência", "Solução definitiva", "Potencializado por IA"); zero subtítulos redundantes e zero *botsplaining*.
6. **UX Completa & Motion com Propósito**: estados reais obrigatórios (loading/skeleton, empty, error+recuperação, sucesso). Animação de página, componente e card é bem-vinda quando comunica mudança de estado; desktop, iOS e Android não compartilham a mesma curva. Proibido `transition-all`, `hover:scale-105` em todo card, `animate-bounce` e loop infinito que não seja espera. Ver [10-motion-anti-slop.md](references/10-motion-anti-slop.md).
7. **Precisão Geométrica & Sistema**: raios concêntricos obrigatórios (`Raio Interno = Raio Externo - Padding`); escala estrita 4/8px sem *magic numbers*; profundidade em Dark Mode por luminosidade de superfície (não sombra preta chapada); alinhamento óptico de ícones e botões.
8. **Semântica & Higiene de Dados**: cores semânticas somente com significado real; sem excesso de badges competindo em listas/tabelas; números alinhados à direita; gráficos proporcionais sem título do tipo de gráfico, sem instrução de leitura e com rótulo direto quando possível.
9. **Formulários, Estados & Interação**: proibido placeholder substituindo `<label>`; proibido remover `:focus-visible` sem substituto equivalente; estados `hover`/`active`/`disabled`/`focus`/`invalid` + erro orientando correção; proibido modal sobre modal e ações destrutivas sem confirmação ou Desfazer.
10. **Ergonomia Nativa Mobile, Desktop & Mídia**: iOS HIG (safe areas, tab bar 2–5, edge-swipe back, thumb zone) e Android Material 3 (insets, predictive back, nav bar→rail, máx 1 FAB, snackbar); Desktop (`⌘K`, atalhos, master-detail/cockpit); proibido scroll aninhado sem justificativa; `object-fit: cover` e fallback em mídias.

---

## Modos Rápidos de Uso

`/designaura` no chat de um projeto começa na hora. Se esse projeto já tem telas, elas não são o modelo: o comando significa que não agradaram. Extraia tarefas e dados, descarte a composição, e redesenhe pelo fluxo de trabalho. O comando está na skill `designaura`.

Quando o usuário pedir uma ação específica em um projeto existente, execute apenas o necessário sem ritual excessivo:

| Pedido | Ação | Referência |
|---|---|---|
| **`biblia`** | Rodar Fase 1 + Fase 2 e gerar `DESIGN-BIBLE.md`, `tokens.json/css` e `screen-manifest.json` | [02-biblia-de-design.md](references/02-biblia-de-design.md) |
| **`construir`** | Ler Bíblia/manifesto existente, orquestrar até 8 subagentes na Fase 3 e gerar vitrine | [03-orquestracao-subagentes.md](references/03-orquestracao-subagentes.md) |
| **`auditar`** | Rodar `audit_contrast.py`, `lint_design_aura.py` e `capture_and_audit.mjs` em modo leitura e emitir relatório | [07-auditoria-e-veredito.md](references/07-auditoria-e-veredito.md) |
| **`polir`** | Aplicar micro-craft, corte de AI tells e correções de auditoria em lote, depois revalidar | [06-micro-craft-e-motion.md](references/06-micro-craft-e-motion.md) |
| **`canvas`** | Gerar ou atualizar apenas `fluxo.html`, `preview.html` e `index.html` a partir do `screen-manifest.json` | [08-canvas-figma-manifest.md](references/08-canvas-figma-manifest.md) |

---

## Mapa de Referências e Scripts

- `references/01-leis-inegociaveis.md` — Especificação completa dos 10 Blocos e regras de reprovação.
- `references/02-biblia-de-design.md` — Estrutura das 12 seções da Bíblia de Design + Bíblia Visual PDF.
- `references/03-orquestracao-subagentes.md` — Dimensionamento (máx. 8 subagentes), contratos e briefing.
- `references/04-desktop-e-sistemas.md` — Janela nativa, cockpit, shell web por largura, tabela que vira lista.
- `references/05-mobile-ios-android.md` — iOS HIG, Android Material 3, polegar, safe area, RN/Flutter/PWA.
- `references/06-micro-craft-e-motion.md` — Raios concêntricos, alinhamento óptico, sombras, tipografia e motion de controle.
- `references/07-auditoria-e-veredito.md` — Protocolo de revisão, formato de relatório e evidências reais.
- `references/08-canvas-figma-manifest.md` — Schema do `screen-manifest.json` e vitrine estilo Figma.
- `references/09-pesquisa-componentes-oss.md` — Como casar uma interação com registry, galeria ou armadilha de licença.
- `references/10-motion-anti-slop.md` — Onde animar, e a diferença objetiva entre desktop, iOS e Android.
- `scripts/design_intel.py` — Pesquisa offline BM25 sobre domínios, tipografia, padrões e bibliotecas OSS.
- `scripts/discover_oss_components.py` — Caça componentes free/OSS por necessidade, stack, plataforma e modo. `--online` consulta GitHub e npm.
- `scripts/generate_tokens.py` — Compila `tokens.json` em CSS, Tailwind v4, TS, Swift, Kotlin e Dart (`--format all`).
- `scripts/audit_contrast.py` — Validador WCAG 2.1 + APCA em Light & Dark.
- `scripts/lint_design_aura.py` — Linter determinístico dos 10 Blocos + AI tells.
- `scripts/build_figma_canvas.py` — Gerador da vitrine `fluxo.html` + `preview.html` + `index.html`.
- `scripts/capture_and_audit.mjs` — Captura multi-viewport Light/Dark e auditoria DOM real via Chromium CDP.
