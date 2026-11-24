# Design Aura — Plano de evolução (v2.5.0 → v3.x)

> Análise feita em 2026-11-23 sobre a v2.5.0 do repositório (incluindo as mudanças ainda não commitadas), as 61 rodadas desta thread, os scripts e catálogos e uma pesquisa externa de bibliotecas e licenças.
> Objetivo declarado: a melhor skill de **direção visual** para apps mobile e desktop, sistemas web e desktop e sites, com telas bonitas, sofisticadas, harmônicas e sem cara de IA.

---

## 0. Resumo

A skill acertou o processo (Bíblia → Telas-Mãe → subagentes com Fast-Audit → vitrine → QA E2E) e acumulou bastante ofício. O risco agora é outro: **cada correção pedida num projeto virou regra global da skill**, com números, hexes e vocabulário daquele projeto. Isso produz três efeitos:

1. **Mesma cara em todo projeto.** A skill prescreve marinho + faixa de cabeçalho da marca + `.icon-emblem` + `.chip-sla` + Geist/Inter + hexes do Tailwind. Na rodada 10 desta thread você pediu explicitamente o contrário.
2. **Regras duras de novo, agora no sentido oposto.** Em 2.1 tiramos o "proibido card". Em 2.4 entraram `border-subtle ≥ 1.85:1`, `Z1/Z2 ≥ 1.18:1`, topo `≤ 210px`, hero `≤ 38%`, `≤ 5 abas`. São números de um projeto, aplicados como reprovação a qualquer projeto. Um site arejado ou um app claro e minimalista reprovaria.
3. **Colcha de retalhos no texto.** A mesma regra aparece em 4–6 lugares com números diferentes, cheia de selos de versão, maiúsculas e exclamações. O modelo obedece ao que grita, e foi assim que nasceu o "sem classe card" na v1.1.13.

O plano propõe **uma release de consolidação antes de qualquer conceito novo** e, depois, três ganhos de qualidade de verdade: **Estúdio de Direção** (2–3 direções comparadas antes da Bíblia), **motor de cor por semente OKLCH** (harmonia sem hex fixo) e **Crítico Visual** independente dos testers funcionais. Sites ganham um guia próprio, porque hoje não têm.

---

## 1. O que a thread ensina (para não repetir)

### O que funcionou e deve ser preservado
- **Parar para aprovar** a Bíblia (Portão 1) e as Telas-Mãe (Portão 2). A rodada 2.1 da Brasitur só deu certo porque os ajustes entraram nas 2 telas-mãe antes dos 9 subagentes.
- **Fronteira da Tela-Mãe**: herda DNA visual, nunca a arquitetura interna (2.0.1).
- **Fatiar 1–3 telas por subagente + Fast-Audit imediato** e `SHELL-CONTRACT.md` curto (acabou com subagentes que liam 4.000 linhas e não gravavam nada).
- **Perguntar antes de descartar** um detalhe do domínio (avião, carimbo), com plano fechado e limite de análise (1.1.13).
- **Estrutura tirada do trabalho real**, não do molde (1.1.4) e o teste de uso humano: onde estou, para onde vou, o que posso fazer, próximo passo (1.1.5).
- **Veredito por evidência** e cobertura declarada (2.5.0).

### Os padrões de erro que se repetem

| Padrão | Onde aconteceu | Como evitar daqui para frente |
|---|---|---|
| Regra escrita como proibição + linter com falso positivo faz o modelo empobrecer a tela | v1.1.13: 661 BLOCK falsos em telas boas, "sem classe card", 40 cascas rasas | Calibrar toda regra num corpus de telas boas e ruins antes de publicar; severidade pela evidência |
| Feedback de um projeto vira número global | Light "branco demais" → `≥ 1.85:1`; hero da Interativa → `≤ 38%`; Mesa → `≤ 210px`, `≤ 5 abas` | Números de composição viram **orçamento do projeto** na Bíblia, com padrão por modo de superfície |
| Vocabulário e hexes do projeto vazam para a skill | "Encarregado", "Aguardando Mesa", "fatura aérea", "pregão", "VM/robô/FIFO", `#0E294B`, `#C6D6EA` | Skill sem dados de cliente; exemplos isolados em `examples/`, gerados por semente |
| Correção vira mais texto em vez de substituir texto | 36 selos de versão, 44 imperativos em maiúsculas e 48 "!" em SKILL + referências | Toda mudança remove ou substitui; histórico vai para `CHANGELOG.md` |
| Veredito "Approve" com problemas visíveis | Interativa v2.4.2: 141 passos E2E verdes, você ainda corrigiu composição, profundidade e gráficos | Crítico visual separado, comparação antes/depois e estado pós-ação obrigatórios |
| Gosto do usuário descoberto tarde, por correção | Cores (azul sumiu, depois voltou), fonte genérica, light lavado | Direções comparadas **antes** da Bíblia, com fragmento real renderizado |
| Instalações divergentes | Agora: `~/.claude` e `~/.gemini` em 2.4.2; `~/.agents` e `~/.codex` em 2.5.0 | Teste de paridade de instalação no release |

---

## 2. Diagnóstico da v2.5.0 (achados verificados)

### 2.1 Higiene e release
1. **v2.5.0 não está commitada nem publicada**: 21 arquivos modificados e `scripts/audit_viewports.mjs` sem rastreio. `dist/` só tem pacotes até 2.4.2.
2. **Instalações em versões diferentes**: `~/.claude/skills/design-aura` e `~/.gemini/config/skills/design-aura` estão na 2.4.2. Um chat no Claude Code usa a versão antiga.

### 2.2 Licenças erradas no catálogo (`components_oss.json` e `registries_oss.json`)
| Peça | Catálogo diz | Realidade | Ação |
|---|---|---|---|
| ApexCharts | MIT | Desde a 5.0, licença dupla: Community abaixo de US$ 2M de receita, comercial acima. Só ≤ 3.54 segue MIT | Mover para armadilha de licença; sugerir ECharts/Unovis/AG Charts Community |
| Solar Icons | MIT | CC BY 4.0, exige atribuição à 480 Design | Corrigir e registrar atribuição |
| Remix Icon | Apache-2.0 | Remix Icon License v1.0 (própria). O Fedora a considera não livre | Mover para armadilha de licença |
| Iconify | MIT | O motor é MIT, mas cada conjunto de ícones tem a sua licença | Registrar a licença do conjunto, não do motor |
| Lightweight Charts | Apache-2.0 | Apache-2.0 com atribuição à TradingView | Anotar a exigência |

ApexCharts também aparece recomendado em `02-biblia-de-design.md` §8 e `04-desktop-e-sistemas.md` §7.

