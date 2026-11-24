# Auditoria, crítica visual e veredito

Nenhuma entrega é aprovada por leitura de código. Aprovação exige os portões automáticos sem BLOCK e HIGH, a captura dos estados que motivaram o trabalho e a inspeção dessas capturas.

## 1. Severidade por evidência

Cada regra tem uma camada em `data/rules.json`, e a camada limita a severidade:

| Camada | Teto | Exemplos | O que fazer |
|---|---|---|---|
| Ofício | BLOCK | contraste, foco, label, recorte, rolagem horizontal, JS, 404, cobertura | Corrigir |
| Sinal de IA genérica | HIGH | gradiente roxo padrão, emoji como ícone, `transition: all` | Corrigir ou registrar a exceção com motivo |
| Acabamento | MEDIUM | raios, escala de espaço, números tabulares | Polimento |
| Composição | REVIEW | vazio, tela rasa, eco de selos, barras empilhadas, dado duplicado, alinhamento | Abrir a captura; corrigir pela causa ou dispensar com motivo |

`--strict` falha com BLOCK ou HIGH. O contraste em tempo real compõe fundos translúcidos e lê as paradas de cor de gradientes: texto que reprova só na parada extrema, mas passa no meio do gradiente, sai como REVIEW; texto de logotipo (`logo`, `wordmark`) não tem exigência de contraste. Os limites de composição são orçamentos do projeto: `project.budgets` (ou `screens[].budgets`) no manifesto, com padrões por modo (`operate`, `read`, `persuade`) em `data/rules.json`. Em sites e páginas de leitura, os detectores que só fazem sentido em app (tela rasa, links como menu, planos planos) ficam desligados.

## 2. Um comando para os portões

```bash
python3 <skill_dir>/scripts/aura_check.py --manifest design/screen-manifest.json --tokens design/tokens.css \
  --bible design/DESIGN-BIBLE.md --shell design/SHELL-CONTRACT.md --project design/telas --out design/audit \
  [--base-url http://127.0.0.1:4188] [--baseline design/audit-antes] [--smoke-interact] --strict
```

Ele roda, conforme os caminhos informados:
- contraste dos tokens (WCAG + APCA, paridade semântica, separação de planos pelo estilo de profundidade);
- linter estático;
- captura no navegador nas larguras e temas do manifesto, com estado pós-clique, peso da página, movimento com `prefers-reduced-motion` e comparação com a linha de base;
- completude da Bíblia (com zonas do manifesto);
- sincronia entre Bíblia, shell e tokens.

O resultado consolidado fica em `aura-check.json`. Portão sem a entrada correspondente aparece como "não rodou" e, com `--strict`, falha a verificação: sem ele o veredito é **pendente de verificação**. Num ajuste pontual que de fato dispensa algum portão, declare `--partial` e escreva o motivo no relatório. O relatório da captura anterior é apagado antes de cada rodada, então um navegador que não abriu nunca devolve resultado velho. Os scripts também rodam isolados (`audit_contrast.py`, `lint_design_aura.py`, `capture_and_audit.mjs`, `render_design_bible.py --check`).

### Estados, ação primária e acessibilidade extra
- **Estados declarados** em `screens[].states` com caminho (`query`, `hash`, `file`, `route`, `click`) viram capturas `tela@estado`. Estado sem caminho e sem `covered_by` fica pendente (`DA-AUDIT-COVERAGE`).
- **Ação primária**: o auditor procura `primaryAction` pelo rótulo ou pelo `selector`, rola até ela e confere se está visível e sem nada por cima (`DA-REACHABLE`, HIGH). Não achar pelo rótulo ou achar desabilitada sai como REVIEW.
- **Zoom de 200%** (metade da largura desktop) e **cores forçadas** rodam uma vez por tela, com capturas `-zoom200` e `-forced-colors` para o crítico. Rolagem horizontal fora de tabelas, texto cortado e controle que perde o contorno saem como REVIEW (`DA-ZOOM-REFLOW`, `DA-FORCED-COLORS`). `--no-a11y-extra` desliga.
- **Histórico de rodadas**: `aura_check.py --log design/aura-log.jsonl` acrescenta um resumo por rodada (totais, portões pulados e regras mais frequentes). Ao fim do projeto ele mostra onde a skill ou a direção ainda falham.

