# Bíblia de Direção de Design — {{PROJECT_NAME}}

> **Versão:** {{VERSION}} · **Plataformas:** {{PLATFORMS}} · **Modo de Superfície:** {{SURFACE_MODE}} (`Operate` | `Read` | `Persuade`)

---

## 0. Contrato de plataforma
Preenchido na Fase 1, antes de cor, tipo e tela. Subagentes leem este bloco e não escolhem outro shell.

- **Trabalho:** remodelar o visual / completar / criar do zero
- **Tipo de produto:** sistema de trabalho / SaaS / app / combinação — `Operate` | `Read` | `Persuade`
- **Superfícies:** web · desktop nativo · iOS · Android. **Principal:** ...
- **Stack por superfície:** web (...) · desktop (...) · iOS (...) · Android (...)
- **Mobile web:** sim / não se aplica
- **Quem usa e a tarefa de um segundo:** ...
- **Tema:** light-first / dark-first / os dois
- **Cores da marca:** sim / não. Se sim, ocupam a ação (10%) e podem tintar a estrutura. Neutros e semântica ficam de fora dessa tinta.
- **Sinal do domínio:** sim / não. Se sim, um gesto só: ...
- **Modelo do Orquestrador:** ...
- **Modelo dos subagentes:** ...
- **Como o trabalho se organiza** (lido no planejamento e no repositório, com as palavras do projeto): ...
- **O que este projeto recusa do molde** (arquétipo, horizonte "Agora / Em Rota / Radar", paleta do catálogo): ...
- **Hipóteses assumidas** (só o que o pedido não fechou): ...

## 1. Diagnóstico & Autópsia (Tolerância Zero aos 10 Blocos)
- **Contexto atual:** *(o que já existe ou quais vícios do setor precisamos evitar desde o início)*
- **Falhas banidas explicitamente:** *(ex.: branco lavado sem contorno, espaços mortos, monocromia onde urgência some, AI slop)*
- **Compromisso:** conformidade total com os **10 Blocos de Leis Inegociáveis** (`references/01-leis-inegociaveis.md`).

## 2. Direção Criativa & Assinatura Única
- **Para quem & Situação de uso:** ...
- **Prioridade em 1 segundo:** o que o operador precisa enxergar e decidir imediatamente.
- **Caráter (traduzido em comportamento observável):** *(proibido adjetivos vazios como "moderno" ou "clean")*
- **1 Assinatura Visual do Domínio:** *(só se o contrato autorizou o sinal. Um gesto. Ex.: linha de rota, não avião em todo card)*
- **Controles & Navegação:** seguem rigorosamente as convenções da plataforma (`Operate`), sem fantasias.
- **Shell por plataforma (tokens iguais, estrutura diferente):**
  - Desktop / web largo (`>= 1024px`): ...
  - Tablet (`768–1023px`): ...
  - Mobile (`< 768px` ou app nativo): terço inferior para a ação, lista no lugar da tabela, sheet em vez de modal central.

## 3. DNA da Marca & Vocabulário do Domínio
- **Essência traduzida em geometria e ritmo:** ...
- **Vocabulário oficial (botões e estados):** *(ex.: "Liberar lote", "Em trânsito", "Atrasado 2d")*
- **Termos banidos de copy:** clichês genéricos de IA, *Lorem ipsum*, *botsplaining*.

## 4. Sistema Cromático (60 · 30 · 10) & Semântica
- **Light Mode (Aterrado / Alto Contraste):** `Z0` `{{LIGHT_Z0}}` · `Z1` `{{LIGHT_Z1}}` · `Z2` `{{LIGHT_Z2}}` · Primária 30% `{{LIGHT_PRIMARY}}` · Acento 10% `{{LIGHT_ACCENT}}`
- **Dark Mode (Luminosidade Progressiva):** `Z0` `{{DARK_Z0}}` · `Z1` `{{DARK_Z1}}` · `Z2` `{{DARK_Z2}}` · Primária 30% `{{DARK_PRIMARY}}` · Acento 10% `{{DARK_ACCENT}}`
- **Papel da marca:** ação e foco. Superfícies e texto neutro não são a mesma cor clareada.
- **Semântica funcional:** Sucesso (`{{SEM_SUCCESS}}`), Alerta (`{{SEM_WARNING}}`), Crítico (`{{SEM_DANGER}}`), Informação (`{{SEM_INFO}}`). Distintas da cor da marca.
- **Auditoria de contraste:** validado por `audit_contrast.py --strict` (WCAG AA + APCA Lc >= 60).

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

## 12. Portões CDO de Aprovação (Saída Onda 2)
- [ ] `audit_contrast.py tokens.css --strict` verde (Light & Dark)
- [ ] `lint_design_aura.py <dir> --strict` com `0` bloqueios
- [ ] `capture_and_audit.mjs` verde em `1440x900`, `768x1024`, `390x844` (Dark & Light)
- [ ] `100%` das telas do `screen-manifest.json` criadas e navegáveis via `fluxo.html`, `preview.html` e `index.html`