### 2.3 Fontes de "cara de IA" que a própria skill prescreve
- **Hexes semânticos e de marca são a paleta padrão do Tailwind**: `#2563EB`, `#DC2626`, `#B91C1C`, `#15803D`, `#4ADE80`, `#F59E0B`, `#B45309`, `#94A3B8`, e nos presets de domínio `#3B82F6`, `#34D399`, `#38BDF8`. É o conjunto de cores mais reconhecível de interface gerada por IA. São ~91 hexes fixos nas referências (02: 24, 04: 26, 06: 19, 08: 11, 01: 6).
- **Fonte recomendada por padrão: Geist/Inter** na entrevista ("Recomendada"). Você reclamou da fonte genérica na rodada 35. A skill `frontend-design` da Anthropic lista Inter, Roboto e Arial como fontes saturadas.
- **Micro-componentes "obrigatórios" iguais em todo projeto**: o scanner marca `shell`, `icons-emblems`, `badges-chips`, `overlays` e `motion` como `always_include`. Toda tela recebe `.icon-emblem` com spotlight, `.chip-sla` com anel e `.card-brand-hero`.
- **Contradição interna**: `DA-B2-02` proíbe "ícone em círculo/quadrado colorido + título", e `DA-B1-04`/§06 prescrevem `.icon-emblem` (ícone em quadrado colorido) como padrão universal. O briefing de subagente manda usar `.card-brand-hero` "no card-rei da tela", em todas as telas.

### 2.4 Vazamento de projeto (Brasitur e Interativa)
45 linhas em 14 arquivos. O pior caso é `ui_elements_recipes.json` (14). Teste feito: um plano de **clínica veterinária** recebeu do scanner "fatura aérea → plane-departure", "pregão → gavel", "PROIBIDO barra de VM/robô/FIFO", "6× Aguardando Mesa" e monogramas de bancos.

### 2.5 Scanner de componentes
- No plano da clínica veterinária ativou 6/16 categorias e **não ativou calendário, tabela nem documento**, embora o texto diga "agendar consultas", "estoque", "prontuário". As palavras-chave são exatas e enviesadas para finanças e licitação ("boleto", "editais", "certidões").
- Saída de 126 linhas com 5–6 bibliotecas por categoria. Isso convida à colcha (`09` §5 diz o contrário).
- As receitas não filtram por stack: o HTML estático recebe instruções de `npx shadcn`.

### 2.6 Números que se contradizem
| Tema | Valor A | Valor B |
|---|---|---|
| Sidebar expandida | `232 ↔ 68px` (SKILL, receitas) | `248 ↔ 68px` e `≥ 244–256px` (04) |
| Abas visíveis | máx. 4–5 (01, 04, template) | máx. 6 (07) |
| Topo mobile | `≤ 38% / ≤ 320px` (05) | `≤ 310px` (template) |
| Registros de demo | `≥ 5` (SKILL) | `≥ 6` (03) |
| Escopo de telas | 12–24 (SKILL) | 14–22 (03) |
| Escala de espaço | 7, 9, 11 permitidos (01) | "zero 11px" (06); `generate_tokens` não aceita 7, 9, 11 |
| Texto mínimo | corpo ≥ 14px (B3) | auditor reprova só < 12px |
| Seções da Bíblia | "12 seções" (02) | 15 no template (0, 3.5, 8.1, 13) |

### 2.7 Modelo de severidade
- `07` define `BLOCK` como "viola qualquer um dos 10 Blocos". Na prática, toda heurística de gosto pode bloquear.
- O subagente só pode responder com `0 BLOCK · 0 HIGH`. `DA-STUB-SCREEN`, `DA-DEAD-SPACE` e `DA-SURFACE-FLAT` são `HIGH` heurísticos. O subagente gasta o turno lutando contra um sinal que pedia olho humano. `DA-DEAD-SPACE` chega a `BLOCK`, e uma página editorial com respiro pode bloquear.
- `DA-LIGHT-WASHED-OUT` (`border ≥ 1.85:1`) é apresentado como contraste. A WCAG 1.4.11 exige 3:1 só para limites necessários à identificação do componente. Borda de card que já se separa por sombra ou degrau não é requisito. É gosto, e deveria ser orçamento da direção.

### 2.8 Lacunas de escopo
- **Sites (`Persuade`/`Read`) praticamente sem guia**: um único preset de domínio ("landing-produto-editorial"), nenhuma regra de narrativa, ritmo de seções, direção de arte, tipografia fluida ou performance. A meta inclui sites.
- **Sem etapa de exploração de direção**: a Bíblia é escrita em uma passada, e o gosto aparece depois, nas correções.
- **Sem crítico visual**: só testers funcionais. Em 2.4.2, o "Approve" saiu e você ainda encontrou problemas visuais.
- **Dados de demo em prosa** (Bíblia §11) em vez de um arquivo compartilhado, o que gera divergência entre subagentes.
- **Acessibilidade parcial**: sem teste de teclado na jornada, zoom de 200%, `forced-colors`, `prefers-reduced-motion` em runtime ou "não depender só de cor".
- **Sem orçamento de performance**: ECharts completo, fontes e imagens nunca são medidos.
- **Tokens fora do padrão**: o formato DTCG ficou estável em 2025.10. Adotá-lo abre Figma Variables, Tokens Studio e Style Dictionary.

### 2.9 Forma do texto
- SKILL.md com 268 linhas densas e um leitor que abre ~1.600 linhas no modo "criar" (SKILL + 01 + 02 + 04/05 + 06 + 09 + 10).
- O guia de escrita de skills da Anthropic recomenda explicar o porquê em vez de "MUSTs" pesados e manter a skill geral, não estreita em exemplos. A Design Aura faz o oposto em várias seções.
- `designaura/SKILL.md` repete a entrevista inteira, o que é mais um ponto de divergência.

---

## 3. Princípios anti-Frankenstein (governança da skill)

1. **Três camadas, nunca misturadas**
   - **Invariantes de ofício** (universais e objetivos): contraste de texto, alvos de toque, foco, labels, estados, nada cortado ou sobreposto, convenções da plataforma, paridade semântica de matiz, zero erro JS/404. Só estes podem dar `BLOCK`.
   - **Direção do projeto** (variáveis): paleta, tipo, densidade, forma, profundidade, assinatura, composição. A skill dá **método e opções**; a Bíblia decide os valores.
   - **Heurísticas de qualidade** (sinais): tells de IA, vazios, empilhamento de barras, eco de selos, monobloco. Produzem `REVIEW` com captura; o orquestrador confirma ou dispensa com motivo.
