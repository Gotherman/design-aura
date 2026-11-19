# Micro-Craft, Precisão Geométrica & Motion (Engenharia de Acabamento)

O que separa uma interface "que funciona" de uma interface **nível Apple / Linear / Stripe** não são efeitos chamativos — é a soma disciplinada de matemática óptica, física de movimento e acabamento em cada pixel que o olho sente mesmo sem saber explicar.

---

## 1. Precisão Geométrica & Raios Concêntricos

### Fórmula da Concentricidade (Obrigatória para `padding <= 24px`)
Quando dois elementos arredondados estão aninhados (card + imagem interna, card + botão interno, barra de segmento + pílula ativa):
```text
Raio Externo = Raio Interno + Padding entre eles
(ou: Raio Interno = Raio Externo - Padding)
```
- **Certo**: container `border-radius: 20px; padding: 8px;` e filho `border-radius: 12px;` (`20 - 8 = 12`).
- **Errado**: container `border-radius: 12px; padding: 8px;` e filho `border-radius: 12px;` (os cantos ficam visualmente beliscados).
- Quando o padding for maior que `24px`, trate como camadas independentes.

### Escala Espacial Base 4px / 8px
- Use exclusivamente: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64px` (e dentro de controles compactos: `2, 6, 10, 14px`).
- **Zero magic numbers** como `13px`, `17px`, `19px`, `11px` em margens ou gaps.
- Irmãos com a mesma função (linhas de lista, cards de uma grade) têm espaçamento idêntico.
- **Lei da Proximidade**: sempre mais espaço **acima** de um título de seção do que abaixo dele (`margin-top > margin-bottom`), conectando visualmente o título ao seu conteúdo.

---

## 2. Alinhamento Óptico

A geometria matemática às vezes parece torta ao olho humano; corrija opticamente:
- **Botão com Texto + Ícone**: reduza `2px` do padding do lado do ícone (`padding-left: 16px; padding-right: 14px` quando o ícone está à direita).
- **Ícone de Play (Triângulo)**: desloque `+2px` para a direita (`margin-left: 2px`) dentro de botões circulares ou quadrados para o centro de massa coincidir com o centro do círculo.
- **Ícones assimétricos (setas, estrelas, carets)**: ajuste o `viewBox` ou `translateX` de `1px` para centralizar visualmente.

---

## 3. Profundidade Física Tátil em 5 Camadas (`Z0 → Z4` · Light & Dark)

Um card chapado com 1 borda simples parece 2D mesmo passando no WCAG. Construa profundidade real combinando **5 técnicas táteis**:

### 3.1 Chanfro Óptico Duplo (`Double-Ring Bevel`) nos Cards `Z2`
```css
/* Dark Mode: Obsidiana com subtom arquitetonico sutil (S=18-25%) + luz zenital + chanfro duplo */
.panel-z2 {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.045) 0%, rgba(255, 255, 255, 0) 38%), var(--surface-z2);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-card-md);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.10),
    inset 0 0 0 1px rgba(255, 255, 255, 0.025),
    0 1px 2px rgba(0, 0, 0, 0.34),
    0 8px 20px -6px rgba(0, 0, 0, 0.42),
    0 18px 36px -14px rgba(0, 0, 0, 0.34);
}

