# Motion com vida, sem cara de template

Sites e páginas têm regras de motion próprias em [11](11-sites-e-paginas.md). O gesto de assinatura do domínio (por exemplo, um avião ao enviar) é definido na direção e registrado na Bíblia com ação, formato, duração, reduced motion e onde não entra.

Animação entra para o produto parecer vivo e responder ao gesto. Ela não entra para a tela "ter animação".

Uma transição de página, um card que abre, um botão que afunda e um sheet que segue o dedo são desejáveis quando respondem a uma mudança real. O mesmo efeito repetido em todo card, em toda linha e em toda troca de aba é slop: o olho aprende a ignorar, e a tarefa fica mais lenta.

O teste, antes de animar qualquer coisa:

1. O que mudou?
2. Para onde o olho deve ir?
3. O que ficaria mudo ou abrupto se esse movimento sumisse?

Se nenhuma resposta for concreta, não anime. "Fica moderno" não conta.

## Onde o movimento é bem-vindo

| Situação | O que a animação comunica | Duração típica |
|---|---|---|
| Troca de página hierárquica (lista para detalhe, e volta) | De onde vim e para onde vou | ver plataforma abaixo |
| Abertura de dialog, sheet, menu, palette, toast | Uma superfície nova passou a existir | 160–280 ms, saída mais curta |
| Press de botão, switch, checkbox, segmento | O controle recebeu o gesto | 80–140 ms |
| Card que expande, seleciona ou é arrastado | O estado *daquele* card mudou | 160–240 ms |
| Skeleton, spinner, barra de progresso | Algo ainda está carregando | loop, só enquanto dura a espera |
| Número que é a mensagem (saldo, contagem) | O valor em si mudou | crossfade curto, com `tabular-nums` |

## Onde o movimento atrapalha

- Cockpit e ERP: orbes, confete, borda que percorre o card, texto que se decifra, parallax, marquee.
- Stagger em cada linha de uma tabela ou lista longa. A pessoa abre aquilo dezenas de vezes por dia.
- `hover:scale` em card grande. O layout pula e no touch não existe hover.
- Animar a primeira pintura de um dashboard operacional além de um fade de no máximo 120 ms no shell.
- Segurar o clique seguinte. Se a pessoa precisa esperar a animação acabar para agir, a animação está longa demais.
- Informação que só aparece no hover. No celular ela não existe.

`transition: all`, bounce decorativo e loop infinito fora de espera saem como sinais fortes (`DA-B6-02A` a `DA-B6-02D`, `DA-B6-04`), e o auditor confere se animações infinitas param com `prefers-reduced-motion` (`DA-REDUCED-MOTION`). O resto é critério, não banimento.

## Assimetria comum às três plataformas

- Entrada desacelera (ease-out). Saída é mais curta e acelera (ease-in).
- Anime `transform` e `opacity`. Layout, blur e sombra em lista custam quadro.
- O gesto cancela a animação no meio. Keyframe que reinicia do zero não serve para controle.
- Reduced motion / remover animações: troca espacial vira crossfade de até 120 ms. Estado ainda muda.
- Detalhe de domínio aprovado fica numa ação real (enviar, validar, confirmar). Não vira cenário nem um efeito diferente em cada tela.

A direção escolhe a personalidade de motion: `none` (resposta curta e sem escala no toque, para ferramentas densas), `subtle` (o padrão) ou `expressive` (entradas mais longas e curva mais marcada, para marca e consumo). `generate_tokens.py --motion` ou o campo `motion` da direção gera as durações e a curva; as transições de página do iOS e do Android continuam as do sistema. Tokens sugeridos em `tokens.json`, sem copiar a duração de uma plataforma para a outra:

```json
"motion": {
  "press": "120ms",
  "hover": "150ms",
  "exit": "140ms",
  "enter": "220ms",
  "page-desktop": "200ms",
  "page-ios": "350ms",
  "page-android": "250ms"
}
```

O número é teto de referência. No iOS e no Android o que manda é a curva do sistema, interrompível, não o cubic-bezier colado do CSS.

## Desktop (mouse, teclado, janela)

O ponteiro é preciso e a pessoa varre a tela o dia inteiro. Resposta curta.

- Hover muda cor, borda ou elevação em 120–160 ms. Não escala card, linha ou painel.
- Foco visível aparece junto com o teclado, em até 80 ms. Não espere o hover.
- Troca hierárquica: 16–24 px na direção da navegação + fade, 180–220 ms. Voltar é mais rápido, cerca de 140 ms. Irmãs (abas do mesmo nível) só fazem crossfade.
- Command palette e menu: fade + escala de 0.98 para 1 em cerca de 140 ms.
- Redimensionar painel e arrastar coluna acompanham o ponteiro sem easing atrasado.
- Atalho repete a ação na hora. A animação não pode engolir o segundo `Cmd+K`.
- Não há parallax de fundo em ferramenta.