2. **Uma regra, um lugar.** `data/rules.json` vira o registro único (id, título, camada, severidade, evidência, parâmetro e onde o valor mora). Gera a tabela de `01`, alimenta `lint` e `capture` e evita números divergentes.
3. **Nenhuma regra sem calibração.** Toda regra nova traz uma fixture boa (não pode disparar) e uma ruim (tem de disparar). O corpus inclui telas aprovadas da Brasitur e da Interativa, anonimizadas, mais um site editorial e um app claro e minimalista.
4. **Funil de promoção.** Correção do usuário → Bíblia do projeto (§13) → candidata (vista em 2 projetos ou reproduzível) → regra da skill com fixture. Nada pula etapa.
5. **Sem valores de cliente na skill.** Nenhum hex, nome ou termo de projeto em `SKILL.md`, `references/` ou `data/`. Exemplos ficam em `examples/`, marcados e gerados por semente.
6. **Substituir, não acrescentar.** Cada PR declara o que removeu. Selos de versão e "agora/novo/fim do" saem do corpo e vão para `CHANGELOG.md`.
7. **Orçamento de leitura.** SKILL.md ≤ 180 linhas (roteador e portões); referência ≤ ~220 linhas; tabela "modo → o que ler". Meta: o modo "criar" lê ≤ ~900 linhas antes de agir.
8. **Tom.** Imperativo calmo com o porquê em uma frase. Maiúscula só em nome próprio.

---

## 4. Workflow revisado, fase a fase

```text
F0  Preparação (sem perguntas)        → modo, superfícies, stack, Bíblia/selo, captura "antes"
F1  Entrevista (1 rodada)             → contrato de plataforma + personalidade + referências
F2A Estúdio de Direção (novo)         → 2–3 direções num direction-board.html  → [Portão 1A]
F2B Bíblia                            → DESIGN-BIBLE (A/B/C) + tokens + manifest + demo-data → [Portão 1]
F2.5 Telas-Mãe                        → 1 por arquétipo dominante (máx. 3) + mobile, com estados → [Portão 2]
F3  Construção                        → subagentes 1–3 telas, mapa de zonas, Fast-Audit
F4  Consolidação                      → `aura check` único + vitrine + matriz de cobertura
F4.5 QA funcional + Crítica visual    → testers (jornadas) + 1 crítico (rubrica) → correções → reteste
F5  Entrega e aprendizado             → veredito por evidência + registro de correções com escopo
```

Os modos curtos (ajuste pontual, polimento, upgrade) usam só F0, a parte afetada de F2B/F3 e as verificações do escopo. Hoje isso já existe, mas está espalhado; vira uma tabela no SKILL.md.

### F0 — Preparação
- Detectar o modo pelo pedido, a superfície, a stack, a Bíblia existente e o seu selo.
- Conferir a versão carregada; se o selo da Bíblia for antigo, listar os deltas.
- Em remodelação e polimento: capturar o **antes** (mesmos dados, largura e tema) já aqui. Isso serve à comparação final.
- Abrir só as referências da tabela "modo → leitura".

### F1 — Entrevista
- Uma rodada, linguagem clara, recomendação **derivada do projeto** e não de um texto fixo. Exemplo: "Para a fila de conferência da Mesa, recomendo abrir o detalhe na mesma área" em vez de "(Recomendado) Resize In-Place" para todo produto.
- Novas perguntas, todas opcionais e só se mudarem a entrega:
  1. **Personalidade**: 3 palavras para como o produto deve parecer e 1 para como não pode parecer.
  2. **Referências**: produtos ou sites que você admira e que detesta (links ou prints).
  3. **Densidade**: compacta, equilibrada ou arejada.
  4. **Idioma e locale** (formatos de data, moeda, documento).
  5. Em sites: objetivo de conversão, prova disponível (clientes, números reais) e ativos de imagem.
- Manter a trava anti-atropelo, o modelo do orquestrador e dos subagentes e os detalhes do domínio com plano fechado.
- Tirar Geist/Inter como recomendação padrão. A tipografia passa a ser decidida no Estúdio de Direção.

### F2A — Estúdio de Direção (novo; resolve "mesma cara" e gosto descoberto tarde)
1. **Pesquisa por arquétipo**: para cada tipo de tela dominante (fila, formulário, painel, hero de site), 3–5 referências reais de `study_references.json` e das galerias. Para cada uma, anotar o que observar (ritmo, densidade, hierarquia). Nada é copiado.
2. **2–3 direções contrastantes**, cada uma com:
   - nome-conceito e 3 adjetivos;
   - semente de cor e tipo de harmonia (análoga, complementar, dividida, monocromática com acento);
   - par tipográfico com o porquê;
   - linguagem de forma (raio e cantos), estilo de profundidade (§6.4), densidade;
   - família de ícones e assinatura (uma);
   - o que ela recusa dos padrões da skill.
3. **`direction-board.html`**: o **mesmo fragmento real** do projeto renderizado em cada direção, Light e Dark. O fragmento é uma linha da fila, um KPI, o botão primário, um badge de estado, um campo e um título com dados do projeto. São fragmentos, não telas, então o custo fica baixo. Cada direção sai de `generate_tokens.py --seed`.
4. **Portão 1A**: você escolhe, mistura ou pede "segue a recomendada". A escolha e o motivo vão para a Bíblia.
5. **Regra de diferenciação**: a direção escolhida declara em quais eixos herda o padrão da skill e por quê. Se herdar tudo, a justificativa é obrigatória.

### F2B — Bíblia
Ver §5. Termina no Portão 1 (PDF), como hoje.

### F2.5 — Telas-Mãe
- **Uma por arquétipo dominante, até 3** (ex.: fila + formulário de configuração + painel), mais uma mobile. Uma só tela-mãe não calibra arquiteturas diferentes.
- Estados obrigatórios no piloto: populado, aberto/pós-ação, vazio e erro.
- Captura da dobra e da página inteira, Light e Dark.
- Variantes só quando houver dúvida material (já está em 2.5; mantém).
- Crítica visual rápida (rubrica de §4 F4.5) antes de mostrar.

### F3 — Construção
- O briefing passa a levar o **mapa de zonas** da tela (diagrama gerado a partir do manifesto: zonas, larguras mínimas e o que mora em cada uma). Isso pega erros como o Atendimento da Brasitur, em que 224 + 3×300 px não cabia em 1024 px.
- `demo-data.json` compartilhado, importado por todas as telas.
- Alvo do subagente: **0 BLOCK**. `HIGH` e `REVIEW` voltam listados para o orquestrador, que tria com a captura.
- Antes de responder, o subagente preenche uma autoavaliação de 5 linhas (foco, ação primária, agrupamento, uso da cor, o que ficou de fora) e devolve os PNGs.

### F4 — Consolidação
- **Um comando** (`scripts/aura_check.mjs` ou `python3 scripts/aura.py check`) roda contraste, lint, captura e cobertura a partir do manifesto e gera um relatório único. Hoje são 4 comandos com flags que o orquestrador precisa lembrar.
- Vitrine como hoje (o Hub e o canvas estilo Figma foram aprovados).

