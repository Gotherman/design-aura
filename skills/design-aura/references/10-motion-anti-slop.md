# Motion com vida, sem cara de template

Animacao entra para o produto parecer vivo e responder ao gesto. Ela nao entra para a tela "ter animacao".

Uma transicao de pagina, um card que abre, um botao que afunda e um sheet que segue o dedo sao desejaveis quando respondem a uma mudanca real. O mesmo efeito repetido em todo card, em toda linha e em toda troca de aba e slop: o olho aprende a ignorar, e a tarefa fica mais lenta.

O teste, antes de animar qualquer coisa:

1. O que mudou?
2. Para onde o olho deve ir?
3. O que ficaria mudo ou abrupto se esse movimento sumisse?

Se nenhuma resposta for concreta, nao anime. "Fica moderno" nao conta.

## Onde o movimento e bem-vindo

| Situacao | O que a animacao comunica | Duracao tipica |
|---|---|---|
| Troca de pagina hierarquica (lista para detalhe, e volta) | De onde vim e para onde vou | ver plataforma abaixo |
| Abertura de dialog, sheet, menu, palette, toast | Uma superficie nova passou a existir | 160–280 ms, saida mais curta |
| Press de botao, switch, checkbox, segmento | O controle recebeu o gesto | 80–140 ms |
| Card que expande, seleciona ou e arrastado | O estado *daquele* card mudou | 160–240 ms |
| Skeleton, spinner, barra de progresso | Algo ainda esta carregando | loop, so enquanto dura a espera |
| Numero que e a mensagem (saldo, contagem) | O valor em si mudou | crossfade curto, com `tabular-nums` |

## Onde o movimento atrapalha

- Cockpit e ERP: orbes, confete, borda que percorre o card, texto que se decifra, parallax, marquee.
- Stagger em cada linha de uma tabela ou lista longa. A pessoa abre aquilo dezenas de vezes por dia.
- `hover:scale` em card grande. O layout pula e no touch nao existe hover.
- Animar a primeira pintura de um dashboard operacional alem de um fade de no maximo 120 ms no shell.
- Segurar o clique seguinte. Se a pessoa precisa esperar a animacao acabar para agir, a animacao esta longa demais.
- Informacao que so aparece no hover. No celular ela nao existe.

`transition: all`, `animate-bounce` e loop infinito fora de espera continuam reprovados pelo linter (`DA-B6-02`, `DA-B6-04`). O resto e criterio, nao banimento.

## Asimetria comum as tres plataformas

- Entrada desacelera (ease-out). Saida e mais curta e acelera (ease-in).
- Anime `transform` e `opacity`. Layout, blur e sombra em lista custam quadro.
- O gesto cancela a animacao no meio. Keyframe que reinicia do zero nao serve para controle.
- Reduced motion / remover animacoes: troca espacial vira crossfade de ate 120 ms. Estado ainda muda.
- Detalhe de domínio aprovado fica numa ação real (enviar, validar, confirmar). Não vira cenário nem um efeito diferente em cada tela.

Tokens sugeridos em `tokens.json`, sem copiar a duracao de uma plataforma para a outra:

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

O numero e teto de referencia. No iOS e no Android o que manda e a curva do sistema, interrompivel, nao o cubic-bezier colado do CSS.

## Desktop (mouse, teclado, janela)

A ponteiro e preciso e a pessoa varre a tela o dia inteiro. Resposta curta.

- Hover muda cor, borda ou elevacao em 120–160 ms. Nao escala card, linha ou painel.
- Foco visivel aparece junto com o teclado, em ate 80 ms. Nao espere o hover.
- Troca hierarquica: 16–24 px na direcao da navegacao + fade, 180–220 ms. Voltar e mais rapido, cerca de 140 ms. Irmas (abas do mesmo nivel) so fazem crossfade.
- Command palette e menu: fade + escala de 0.98 para 1 em cerca de 140 ms.
- Redimensionar painel e arrastar coluna acompanham o ponteiro sem easing atrasado.
- Atalho repete a acao na hora. A animacao nao pode engolir o segundo `Cmd+K`.
- Nao ha parallax de fundo em ferramenta.

