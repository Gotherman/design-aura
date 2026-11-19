# Orquestração de Subagentes (Limite Máximo: 8)

O Orquestrador é o **Diretor de Design e Arquiteto-Chefe**. Subagentes são **especialistas de execução paralela** que constroem módulos sobre uma fundação já travada — nunca decidem cores, fontes ou regras globais por conta própria.

**Teto rígido:** **nunca dispare mais de 8 subagentes** no ciclo inteiro de construção de um projeto (`Onda 1 + Onda 2 <= 8`).

---

## O Padrão em 3 Ondas

```text
ONDA 0 (Orquestrador — 0 subagentes de design)
  A ordem é a Fase 1 e a Fase 2 do SKILL.md. Este arquivo não tem um atalho paralelo.
  ├─ Lê pedido, repo e docs. Pergunta só a decisão que ainda muda shell, stack ou Bíblia
  ├─ Grava o Contrato de plataforma no topo da DESIGN-BIBLE.md
  ├─ Roda design_intel.py e, para cada interação real, discover_oss_components.py
  ├─ Fecha o resto da Bíblia, inclusive o motion do guia 10 (desktop, iOS e Android separados)
  ├─ Gera tokens.json e exporta com generate_tokens.py. audit_contrast.py --strict é o Portão 0
  ├─ Fecha o mapa de telas dentro da Bíblia e o screen-manifest.json (plano, ainda sem construir)
  ├─ Gera DESIGN-BIBLE.pdf sem limite de páginas
  └─ PARA. Entrega o PDF e espera aprovação explícita antes de qualquer tela

ONDA 1 (só depois do "aprovado" — 1 a 7 subagentes)
  ├─ Constrói o shell de cada superfície do contrato (não um layout único espremido)
  ├─ Cada subagente recebe apenas seu slice do screen-manifest.json
  ├─ Constrói todas as telas reais do seu módulo usando tokens.css + shell
  └─ Garante estados (loading/empty/error), dados coerentes e links inter-módulos

ONDA 2 (Consolidação + Auditoria Visual — 1 subagente Auditor + Vitrine)
  ├─ Orquestrador confere 100% de cobertura das telas no disco e links reais
  ├─ Orquestrador roda build_figma_canvas.py (fluxo.html, preview.html, index.html)
  └─ 1 Subagente Auditor roda audit_contrast.py + lint_design_aura.py + capture_and_audit.mjs,
     inspeciona PNGs (1440px e 390px, Dark/Light), corrige ou reporta e emite Verdict
```

---

## Tabela de Dimensionamento (Nunca Desperdice Nem Sature)

| Escopo do Projeto | Total de Telas | Subagentes Onda 1 | Subagente Onda 2 | Total |
|---|---|---|---|---|
| Ajuste pontual / 1–3 telas | `1–3` | `0` (Orquestrador faz direto) | `0–1` (auditoria direta) | `0–1` |
| App focado / MVP enxuto | `4–8` | `2–3` (por fluxo ou desktop vs mobile) | `1` Auditor | `3–4` |
| Sistema completo / Multi-plataforma | `9–16` | `4–6` (por módulo + shell mobile) | `1` Auditor | `5–7` |
| Ecossistema massivo (ERP + Desktop + Mobile) | `17–30+` | **máx. `7`** (agrupando módulos menores no mesmo slice) | `1` Auditor | **máx. `8`** |

**Regra de agrupamento acima de 16 telas:** nunca exceda 7 construtores; agrupe módulos afins com 3–5 telas cada no mesmo subagente (ex.: Subagente 1 = Acesso + Portal + Configurações; Subagente 2 = Financeiro Caixa/Pagar/Receber; Subagente 3 = App Mobile 5–7 telas).

---

## Isolamento de Contexto (Por que Projetos Falham sem Isso)

### O que SEMPRE passar para cada subagente construtor:
1. **Caminho exato de saída** de cada tela do seu slice (ex.: `design/telas/desktop-caixa.html` ou `src/pages/Caixa.tsx`).
2. **Contrato do Slice** recortado do `screen-manifest.json` (ID, título, plataforma, viewport, links de entrada e links de saída exatos para que todos os botões/âncoras naveguem para rotas reais).
3. **Referência direta aos artefatos travados**: o Contrato de plataforma e as seções da `DESIGN-BIBLE.md` que cabem no slice (paleta, planos Z0–Z4, tipografia, componentes, motion daquela superfície), mais `tokens.css` e o shell da plataforma dele.
4. **Bloco de Dados Fictícios Compartilhados**: lista curta com os números, nomes, CNPJs/IDs fictícios e alertas oficiais que aparecem em múltiplos módulos (ex.: `"Fatura #7273 = R$ 75.657,36 vence em 2 dias"`).
5. **Lembrete explícito dos 10 Blocos de Leis Inegociáveis** e do checklist local antes de finalizar (`lint_design_aura.py` no próprio slice).