### F4.5 — QA funcional + Crítica visual
- **Testers** como hoje, mais os testes da 2.5 (alcançabilidade, valor exato pós-ação) e um passo de teclado por jornada.
- **Crítico visual (novo, somente leitura)**: um subagente com contexto limpo recebe a Bíblia parte A, os PNGs (antes e depois, dobra e página inteira) e uma rubrica:
  1. foco: dá para apontar o ponto focal com a tela desfocada?
  2. ação: uma primária por contexto, no lugar que a plataforma ensinou?
  3. agrupamento: o espaço dentro dos grupos é menor que entre grupos?
  4. ritmo: alinhamentos e espaçamentos se repetem?
  5. cor: a marca aparece onde a direção disse, a semântica só com significado e o acento contido?
  6. profundidade: cada plano tem as pistas do estilo escolhido, sem excesso?
  7. conteúdo: dados verossímeis, sem eco ou duplicação, sem jargão?
  8. tells de IA (catálogo de `01`, camada de heurística).
  Saída: até 10 achados ranqueados, agrupados por causa, com recorte da captura. Um ciclo de correção e reteste.
- Isso ataca o padrão "testes verdes, usuário ainda corrige".

### F5 — Entrega e aprendizado
- Veredito da 2.5 (aprovado, requer correção, pendente de verificação).
- **Registro de aprendizado**: cada correção sua entra na Bíblia §13 com escopo (só este projeto ou candidata à skill) e motivo. A skill só muda pelo funil de §3.4.

---

## 5. Bíblia de direção visual

### Problemas atuais
- Repete as leis da skill por extenso: o template copia `DA-TECH-JARGON-UI`, a lista de termos proibidos e os hexes de referência. Isso dá trabalho e diverge.
- Mistura o que você precisa para aprovar com o que o subagente precisa para construir.
- Decisões críticas podem ficar em branco sem aviso. Já aconteceu: botão primário no mobile, cor da linha selecionada, cor de série de gráfico.
- Dados de demo em prosa.

### Nova estrutura (um documento, três partes)
**Parte A — Para aprovar (4–6 páginas, visual)**
1. Conceito da direção, 3 adjetivos e o que ela recusa.
2. Referências usadas (miniaturas e o que observar em cada uma).
3. Paleta em contexto: escalas geradas, os pares de texto e o fragmento real nos dois temas.
4. Tipografia com conteúdo real do projeto (números, nomes longos, acentuação PT-BR).
5. Fragmentos-chave (botão, badge, linha, campo, card) em Light e Dark.
6. Mapa de telas com arquétipo de cada uma.

**Parte B — Para construir (sem limite de páginas)**
1. Contrato de plataforma (como hoje).
2. Tokens (tabela Light | Dark gerada) e **orçamentos do projeto** (topo, hero mobile, abas, densidade, orçamento de atenção) com o motivo de cada valor.
3. Anatomia CSS executável (8.1 de hoje) só com `var(--token)`.
4. Por tela: arquétipo, **diagrama de zonas com larguras**, ação primária e posição por largura, estados, o que ficou de fora e onde mora.
5. Componentes com caminho, versão fixada, licença e adaptação (§7).
6. Motion por plataforma (como hoje).
7. Kit de conteúdo: guia de microcopy e `demo-data.json`.
8. **Leis do projeto**: as 10–15 regras derivadas para este projeto, com números. Isso a mantém autossuficiente para threads sem a skill (a lição da Interativa) sem copiar as leis inteiras.

**Parte C — Para verificar**
Portões, matriz de cobertura (tela × largura × tema × estado), histórico de revisões e evidência.

### Mecânica
- **`render_design_bible.py --check`** passa a validar campos obrigatórios. Exemplos: cada tela precisa de arquétipo, zonas, ação primária e estados; cada série de gráfico precisa de cor; cada tema precisa da cor de seleção. Sem isso a Bíblia não chega ao Portão 1.
- **Diagramas de zona** gerados do manifesto em SVG, com aviso quando a soma das larguras fixas passa da largura mínima declarada.
- **Diff de direção** em remodelação e upgrade: o que mudou em relação à versão anterior e em relação aos padrões da skill.
- O sincronismo Bíblia ↔ shell ↔ CSS da 2.5 continua.

---

## 6. Sistema visual: cor, tipo, espaço, estrutura, anti-poluição, profundidade, conteúdo

Hoje isso está espalhado entre 02 §4–7, 04 §5 e 06 §1–4. Proposta: reunir num único guia (`06-sistema-visual-e-acabamento.md`) e tirar as cópias de 02 e 04.

### 6.1 Cor: método por semente, não hex fixo
- **`generate_tokens.py --seed`** recebe a cor da marca (ou 2–3 cores), o tipo de harmonia e a densidade. Gera em OKLCH:
  - escala de 12 degraus para marca, neutro e acento (no modelo das Radix Colors: degraus com função, como fundo, hover, borda, sólido e texto);
  - **neutro tingido pela matiz da marca** (croma baixo, ~0,005–0,02), o que dá coesão sem monobloco cinza;
  - **semânticas harmonizadas**: a família de matiz é fixa (vermelho ~25–30°, verde ~145–155°, âmbar ~70–85°), mas luminosidade e croma acompanham a escala da marca. Assim continuam "vermelho real" sem parecer Tailwind;
  - Dark derivado da mesma escala por luminosidade, com elevação mais clara por plano;
  - paleta de gráfico com luminosidade percebida parecida, distância mínima entre séries e checagem de daltonismo (deuteranopia e protanopia).
- **Proporção de área** como heurística da direção, não regra: neutros 70–85%, estrutura da marca 10–20%, acento ≤ 5–10%, semântica só com significado. Os "65/20/10/5" de hoje viram um dos padrões possíveis.
- **Presença da marca**: as 3 zonas da 2.4 continuam como opção ("estou aqui"), mas cada direção decide onde a marca aparece. Faixa de cabeçalho marinho não é obrigatória.
- **Contraste por papel**: texto (WCAG AA e APCA, como hoje), limites essenciais de componente (3:1, WCAG 1.4.11) e separação de planos (§6.4). `DA-LIGHT-WASHED-OUT` e `DA-DARK-FLAT-MONOLITH` viram `REVIEW` com parâmetros do estilo de profundidade escolhido. `DA-SEMANTIC-HUE-PARITY` continua `BLOCK`, agora por faixa de matiz.
- Ferramentas de referência: Radix Colors, Harmonizer/Harmony (Evil Martians, OKLCH + APCA), apcach, colorjs.io e culori.

### 6.2 Tipografia: método por personalidade
- Matriz de personalidade → família: precisa e neutra, humanista e calorosa, geométrica, grotesca e industrial, editorial serifada (Read e Persuade). Cada direção propõe um par de uma linha diferente.
- **Teste com conteúdo real**: números tabulares, nomes longos e **acentos PT-BR** (ç, ã, õ, maiúsculas acentuadas). Várias fontes de display falham aqui.
- Escala por modo: Operate 1.125–1.2; Read 1.2–1.25; Persuade 1.25–1.5 com escala fluida (`clamp`, no estilo Utopia).
- Até 2 famílias e uma mono; tracking negativo só no display; números tabulares onde há dados (mantém).
- `DA-SERIF-OPERATE` continua, mas como `REVIEW` com exceção registrável. Um sistema jurídico ou editorial pode pedir serifa nos títulos.
- Carregamento: fontes auto-hospedadas, `font-display: swap`, subset latino e no máximo 4 pesos.