Web: `transition-property` explicito e `@media (prefers-reduced-motion: reduce)`. View Transitions API e aceitavel para a troca de rota se a duracao respeitar a tabela e o reduced motion cair para fade.

## iOS (SwiftUI / UIKit)

O dedo esta em contato e pode mudar de ideia. A transicao boa e a que o polegar consegue segurar.

- Push e pop de `NavigationStack` usam a transicao do sistema. O swipe da borda esquerda cancela o push no meio. Nao substitua por um fade de web.
- Duracao percebida do push fica perto de 300–400 ms porque e uma mola, nao porque a tela fica bloqueada. `page-ios` no token e esse teto, nao um `ease` de CSS.
- Sheet sobe de baixo, com detent e arrasto para fechar. Rubber band fica dentro do que o UIKit ja faz.
- Tab bar troca de selecao na hora. O indicador se move; a tela inteira nao da crossfade.
- Lista para detalhe pode usar matched geometry ou zoom de navegacao quando o elemento de origem e obvio (a linha tocada). Nao invente origem.
- Toque primario: escala 0.97 no controle, nunca no card de lista inteiro.
- Haptico leve (`impact` light ou selection) na confirmacao e na troca de segmento. Nao haptico em scroll nem em cada celula.
- `UIAccessibility.isReduceMotionEnabled` / `accessibilityReduceMotion`: sem parallax, sem zoom, crossfade curto. O estado continua claro.
- 120 Hz nao e desculpa para animar bounds de celula. Transform e opacity.

## Android (Material 3 / Compose)

O sistema ja tem um vocabulario. Inventar outra mola faz o app parecer um site dentro do telefone.

- **Eixo compartilhado vertical** para hierarquia (lista para detalhe). **Eixo horizontal** para irmaos. **Fade through** quando as duas telas nao tem parentesco.
- **Container transform** quando um card ou o FAB vira a tela seguinte.
- Duracoes Material: curta 150–200 ms (controle), media 200–300 ms (superficie), longa 400–500 ms so na transicao espacial grande. `page-android` fica na media, ~250 ms, com emphasized decelerate na entrada e emphasized accelerate na saida.
- Predictive back: a superficie segue o dedo e revela o que esta atras. Nao bloqueie o gesto com um modal sem destino.
- Navigation bar virando rail em tela larga e uma transicao de container, nao um bounce.
- No maximo um FAB. O movimento dele e a dica espacial principal, nao um enfeite.
- `MotionScheme` expressivo e para produto de marca. Em Operate use o scheme padrao.
- Respeite a escala de animacao do sistema (`Settings.Global.ANIMATOR_DURATION_SCALE` e "remover animacoes"). Em Compose, o framework ja encurta; nao force `tween` que ignora isso.
- Haptico `CONFIRM` e `CONTEXT_CLICK` com parcimonia. Snackbar nao pula.
- Alvo de 48 dp nao encolhe durante a animacao.

## React Native, Flutter e PWA

Nao exporte um `transition` de CSS para os tres.

- **React Native:** Reanimated + Gesture Handler. O gesto e a fonte da verdade; a mola continua de onde o dedo soltou. No iOS, espelhe o push interrompivel. No Android, espelhe predictive back e container transform. `FlashList` nao anima entrada de linha.
- **Flutter:** `Curves.easeOutCubic` na entrada, `Curves.easeIn` na saida. Duracao de pagina 250 ms no Android e um pouco mais folgada no iOS so se o `Theme` daquela plataforma pedir. `MediaQuery.disableAnimations` zera o deslocamento.
- **PWA:** siga a coluna Desktop quando houver ponteiro e hover real. Com ponteiro coarse, siga a coluna do sistema operacional do aparelho: sheet e swipe no iOS, eixo compartilhado e back preditivo no Android. `100dvh` e safe area nao sao motion, mas a transicao nao pode cobrir o indicador home.

## O que o linter pega e o que fica para o olho

O linter marca `transition-all`, bounce, scale de hover em 105%, duracao de controle acima de 300 ms e loop infinito que nao e espera. Ele nao sabe se a troca de pagina tem motivo. Isso continua na revisao: uma animacao por mudanca de estado, nenhuma animacao para "dar vida" generica, e a curva da plataforma em vez de uma receita unica.
