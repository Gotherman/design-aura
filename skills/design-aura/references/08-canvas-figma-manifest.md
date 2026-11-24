# Vitrine Interativa Estilo Figma & Contrato `screen-manifest.json`

Ao final da construção, o Orquestrador compila todas as telas do projeto em uma **vitrine navegável estilo Figma** usando `scripts/build_figma_canvas.py`. Isso permite ao usuário inspecionar o sistema inteiro, testar fluxos ponta a ponta e validar a navegação Desktop + Mobile no navegador.

```bash
python3 <skill_dir>/scripts/build_figma_canvas.py screen-manifest.json --tokens tokens.css [--app-base /app] [--thumbs <dir_audit>] --out <pasta_saida> --verify-files [--relayout]
node <skill_dir>/scripts/serve_entrega.mjs --design-dir <pasta_saida> [--app-dir <dist>] --port 4188
```

Arquivos gerados automaticamente na pasta `<pasta_saida>`:
0. **`entrega.html`** — **Hub Unificado de Link Único (raiz `.da-hub`):**
   - Barra superior única unificando **`Mapa Figma · App ao Vivo (se SPA) · Preview Guiado · Galeria · Bíblia Visual + PDF + Tema Dark/Light`**.
   - **Aba inteligente por dispositivo:** Desktop abre em `Mapa Figma` (ou `?tab=app`); Mobile (`<= 768px`) abre em `App ao Vivo` / `Preview Guiado` com grade de botões `>= 44px`.
   - **Sincronia de Tema em 3 Canais:** `localStorage`, `postMessage({ type: 'designaura:theme' })` e injeção direta `data-theme` nos iframes filhos.
   - Servido em **1 única porta** (`0.0.0.0:4188`) por `scripts/serve_entrega.mjs` combinando `/`, `/design/*` e `/app/*` (fallback SPA de `dist/`).
1. **`fluxo.html`** — Canvas Infinito Estilo Figma:
   - **Estúdio Dark-First** (`project.canvasTheme` padrão `"dark"`, independente do tema padrão do app; tecla `T` alterna Dark/Light e propaga para todos os iframes).
   - **Auto-Layout Hub-and-Spoke panorâmico:** organiza automaticamente Acesso/Conta à esquerda → **`★ Tela Inicial / Hub`** em destaque central com borda laranja → módulos Desktop em **raias horizontais equilibradas** à direita → faixa dedicada **Mobile** embaixo. Detecta torres verticais degeneradas (`height > width * 1.12` com `>= 10` telas) e reorganiza automaticamente (use `--relayout` para forçar ou `project.lockManualLayout: true` para travar coordenadas manuais).
   - **Higiene de arestas (`tier: "primary" | "secondary"`):** em mapas grandes (`> 22` arestas), exibe apenas as setas principais coloridas por módulo na visão geral — eliminando a macarronada de linhas cruzadas. Ao clicar/isolar uma tela ou ativar **`Setas: Todas (E)`**, todas as conexões secundárias/de retorno acendem instantaneamente.
   - **Barra superior de estúdio:** filtros por fluxo com contagem (`Todos (21)`, `Financeiro (6)`), botões de salto rápido **`★ Início (H)`** e **`Mobile`**, alternância **`Setas (E)`**, previews ao vivo em lotes (`L`), `Fit (F)` e barra inferior de atalhos.
   - **Inspetor flutuante** (canto inferior esquerdo) com saltos clicáveis de entrada/saída, **Abrir Modal** e **Tela Cheia**, mais **Minimapa interativo** (canto inferior direito).
2. **`preview.html`** — Player Guiado de Uso Real:
   - Seletor de jornadas por perfil/persona, breadcrumb dinâmico, `Voltar` / `Portal` / `Abrir pura`.
   - Palco ao vivo que detecta automaticamente quando o usuário clica em links internos das telas e sincroniza a trilha de passos; ajusta automaticamente o enquadramento quando a tela é `platform: "mobile"`.
   - Dock inferior recolhível com passos numerados e instruções de teste daquela etapa.
3. **`index.html`** — Galeria de Telas + Command Palette (`⌘K` / `Ctrl+K`):
   - Visão executiva do projeto, CTAs principais (`Preview Guiado`, `Mapa Estilo Figma`, `Tela Inicial`, `Bíblia de Design`), filtros por módulo/plataforma e busca instantânea por teclado (`⌘K`).

---

## Como funciona para Protótipos HTML e para Apps Reais 