### 6.3 Espaço e estrutura
- **Tokens por papel**: `inset` (padding), `stack` (vertical), `inline` (horizontal), `section`, todos sobre a base 4/8 com ajustes ópticos de 2px.
- **Densidade** como multiplicador (compacta, equilibrada, arejada) decidida na direção.
- **Razão de proximidade**: espaço interno do grupo ≤ ½ do espaço entre grupos. Mais objetivo que a "Lei da Proximidade" em prosa, e o auditor consegue medir.
- **Grade e medida**: colunas, gutters e margens por breakpoint; largura máxima de conteúdo; medida de leitura de 60–75 caracteres; container queries em componentes.
- **Linhas de alinhamento**: poucas bordas esquerdas distintas por tela dão calma. O auditor conta as posições x distintas e acusa excesso como `REVIEW`.
- **Ritmo vertical**: `line-height` em múltiplos de 4 e espaço acima do título maior que abaixo (mantém).
- Correção da contradição da escala: uma lista só, gerada de `rules.json`.

### 6.4 Profundidade: estilos de profundidade
O que a 2.2–2.4 chamou de "5 camadas táteis" vira **um** dos estilos possíveis. Cada direção escolhe um:

| Estilo | Pistas usadas | Parece com |
|---|---|---|
| Linha fina (hairline) | borda sutil + degrau leve; sombra só em Z3/Z4 | ferramentas densas de produto |
| Suave | sombras em camadas, borda quase invisível | SaaS editorial, checkout |
| Tonal | só degraus de luminosidade, sem borda | Material 3, apps mobile |
| Tátil | borda iluminada + bisel + sombra de 3 camadas | a direção aprovada da Brasitur |

Regras comuns: no máximo 2 pistas por plano, o mesmo plano com o mesmo tratamento em todas as telas, sombra forte reservada para Z3/Z4, Dark com elevação mais clara e poços (Z0) só em controles. O auditor `DA-SURFACE-FLAT` mede se existe **alguma** pista entre Z1 e Z2, não se existem todas.

### 6.5 Anti-poluição: orçamento de atenção
Os limites numéricos de hoje (topo, abas, hero) viram **orçamentos do projeto** com padrões por modo:

| Orçamento | Padrão Operate desktop | Padrão mobile | Padrão Persuade |
|---|---|---|---|
| Ponto focal por região | 1 | 1 | 1 por seção |
| Ação primária por contexto | 1 | 1 | 1 por seção |
| Níveis de ênfase visíveis | ≤ 3 | ≤ 3 | ≤ 4 |
| Cromo (barras fixas) sobre a altura útil | ≤ ~25% | ≤ ~38% | livre no hero |
| Ocorrências do acento por vista | poucas e intencionais | poucas | uma por seção |

Ferramentas do auditor, todas `REVIEW`: captura desfocada (teste de apertar os olhos), detector de texto duplicado na mesma vista (fora da navegação), contagem de alinhamentos e proporção de cromo. A escada de revelação progressiva entra em `04`: inline → popover → drawer/sheet → página. O Resize In-Place é um degrau dessa escada, não o padrão de toda fila.

### 6.6 Harmonia de conteúdo
- **Kit de conteúdo PT-BR**: `R$ 1.234,56`, `dd/mm/aaaa`, máscaras de CPF e CNPJ, telefone e CEP; nomes diversos e com comprimentos variados; números com distribuição plausível (nada de 100, 200, 300).
- **Guia de microcopy curto**: botões com verbo e objeto, frase em caixa normal (sem Title Case), rótulos de até 3 palavras, fórmula de vazio (o que é, por que está vazio, próxima ação) e de erro (o que houve, como resolver).
- **Casos extremos nos dados de demo**: texto longo, campo ausente, lista cheia e zero, alimentando o QA (Break UI, já citado na 2.5).
- Cada bloco responde a uma pergunta do usuário. Se não responde, sai ou desce na escada de revelação.

### 6.7 Iconografia
- Uma família por projeto, escolhida na direção pelo traço e pela forma que combinam com a tipografia.
- Tamanhos de 16, 20 e 24 com traço ajustado ao tamanho.
- `.icon-emblem` vira padrão opcional, com cota: identidade de entidade ou categoria em listas, nunca em todo ícone. A contradição com `DA-B2-02` acaba.

---

## 7. Componentes open source: método de escolha

### 7.1 Em quatro passos
1. **Necessidades a partir do mapa de telas**, não de palavras-chave: para cada arquétipo, verbos de interação ("agendar com conflito de horário", "comparar 300 linhas e editar célula"). O scanner passa a ajudar: tokenização com radical e sinônimos PT/EN, e a lista escrita pelo orquestrador como entrada principal.
2. **Uma fundação por stack** (comportamento e acessibilidade), antes de qualquer peça especialista:

| Stack | Fundação recomendada | Observação |
|---|---|---|
| React | Base UI 1.x, Radix ou React Aria, via `shadcn create` | `shadcn create` tem estilos visuais (Vega, Nova, Maia, Lyra, Mira e outros) e bases Radix, Base UI e React Aria. O estilo entra na direção, não no padrão |
| Vue / Nuxt | Reka UI, shadcn-vue, Nuxt UI | |
| Svelte | Bits UI, Melt UI, shadcn-svelte | |
| Solid | Kobalte, Ark UI | |
| HTML estático (protótipos da skill) | HTML nativo (`<dialog>`, Popover API, `<details>`) + Web Awesome (MIT, sucessor do Shoelace) + Open Props | Hoje o HTML estático recebe receitas de `npx shadcn`, que não se aplicam |
| React Native / Expo | Expo UI (SwiftUI e Jetpack Compose nativos, estável no SDK 56) + React Native Reusables ou gluestack | |
| Flutter | Material 3 + forui ou shadcn_ui | |
| SwiftUI / Compose | primitivos da plataforma | |

3. **Uma peça por categoria especialista** (tabela, gráfico, calendário, arrastar, editor, mapa de nós), com pontuação de compatibilidade:
   - aceita os tokens (headless ou tema por variáveis)?
   - acessibilidade no comportamento?
   - estados (carregando, vazio, erro, desabilitado)?
   - peso razoável para o uso?
   - release nos últimos 12 meses?
   - **licença conferida na versão fixada** (arquivo LICENSE e data da checagem)?
   - DNA visual (raio, densidade, motion) compatível com a direção?
