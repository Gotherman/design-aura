# Estudos de caso

Lições dos projetos em que a skill foi usada. Servem para entender por que certas regras existem. Os valores e o vocabulário destes projetos **não** são padrão para outros.

## Sistema de agência de viagens (ERP + app dos sócios)

- **Primeira rodada sem Telas-Mãe:** 40 telas rasas, fonte serifada em sistema operacional e paleta bege. A causa principal foi um linter que acusava falso "card dentro de card" e levou o modelo a proibir cartões. Daí vieram o Portão 2 (Telas-Mãe), o limite de 1–3 telas por construtor e a calibração das regras em telas boas.
- **Segunda rodada:** aprovada depois de ajustes nas Telas-Mãe. O usuário pediu marca mais presente sem virar massa monocromática, Light menos branco, ícones menos genéricos e gráficos menos "tutorial". Dessas correções vieram o estilo de profundidade tátil (`estilo-tatil.css`), os padrões de prazo e estado em `recipes.json` e a orientação de escala dinâmica em gráficos.
- **Lição de direção:** o gosto do usuário apareceu nas correções, tarde. Isso motivou o Estúdio de Direção.

## Portal operacional de ponto (mesa de conferência + app de campo)

- Telas passaram em todos os testes e ainda pediam estudo para usar: topo com cinco faixas, dados repetidos em dois cartões, jargão técnico e erro em rosa no Dark. Daí vieram a escada de revelação, o padrão "lista → detalhe na mesma área", a paridade semântica e o detector de dado duplicado.
- Os números desse projeto (topo ≤ 210 px, hero mobile ≤ 38%, ≤ 5 abas) viraram, por um tempo, limites globais e começaram a reprovar telas boas de outros tipos. Hoje são orçamentos por projeto, com padrões por modo em `data/rules.json`.
- Depois de 141 passos de teste verdes, o usuário ainda corrigiu composição, profundidade e gráficos. Isso motivou o crítico visual independente, a comparação antes/depois e a exigência de evidência do estado pós-ação.