- **Protótipos HTML estáticos / Sistema de páginas:** `file` aponta para caminhos relativos (`"desktop-portal.html"`, `"mobile-hoje.html"`).
- **Apps reais SPA (React / Vite / Next.js / Vue / Expo Web):** use `"route": "/fila-operacional"` (ou `file` começando com `/`) no `screen-manifest.json`, passe `--app-base /app` (ou `http://127.0.0.1:4188/app`) no `build_figma_canvas.py` e `--base-url http://127.0.0.1:4188` no `capture_and_audit.mjs`, e sirva tudo junto na mesma porta com `serve_entrega.mjs --design-dir ./design --app-dir ./dist`.
- **Smoke pós-clique opcional por tela:** adicione `"clickSelector": "[data-da-open]"` (ou seletor da 1ª pendência) em qualquer tela do `screen-manifest.json` para que `capture_and_audit.mjs --smoke-interact` valide automaticamente o estado aberto/redimensionado.

---

## Schema Oficial do `screen-manifest.json`

Veja um exemplo completo funcional em [assets/screen-manifest.example.json](../assets/screen-manifest.example.json).

```json
{
  "project": {
    "name": "Nome do Produto",
    "subtitle": "Direção de Design & Fluxo",
    "version": "1.0",
    "startScreenId": "portal",
    "bibleLink": "../DESIGN-BIBLE.md",
    "defaultTheme": "dark",
    "surfaceMode": "operate",
    "minDesktopWidth": 1024,
    "budgets": {"headerMaxBars": 2, "headerMaxPx": 200, "mobileTopMaxPct": 40},
    "worldWidth": 2800,
    "worldHeight": 1900
  },
  "theme": {
    "brandAccent": "#D95D24",
    "brandAccentDeep": "#B84714",
    "brandNavy": "#0F2942",
    "canvasBgDark": "#0B1522",
    "surfaceCardDark": "#122134",
    "canvasBgLight": "#EAE5DC",
    "surfaceCardLight": "#FFFFFF"
  },
  "sections": [
    {
      "id": "sec-core",
      "flow": "inicio",
      "label": "NÚCLEO & ACESSO",
      "x": 40,
      "y": 40,
      "w": 820,
      "h": 440,
      "accent": "#3B82F6",
      "isStart": true,
      "isMobileSection": false
    }
  ],
  "screens": [
    {
      "id": "portal",
      "flow": "inicio",
      "sectionId": "sec-core",
      "group": "Portal Executivo",
      "title": "Painel de Comando",
      "file": "desktop-portal.html",
      "platform": "desktop",
      "x": 440,
      "y": 90,
      "w": 360,
      "h": 340,
      "vw": 1440,
      "vh": 900,
      "accent": "#D95D24",
      "metric": "4 pendências · SLA 98%",
      "badge": "Início",
      "isStart": true,
      "desc": "Visão do dia com o que exige ação primeiro e acesso em 1 clique.",
      "archetype": "painel",
      "primaryAction": {"label": "Abrir fila", "desktop": "cabeçalho do bloco urgente", "mobile": "barra inferior"},
      "states": ["populado", {"name": "vazio", "query": "estado=vazio"}, {"name": "erro", "query": "estado=erro"}, {"name": "aberto", "click": "[data-da-open]", "after": ".drawer"}],
      "zones": [{"name": "Navegação", "width": 240}, {"name": "Hoje", "width": "1fr", "min": 520}, {"name": "Próximos", "width": 360}],
      "minWidth": 1280,
      "viewports": ["desktop", "1920x1080"]
    }
  ],
  "edges": [
    {
      "id": "e-portal-ops",
      "from": "portal",
      "fromSide": "r",
      "to": "ops",
      "toSide": "l",
      "label": "Abrir Fila Operacional",
      "color": "#D95D24",
      "flow": "operacao",
      "dashed": false,
      "curve": 0.35
    }
  ],
  "journeys": [
    {
      "id": "operador",
      "name": "Jornada · Operador Desktop",
      "color": "#D95D24",
      "steps": [
        {
          "screenId": "portal",
          "short": "Portal",
          "title": "Triagem matinal no Painel Executivo",
          "tip": "Verifique o que vence hoje e clique em Abrir fila."
        }
      ]
    }
  ]
}
```


## Campos que a Bíblia e a auditoria usam

