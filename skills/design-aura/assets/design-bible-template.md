# Bíblia de Direção de Design — {{PROJECT_NAME}}

> **Versão do Projeto:** {{VERSION}} · **Design Aura:** `v2.5.0` · **Plataformas:** {{PLATFORMS}} · **Modo de Superfície:** {{SURFACE_MODE}} (`Operate` | `Read` | `Persuade`)

---

## 0. Contrato de plataforma
Preenchido na Fase 1, antes de cor, tipo e tela. Subagentes leem este bloco e não escolhem outro shell.

- **Trabalho:** remodelar o visual (autópsia seletiva: o que preservar vs o que corrigir) / completar / criar do zero
- **Tipo de produto:** sistema de trabalho / SaaS / app / combinação — `Operate` | `Read` | `Persuade`
- **Superfícies:** web · desktop nativo · iOS · Android. **Principal:** ...
- **Papel do Mobile (se existir):** app executivo/focado dedicado OU mesmas rotinas do desktop adaptadas
- **Stack por superfície:** web (...) · desktop (...) · iOS (...) · Android (...)
- **Quem usa e a tarefa de um segundo:** ...
- **Tema:** dark-first / light-first / os dois obrigatórios
- **Cores da marca:** sim / não. Se sim, preservam vitalidade cromática na ação (10%) e tintam a estrutura (30%) sem apagar em marrom/bege morto (`DA-B3-04`). Neutros e semântica ficam separados.
- **Detalhes do domínio:** aprovados / recusados. Para cada aprovado: ação, o que aparece, formato, duração, reduced motion, onde não entra.
- **Modelo do Orquestrador (OBRIGATÓRIO):** ...
- **Modelo dos subagentes (OBRIGATÓRIO):** ...
- **Telas-Mãe (Onda 0.5):** Desktop (`<id>`) · Mobile (`<id>`)
- **Como o trabalho se organiza** (lido no planejamento e no repositório, com as palavras do projeto): ...
- **Adaptações do molde ao vocabulário do projeto** *(adapte nomes e fluxos, NUNCA descarte cards `Z2`, gráficos OSS, ícones ou 3 zonas quando o trabalho pedir)*: ...
- **Orçamento de escopo:** total de `N` telas consolidadas (alvo `12–24`; se `> 24`, justificativa aprovada) em slices de `1–3` telas/subagente.
- **Hipóteses assumidas** (só o que o pedido não fechou): ...

## 1. Diagnóstico & Autópsia (Tolerância Zero aos 10 Blocos)
- **Contexto atual:** *(o que já existe ou quais vícios do setor precisamos evitar desde o início)*
- **Falhas banidas explicitamente:** *(ex.: branco lavado sem contorno, espaços mortos, monocromia onde urgência some, AI slop)*
- **Compromisso:** conformidade total com os **10 Blocos de Leis Inegociáveis** (`references/01-leis-inegociaveis.md`).

## 2. Direção Criativa & Assinatura Única
- **Para quem & Situação de uso:** ...
- **Prioridade em 1 segundo:** o que o operador precisa enxergar e decidir imediatamente.
- **Caráter (traduzido em comportamento observável):** *(proibido adjetivos vazios como "moderno" ou "clean")*
- **Detalhes visuais do domínio:** *(só os aprovados, cada um com o plano fechado. Ex.: avião ao enviar. Não é cenário de fundo.)*
- **Controles & Navegação:** seguem rigorosamente as convenções da plataforma (`Operate`), sem fantasias.
- **Shell por plataforma (tokens iguais, estrutura diferente):**
  - Desktop / web largo (`>= 1024px`): ...
  - Tablet (`768–1023px`): ...
  - Mobile (`< 768px` ou app nativo): terço inferior para a ação, lista no lugar da tabela, sheet em vez de modal central.

