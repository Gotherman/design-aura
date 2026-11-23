# Histórico da Design Aura

Use este arquivo no modo Upgrade: compare o selo da Bíblia do projeto com a versão atual e aplique os deltas que se aplicam.

## 3.1.0 — Catálogo vivo e verificação ampliada
- Base de componentes pré-categorizada em `data/catalog/` (24 categorias, mais de 110 necessidades, cerca de 360 entradas) com stacks, plataformas, modos, estilo, licença e acabamento. Um projeto usa várias bibliotecas: uma peça por necessidade, todas re-tematizadas.
- `discover_oss_components.py` detecta necessidades com radical e sinônimos PT/EN, devolve até três candidatos por necessidade de qualquer biblioteca, ajusta o ranking à direção (`--direction`, `--shape`, `--density`, `--motion`, `--skin`) e avalia necessidades de site no modo Persuade.
- `refresh_catalog.py` confere licença, arquivamento e atividade no GitHub e no npm e gera um diff para revisão.
- Licenças corrigidas: ApexCharts ≥ 5 (licença dupla com limite de receita), Remix Icon (licença própria), Solar (CC BY 4.0, atribuição), Iconify (motor MIT, conjuntos com licença própria), Lightweight Charts (atribuição). Novas armadilhas: tldraw, Shepherd.js, Intro.js.
- Probe de jornadas: teclado real (`key`, `tabTo`, `assertFocused`) e `setReducedMotion`.
- Auditor: dado duplicado, alinhamento disperso, peso da página, movimento com `prefers-reduced-motion` e comparação com a linha de base (`--baseline`).

## 3.0.0 — Direção
- Estúdio de Direção (F2A): 2–3 direções sobre o mesmo trecho real, em Light e Dark (`render_direction_board.py`), antes da Bíblia (Portão 1A).
- Motor de cor OKLCH (`color_engine.py`, `generate_tokens.py --seed`): escalas de 12 degraus, neutros tingidos pela marca, semânticas com família fixa e energia da marca, sólidos ajustados para WCAG + APCA, gráficos com checagem de daltonismo. Exportação DTCG 2025.10.
- Quatro estilos de profundidade (linha fina, suave, tonal, tátil), três linguagens de forma e três densidades.
- Bíblia em três partes (aprovar, construir, verificar) com `render_design_bible.py --check` e diagramas de zona gerados do manifesto.
- Crítico visual independente na F4.5.
- Guia novo de sites e páginas (`11-sites-e-paginas.md`); guia 06 passa a ser o sistema visual completo.
- Tipografia por personalidade (38 pares); domínios sugerem sementes de cor com motivo em vez de paletas fixas.

## 2.6.0 — Consolidação
- Registro único de regras (`data/rules.json`) com quatro camadas: ofício (pode bloquear), sinal de IA genérica (até HIGH), acabamento (até MEDIUM) e composição (REVIEW). Heurísticas nunca bloqueiam.
- Orçamentos de composição por projeto (`project.budgets`), com padrões por modo.
- Corpus de calibração em `tests/fixtures/good` e `bad`.
- `aura_check.py`: todos os portões num comando.
- SKILL.md vira roteiro; selos de versão e maiúsculas saem do corpo das instruções; receitas visuais deixam de ser obrigatórias e viram padrões por problema (`data/recipes.json`).
- Removidos valores e vocabulário de projetos específicos da skill (agora em `examples/`).

## 2.5.1 — Higiene
- Commit da 2.5.0, instalações sincronizadas e contradições numéricas unificadas (sidebar, abas, topo mobile, escala de espaço, registros de demo, número de telas).

## 2.5.0
- Cobertura por tela e largura, verificação de ação alcançável e de valor exato após interação, sincronia Bíblia/shell/CSS.

## 2.4.x
- Paridade semântica Light/Dark, presença da marca no workspace, resize in-place, vitrine em link único, suporte a SPA, testers E2E (Fase 4.5), atualização da Bíblia em polimento, modo Upgrade com selo de versão.

## 2.0–2.3
- Bíblia visual em PDF, Telas-Mãe, subagentes de 1–3 telas com auditoria por entrega, canvas estilo Figma, auditoria paralela.

## 1.x
- Primeira versão, descoberta de componentes, motion por plataforma, comando `/designaura`, parada para aprovação da Bíblia.