| Campo | Onde | Para quê |
|---|---|---|
| `project.surfaceMode` | projeto | `operate`, `read` ou `persuade`; escolhe os orçamentos padrão e os detectores que se aplicam |
| `project.budgets` / `screens[].budgets` | projeto ou tela | Orçamentos do projeto (`headerMaxBars`, `headerMaxPx`, `mobileTopMaxPct`, `mobileTopMaxPx`, `maxSiblingTabs`, `deadSpaceReviewPct`, `cardVoidPx`, `duplicateTextMin`, `alignEdgesMax`, `perfMaxKB`, `perfMaxRequests`, `perfMaxFonts`) |
| `project.minDesktopWidth` / `screens[].minWidth` | projeto ou tela | Largura mínima em que as zonas precisam caber (padrão 1024) |
| `screens[].archetype` | tela | Arquétipo da tela ([04](04-desktop-e-sistemas.md)); obrigatório para a Bíblia passar no `--check` |
| `screens[].primaryAction` | tela | Rótulo e posição da ação primária em cada largura. O auditor procura o botão pelo rótulo (ou por `selector`) e confere se está visível e sem nada por cima |
| `screens[].states` | tela | Estados que precisam existir e ser vistos. Texto simples marca o estado; um objeto diz como chegar nele e vira captura própria (`tela@estado`): `query` ou `hash` na mesma tela, `file` ou `route` em outra, `click` + `after` para pós-clique, `primaryAction` própria. `"covered_by": "probe"` quando uma jornada E2E cobre. Estado sem caminho aparece como `DA-AUDIT-COVERAGE` (pendente). Vazio, erro e carregando não recebem sinais de tela rasa ou vazio grande |
| `screens[].zones` | tela | Zonas com `width` (px) ou `"1fr"` com `min`; viram diagramas na Bíblia e são conferidas contra a largura mínima |
| `screens[].viewports` | tela | Larguras auditadas para esta tela |
| `screens[].clickSelector` / `afterClickSelector` | tela | Estado pós-clique verificado na captura |
| `screens[].mode` | tela | Sobrescreve `surfaceMode` (por exemplo, o site institucional dentro de um sistema) |

## Fluxo navegável

A vitrine é um percurso, não um cartaz de telas soltas.

- `startScreenId` é a tela inicial de verdade, a mesma para onde o produto volta.
- Toda tela tem aresta de saída e caminho de volta para o lugar de onde a pessoa veio. Beco sem retorno é aresta faltando.
- O botão dentro da tela e a seta do `fluxo.html` contam a mesma história. Se o canvas diz "voltar ao início", a tela tem esse controle.
- Jornadas atravessam um workflow inteiro. Formas válidas: inicial → específica → volta à inicial → outra específica → volta. Lista → detalhe → ação → confirmação → lista. Perfil → configurações → volta ao perfil.
- Perfil e configurações entram no mapa quando o produto tem conta, sessão, preferência, notificação ou automação para governar, mesmo que o planejamento não tenha nomeado a tela. Não entram para enfeitar um produto sem conta. A Bíblia registra o motivo.

### Regras de Posicionamento no Canvas (Evite Sobreposição)
- Mantenha pelo menos **60px de folga horizontal** e **70px de folga vertical** entre artboards vizinhos dentro da mesma seção.
- Telas Desktop recomendam artboard `w: 360, h: 330–360` com `vw: 1440, vh: 900`.
- Telas Mobile recomendam artboard `w: 250–270, h: 350–380` com `vw: 430, vh: 932` (ou `390x844`).
- `fromSide` e `toSide` aceitam `"l"` (esquerda), `"r"` (direita), `"t"` (topo), `"b"` (base).
- Sempre garanta que todas as strings de `screens[].id`, `edges[].from/to` e `journeys[].steps[].screenId` existam de verdade no array `screens`. O script `build_figma_canvas.py` valida referências quebradas e aborta com erro claro se algo estiver desconectado.


## Demonstrações ilustrativas, quando solicitadas

Para still, animação ou bento de apresentação, escolha uma ação e seu resultado. Confira a abertura, o quadro mais carregado, o resultado e o reinício na composição publicada e em mobile quando aplicável. Use o quadro do resultado como alternativa estática quando contar a história sozinho. Identifique o material como ilustrativo. O QA do produto continua nas rotas e interações reais. [Stageshow](https://benji.org/stageshow) · [Ensaio](https://raw.githubusercontent.com/benjitaylor/skills/main/stageshow/references/rehearse.md)
