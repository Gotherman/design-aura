# Sistema visual: cor, tipo, espaço, profundidade, atenção, conteúdo e acabamento

Este guia é o método de cada eixo da direção. Ele não traz uma paleta, uma fonte ou um raio padrão: traz como escolher e como verificar. Os valores do projeto ficam na Bíblia.

## 1. Cor

### Gere a paleta pela semente
```bash
python3 <skill_dir>/scripts/generate_tokens.py --seed "#<marca>" [--accent "#<acento>"] --harmony <complementar|analoga|dividida|triade|mono> \
  --depth-style <hairline|soft|tonal|tactile> --shape <sharp|soft|round> --density <compact|regular|airy> --emit-json design/tokens.json --out design/ --format all --check-contrast
```
O motor trabalha em OKLCH e entrega:
- **Escalas de 12 degraus** para marca, acento e neutro, cada degrau com função: 1–2 fundos, 3–5 elementos (repouso, hover, ativo), 6–8 bordas, 9–10 sólido, 11–12 texto.
- **Neutros tingidos pela matiz da marca** (croma ~0,005–0,02). É o que dá coesão sem monobloco cinza: o cinza "pertence" à marca.
- **Semânticas com família fixa e energia da marca.** Erro fica em vermelho, sucesso em verde e atenção em âmbar nos dois temas; a luminosidade e o croma acompanham a marca, e a matiz se aproxima dela no máximo 6°. Assim o vermelho é vermelho de verdade sem parecer a paleta padrão do Tailwind.
- **Sólidos com texto legível.** Cada cor sólida é ajustada o mínimo possível (escurecer com texto branco ou clarear com texto escuro) até passar WCAG 4,5:1 e APCA |Lc| 60. Uma cor viva da marca não vira marrom para caber texto branco.
- **Dark derivado das mesmas escalas**, com elevação mais clara a cada plano.
- **Gráficos** com seis cores de luminosidade parecida, separadas também para deuteranopia e protanopia.

Se a marca já tem tokens próprios, escreva o `tokens.json` à mão e use o mesmo pipeline; o auditor confere tudo igual.

### Distribua a cor pela área
A proporção é decisão da direção. Um bom ponto de partida: neutros tingidos em 70–85% da área, estrutura da marca em 10–20%, acento até 5–10%, semânticas só onde existe estado. A marca aparece em zonas escolhidas (identidade, estado ativo e seleção, no máximo uma superfície de destaque por tela), não em todo cartão.

### O que evitar
- Gradiente roxo ou neon como identidade padrão; hexes da paleta padrão do Tailwind como marca.
- Massa monocromática (todas as superfícies na matiz da marca) ou o extremo oposto (neutro sem matiz em que a marca só aparece no logo).
- Cor semântica como enfeite. Estado nunca depende só da cor: ícone ou texto acompanham.

## 2. Tipografia

### Escolha por personalidade
`data/typography.json` agrupa pares por personalidade: precisa e neutra, humanista e calorosa, geométrica (amigável ou técnica), grotesca (expressiva ou industrial), editorial serifada, institucional clara e nativa da plataforma. Cada direção do estúdio usa uma personalidade diferente. Inter e Geist são boas em densidade, mas não são padrão: viram escolha quando a direção pede neutralidade precisa.

### Teste com conteúdo real
Números tabulares, nomes longos, valores monetários e acentos do português (ç, ã, õ, maiúsculas acentuadas). Muitas fontes de display falham nos acentos.

### Escala e ritmo
- Razão da escala: Operate 1,125–1,2; Read 1,2–1,25; Persuade 1,25–1,5, com tamanhos fluidos (`clamp()`) em sites.
- Até duas famílias e uma mono. Mono só para códigos, IDs e atalhos; números de dados ficam na fonte da interface com `tabular-nums`.
- Tracking negativo só em display; `text-wrap: balance` em títulos, `pretty` em parágrafos; medida de 60–75 caracteres em leitura.
- Fontes auto-hospedadas (Fontsource), `font-display: swap`, subset latino, no máximo quatro pesos.
- Serifa editorial em sistema operacional é escolha da direção registrada na Bíblia, não padrão.

## 3. Espaço e forma

- **Tokens por papel:** `inset` (padding), `stack` (vertical), `inline` (horizontal), `section`, todos sobre 4/8 px. Ajustes ópticos de 2 px dentro de controles são normais.
- **Densidade:** compacta, equilibrada ou arejada, decidida na direção. Ela muda o espaçamento, não a hierarquia.
- **Proximidade:** o espaço interno de um grupo é no máximo metade do espaço entre grupos. Mais espaço acima de um título do que abaixo.
- **Grade:** colunas, gutters e margens por breakpoint; largura máxima de conteúdo; container queries em componentes que mudam de forma.
- **Linhas de alinhamento:** poucas bordas esquerdas distintas por tela dão calma. O auditor conta e sinaliza excesso como REVIEW.
- **Forma:** reta (2–8 px), suave (6–16 px) ou arredondada (10–24 px). Raios concêntricos: interno = externo − padding quando o padding é até 24 px.

## 4. Profundidade

Escolha um estilo na direção. Cada um usa no máximo duas pistas por plano e o mesmo tratamento para o mesmo plano em todas as telas; sombra forte só em Z3/Z4.

