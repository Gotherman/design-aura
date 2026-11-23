# Estúdio de Direção e Bíblia de Design

A Bíblia é o contrato visual do projeto. Ela precisa servir a três leitores: a pessoa que aprova, os subagentes que constroem e qualquer thread futura que abra o projeto sem a skill carregada. Por isso guarda decisões e o motivo de cada uma, não cópias das leis da skill.

Antes dela vem o Estúdio de Direção. Uma Bíblia escrita numa passada só descobre o gosto da pessoa nas correções; comparar direções sobre o mesmo trecho real resolve isso antes de construir.

## Estúdio de Direção (F2A)

### 1. Pesquisa por arquétipo
Para cada tipo de tela dominante do projeto (fila de trabalho, formulário, painel, conversa, hero de site), separe 3 a 5 referências reais e anote o que observar em cada uma: ritmo, densidade, hierarquia, onde fica a ação. Fontes: `discover_oss_components.py --category references` e `data/catalog/references.json`. Referência ensina estrutura; nada é copiado.

`design_intel.py "<domínio>"` devolve hipóteses do setor (sementes de cor com motivo, tipografias por personalidade, arquétipos prováveis e erros comuns). São pontos de partida. A cor da marca, o fluxo lido no projeto e a escolha da pessoa prevalecem.

### 2. Duas ou três direções diferentes de verdade
Cada direção fecha estes eixos:

| Eixo | Opções | Onde está o método |
|---|---|---|
| Conceito | nome, 3 adjetivos, uma frase | — |
| Cor | semente (a marca, se houver), acento, harmonia (complementar, análoga, dividida, tríade, mono) | 06 · Cor |
| Tipografia | um par por personalidade | 06 · Tipografia, `data/typography.json` |
| Forma | reta, suave, arredondada | 06 · Espaço e forma |
| Densidade | compacta, equilibrada, arejada | 06 · Espaço e forma |
| Profundidade | linha fina, suave, tonal, tátil | 06 · Profundidade |
| Ícones | uma família que combine com o traço da fonte | 06 · Ícones |
| Assinatura | um gesto ligado ao domínio, se aprovado | 10 · Motion |
| Recusa | o que esta direção não faz | — |

As direções precisam diferir em pelo menos três eixos. O script avisa quando duas ficam parecidas demais. Se todas puxarem para o mesmo painel genérico, troque o padrão de interação (tabela em vez de cartões, linha do tempo em vez de feed) e não só a cor.

### 3. O mesmo trecho real
Escolha um trecho que represente o produto: a barra do app, um título com subtítulo, um KPI, quatro linhas da lista principal com estados diferentes, as ações primária e secundária e um campo. Use dados do próprio projeto. Veja `assets/direction-board.example.json`.

```bash
python3 <skill_dir>/scripts/render_direction_board.py direcoes.json --out design/direcao
```

Sai `direction-board.html` (cada direção em Light e Dark) e `direcao-N.tokens.json/.css` de cada uma, já calibrados pelo motor de cor (contraste e paridade semântica verificados).

### 4. Portão 1A
Mostre o board e peça uma escolha: uma direção, uma mistura de eixos ("a cor da 1 com a forma da 2") ou outra rodada. Registre a escolha e o motivo na Parte A. Se a pessoa autorizou seguir direto, use a recomendada e diga qual foi.

## A Bíblia (F2B)

Um documento, três partes. Use `assets/design-bible-template.md`.

### Parte A — Para aprovar (4 a 6 páginas)
1. Direção escolhida: conceito, adjetivos, o que recusa e por que venceu as outras.
2. Referências usadas e o que cada uma ensinou.
3. Paleta em contexto: escalas geradas, pares de texto, o trecho real nos dois temas.
4. Tipografia com conteúdo do projeto (números, nomes longos, acentos).
5. Fragmentos-chave nos dois temas: botões, badge, linha selecionada, campo, cartão.
6. Mapa de telas com o arquétipo de cada uma.