4. **Registro na Bíblia §B5**: peça, versão fixada, licença, caminho, o que foi aproveitado, como foi re-tematizada e as peças recusadas com o motivo.

### 7.2 Receitas viram padrões por problema
`ui_elements_recipes.json` deixa de ter `always_include`. Cada receita vira "problema → 2–3 soluções", e a direção escolhe. Exemplo, prazo com consumo: anel no chip, barra linear fina ou texto com tom semântico. Cada solução é descrita para as linguagens de forma (reta, suave, arredondada). Exemplos de domínio saem do JSON e vão para `examples/`.

### 7.3 Catálogo vivo
- `scripts/refresh_catalog.py` (v3.1): consulta GitHub e npm, compara a licença atual com a registrada, a data da última release e o arquivamento, e gera um diff para revisão humana. Nada muda sozinho.
- Campos novos: `version_pinned`, `license_checked_at`, `license_url`, `attribution_required`, `stacks`, `skin_by_tokens`.
- Lista de armadilhas atualizada: ApexCharts ≥ 5, React Bits (MIT + Commons Clause), Aceternity, Tailwind Plus, Remix Icon (licença própria), tldraw (licença própria), Highcharts, Handsontable, AG Grid Enterprise, MUI X Pro, Untitled UI PRO, Font Awesome Pro. Com atribuição: Solar e Lightweight Charts. Com licença proprietária gratuita: GSAP (standard no-charge, com restrições).

---

## 8. Fontes novas: bibliotecas, ferramentas e galerias

Legenda de uso: **D** dependência · **R** registry/código copiado · **Ref** referência (sem código) · **F** fonte/ferramenta.
Licenças marcadas com ✓ foram conferidas nesta análise. As demais vêm do meu conhecimento e entram no catálogo com `license_checked_at` vazio, para o `refresh_catalog` confirmar.

### 8.1 Fundações e kits
| Nome | Uso | Licença | Por que entra |
|---|---|---|---|
| Base UI 1.x (`@base-ui/react`) | D | MIT ✓ | Estável desde dez/2025; base de shadcn |
| React Aria Components | D | Apache-2.0 | Acessibilidade de referência; agora base do shadcn ✓ |
| shadcn `create` + Registry Directory | R | MIT ✓ | Estilos (Vega, Nova, Maia, Lyra, Mira, Luma, Sera, Rhea) e diretório oficial de registries; ajuda a variar a cara |
| Untitled UI React (parte livre) | R | MIT ✓ (só a parte free) | Componentes de app maduros sobre React Aria |
| Reka UI / shadcn-vue / Nuxt UI | D/R | MIT | Vue |
| Bits UI / Melt UI / shadcn-svelte | D/R | MIT | Svelte |
| Ark UI / Park UI / Zag.js | D | MIT | Multi-framework, máquinas de estado |
| Web Awesome (free) | D | MIT ✓ | Web Components para HTML estático |
| Open Props | D | MIT | Tokens CSS prontos para protótipo |
| Blueprint (Palantir) | Ref/D | Apache-2.0 | Desktop denso de dados |
| Fluent UI React v9 | Ref/D | MIT | Apps Windows e corporativos |
| Carbon | Ref | Apache-2.0 | Tabelas e formulários enterprise |
| GOV.UK Design System | Ref | MIT/OGL | Formulários, erros e conteúdo claros: ótimo para anti-poluição |
| gov.br Design System | Ref | verificar | Govtech brasileira (caso SEDUC) |
| Expo UI | D | MIT | SwiftUI e Compose nativos no RN, estável no SDK 56 ✓ |
| React Native Reusables / gluestack-ui / Tamagui | D/R | MIT | RN |
| forui / shadcn_ui (Flutter) | D | MIT | Flutter |

### 8.2 Peças com acabamento (usar com a direção, uma por necessidade)
| Nome | Uso | Licença | Nota |
|---|---|---|---|
| Magic UI | R | MIT | Efeitos; filtrar em Operate |
| Animate UI | R | MIT (verificar) | Primitivos shadcn com motion |
| Motion Primitives | R | MIT | Microinterações |
| Cult UI / Kokonut UI / Smooth UI / Eldora UI | R | MIT (verificar) | Peças de landing e produto |
| Spectrum UI | R | Apache-2.0 (pela listagem) | Animado e acessível |
| Kibo UI / Dice UI / coss ui / ReUI | R | MIT | Já estão no catálogo; manter |
| Tailark / Launch UI / HyperUI / Preline / Flowbite | R | MIT | Seções de site |
| Sonner / cmdk / Vaul | D | MIT | Vaul: verificar manutenção |
| Number Flow | D | MIT | Números que mudam |

### 8.3 Dados, gráficos e áreas de trabalho
| Nome | Uso | Licença | Nota |
|---|---|---|---|
| Apache ECharts | D | Apache-2.0 | Mantém como principal no HTML |
| Unovis | D | Apache-2.0 | Gráficos, mapas e redes, multi-framework |
| Observable Plot | D | ISC | Relatórios e exploração |
| visx / Nivo / Recharts | D | MIT | React |
| AG Charts Community / AG Grid Community | D | MIT | Financeiro e grades densas |
| uPlot | D | MIT | Séries longas e rápidas |
| Lightweight Charts | D | Apache-2.0 + atribuição | Séries financeiras |
| Vega-Lite | D | BSD-3 | Declarativo |
| TanStack Table / Glide Data Grid | D | MIT | Tabelas |
| React Flow (xyflow) | D | MIT | Editores de nós e fluxos |
| Schedule-X / Event Calendar (vkurko) / FullCalendar core | D | MIT | Agenda (a clínica veterinária precisaria) |
| SVAR Gantt / Frappe Gantt | D | MIT (verificar SVAR) | Cronogramas |
| Lexical / Tiptap core / Plate | D | MIT | Editores |
| Dockview / allotment / react-resizable-panels | D | MIT | Painéis de desktop |
| Victory Native XL (Skia) / Vico (Compose) / fl_chart | D | MIT / Apache | Gráficos mobile |

### 8.4 Ícones
| Nome | Licença | Nota |
|---|---|---|
| Lucide | ISC | Geométrico neutro |
| Tabler | MIT | Operacional amplo |
| Phosphor | MIT | Humanista, 6 pesos (casa com sans calorosas) |
| Heroicons | MIT | Micro 16px para chips |
| Iconoir / MingCute / IconPark | MIT / Apache / Apache | Alternativas com personalidade |
| Material Symbols | Apache-2.0 | Android e variável |
| Fluent System Icons | MIT | Windows |
| SF Symbols | licença Apple | Só em plataformas Apple |
| Solar | CC BY 4.0 ✓ | Exige atribuição |
| Remix Icon | licença própria ✓ | Armadilha |