| Estilo | Pistas | Combina com |
|---|---|---|
| **Linha fina** (`hairline`) | borda sutil + degrau leve; sombra só em flutuantes | ferramentas densas, produto técnico |
| **Suave** (`soft`) | sombras em camadas, borda quase invisível, cartões brancos | SaaS editorial, checkout, sites |
| **Tonal** (`tonal`) | degraus de luminosidade, sem borda | mobile, Material 3, interfaces calmas |
| **Tátil** (`tactile`) | borda com brilho, bisel e sombra de três camadas; canvas mais aterrado | operação com muitos painéis, marcas sólidas (receita completa em `examples/estilo-tatil.css`) |

Os planos:
- **Z0** poço (trilhos, campos, colunas de kanban);
- **Z1** canvas;
- **Z2** cartões e painéis;
- **Z3** flutuantes (popover, menu, paleta, barras fixas);
- **Z4** modal, drawer, sheet.

No Dark, elevar é clarear. No Light, elevar é sombra + superfície mais clara (ou, no tonal, superfície de outro tom). O auditor de contraste mede a separação conforme o estilo declarado em `--da-depth-style` e devolve REVIEW quando falta.

Painéis compostos ganham dois planos internos (cabeçalho ou rodapé levemente diferente do miolo) em vez de um caixote liso. Uma faixa recuada ou um bloco de evidência dentro do painel organiza; um cartão idêntico dentro de outro só polui.

## 5. Anti-poluição: orçamento de atenção

| Por vista | Operate desktop | Mobile | Persuade |
|---|---|---|---|
| Ponto focal por região | 1 | 1 | 1 por seção |
| Ação primária por contexto | 1 | 1 | 1 por seção |
| Níveis de ênfase visíveis | até 3 | até 3 | até 4 |
| Cromo (barras fixas) sobre a altura útil | ~25% | ~40% | livre no hero |
| Usos do acento | poucos e intencionais | poucos | um por seção |

Ferramentas:
- **Teste de apertar os olhos.** Desfoque a captura: o foco e a ação principal continuam óbvios?
- **Uma vez por vista.** O mesmo dado (nome, unidade, solicitante) aparece uma vez; o auditor sinaliza duplicação.
- **Escada de revelação.** Na linha, popover, drawer ou sheet, detalhe na mesma área, página. Veja [04](04-desktop-e-sistemas.md).
- **Controles de demonstração isolados.** Seletor de cenário ou simulador nunca fica junto das ações reais.

Os números exatos são orçamentos do projeto (Parte B da Bíblia e `project.budgets` no manifesto).

## 6. Conteúdo

- **Formatos PT-BR:** `R$ 1.234,56`, `dd/mm/aaaa`, CPF, CNPJ, CEP e telefone com máscara.
- **Dados de demo** em `demo-data.json`: nomes diversos e de comprimentos diferentes, números com distribuição plausível (nada de 100, 200, 300), casos extremos (texto longo, campo vazio, lista cheia e vazia).
- **Microcopy:** botão com verbo e objeto; frases em caixa normal; rótulos de até três palavras; vazio diz o que é, por que está vazio e a próxima ação; erro diz o que houve e como resolver.
- **Vocabulário do domínio.** Termos técnicos de infraestrutura ficam fora da tela de quem não é técnico; em ferramentas de desenvolvimento eles são o vocabulário certo.
- Cada bloco responde a uma pergunta da pessoa. Se não responde, sai da tela ou desce na escada de revelação.

## 7. Ícones

- Uma família por projeto, escolhida pela forma da fonte: Lucide ou Tabler com geométricas, Phosphor com humanistas, Material Symbols no Android, SF Symbols no iOS, Fluent no Windows.
- Tamanhos 16, 20 e 24 com traço ajustado ao tamanho; ícones de 13–14 px dentro de chips.
- Vocabulário do domínio em vez do mesmo ícone genérico repetido.
- Emblema (ícone dentro de uma caixa com tom) é um padrão opcional para identidade de entidade ou categoria em listas, um por linha. Em todo ícone da tela ele vira o template "ícone em quadrado colorido".
- Logos de terceiros (bancos, canais) vêm de Simple Icons ou SVGL, sem recolorir.

## 8. Acabamento óptico

- Botão com ícone: 2 px a menos de padding do lado do ícone. Ícone de play desloca 1–2 px para a direita.
- Linhas clicáveis: hover troca a superfície; seleção usa `primary-surface` e um indicador de 2–3 px; o link "Abrir" vira botão no hover.
- Superfícies do navegador tematizadas: `::selection`, `caret-color`, `:focus-visible` com anel de 2 px e offset de 2 px, barras de rolagem finas nas cores dos planos, `text-underline-offset: 3px`.
- Interações de controle e performance de motion estão em [10](10-motion-anti-slop.md).

## 9. Padrões visuais por problema

`data/recipes.json` reúne problemas recorrentes (prazo consumido, estado de item, identidade de entidade, metadados, ranking, série temporal, cascata, lista para detalhe, ações de decisão, confirmação reversível, vazio, kanban, importação, atendimento, acesso, resumo mobile, hero de site, prova social, preços). Cada problema tem duas a quatro soluções com quando usar e o que evitar. A direção escolhe a solução; nenhuma é obrigatória.
