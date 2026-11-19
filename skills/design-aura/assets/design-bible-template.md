# Bíblia de Direção de Design — {{PROJECT_NAME}}

> **Versão:** {{VERSION}} · **Plataformas:** {{PLATFORMS}} · **Modo de Superfície:** {{SURFACE_MODE}} (`Operate` | `Read` | `Persuade`)

---

## 1. Diagnóstico & Autópsia (Tolerância Zero aos 10 Blocos)
- **Contexto atual:** *(o que já existe ou quais vícios do setor precisamos evitar desde o início)*
- **Falhas banidas explicitamente:** *(ex.: branco lavado sem contorno, espaços mortos, monocromia onde urgência some, AI slop)*
- **Compromisso:** conformidade total com os **10 Blocos de Leis Inegociáveis** (`references/01-leis-inegociaveis.md`).

## 2. Direção Criativa & Assinatura Única
- **Para quem & Situação de uso:** ...
- **Prioridade em 1 segundo:** o que o operador precisa enxergar e decidir imediatamente.
- **Caráter (traduzido em comportamento observável):** *(proibido adjetivos vazios como "moderno" ou "clean")*
- **1 Assinatura Visual do Domínio:** *(ex.: trilha de status estilo despacho com ETA em tempo real)*
- **Controles & Navegação:** seguem rigorosamente as convenções da plataforma (`Operate`), sem fantasias.

## 3. DNA da Marca & Vocabulário do Domínio
- **Essência traduzida em geometria e ritmo:** ...
- **Vocabulário oficial (botões e estados):** *(ex.: "Liberar lote", "Em trânsito", "Atrasado 2d")*
- **Termos banidos de copy:** clichês genéricos de IA, *Lorem ipsum*, *botsplaining*.

## 4. Sistema Cromático (60 · 30 · 10) & Semântica
- **Light Mode (Aterrado / Alto Contraste):** `Z0` `{{LIGHT_Z0}}` · `Z1` `{{LIGHT_Z1}}` · `Z2` `{{LIGHT_Z2}}` · Primária 30% `{{LIGHT_PRIMARY}}` · Acento 10% `{{LIGHT_ACCENT}}`
- **Dark Mode (Luminosidade Progressiva):** `Z0` `{{DARK_Z0}}` · `Z1` `{{DARK_Z1}}` · `Z2` `{{DARK_Z2}}` · Primária 30% `{{DARK_PRIMARY}}` · Acento 10% `{{DARK_ACCENT}}`
- **Semântica funcional:** Sucesso (`{{SEM_SUCCESS}}`), Alerta (`{{SEM_WARNING}}`), Crítico (`{{SEM_DANGER}}`), Informação (`{{SEM_INFO}}`).
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

## 8. Arsenal Open-Source Escolhido
Saída de `discover_oss_components.py`. Galeria não ocupa a coluna de licença permissiva.

| Papel | Fonte | Licença | Uso (Referência / Dependência / Registry) | O que foi aproveitado e re-tematizado |
|---|---|---|---|---|
| ... | ... | MIT / Apache-2.0 / BSD / ISC | ... | ... |

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

## 10. Arquitetura de Fluxos & Horizontes Temporais
- **Horizonte 1 · Agora:** ...
- **Horizonte 2 · Em Rota:** ...
- **Horizonte 3 · Radar:** ...

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
