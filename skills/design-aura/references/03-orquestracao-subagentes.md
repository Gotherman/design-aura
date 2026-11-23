# Orquestração: construtores, testers e crítico

O orquestrador é o diretor de design: lê o projeto, conduz a direção, escreve a Bíblia, constrói a fundação e as Telas-Mãe, audita cada entrega e decide o veredito. Subagentes executam recortes pequenos sobre uma fundação já aprovada.

Quando o ambiente não oferece subagentes, o orquestrador segue as mesmas etapas sozinho, em lotes, com a mesma auditoria por lote.

## Quem faz o quê

| Papel | Faz | Não faz |
|---|---|---|
| Orquestrador | Direção, Bíblia, fundação, Telas-Mãe, auditoria por entrega, triagem, veredito | Delegar a direção ou o veredito |
| Construtor | 1–3 telas com arquitetura própria sobre a fundação | Editar tokens, `shell.css`, `shell.js` ou arquivos de outro construtor |
| Tester | Percorre jornadas e reporta falhas com evidência | Editar código |
| Crítico visual | Lê capturas contra a Parte A da Bíblia e a rubrica | Editar código ou propor uma direção nova |

## Fatiamento

| Tela | Telas por construtor |
|---|---|
| Densa com várias zonas, gráficos e interação rica | 1 |
| Operacional padrão ou mobile rica | 2–3 |
| Auxiliar (acesso, perfil, preferências) | até 3 |

Não existe teto de construtores; o que segura a qualidade é o tamanho do recorte. Dispare em lotes de 3 a 4 e acompanhe a atividade em disco. Se um construtor parar sem gravar arquivos, encerre-o e assuma o recorte em vez de deixar a pessoa esperando. Prefira 12 a 24 telas profundas (abas, filtros, drawers, sheets) a 40 telas rasas; acima disso, justifique na Bíblia.

## Briefing do construtor

```markdown
### Recorte: <módulo> (<n> telas) — <projeto>

Leia, nesta ordem e só isto antes de gravar o primeiro arquivo:
1. <caminho>/SHELL-CONTRACT.md (head, esqueleto do shell, classes e helpers).
2. Parte B da Bíblia, seções desta(s) tela(s): <âncoras>.
Consulte a Tela-Mãe (<caminho>) só para trechos pontuais.

Telas:
- `<id>` → <arquivo ou rota> · arquétipo: <...> · zonas: <nome largura | nome largura | nome 1fr (min ...)>
  · ação primária: <rótulo e posição por largura> · estados: <populado, aberto, vazio, erro>
  · peças da base de componentes: <peça — necessidade — caminho>
  · padrões visuais escolhidos: <recipes.json: id/opção>
  · saídas: <links reais>

Dados: importe `demo-data.json` (<caminho>). Não invente outros valores.

Liberdade: herde tokens, shell, gramática de componentes e acabamento da Tela-Mãe; a estrutura interna sai da tarefa desta tela. Pode escrever CSS local usando só `var(--token)`.

Ordem: grave a tela 1, grave a tela 2, rode a verificação, corrija os BLOCK. Não termine o turno só com um plano.
Verificação:
  python3 <skill_dir>/scripts/lint_design_aura.py <arquivos> --strict
  node <skill_dir>/scripts/capture_and_audit.mjs <arquivos> --out <dir>/<recorte> --themes dark,light --viewports <larguras> --strict
Não instale Playwright nem Puppeteer.

Resposta: caminhos gravados, PNGs, achados HIGH e REVIEW restantes e uma autoavaliação de 5 linhas:
foco da tela · ação primária · agrupamento · uso da cor · o que ficou de fora e onde mora.
```

Nunca escreva no briefing coisas como "sem cards", "só use classes do shell" ou "faça poucas linhas porque é amostra". Essas proibições produziram as telas rasas da primeira versão da skill.

## Auditoria por entrega

Assim que um construtor responde:
1. Rode o lint e a captura do recorte.
2. Abra os PNGs e compare com a Tela-Mãe: mesma linguagem, arquitetura própria, dados completos, interação funcionando, nada cortado.
3. Decida: aceito; ajuste pequeno feito pelo orquestrador; ou devolução com lista objetiva do que faltou, citando a captura.

REVIEW não reprova sozinho. Abra a captura, decida e anote o motivo quando dispensar.

## Testers (F4.5)

Dois ou três testers em paralelo, um por jornada ou persona. Cada um recebe:

```markdown
### Jornada <nome> (somente leitura) — <projeto>
Produto: <2–3 frases com perfis e regra de negócio>.
Passos: <ação → resultado esperado>, incluindo a ação positiva e a negativa (ex.: aprovar; recusar exige motivo).
Invariantes: contadores e totais mudam após a ação; o estado vale nos dois temas; a ação principal fica alcançável com toast ou sheet abertos; zero erro JS ou 404; nada cortado após a ação.
Teclado: um trecho da jornada só com teclado (`tabTo`, `key`, `assertFocused`), com anel de foco visível.
Dados extremos: nome longo, campo vazio, lista cheia e lista vazia (de `demo-data.json`).
Movimento: repita a ação com `setReducedMotion`; o estado continua claro.
Execução: node <skill_dir>/scripts/run_workflow_probe.mjs --scenario <cenario.json> --out <dir> [--base-url ...] --strict
Retorno: PASS/FAIL, relatório e PNGs; cada achado com severidade (P0 quebra, P1 fluxo ou layout pós-ação, P2 polimento), passo, esperado × observado, erro de console e captura.
```

## Crítico visual (F4.5)

Um subagente com contexto limpo recebe a Parte A da Bíblia, as capturas (antes e depois quando houver, dobra e página inteira, Light e Dark) e a rubrica de [07](07-auditoria-e-veredito.md). Ele não vê o código. Devolve até 10 achados ranqueados, agrupados pela causa, cada um com recorte da captura e a menor correção que resolve. O crítico existe porque testes funcionais verdes não garantem uma tela bonita nem legível.

## Triagem e correção

1. Confirme cada achado na evidência e descarte falsos positivos com motivo.
2. Agrupe sintomas pela causa (grade, token, componente compartilhado, estado global).
3. Corrija a causa: o orquestrador cuida do que é compartilhado; construtores cuidam do que é local.
4. Reteste as jornadas e as capturas afetadas.
5. No máximo dois ciclos. O que restar vira pendência explícita no veredito.

## Polimento sobre telas aprovadas

1. Capture o estado atual (mesmos dados, larguras e temas) em `audit-antes/`.
2. Atualize `tokens.json`, a Bíblia (texto das seções afetadas e histórico), o `SHELL-CONTRACT.md` e o manifesto antes de tocar nas telas.
3. Valide um piloto por plataforma afetada; uma mudança de direção reabre o piloto.
4. Propague em lotes pequenos. Se o polimento for de classes e tokens compartilhados, o orquestrador pode aplicar direto, sem subagentes.
5. Em SPA, rode o build antes de auditar. Se o formato dos dados de demo mudar, versione a chave de `localStorage`.
6. Feche com `aura_check.py --baseline audit-antes` para ver o que mudou em cada tela.

## Upgrade de versão da skill

Leia o selo da Bíblia, o `CHANGELOG.md` entre as versões e as referências tocadas pelos deltas. Aplique o que vale para o projeto, registre exceções com motivo, valide pilotos e só então promova o selo. Passe a cada colaborador apenas o contrato e os trechos do seu trabalho.

## Não deixe trabalho em segundo plano

Auditorias e capturas terminam dentro do turno. Se algo rodar em segundo plano, aguarde o fim antes de responder; um turno que termina com "aguardando auditoria" não tem veredito.
