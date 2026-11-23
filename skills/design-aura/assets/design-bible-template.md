# Bíblia de Direção Visual — {{PROJETO}}

> **Versão do projeto:** {{VERSAO}} · **Design Aura:** `v3.1.0` · **Superfícies:** {{SUPERFICIES}} · **Modo:** {{Operate | Read | Persuade}}

Como usar: a Parte A é para aprovar, a Parte B é para construir, a Parte C é para verificar. Troque todo `{{...}}` e todo `...` por decisões. `render_design_bible.py --check` aponta o que ficou em aberto.

---

# Parte A — Para aprovar

## A1. Direção escolhida
- **Nome e conceito:** {{nome}} — {{uma frase}}
- **Adjetivos:** {{três palavras}} · **Não pode parecer:** {{uma palavra}}
- **Por que venceu:** {{o que ela resolve melhor que as outras direções do estúdio}}
- **O que recusa:** {{lista curta}}
- **O que herda dos padrões da skill e por quê:** {{eixos herdados, ou "nenhum"}}
- **Board do estúdio:** `design/direcao/direction-board.html`

## A2. Referências usadas
| Referência | O que observar | O que entrou | O que não entrou |
|---|---|---|---|
| {{produto ou galeria}} | {{ritmo, densidade, hierarquia}} | {{...}} | {{...}} |

## A3. Cor em contexto
- **Semente:** {{hex}} · **Acento:** {{hex}} · **Harmonia:** {{complementar/análoga/...}} · **Neutros:** tingidos pela marca ({{croma}})
- **Onde a marca aparece:** {{identidade, estado ativo, um destaque por tela...}}
- **Proporção de área:** {{neutros / estrutura / acento}}
- O trecho real nos dois temas está nas pranchas no início deste PDF.

## A4. Tipografia
- **Personalidade:** {{precisa-neutra, humanista-calorosa, ...}} · **Par:** {{display}} + {{texto}} + {{mono}}
- **Escala:** razão {{1,2}} · base {{16px}} · **Teste:** números, nomes longos e acentos conferidos em {{tela}}

## A5. Fragmentos-chave
Botões, badge por estado, linha selecionada, campo, cartão e toast nos dois temas (pranchas geradas de `tokens.css`).

## A6. Mapa de telas
| ID | Tela | Arquétipo | Plataforma |
|---|---|---|---|
| `{{id}}` | {{título}} | {{arquétipo}} | {{desktop/mobile}} |

---

# Parte B — Para construir

## B1. Contrato de plataforma
- **Trabalho:** {{criar | remodelar | polir | upgrade}}
- **Tipo de produto e modo:** {{...}}
- **Superfícies e a principal:** {{web, desktop, iOS, Android}} · principal: {{...}}
- **Papel do mobile:** {{app focado | mesmas rotinas adaptadas | não há}}
- **Stack por superfície:** {{...}}
- **Tema padrão:** {{claro | escuro}} com alternância {{sim/não}}
- **Detalhes do domínio aprovados:** {{ação, formato, duração, reduced motion, onde não entra}} ou {{nenhum}}
- **Modelos:** orquestrador {{...}} · subagentes {{...}}
- **Telas-Mãe:** {{ids}}
- **Como o trabalho se organiza (palavras do projeto):** {{...}}
- **Hipóteses não confirmadas:** {{...}}

## B2. Tokens
- **Arquivos:** `tokens.json` (fonte única) → `tokens.css` usado pelo app e pela vitrine.
- **Profundidade:** {{hairline | soft | tonal | tactile}} · **Forma:** {{sharp | soft | round}} · **Densidade:** {{compact | regular | airy}}

| Token | Light | Dark |
|---|---|---|
| `--surface-z1` | `{{hex}}` | `{{hex}}` |
| `--surface-z2` | `{{hex}}` | `{{hex}}` |
| `--border-subtle` | `{{hex}}` | `{{hex}}` |
| `--text-strong` | `{{hex}}` | `{{hex}}` |
| `--text-muted` | `{{hex}}` | `{{hex}}` |
| `--primary` | `{{hex}}` | `{{hex}}` |
| `--accent` | `{{hex}}` | `{{hex}}` |
| `--danger` | `{{hex}}` | `{{hex}}` |
| `--success` | `{{hex}}` | `{{hex}}` |
| `--warning` | `{{hex}}` | `{{hex}}` |