## 3. DNA da Marca & Vocabulário do Domínio
- **Essência traduzida em geometria e ritmo:** ...
- **Vocabulário oficial (botões e estados):** *(ex.: "Aprovar", "Devolver", "Indeferir", "Em dia", "Aguardando")*
- **Zero jargão técnico na tela do trabalhador (`DA-TECH-JARGON-UI`):** proibido expor termos de engenharia/infraestrutura em telas operacionais ou login (`deviceId`, `Fallback VLM`, `Dry-Run`, `SHA-256`, `Backup R2`, `PWA Mobile`, `ScreenMap`, `auto-reserva`, `Fila FIFO`).
- **Termos banidos de copy:** clichês genéricos de IA, *Lorem ipsum*, *botsplaining* e referências a sistemas terceiros (`DA-REF-COPY-LEAK`).

## 3.5 Orçamentos de Composição, Resize In-Place & Anti-Poluição *(Autossuficiente — Vale mesmo fora da skill)*
- **Topo Desktop (`DA-HEADER-STACK-BLOAT`):** máximo **2 barras horizontais** (`<= 210px` totais) antes do primeiro dado real; máximo **4–5 abas de filtro** visíveis + menu `"Mais status"` (`DA-TAB-OVERFLOW`).
- **Estrutura de Trabalho por Resize In-Place (Filas & Conferência):** **PROIBIDO** jogar fila + 8 abas + resumo duplicado + documento + barra de decisão todos de uma vez na tela! Abra na **Fila Limpa (100% da área útil)** → clicar numa pendência faz um **resize suave na mesma área** abrindo a **Conferência & Aprovação Focada** em 3 blocos únicos (1. Identificação única sem duplicar nome/unidade 2×; 2. Evidência/Documento real do trabalho; 3. Rodapé estrutural `flex-shrink: 0` com ações coesas).
- **Zero Duplicação (`Single Source of Truth`) & Zero Selo-Eco (`DA-BADGE-ECHO`):** cada dado (colaborador, unidade, solicitante) aparece **1 única vez** no painel; proibido repetir o mesmo badge-eco em cada card de uma aba que já diz aquele estado.
- **Orçamento Mobile (`DA-MOBILE-HERO-BLOAT`):** Hero + avisos no topo ocupam no máximo **`38%` (`<= 310px` em `390×844`)** para a lista acionável principal aparecer imediatamente acima da dobra.
- **Isolamento Estrito de Controles de Demo/Simulador:** seletores de cenário ou botões de simulação NUNCA entram dentro da barra operacional nem no rodapé de decisão real (ficam num drawer/rodapé discreto de demonstração).

## 4. Sistema Cromático (Marca no Workspace + Paridade Light/Dark)
- **Fim do Monobloco Cinza (Dark) e do Tudo-Branco (Light):** traga variações fortes e suaves da **cor oficial da marca** da Sidebar para dentro da área de trabalho — cabeçalhos de painel (`--surface-brand-header`), cards em destaque (`--surface-brand-panel`), abas ativas (`--primary` sólido com `--on-primary`) e bordas estruturais. Preto e cinza entram apenas como apoio sutil.
- **Light Mode (Aterrado / Alto Contraste):** `Z0` `{{LIGHT_Z0}}` · `Z1` `{{LIGHT_Z1}}` (`>= 1.18:1` vs `Z2`) · `Z2` `{{LIGHT_Z2}}` · `border-subtle` (`>= 1.85:1` vs `Z2`, ideal `2.0–2.4:1`) · Primária `{{LIGHT_PRIMARY}}` · Acento `{{LIGHT_ACCENT}}`
- **Dark Mode (Profundidade Real `Z0→Z4` + Marca):** `Z0` `{{DARK_Z0}}` · `Z1` `{{DARK_Z1}}` · `Z2` `{{DARK_Z2}}` (`>= 1.08:1` vs `Z1`, `border-subtle >= 1.25:1`, `--rim-highlight`) · Primária `{{DARK_PRIMARY}}` · Acento `{{DARK_ACCENT}}`
- **Paridade Semântica Obrigatória (`DA-SEMANTIC-HUE-PARITY`):** a família de cor de cada estado é **idêntica** no Light e no Dark — **NUNCA** erro vermelho no Claro e rosa pastel (`#FDA4AF`) no Escuro, nem sucesso esmeralda no Claro e verde-água neon com texto preto no Escuro:
  - **Erro / Falha / Indeferir:** Vermelho real nos dois modos (`--danger` / `--danger-surface` / `--danger-border` / `--danger-text`)
  - **Sucesso / Aprovar:** Verde esmeralda real nos dois modos (`--success` / `--success-surface` / `--success-border` / `--success-text`)
  - **Atenção / Pendente:** Âmbar real nos dois modos (`--warning` / `--warning-surface` / `--warning-border` / `--warning-text`)
  - **Marca / Ativo / Info:** Azul/cor da marca coesa nos dois modos (`--primary` / `--primary-surface` / `--primary-border` / `--primary-text`)