### O que NUNCA fazer na delegação:
- Não peça para um subagente "inventar o design system" ou "escolher cores próprias".
- Não deixe dois subagentes editarem o mesmo arquivo (`tokens.css`, `shell.css`, `index.html`, `fluxo.html`). **Arquivos compartilhados pertencem exclusivamente ao Orquestrador.**
- Não deixe o subagente pesquisar ou criar telas fora do seu slice sem registrar antes no manifesto.
- Nunca passe o histórico inteiro de conversas ou PDFs gigantes brutos no prompt do subagente; passe o contrato destilado.

---

## Template Obrigatório de Briefing de Subagente

Copie e preencha este bloco para cada subagente da Onda 1:

```markdown
### Tarefa: Construir Slice [NOME_DO_MODULO] — Projeto [NOME_DO_PROJETO]

Você é um Engenheiro de UI Sênior da Design Aura. Sua entrega deve seguir 100% a Bíblia de Design e os 10 Blocos de Leis Inegociáveis, sem criar tokens soltos ou estilos paralelos. Se o contrato diz remodelar, não reproduza a cara antiga. Cada tela do slice liga para a próxima e oferece volta.

1. **Artefatos de Fundação (LEITURA OBRIGATÓRIA antes de codar):**
   - `DESIGN-BIBLE.md`, começando pelo Contrato de plataforma. Use só os componentes da seção 8, pelos caminhos escritos lá. Não troque superfície, stack nem shell.
   - `tokens.css` (e o shell desta superfície em `<caminho>`)

2. **Telas do Seu Slice (TODAS devem ser entregues completas):**
   - `[id-1]` -> `<caminho/arquivo-1>` (Viewport: `1440x900` | Destino dos links: `<arquivo-destino>`)
   - `[id-2]` -> `<caminho/arquivo-2>` (...)

3. **Dados Fictícios Compartilhados (USE EXATAMENTE ESTES VALORES):**
   - Empresa/Sistema: <...>
   - Perfis/Usuários: <...>
   - Métricas/Alertas integrados: <...>

4. **Restrições Técnicas e os 10 Blocos:**
   - Suporte completo a `data-theme="dark"` e `data-theme="light"` via variáveis do `tokens.css`.
   - Zero `transition-all`, zero `Lorem ipsum`, zero emojis como ícones, zero card-dentro-de-card, zero gradientes roxo-neon, zero magic numbers fora da escala 4/8px.
   - `tabular-nums` em todos os valores numéricos, tabelas alinhadas à direita para números, `<label>` em todo input, `:focus-visible` preservado, touch target >= 44px em mobile.
   - Inclua estados interativos reais (tabs/filtros funcionais, modal/sheet/drawer com fechar por `Esc` e feedback com toast).

5. **Validação Local Obrigatória antes de Responder:**
   - Rode `python3 <skill_dir>/scripts/lint_design_aura.py <seus-arquivos> --strict` e corrija qualquer falha `BLOCK`.
   - Responda listando: arquivos criados/editados, links internos conectados e resultado do linter.
```

---

## Reconciliação Final de Cobertura (Checklist do Orquestrador)

Antes de chamar `build_figma_canvas.py` e o Auditor da Onda 2, o Orquestrador verifica:
1. **100% das telas listadas em `screen-manifest.json`** existem no disco e têm tamanho > 0.
2. **Zero links quebrados**: todos os `href`/`to` entre telas de módulos diferentes batem exatamente com os nomes de arquivo/rota do manifesto.
3. **Coerência de dados**: os números mostrados no Portal/Home batem com os números detalhados nas telas internas.
4. **Vitrine gerada**: executar `build_figma_canvas.py` para produzir `fluxo.html`, `preview.html` e `index.html`.
5. **Onda 2 disparada**: o subagente Auditor (ou o Orquestrador se escopo pequeno) roda os 3 portões (`audit_contrast.py`, `lint_design_aura.py`, `capture_and_audit.mjs`) e inspeciona visualmente os PNGs antes de encerrar.