### 8.5 Tipografia (gratuita)
- **OFL (Google Fonts e outros)**: Geist, Inter, IBM Plex Sans, Manrope, Plus Jakarta Sans, DM Sans, Figtree, Onest, Instrument Sans e Serif, Mona Sans e Hubot Sans, Bricolage Grotesque, Schibsted Grotesk, Hanken Grotesk, Funnel Sans e Display, Host Grotesk, Geologica, Atkinson Hyperlegible Next, Fraunces, Newsreader, Literata, Source Serif 4, Young Serif.
- **Mono**: JetBrains Mono, Geist Mono, IBM Plex Mono, Commit Mono, Martian Mono, Monaspace, Departure Mono.
- **Fontshare** (licença gratuita própria, não OFL): Satoshi, General Sans, Switzer, Cabinet Grotesk, Clash Display, Erode, Gambetta, Supreme.
- **Expressivas para Persuade**: Velvetyne e Collletttivo (OFL).

### 8.6 Cor, tokens e motion
| Nome | Uso | Licença | Nota |
|---|---|---|---|
| Radix Colors | F | MIT | Escalas de 12 degraus com função |
| Harmonizer / Harmony (Evil Martians) | F | verificar | OKLCH + APCA |
| apcach | F | MIT | Cor com contraste APCA alvo |
| colorjs.io / culori | F | MIT | Conversões OKLCH no gerador |
| Utopia | F | gratuito | Escalas fluidas de tipo e espaço |
| Especificação DTCG 2025.10 | F | aberta ✓ | Formato de `tokens.json` interoperável |
| Style Dictionary / Terrazzo | F | Apache / MIT | Exportação de tokens |
| Motion (motion.dev) / Anime.js v4 / AutoAnimate | D | MIT | Motion web |
| Rive runtimes / lottie-web | D | MIT | Animação de marca (o avião da Brasitur) |
| GSAP | D | proprietária gratuita ✓ | Permitido com nota de restrição |
| Reanimated / Pow (SwiftUI) | D | MIT | Mobile |

### 8.7 Galerias e referências de ofício (Ref, sem código)
- **Produto real**: Mobbin e Refero (freemium), NicelyDone, Page Flows, SaaS Interface, Component Gallery, Design Systems Surf.
- **Sites**: Godly, Land-book, Lapa Ninja, SaaSFrame, Siteinspire, Minimal Gallery, One Page Love, Httpster, Awwwards.
- **Ofício e diretrizes**: Vercel Web Interface Guidelines (versão para agentes), Rauno (interfaces), Emil Kowalski, Laws of UX, Refactoring UI (conceitos), Every Layout (conceitos).

---

## 9. Outros pontos que melhoram a skill (proativos)

1. **Corpus de calibração** em `tests/fixtures/` com `good/` e `bad/`. Executado em todo release; telas boas com 0 BLOCK.
2. **Benchmark anti-convergência**: rodar F2A em 3 briefings (clínica veterinária Operate + mobile, SaaS jurídico claro, site de escola de surfe). As 3 direções precisam diferir em matiz principal, família tipográfica e estilo de profundidade, sem nenhum termo vazado de outro projeto. Usar o laço de avaliação do `skill-creator` (com e sem skill, avaliador com assertivas).
3. **Paridade de instalação** como teste: as 4 pastas (`~/.claude`, `~/.agents`, `~/.codex`, `~/.gemini/config`) com a mesma versão e hash, mais o pacote em `dist/`.
4. **Acessibilidade extra no probe**: jornada só por teclado, zoom de 200% sem perda, `forced-colors`, `prefers-reduced-motion` em runtime e estados que não dependem só de cor (ícone ou texto junto).
5. **Orçamento de performance na captura**: peso transferido, número de requisições, fontes carregadas e LCP aproximado, como `REVIEW`. ECharts completo num protótipo é um alvo óbvio.
6. **Linha de base visual no polimento**: PNG de referência por tela e estado e diff de pixels. Mostra o que mudou e flagra regressão.
7. **`demo-data.json`** como fonte única de dados fictícios.
8. **Comando `/designaura` enxuto**: só disparo e ponteiro para o SKILL.md, para não haver duas entrevistas divergentes.
9. **Plataformas desktop nativas**: Windows 11 (Mica e Acrylic são do sistema), macOS (vibrância, toolbar unificada), Linux (GTK e libadwaita). Hoje só há titlebar e atalhos.
10. **Mobile atual**: Liquid Glass (iOS 26) e Material 3 Expressive já citados. Falta o critério para Expo UI versus kit JS.
11. **Formato de saída para Figma**: tokens DTCG → Figma Variables via Tokens Studio, para quem quiser continuar no Figma.
12. **Telemetria leve de rodada**: tempo por fase, número de correções pedidas pelo usuário e por categoria. Mostra onde a skill ainda falha.

---

## 10. Roadmap de releases (com critérios de aceite)

### v2.5.1 — Higiene (1 sessão, sem mudança de comportamento)
- Commit e publicação da v2.5.0, pacote em `dist/`, sincronização das 4 instalações.
- Corrigir as 5 licenças de §2.2 nos dois catálogos e nos textos de 02 e 04.
- Remover os 45 vazamentos de projeto (mover exemplos para `examples/`).
- Resolver as 8 contradições de §2.6 com um valor só.
- **Aceite**: `grep` de termos de projeto retorna 0 fora de `examples/`; teste de paridade de instalação verde; 25 testes atuais verdes.

### v2.6.0 — Consolidação (a release anti-Frankenstein)
- `data/rules.json` como registro único; `01` gerado a partir dele; lint e capture leem severidade e parâmetros dele.
- Modelo de severidade em três camadas (`BLOCK` só para invariantes; `HIGH`; `REVIEW` para heurísticas). Subagente com alvo de 0 BLOCK.
- Orçamentos de composição por projeto (Bíblia e manifesto), com padrões por modo.
- Corpus de calibração (`tests/fixtures/good|bad`).
- Reescrita de tom: SKILL.md como roteador ≤ 180 linhas, tabela "modo → leitura", `CHANGELOG.md`, sem selos de versão, maiúsculas ou exclamações no corpo.
- Scanner: radical e sinônimos PT/EN, filtro por stack, fim do `always_include`, saída ≤ ~40 linhas com uma peça por categoria.
- **Aceite**: telas aprovadas da Brasitur 2.2.1 e da Interativa com 0 BLOCK; fixtures ruins (casca da 1.1.13, erro rosa no Dark, mobile cortado, toast sobre decisão) detectadas; o plano da clínica veterinária ativa agenda, tabela e documento sem nenhum termo de outro projeto; o modo "criar" lê ≤ ~900 linhas.