### Cobertura declarada
- `screens[].viewports` define larguras por tela (`"desktop"`, `"1920x1080"`, `"mobile-360x800"`); `project.vitrineViewports` cobre a vitrine.
- `clickSelector` + `afterClickSelector` verificam o estado aberto. Estados que pedem preparo vão para uma jornada E2E.
- Tela, largura ou estado declarado sem captura aparece como `DA-AUDIT-COVERAGE`: pendente, nunca aprovado.
- `data-da-workspace` marca o contêiner largo quando o vazio fora do conteúdo importa. Formulários e leitura mantêm a medida.

### Antes e depois
Em remodelação e polimento, capture o estado anterior em F0 e passe `--baseline`. O auditor gera `*-diff.png` e o percentual de pixels alterados por tela. Compare no mesmo tema, largura, dados e estado.

## 3. Jornadas (testers)

```bash
node <skill_dir>/scripts/run_workflow_probe.mjs --scenario cenario.json --out design/qa/<jornada> [--base-url ...] --strict
```

Ações disponíveis:
- navegação e entrada: `goto`, `click`, `fill`, `select`, `press`;
- teclado real: `key`, `tabTo`, `assertFocused`;
- ambiente: `setTheme`, `setReducedMotion`;
- espera: `wait`, `waitFor`;
- resultado: `assertVisible`, `assertHidden`, `assertCount` (quantidade de itens), `assertText` (com `equals` para valor exato), `assertReachable` (ação visível e não encoberta; falha como `DA-REACHABLE`);
- layout pós-ação: `assertNoOverflow`, `assertNoClip`;
- evidência: `screenshot`.

Um clique mostra que a ação existe; a assertiva mostra o resultado. O brief do tester está em [03](03-orquestracao-subagentes.md).

## 4. Crítica visual

O crítico recebe a Parte A da Bíblia e as capturas (dobra e página inteira, Light e Dark, antes e depois). Ele responde a esta rubrica e devolve até 10 achados ranqueados, agrupados pela causa:

1. **Foco.** Com a captura desfocada, o ponto focal e a ação principal continuam óbvios?
2. **Ação.** Há uma ação primária por contexto, no lugar que a plataforma ensinou?
3. **Agrupamento.** O espaço dentro dos grupos é menor que o espaço entre eles? Os alinhamentos se repetem?
4. **Cor.** A marca aparece onde a direção decidiu? A semântica só aparece com significado? O acento está contido?
5. **Profundidade.** Cada plano tem as pistas do estilo escolhido, sem excesso nem planos colados?
6. **Tipografia.** A hierarquia de tamanho e peso lê em três níveis ou menos? Números tabulares e alinhados?
7. **Conteúdo.** Dados verossímeis, nenhum dado duplicado, nada de jargão ou texto de bastidor?
8. **Fidelidade.** A tela pertence à direção escolhida e não a um template genérico?
9. **Estados.** O estado pós-ação, o vazio e o erro estão resolvidos?

Cada achado traz a evidência (recorte), a causa provável e a menor correção. Correção na causa (grade, token, componente compartilhado) vale mais que três retoques locais.

## 5. Relatório

### Escopo e cobertura
Modo, build testado, telas, larguras, temas e estados efetivamente vistos. Nunca sugira que algo não testado passou.

### Achados

| Severidade | Onde | Antes | Depois | Por quê |
|---|---|---|---|---|
| BLOCK | `telas/acesso.html:48` | `<input placeholder="E-mail">` | `<label for="email">E-mail</label><input id="email">` | `DA-B9-01`: placeholder não substitui label |

### Considerado e mantido
Dois a cinco candidatos avaliados e mantidos de propósito, com o motivo (por exemplo, um REVIEW de vazio num formulário de leitura).

### Verificação e veredito
- Registro: comandos, artefatos, capturas inspecionadas, resultado das jornadas, sincronia Bíblia/shell/tokens.
- **Aprovado** quando os portões estão sem BLOCK e HIGH, as jornadas passaram e a inspeção visual do escopo foi feita no build final.
- **Requer correção** quando a evidência mostra um problema dentro do escopo.
- **Pendente de verificação** quando falta evidência exigida (largura, tema, estado, jornada).

## 6. Entrega em um link

```bash
node <skill_dir>/scripts/serve_entrega.mjs --design-dir design --app-dir dist --port 4188
```

Em ambiente remoto, use o preview integrado ou uma URL acessível verificada com HTTP 200. Confirme que cada rota abre a tela esperada e que os downloads respondem com o arquivo real (fallback de SPA pode responder HTML no lugar).