Web: `transition-property` explícito e `@media (prefers-reduced-motion: reduce)`. View Transitions API é aceitável para a troca de rota se a duração respeitar a tabela e o reduced motion cair para fade.

## iOS (SwiftUI / UIKit)

O dedo está em contato e pode mudar de ideia. A transição boa é a que o polegar consegue segurar.

- Push e pop de `NavigationStack` usam a transição do sistema. O swipe da borda esquerda cancela o push no meio. Não substitua por um fade de web.
- Duração percebida do push fica perto de 300–400 ms porque é uma mola, não porque a tela fica bloqueada. `page-ios` no token e esse teto, não um `ease` de CSS.
- Sheet sobe de baixo, com detent e arrasto para fechar. Rubber band fica dentro do que o UIKit já faz.
- Tab bar troca de seleção na hora. O indicador se move; a tela inteira não dá crossfade.
- Lista para detalhe pode usar matched geometry ou zoom de navegação quando o elemento de origem é óbvio (a linha tocada). Não invente origem.
- Toque primário: escala 0.97 no controle, nunca no card de lista inteiro.
- Háptico leve (`impact` light ou selection) na confirmação e na troca de segmento. Não háptico em scroll nem em cada célula.
- `UIAccessibility.isReduceMotionEnabled` / `accessibilityReduceMotion`: sem parallax, sem zoom, crossfade curto. O estado continua claro.
- 120 Hz não é desculpa para animar bounds de célula. Transform e opacity.

## Android (Material 3 / Compose)

O sistema já tem um vocabulário. Inventar outra mola faz o app parecer um site dentro do telefone.

- **Eixo compartilhado vertical** para hierarquia (lista para detalhe). **Eixo horizontal** para irmãos. **Fade through** quando as duas telas não têm parentesco.
- **Container transform** quando um card ou o FAB vira a tela seguinte.
- Durações Material: curta 150–200 ms (controle), média 200–300 ms (superfície), longa 400–500 ms só na transição espacial grande. `page-android` fica na média, ~250 ms, com emphasized decelerate na entrada e emphasized accelerate na saída.
- Predictive back: a superfície segue o dedo e revela o que está atrás. Não bloqueie o gesto com um modal sem destino.
- Navigation bar virando rail em tela larga é uma transição de container, não um bounce.
- No máximo um FAB. O movimento dele é a dica espacial principal, não um enfeite.
- `MotionScheme` expressivo é para produto de marca. Em Operate use o scheme padrão.
- Respeite a escala de animação do sistema (`Settings.Global.ANIMATOR_DURATION_SCALE` e "remover animações"). Em Compose, o framework já encurta; não force `tween` que ignora isso.
- Háptico `CONFIRM` e `CONTEXT_CLICK` com parcimônia. Snackbar não pula.
- Alvo de 48 dp não encolhe durante a animação.

## React Native, Flutter e PWA

Não exporte um `transition` de CSS para os três.

- **React Native:** Reanimated + Gesture Handler. O gesto é a fonte da verdade; a mola continua de onde o dedo soltou. No iOS, espelhe o push interrompível. No Android, espelhe predictive back e container transform. `FlashList` não anima entrada de linha.
- **Flutter:** `Curves.easeOutCubic` na entrada, `Curves.easeIn` na saída. Duração de página 250 ms no Android e um pouco mais folgada no iOS só se o `Theme` daquela plataforma pedir. `MediaQuery.disableAnimations` zera o deslocamento.
- **PWA:** siga a coluna Desktop quando houver ponteiro e hover real. Com ponteiro coarse, siga a coluna do sistema operacional do aparelho: sheet e swipe no iOS, eixo compartilhado e back preditivo no Android. `100dvh` e safe area não são motion, mas a transição não pode cobrir o indicador home.

## O que o linter pega e o que fica para o olho

O linter marca `transition-all`, bounce, scale de hover em 105%, duração de controle acima de 300 ms e loop infinito que não é espera. Ele não sabe se a troca de página tem motivo. Isso continua na revisão: uma animação por mudança de estado, nenhuma animação para "dar vida" genérica, e a curva da plataforma em vez de uma receita única.


## Revisão de gestos e interrupções

Para gestos e transições alterados, exercite abrir, cancelar, inverter e repetir rapidamente. O alvo deve acompanhar a interação e assentar no estado correto após a soltura. Verifique foco e controles críticos durante e após a transição. A alternativa com movimento reduzido preserva a relação entre ação e resultado. Em caso de lentidão, identifique a causa antes de mudar a técnica ou a biblioteca. [Gestos](https://aiforui.dev/skills/gestures) · [Performance](https://aiforui.dev/skills/animation-performance)