### Parte B — Para construir
1. **Contrato de plataforma**: modo de trabalho, tipo de produto (Operate, Read, Persuade), superfícies e a principal, papel do mobile, stack por superfície, tema padrão, uso da cor da marca, detalhes do domínio aprovados (com ação, formato, duração, reduced motion e onde não entram), modelos do orquestrador e dos subagentes, hipóteses não confirmadas.
2. **Tokens**: tabela Token | Light | Dark gerada do `tokens.css`, mais o estilo de profundidade, a forma e a densidade.
3. **Orçamentos do projeto**: topo desktop (barras e altura), topo mobile (percentual e altura), abas irmãs, vazio aceitável, buraco em cartão, peso da página. Cada valor com o motivo. Os mesmos números vão para `project.budgets` no manifesto.
4. **Anatomia executável**: CSS dos componentes base só com `var(--token)`: botões, campo, linha de tabela e seleção, item de navegação, badge por estado, toast, drawer, vazio, foco.
5. **Telas**: para cada tela, arquétipo, zonas com larguras (o diagrama sai do manifesto), ação primária e onde fica em cada largura, estados obrigatórios, o que ficou de fora e em qual tela mora.
6. **Componentes**: uma linha por peça usada, com necessidade, fonte, versão fixada, licença, caminho, o que foi aproveitado e como foi re-tematizada; peças recusadas e o motivo.
7. **Motion**: o que anima, o que fica quieto, durações separadas para desktop, iOS e Android, e o gesto de assinatura se existir.
8. **Conteúdo**: guia curto de microcopy, formatos de data, moeda e documento, e `demo-data.json` com os dados que todas as telas usam (inclusive casos extremos).
9. **Leis do projeto**: as 10 a 15 regras derivadas para este projeto, com os números dele. Isso deixa a Bíblia autossuficiente sem copiar as leis da skill.

### Parte C — Para verificar
Portões, matriz de cobertura (tela × largura × tema × estado), histórico de revisões e evidências.

## Checagens

```bash
# completude: seções, decisões em aberto, telas do manifesto, zonas que não cabem
python3 <skill_dir>/scripts/render_design_bible.py design/DESIGN-BIBLE.md --tokens design/tokens.css --manifest design/screen-manifest.json --check
# HTML + PDF com pranchas reais e diagramas de zona
python3 <skill_dir>/scripts/render_design_bible.py design/DESIGN-BIBLE.md --tokens design/tokens.css --manifest design/screen-manifest.json --out-dir design
# sincronia Bíblia, shell e cópias de CSS
python3 <skill_dir>/scripts/render_design_bible.py design/DESIGN-BIBLE.md --tokens design/tokens.css --check-sync --shell design/SHELL-CONTRACT.md [--compare-css src/styles/tokens.css]
```

`--check` falha com placeholders (`{{...}}`, `...`, `_a fixar_`), seções ausentes, telas sem arquétipo, ação primária ou estados, telas do manifesto que a Bíblia não cita e zonas cujas larguras fixas não cabem na largura mínima declarada. A Bíblia só vai para o Portão 1 com `--check` limpo.

## Atualização em polimento e upgrade

- Nunca apague domínio, rotas ou fluxos aprovados. Atualize o texto das seções que mudaram, não só os hexes.
- Fonte única: `tokens.json` → `tokens.css` usado pelo app e pela vitrine. Nada de cópia bifurcada em `src/`.
- Registre cada revisão no histórico: o que mudou, por quê e quais artefatos foram sincronizados (tokens, `SHELL-CONTRACT.md`, manifesto, PDF).
- Upgrade de versão: compare o selo com a versão da skill, leia o `CHANGELOG.md` entre as duas, aplique os deltas que se aplicam e anote as exceções com motivo. Promova o selo só depois da verificação.
- Correções do usuário entram no histórico com escopo (só este projeto ou candidata à skill). Uma preferência local não vira regra da skill sem se repetir em outro projeto.