### v3.0.0 — Direção
- F2A Estúdio de Direção + `direction-board.html` + Portão 1A.
- `generate_tokens.py --seed` (OKLCH, neutros tingidos, semânticas harmonizadas, gráficos com checagem de daltonismo) e tokens no formato DTCG.
- `06-sistema-visual-e-acabamento.md` (cor, tipo, espaço, profundidade, ícones, acabamento) absorvendo as partes de 02, 04 e 06.
- Bíblia em partes A, B e C + `render_design_bible.py --check` + diagramas de zona.
- Crítico visual em F4.5.
- `11-sites-e-paginas.md` (Persuade e Read): narrativa (promessa, prova, mecanismo, objeções, chamada), ritmo de seções, direção de arte, tipografia fluida, performance (LCP, fontes), motion de rolagem com redução, SEO semântico e tells específicos de landing (bento em excesso, blobs, logos falsos de clientes, depoimentos inventados, 3 cards de feature com ícone).
- **Aceite**: o benchmark anti-convergência passa; uma remodelação real (Brasitur ou Interativa) atinge o Portão 2 com menos correções suas que na última rodada; o crítico aponta pelo menos os problemas que você apontou na Interativa 2.4.2 quando rodado sobre aquelas capturas.

### v3.1.0 — Catálogo vivo e verificação ampliada
- `refresh_catalog.py`, campos de licença e versão, fontes de §8.
- Fundações por stack (Web Awesome no HTML estático, Expo UI no RN).
- Acessibilidade extra, orçamento de performance, linha de base visual.
- **Aceite**: o refresh detecta as mudanças de licença de §2.2 se forem revertidas no JSON; o probe de teclado roda nas jornadas da Interativa.

---

## 11. O que não fazer

- Não criar fase ou guia novo além de F2A, do crítico e de `11-sites` (os três substituem lacunas reais; todo o resto é consolidação).
- Não transformar números de um projeto em limite global.
- Não colar skills externas: cada ideia entra numa etapa existente, com critério de aceite (a regra da 2.5 continua valendo).
- Não deixar o catálogo crescer sem o método de escolha: mais opções sem filtro é colcha.
- Não tornar nenhuma receita visual obrigatória.
- Não pôr hex, nome ou termo de cliente em `references/` ou `data/`.
- Não declarar aprovação sem a evidência visual do estado que motivou o trabalho.

---

## 12. Mapa de arquivos ao final (v3.1)

```text
skills/design-aura/
  SKILL.md                         roteador: modos, fases, portões, tabela de leitura (≤ 180 linhas)
  CHANGELOG.md                     histórico (sai do corpo das instruções)
  references/
    01-leis.md                     gerado de rules.json: invariantes + catálogo de heurísticas
    02-biblia.md                   processo e estrutura A/B/C (sem cópias de cor/tipo)
    03-orquestracao.md             subagentes, briefing com mapa de zonas, testers, crítico
    04-desktop-e-sistemas.md       arquétipos, escada de revelação, shell por largura (sem cor)
    05-mobile.md                   iOS, Android, cross-platform, Expo UI
    06-sistema-visual.md           cor por semente, tipo, espaço, profundidade, ícones, acabamento
    07-auditoria.md                severidade por evidência, cobertura, veredito
    08-vitrine-manifest.md         como hoje + zonas no manifesto
    09-componentes.md              método de 4 passos, fundações por stack, armadilhas
    10-motion.md                   como hoje
    11-sites-e-paginas.md          novo
  data/
    rules.json                     novo: registro único de regras
    *.json                         catálogos com licença conferida e versão fixada
  examples/                        exemplos de projeto, marcados (Brasitur, Interativa anonimizados)
  scripts/
    aura_check.mjs                 novo: um comando para todos os portões
    refresh_catalog.py             novo (v3.1)
    generate_tokens.py             + --seed OKLCH, saída DTCG
    render_design_bible.py         + --check, diagramas de zona
    (demais como hoje)
  tests/
    fixtures/good, fixtures/bad    novo: corpus de calibração
```

---

## Fontes consultadas nesta análise
- ApexCharts: [Opções de licença](https://apexcharts.com/license/) · [Novo modelo de licenciamento](https://apexcharts.com/blog/new-licencing-model/)
- Solar: [Repositório 480 Design](https://github.com/480-Design/Solar-Icon-Set) · [Pacote @iconify-icons/solar](https://npmjs.com/package/@iconify-icons/solar)
- Remix Icon: [Repositório](https://github.com/Remix-Design/remixicon) · [Relato do Fedora](https://bugzilla.redhat.com/show_bug.cgi?id=2390280)
- React Bits: [README oficial](https://raw.githubusercontent.com/DavidHDev/react-bits/main/README.md)
- GSAP: [Licença standard](https://gsap.com/community/standard-license/) · [Webflow torna o GSAP gratuito](https://webflow.com/blog/gsap-becomes-free)
- DTCG: [Primeira versão estável](https://w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/) · [Especificação 2025.10](https://www.designtokens.org/tr/2025.10/)
- shadcn: [Registry Directory](https://ui.shadcn.com/docs/changelog/2025-10-registry-directory) · [shadcn create](https://ui.shadcn.com/docs/changelog/2025-12-shadcn-create) · [Base React Aria](https://ui.shadcn.com/docs/changelog/2026-07-react-aria) · [Estilos explicados](https://www.shadcnblocks.com/blog/shadcn-component-styles-vega-nova-maia-lyra-mira)
- Base UI: [Release 1.0.0](https://app.unpkg.com/@base-ui/react@1.6.0/files/docs/react/overview/releases/v1-0-0.md) · [InfoQ](https://www.infoq.com/news/2026/02/baseui-v1-accessible)
- Untitled UI React: [Documentação](https://www.untitledui.com/react/docs/introduction) · [Repositório](https://github.com/untitleduico/react)
- Web Awesome: [Repositório](https://github.com/shoelace-style/webawesome) · [Anúncio](https://blog.fontawesome.com/introducing-web-awesome/)
- Expo UI: [Estável no SDK 56](https://expo.dev/blog/expo-ui-stable-sdk-56) · [Documentação](https://docs.expo.dev/versions/latest/sdk/ui/)
- OKLCH: [Ecossistema OKLCH (Evil Martians)](https://evilmartians.com/chronicles/exploring-the-oklch-ecosystem-and-its-tools) · [Harmony](https://www.npmjs.com/package/@evilmartians/harmony) · [apcach](https://www.npmjs.com/package/apcach)
- Gráficos: [Comparativo TanStack](https://tanstack.com/charts/latest/docs/comparison) · [Unovis](https://bestofjs.org/projects/unovis)
- Bibliotecas animadas: [Roundup 2026](https://ui.spectrumhq.in/best-animated-react-component-libraries) · [21st.dev shadcn directory](https://21st.dev/community/shadcn-directory)
- Galerias: [Alternativas ao Mobbin (2026)](https://mobbin.com/blog/best-mobbin-alternatives)
- Diretrizes: [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) · [Skill frontend-design (Anthropic)](https://tessl.io/registry/skills/github/anthropics/skills/frontend-design)