/* Light Mode Ancorado pela Marca: Porcelana fria + contorno nitido + sombras tintadas pelo marinho */
html[data-theme="light"] .panel-z2 {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
  border: 1px solid var(--border-subtle);
  box-shadow:
    inset 0 1px 0 #FFFFFF,
    0 1px 2px rgba(14, 41, 75, 0.08),
    0 6px 16px -4px rgba(14, 41, 75, 0.12),
    0 14px 28px -10px rgba(14, 41, 75, 0.08);
}
html[data-theme="light"] .sidebar,
html[data-theme="light"] .auth-brand-pane,
html[data-theme="light"] .card-brand-hero {
  background: linear-gradient(155deg, var(--surface-brand-dark, #0E294B) 0%, var(--surface-brand-dark-2, #163E70) 100%);
  color: var(--on-brand-dark, #F8FAFC);
}
html[data-theme="light"] .panel-head,
html[data-theme="light"] .data-table th {
  background: var(--surface-tint-soft, #E6F0FD);
  border-bottom-color: var(--border-tint, #B5CEF0);
  color: var(--surface-brand-dark, #0E294B);
}
```

### 3.2 Anatomia em 2 Planos dentro de Painéis Compostos + Poços `Z0` + Card-Rei da Marca (`.card-brand-hero`)
- **Painéis compostos** (tabelas, gráficos, formulários): separe o cabeçalho e o rodapé de resumo em uma faixa sutil (`background: color-mix(in srgb, var(--surface-z3) 55%, var(--surface-z2))` + hairline `1px`), evitando caixotes lisos do topo à base.
- **Poços `.well-z0`** (trilhos `.subtabs`, `.seg`, inputs, colunas Kanban): recesso físico com `box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.30), 0 1px 0 rgba(255, 255, 255, 0.05)`.
- **Card-Rei Institucional (`.card-brand-hero`):** destaque o painel focal de cada tela com a cor da marca dizendo *"Estou aqui!"*:
  ```css
  .card-brand-hero {
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 20%, var(--surface-z2)) 0%, var(--surface-z2) 62%);
    border: 1px solid color-mix(in srgb, var(--primary) 36%, var(--border-subtle));
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14), 0 12px 28px -10px rgba(0, 0, 0, 0.45);
  }
  ```
- **Elevação Interativa em Linhas Clicáveis (`tbody tr:hover`):** fundo `--surface-z3`, filete indicador esquerdo `box-shadow: inset 3px 0 0 var(--primary)` e transformação do link `"Abrir →"` em pílula preenchida.

---

## 4. Tipografia de Precisão (Números Proporcionais Tabulares vs Mono Técnico)

- **Sans-Serif Executiva (`Geist` / `Inter` / `IBM Plex Sans`) + `.num`:** valores financeiros (`R$ 1.248.920,50`), KPIs grandes, percentuais e colunas numéricas usam a **sans-serif principal com `font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1`** — alinha perfeitamente sem criar buracos largos de monoespaçada!
- **Mono Técnico (`.mono` — `Geist Mono` / `JetBrains Mono`):** reservado exclusivamente para CNPJ, linha digitável de boleto, IDs/protocolos, hashes e tags `<kbd>`.
- **`text-wrap: balance`** em títulos (`h1–h3`), **`text-wrap: pretty`** em parágrafos e **`-webkit-font-smoothing: antialiased`** no root.

---

## 5. Iconografia de Alta Precisão, Emblemas Spotlight & Micro-Chips de Status (`v2.2.0` · Anti-Ícone Fraco)

Elimine ícones genéricos borrados em quadrados marrons chapados e pílulas de tempo/status sem vida:

1. **SVG Vetorial Nítido (`Tabler 1.75px` / `Solar Duotone` / `Lucide` / `Heroicons Micro 16px` / `<iconify-icon>`):**
   - Prefira `<svg>` inline ou Duotone em 2 camadas (base `fill-opacity="0.18"` + traço `stroke-width="1.75"`) em vez de fontes de ícones borradas;
   - **Vocabulário Semântico do Domínio (`DA-ICON-GENERIC-REPEAT`):** PROIBIDO repetir `ph-bank` (templo grego) ou `ph-warning-circle` (`!`) em 5 cards diferentes! Use `plane-departure`/`receipt-tax` para fatura aérea, `file-certificate`/`shield-check` para certidão, `gavel` para pregão, e **Monogramas Vetoriais (`.bank-emblem`: `BB`, `CX`, `ST`, `BTG`)** para bancos!

2. **Emblema de Ícone com Spotlight Radial e Duplo Anel (`.icon-emblem` — substitui quadrados marrons chapados):**
   ```css
   .icon-emblem {
     width: 38px; height: 38px; border-radius: 10px;
     display: inline-flex; align-items: center; justify-content: center; flex: none;
     background: radial-gradient(120% 120% at 25% 18%,
       color-mix(in srgb, var(--tone, var(--primary)) 32%, transparent) 0%,
       color-mix(in srgb, var(--tone, var(--primary)) 7%, var(--surface-z3)) 75%,
       var(--surface-z2) 100%);
     border: 1px solid color-mix(in srgb, var(--tone, var(--primary)) 40%, var(--border-subtle));
     color: var(--tone, var(--primary));
     box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.20), 0 4px 10px -2px rgba(0, 0, 0, 0.30);
   }
   .icon-emblem svg { width: 18px; height: 18px; filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.32)); }
   ```

3. **Pílula de SLA / Janela 24h com Anel SVG Circular (`.chip-sla` — substitui `[ 41 min ]` e `[ Janela aberta: 22h 18m ]` chapados):**
   - Usa **`border-radius: 8px`** (squircle técnico, não oval `999px` em tudo), chanfro `inset 0 1px 0 rgba(255,255,255,0.14)`, um **anel `<svg width="14" height="14" viewBox="0 0 16 16">` com `stroke-dasharray`** mostrando a fração real do prazo consumido, rótulo de contexto (`SLA` / `Janela 24h`) e valor tabular em negrito (`41m` / `22h 18m`).

4. **Chip de Status com Halo Duplo + Glifo Vetorial (`.chip-status`) & Chip Bipartido (`.chip-kv`):**
   - Em vez de uma bolinha CSS morta (`[ • Transbordo ]`), use ponto luminoso com halo (`box-shadow: 0 0 0 3px color-mix(in srgb, var(--tone) 24%, transparent)`) ou micro-ícone SVG de transição (`13px`, ex.: `⇄` para transbordo).
   - Para métricas rotuladas (`[ Nota | 96 ]`, `[ Atraso | 2d ]`, `[ Regra | #04 ]`), use `.chip-kv` bipartido (compartimento esquerdo `--surface-z0`, direito semântico calibrado).

---

## 6. Motion de controle

A decisão do que anima, e a curva de desktop, iOS e Android, está em [10-motion-anti-slop.md](10-motion-anti-slop.md). Esta seção guarda só o acabamento que vale nas três quando o movimento já tem motivo.

## 6.1. Performance do controle

- **PROIBIDO `transition: all` / `transition-all`**: especifique sempre as propriedades exatas (`transition-property: transform, background-color, border-color, opacity`).
- **CSS Transitions para controles interativos** (hover, drawer, accordion, tabs, switches): se o usuário cancelar no meio, a transição interpola suavemente de volta ao estado atual; `@keyframes` reiniciam do zero e quebram a sensação tátil — reserve keyframes apenas para entradas únicas (`fadeInUp`) ou spinners reais.
- **Assimetria Enter vs Exit**: saídas devem ser **mais rápidas e discretas** que entradas (`enter: 200–280ms ease-out` / `exit: 120–160ms ease-in`).
- **Feedback de toque (`active:scale-[0.97]`)**: escala entre `0.96` e `0.98` ao pressionar botões/controles (nunca `< 0.95`, que parece elástico demais; nunca em cards grandes).
- **`will-change` cirúrgico**: apenas `transform` ou `opacity` em elementos animados continuamente; nunca `will-change: all`.
- **`prefers-reduced-motion: reduce`**: obrigatório reduzir/remover deslocamentos e manter apenas crossfades instantâneos (`<= 120ms`).

---

## 7. Superfícies do Navegador Tematizadas (Assinatura de Acabamento)

Nunca deixe padrões crus do navegador vazarem sobre o seu Design System:
- **`::selection`**: fundo da marca com contraste legível.
- **`caret-color`**: cor primária/acento nos inputs.
- **`:focus-visible`**: anel nítido `2px` com `outline-offset: 2px` em todos os controles focáveis.
- **Scrollbars customizadas discretas** (`scrollbar-width: thin` + `::-webkit-scrollbar` casando com `Z0`/`Z2`).
- **`text-underline-offset: 3px`** e `text-decoration-thickness: 1.5px` em links de texto.