- **Auditoria de contraste:** validado por `audit_contrast.py --strict` (WCAG AA + APCA + `DA-SEMANTIC-HUE-PARITY` + `DA-DARK-FLAT-MONOLITH` + `DA-LIGHT-WASHED-OUT`).

## 5. Arquitetura de Profundidade em 5 Planos (`Z0 → Z4`)
| Plano | Papel | Light Mode | Dark Mode |
|---|---|---|---|
| `Z0` Poço / Recesso | Trilhos de abas, inputs em repouso | Base mais baixa + borda sutil | Mais escuro que `Z1` |
| `Z1` Canvas Base | Fundo da janela/viewport | Superfície aterrada sem clarão | Grafite/Ardósia profundo |
| `Z2` Painéis & Cartões | Unidades reais de conteúdo | Contorno `1.25px` nítido + sombra 3 camadas | `+8%` luminosidade + borda topo sutil |
| `Z3` Flutuante | Popovers, menus, barras de ação, `⌘K` | Fundo elevado + sombra média | `+14%` luminosidade + borda `14%` |
| `Z4` Modal / Sheet | Drawers, diálogos, bottom sheets | Backdrop + sombra alta | `+18%` luminosidade + borda `18%` |

## 6. Sistema Tipográfico
- **Display:** `{{FONT_DISPLAY}}` (`tracking: -0.025em`, `text-wrap: balance`)
- **UI / Corpo:** `{{FONT_UI}}` (base `14px–16px`, `text-wrap: pretty`, medida `65–75ch`)
- **Mono / Telemetria:** `{{FONT_MONO}}` (`font-variant-numeric: tabular-nums` obrigatório em dados)

## 7. Escala Espacial (4/8px) & Raios Concêntricos
- **Espaçamentos permitidos:** `4, 8, 12, 16, 20, 24, 32, 40, 48, 64px` (+ `2, 6, 10, 14px` internos de controle).
- **Raios concêntricos:** Container `20px` + padding `8px` → Interno `12px`; Card `16px` + padding `8px` → Interno `8px`.

## 8. Arsenal com caminho para o subagente
Cada componente, card ou elemento vindo de código aberto ou de um produto estudado entra nesta tabela. Sem caminho, o subagente não usa.

| Peça | Onde entra | Licença | Uso | Caminho | O que copiar e como re-tematizar |
|---|---|---|---|---|---|
| Nome do componente | Tela ou shell | MIT / Apache-2.0 / BSD / ISC | Dependência, registry ou só referência | URL do repo, comando de instalação e caminho do arquivo no projeto depois de copiado | ... |

## 8.1 Anatomia que o subagente copia
Prosa não basta. Antes da aprovação, esta seção traz CSS real, nos dois temas, usando só `var(--token)`. Sem isto, cada tela inventa um botão.

- **Variáveis:** tabela `token` → hex claro → hex escuro. O arquivo é `tokens.css`. Proibido hex solto na tela.
- **Ordem do shell:** a sequência do DOM (faixa, navegação, miolo, inspector). Igual em todas as telas daquela largura.
- **Botão primário:** onde ele fica no desktop, no tablet e no telefone. Um lugar por largura, não um botão solto em cada canto.
- **Estados:** repouso, hover, ativo, foco e desabilitado de botão, campo, linha de tabela e item de navegação.
- **Seleção e gráfico:** cor da linha selecionada e a única cor de série. Sem uma segunda paleta.
- **Toast, gaveta e vazio:** canto, largura, e o desenho do esqueleto.

```css
.btn-primary { background: var(--accent); color: var(--on-accent); }
```