## B3. Orçamentos do projeto
| Orçamento | Valor | Motivo |
|---|---|---|
| Barras no topo desktop | {{2}} / {{200px}} | {{...}} |
| Topo mobile antes da lista | {{40%}} / {{320px}} | {{...}} |
| Abas irmãs visíveis | {{5}} | {{...}} |
| Vazio aceitável na área de trabalho | {{70%}} | {{...}} |
| Peso da página | {{3000 KB}} | {{...}} |

Os mesmos valores estão em `project.budgets` no manifesto.

## B4. Espaço e forma
- **Escala:** {{4, 8, 12, 16, 20, 24, 32, 40, 48, 64}} · **Proximidade:** dentro do grupo ≤ metade do espaço entre grupos
- **Raios concêntricos:** {{contêiner 16 + padding 8 → interno 8}}
- **Grade:** {{colunas, gutters, largura máxima}}

## B5. Anatomia executável
CSS dos componentes base usando só `var(--token)`: botão primário, secundário, fantasma e destrutivo; campo com label, erro e foco; linha de tabela com hover e seleção; item de navegação ativo; badge por estado; toast; drawer; vazio.

```css
.btn-primary { background: var(--primary); color: var(--on-primary); border-radius: var(--radius-control-md); }
```

## B6. Telas
### `{{id}}` — {{título}}
- **Arquétipo:** {{...}} · **Zonas:** {{nome largura | nome 1fr (min)}} (diagrama abaixo, gerado do manifesto)
- **Ação primária:** {{rótulo}} — desktop: {{posição}} · mobile: {{posição}}
- **Estados:** populado, aberto/pós-ação, vazio, erro
- **Padrões visuais:** {{recipes.json: id/opção}}
- **Fora desta tela e onde mora:** {{...}}

## B7. Componentes
| Necessidade | Peça | Uso | Versão fixada | Licença | Caminho | Aproveitado e re-tema |
|---|---|---|---|---|---|---|
| {{...}} | {{...}} | {{dependência/cópia/plataforma}} | {{x.y.z}} | {{...}} | {{npm/caminho}} | {{...}} |

**Recusadas:** {{peça — motivo}}

## B8. Motion
- **Anima:** {{...}} · **Fica quieto:** {{...}}
- **Desktop:** {{hover 120–160 ms; página ~200 ms}} · **iOS:** {{push do sistema; sheet com detent}} · **Android:** {{eixo compartilhado ~250 ms; predictive back}}
- **Gesto de assinatura:** {{ou nenhum}} · **Reduced motion:** {{...}}

## B9. Conteúdo e dados fictícios
- **Microcopy:** {{verbos, caixa, tom}} · **Formatos:** {{R$ 1.234,56; dd/mm/aaaa; CPF/CNPJ}}
- **Dados de demo:** `design/demo-data.json` (inclui texto longo, campo vazio, lista cheia e vazia).

## B10. Leis do projeto
1. {{regra derivada com número deste projeto}}
2. {{...}}

---

# Parte C — Para verificar

## C1. Portões
- [ ] `render_design_bible.py --check` limpo
- [ ] `aura_check.py ... --strict` sem BLOCK e HIGH; REVIEW decididos com motivo
- [ ] Jornadas com `run_workflow_probe.mjs` (inclui trecho só por teclado e dados extremos)
- [ ] Crítica visual feita e achados tratados
- [ ] Vitrine em link único verificada

## C2. Cobertura
| Tela | Larguras | Temas | Estados | Evidência |
|---|---|---|---|---|
| `{{id}}` | {{desktop, 1920x1080, mobile-360x800}} | {{dark, light}} | {{...}} | {{caminho das capturas}} |

## C3. Histórico de revisões
| Versão | Data | O que mudou e por quê | Escopo (projeto ou candidata à skill) | Artefatos sincronizados |
|---|---|---|---|---|
| `v1.0` | `{{AAAA-MM-DD}}` | Direção aprovada no Portão 1 | projeto | `tokens.json`, `tokens.css`, PDF, `SHELL-CONTRACT.md`, manifesto |
