# Componentes open source: a base pré-categorizada

Interface sofisticada não nasce de uma biblioteca famosa. Nasce de escolher, para cada necessidade do projeto, a melhor peça disponível, e de vestir todas com os mesmos tokens. Por isso a skill mantém uma base ampla e já categorizada, e um projeto pode, e normalmente deve, usar várias bibliotecas.

## 1. Como a base é organizada

- `data/taxonomy.json`: 24 categorias e mais de 110 necessidades, cada necessidade com palavras-chave em português e inglês.
- `data/catalog/<categoria>.json`: cerca de 360 entradas. Cada uma traz:
  - **uso**: dependência, código copiado via registry, primitivo de plataforma, ferramenta ou referência;
  - **stacks e plataformas**: html, react, vue, svelte, solid, angular, rn, flutter, ios, android, electron, tauri;
  - **modos**: operate, read, persuade; `flashy` marca peças de impacto que só entram em Persuade;
  - **estilo**: como re-tematizar (`headless`, `tokens`, `tailwind`, `themeable`, `native`) e o tipo de motion (`none`, `subtle`, `expressive`);
  - **licença**: `license_status` (`ok`, `attribution`, `free-license`, `platform`, `verify`, `trap`, `study-only`, `reference`) e `license_checked_at`;
  - **acabamento**: `craft` de 1 a 3, a qualidade de acabamento observada;
  - **resumo, instalação e notas**: o que a peça resolve, como entra e as ressalvas (partes pagas, atribuição, manutenção).

Categorias: fundações e kits, navegação, tabelas, gráficos, KPIs, formulários, agenda, arrastar e kanban, overlays e feedback, editores e documentos, conversa e IA, canvas e diagramas, desktop, mobile, ícones, tipografia, imagem, motion, efeitos, seções de site, acesso e configurações, cor e tokens, referências.

```bash
python3 <skill_dir>/scripts/discover_oss_components.py --list-categories
python3 <skill_dir>/scripts/discover_oss_components.py --category charts --stack react
```

## 2. Escolha em quatro passos

### Passo 1 — Necessidades
Escreva a necessidade como verbo e contexto, não como "componente bonito": "agendar consultas por profissional com conflito de horário", "comparar 300 linhas e editar uma célula", "abrir um sheet arrastável com o polegar". O scanner lê o planejamento e o repositório e propõe as necessidades; o orquestrador corrige a lista.

```bash
python3 <skill_dir>/scripts/discover_oss_components.py --scan <repo-ou-plano> --stack <stack> --platform <plataforma> --mode <modo>
python3 <skill_dir>/scripts/discover_oss_components.py --need "agenda por profissional com conflito" --stack html
```

### Passo 2 — Candidatos por necessidade
Para cada necessidade, o script devolve até três candidatos de qualquer biblioteca, ranqueados por:
- aderência à necessidade e à stack exata;
- acabamento;
- compatibilidade com a direção escolhida (`--direction design/direcao/escolhida.json` ou `--shape`, `--density`, `--motion`, `--skin`).

Peças chamativas perdem pontos fora de direções expressivas. Necessidades de site e de efeito são avaliadas no modo Persuade mesmo dentro de um sistema. A saída traz também referências para estudar, peças promissoras com licença a conferir e os padrões visuais de `recipes.json`.

### Passo 3 — Compatibilidade
Antes de adotar, confirme:
1. **Resolve a necessidade escrita?**
2. **Stack:** funciona na versão real do projeto?
3. **Tema:** aceita os tokens (headless, variáveis CSS, tema configurável) ou impõe uma pele própria?
4. **Acessibilidade:** teclado, foco e nome acessível no comportamento, não só no README?
5. **Estados:** carregando, vazio, erro, desabilitado?
6. **Peso:** razoável para o uso?
7. **Manutenção:** release recente e repositório não arquivado?
8. **Licença:** conferida no arquivo LICENSE da versão fixada?

### Passo 4 — Registro
Na Parte B da Bíblia, uma linha por peça: necessidade, peça, uso, versão fixada, licença, caminho, o que foi aproveitado e como foi re-tematizada. Registre também as peças recusadas e o motivo. Sem caminho, o subagente não usa.

## 3. Várias bibliotecas, uma linguagem

Misturar bibliotecas é normal. O que evita a colcha:
- **Uma peça por necessidade.** Não use duas bibliotecas de tabela nem dois motores de gráfico sem motivo.
- **Tudo re-tematizado.** Cor, raio, tipografia, sombra e foco vêm dos tokens. Nenhuma peça mantém a paleta da demo.
- **Uma família de ícones e um sistema de motion** para o projeto inteiro.
- **Comportamento de uma base acessível quando possível.** Em React, primitivos como Base UI, Radix ou React Aria (inclusive via `shadcn create`, que oferece estilos visuais diferentes) seguram teclado e foco; peças especializadas entram por cima. Em HTML estático, prefira o HTML nativo (`<dialog>`, Popover API, `<details>`) e Web Components como Web Awesome. No React Native, Expo UI dá controles nativos de SwiftUI e Compose.
- Se todos os candidatos levam ao mesmo painel genérico, troque o padrão de interação (tabela em vez de cartões, linha do tempo em vez de feed), não só a cor.

## 4. Licenças

| Situação | O que significa | Uso |
|---|---|---|
| `ok` | MIT, Apache-2.0, BSD, ISC, MPL, CC0 | Livre, mantendo os avisos |
| `attribution` | Exige crédito (ex.: Solar Icons CC BY 4.0, Lightweight Charts) | Use e registre a atribuição na Bíblia e no produto |
| `free-license` | Gratuita, mas não open source (ex.: GSAP, Fontshare, Unsplash) | Use lendo as restrições |
| `platform` | SDK ou padrão da plataforma | Use na plataforma dele |
| `verify` | Promissora, licença a confirmar | Confirme antes de copiar |
| `trap` | Não é permissiva (ApexCharts ≥ 5, React Bits, Aceternity, Tailwind Plus, Remix Icon, tldraw, Shepherd.js, Intro.js) | Não entra como código |
| `study-only` | Produto AGPL ou GPL | Leia para aprender; não copie |
| `reference` | Galeria ou diretriz | Estude estrutura; não há código |

Código visível no navegador não é open source. Preview público de biblioteca paga também não. Algumas bibliotecas têm partes livres e partes pagas (Untitled UI, Tiptap, AG Grid, FullCalendar, Schedule-X, MUI X): use só a parte livre e anote.

## 5. Referências: estudar sem clonar

Galerias de produto (Mobbin, Refero, NicelyDone, SaaS Interface), de sites (Godly, Land-book, Lapa Ninja, Siteinspire, Minimal Gallery) e diretrizes (Apple HIG, Material 3, Fluent 2, GOV.UK, APG, Vercel Web Interface Guidelines) ensinam estrutura, hierarquia e fluxo. Uma referência por necessidade; três produtos misturados numa tela viram colcha. Produtos AGPL e GPL servem para ler.

## 6. Manter a base viva

```bash
python3 <skill_dir>/scripts/refresh_catalog.py --category charts          # relatório de licença, arquivamento e atividade
GITHUB_TOKEN=... python3 <skill_dir>/scripts/refresh_catalog.py --mark-checked
python3 <skill_dir>/scripts/discover_oss_components.py --need "<necessidade>" --online   # GitHub e npm ao vivo, só licença permissiva
```

O refresh não muda licenças sozinho: ele aponta divergências para revisão humana. Para acrescentar uma peça, adicione a entrada no arquivo da categoria com todos os campos, use necessidades existentes da taxonomia (ou crie a necessidade com palavras-chave) e rode os testes.