## 9. Matriz de Componentes & Estados Obrigatórios
- **Botões:** máximo 1 primário por dobra; `iconPad = textPad - 2px`; `active:scale-[0.97]`.
- **Formulários:** `<label>` sempre visível + `:focus-visible` `2px` + erro acionável junto ao campo.
- **Estados:** `loading` (skeleton), `empty` (com CTA), `error` (com retry), `success` (toast com Desfazer).
- **Motion (guia 10):** anima só mudança de estado. Uma linha para desktop, uma para iOS e uma para Android.
  - Desktop: hover de cor/borda 120–160 ms; página hierárquica ~200 ms; sem scale em card.
  - iOS: push do sistema, interrompível pelo swipe, teto ~350 ms; sheet com detent; haptico só na confirmação.
  - Android: eixo compartilhado ou container transform, ~250 ms, predictive back, scheme padrão em Operate.
  - Quieto de propósito: ...
  - Signature move único: ...

## 10. Arquitetura do trabalho nesta tela
Nomes e zonas saem do fluxo real. Não copie Agora / Em Rota / Radar se o negócio não fala assim.

- **O que a pessoa decide primeiro:** ...
- **O que fica visível ao mesmo tempo:** ...
- **O que é fila, o que é documento, o que é consulta:** ...
- **Como volta:** ...
- **Onde estou / para onde vou / o que posso fazer / próximo passo:** ...
- **O que ficou de fora desta tela, e em qual tela mora:** ...

## 11. Mapa Completo de Telas & Dados Fictícios Compartilhados

### Dados Fictícios Oficiais (Todos os Subagentes Devem Usar Estes Valores)
- **Empresa / Produto:** ...
- **Operadores / Perfis:** ...
- **Métricas & Alertas integrados:** ...

### Inventário de Telas (`100%` mapeado no `screen-manifest.json`)
| ID | Tela | Arquivo / Rota | Plataforma | Módulo | Conexões de Saída |
|---|---|---|---|---|---|
| `...` | `...` | `...` | `...` | `...` | `...` |

## 12. Portões CDO de Aprovação (Saída Onda 2 + Onda 3 QA E2E)
- [ ] `audit_contrast.py tokens.css --strict` verde (Light & Dark + `DA-SEMANTIC-HUE-PARITY` + `DA-DARK-FLAT-MONOLITH` + `DA-LIGHT-WASHED-OUT >= 1.85:1`)
- [ ] `lint_design_aura.py <dir> --strict` com `0` bloqueios (`DA-TECH-JARGON-UI`, `DA-BADGE-ECHO`, 10 Blocos)
- [ ] `capture_and_audit.mjs` verde em Desktop e Mobile (Dark & Light + pós-clique `--smoke-interact`)
- [ ] **Fase 4.5 (Onda 3 · Subagentes Testers E2E):** fluxos clicáveis validados com `run_workflow_probe.mjs` (0 falhas P0/P1, zero erro JS/404)
- [ ] `100%` das telas navegáveis em link único via `entrega.html` (`serve_entrega.mjs` · `Mapa Figma · App ao Vivo · Preview · Galeria · Bíblia + PDF`)

## 13. Histórico de Revisões *(Anti-Drift em Refinamentos · Modo 3)*
> Sempre que um refinamento alterar tokens, composição, paridade semântica ou componentes, atualize cirurgicamente as seções afetadas acima, sincronize `SHELL-CONTRACT.md` + `DESIGN-BIBLE.pdf` e registre 1 linha aqui.

| Versão | Data | O que mudou na Bíblia | Artefatos sincronizados |
|---|---|---|---|
| `v1.0` | `YYYY-MM-DD` | Direção inicial aprovada (Portão 1) | `tokens.json`, `tokens.css`, `DESIGN-BIBLE.pdf`, `SHELL-CONTRACT.md` |


### Evidência da revisão

- Modo, escopo, deltas aplicáveis e exceções com motivo.
- Pilotos e estado anterior comparável, quando disponível. Aprovação ou autorização para seguir direto.
- Build, cobertura declarada no manifesto e relatórios da inspeção visual e do QA funcional.
- Decisões de acabamento e interação com referência à implementação local. Rotas e artefatos publicados verificados por conteúdo.
