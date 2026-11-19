# Vitrine Interativa Estilo Figma & Contrato `screen-manifest.json`

Ao final da construção, o Orquestrador compila todas as telas do projeto em uma **vitrine navegável estilo Figma** usando `scripts/build_figma_canvas.py`. Isso permite ao usuário inspecionar o sistema inteiro, testar fluxos ponta a ponta e validar a navegação Desktop + Mobile no navegador.

```bash
python3 <skill_dir>/scripts/build_figma_canvas.py screen-manifest.json --tokens tokens.css --out <pasta_saida>
```

Arquivos gerados automaticamente na pasta `<pasta_saida>`:
1. **`fluxo.html`** — Canvas Infinito Estilo Figma:
   - Pan livre (arrastar fundo), zoom centrado no cursor (`wheel` + `+`/`-`), `Fit All (F)`, `100% (0)`.
   - Seções coloridas por módulo/plataforma com pill de título e destaque para tela inicial (`isStart`) e módulo mobile (`isMobileSection`).
   - Artboards com previews ao vivo em `<iframe>` escalados (carregamento progressivo em lotes de 2) ou modo Esquemático leve (`L`).
   - Conexões SVG Bézier cúbicas com setas e pílulas clicáveis de fluxo que centralizam na tela de destino.
   - Modo **Isolar Conexões (`I`)**: clicar em qualquer artboard destaca apenas suas entradas e saídas.
   - **Inspetor flutuante** (canto inferior esquerdo) com resumo da tela, saltos clicáveis de entrada/saída, botão **Preview Modal** e **Abrir Tela Completa**.
   - **Minimapa interativo** (canto inferior direito) + sincronização Light/Dark (`T`) propagada ao vivo para todos os iframes.
2. **`preview.html`** — Player Guiado de Uso Real:
   - Seletor de jornadas por perfil/persona, breadcrumb dinâmico, `Voltar` / `Portal` / `Abrir pura`.
   - Palco ao vivo que detecta automaticamente quando o usuário clica em links internos das telas e sincroniza a trilha de passos; ajusta automaticamente o enquadramento quando a tela é `platform: "mobile"`.
   - Dock inferior recolhível com passos numerados e instruções de teste daquela etapa.
3. **`index.html`** — Galeria de Telas + Command Palette (`⌘K` / `Ctrl+K`):
   - Visão executiva do projeto, CTAs principais (`Preview Guiado`, `Mapa Estilo Figma`, `Tela Inicial`, `Bíblia de Design`), filtros por módulo/plataforma e busca instantânea por teclado (`⌘K`).

---

## Como funciona para Protótipos HTML e para Apps Reais

- **Protótipos HTML estáticos / Sistema de páginas**: `file` aponta para caminhos relativos na mesma pasta ou subpastas (ex.: `"desktop-portal.html"`, `"mobile-hoje.html"`).
- **Apps reais (React / Vite / Next.js / Electron Web / Expo Web / Flutter Web)**: rode o servidor de dev local (ex.: `http://127.0.0.1:5173`) e preencha `file` com a rota/URL completa ou relativa (`"/portal"`, `"http://127.0.0.1:5173/financeiro/pagar"`), ou gere o build estático e sirva a vitrine junto.

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
      "desc": "Visão executiva com triagem por horizonte temporal e acesso em 1 clique."
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
          "tip": "Verifique os alertas prioritários no bloco Agora e clique em Abrir Fila Operacional."
        }
      ]
    }
  ]
}
```

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
