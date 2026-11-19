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

## 3. Profundidade Física (Light Mode vs Dark Mode)

### Light Mode: Contorno Nítido + Sombra-como-Borda (3 Camadas)
Bordas opacas grossas pesam, e bordas de `6–8%` somem em telas lavadas. Combine contorno perceptível ou sombra em 3 camadas:
```css
:root {
  --shadow-card:
    0 0 0 1px rgba(15, 23, 42, 0.10),
    0 1px 2px -1px rgba(15, 23, 42, 0.08),
    0 4px 10px -2px rgba(15, 23, 42, 0.06);
}
```
- **Nunca substitua divisores internos** (`border-bottom` de linhas de tabela, separadores horizontais) por `box-shadow` — divisores de layout devem permanecer como bordas finas.

### Dark Mode: Hierarquia por Luminosidade de Superfície
Em Dark Mode, **sombras pretas chapadas desaparecem** e não criam elevação real. Construa os 5 planos `Z0→Z4` subindo a luminosidade (`L` em OKLCH/HSL) progressivamente + borda sutil translúcida:
- `Z0` Poço/Recesso: `#080D14`
- `Z1` Canvas Base: `#0D1520`
- `Z2` Card/Painel: `#131E2E` + `1px solid rgba(255, 255, 255, 0.10)` + topo `inset 0 1px 0 rgba(255, 255, 255, 0.06)`
- `Z3` Popover / Dock: `#19273C` + `1px solid rgba(255, 255, 255, 0.14)`
- `Z4` Modal / Sheet: `#1F3049` + `1px solid rgba(255, 255, 255, 0.18)`

---

## 4. Tipografia de Precisão

- **`font-variant-numeric: tabular-nums`**: obrigatório em tabelas numéricas, saldos, moedas, percentuais, badges de contagem, timers e relógios. Evita que os números dancem quando o valor atualiza.
- **`text-wrap: balance`**: obrigatório em headings (`h1`–`h3`) e títulos curtos (`<= 6 linhas`) para evitar uma palavra solitária na última linha.
- **`text-wrap: pretty`**: padrão em parágrafos, descrições de card, tooltips e captions (`< 10 linhas`) para evitar órfãs tipográficas.
- **Anti-aliasing no root**: aplique `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;` uma única vez no `html`/`body`.
- **Medida e Tracking**: corpo entre `60–75ch`; display grande com tracking `-0.02em` a `-0.035em` (piso `-0.04em`).

---

## 5. Iconografia Consistente

- **Uma única família por superfície** (Phosphor Duotone/Regular, Lucide, Heroicons, SF Symbols ou Material Symbols). Nunca misture espessuras ou estilos diferentes.
- **Stroke casado com peso tipográfico** (grade 24px): texto `400` → ícone `1.5px`; texto `500–600` → ícone `2px`; `700` → `2.25–2.5px`.
- **Outline no padrão, Fill apenas no estado ativo** (ex.: aba selecionada, favorito marcado).
- **Um SVG com `currentColor`**: deixe CSS controlar hover, ativo e disabled em vez de manter dois arquivos de imagem.
- Ícone puramente decorativo junto de rótulo visível recebe `aria-hidden="true"`; botão somente-ícone exige `aria-label`.

---

## 6. Motion Interrompível & Performance

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
