# Sites, landings e páginas de leitura

Sistemas servem a quem trabalha; sites convencem, explicam ou informam quem acabou de chegar. A gramática muda: mais espaço, tipografia com personalidade, direção de arte e narrativa. O ofício continua o mesmo (contraste, foco, acesso, desempenho), e a régua contra interface genérica fica mais exigente, porque é em sites que o "visual de IA" mais aparece.

Modo `persuade` para landing, vitrine e campanha; `read` para documentação, blog, relatório e portal editorial. Declare em `project.surfaceMode` ou `screens[].mode`.

## 1. Narrativa antes de layout

Escreva a página como uma sequência de perguntas que o visitante faz:

1. **O que é e para quem?** Promessa concreta no hero, com o produto real ou o resultado real.
2. **Por que acreditar?** Prova: números verdadeiros com fonte, clientes que autorizaram, demonstração.
3. **Como funciona?** O mecanismo em três a cinco passos ou uma demonstração de uma ação.
4. **E se...?** Objeções respondidas: preço, prazo, segurança, suporte.
5. **O que faço agora?** Uma chamada clara, repetida no fim.

Cada seção responde a uma pergunta. Seção que não responde a nenhuma sai.

## 2. Composição e ritmo

- **Grade:** 12 colunas com margens generosas; composições assimétricas e editoriais valem mais que blocos centralizados em série.
- **Ritmo:** alterne densidade e respiro, texto e imagem, claro e escuro. Seções iguais em sequência cansam.
- **Medida:** 60–75 caracteres em parágrafos; títulos curtos com `text-wrap: balance`.
- **Uma ação primária por seção**, com a mesma cor e forma em toda a página.
- **Bento** é uma ferramenta, não o padrão: use quando os itens têm pesos diferentes de verdade.
- **Mobile não é a versão espremida do desktop.** Reordene, corte e recomponha. A chamada principal aparece cedo.

## 3. Tipografia de site

- Escala fluida com `clamp()` (Utopia ajuda) e razão de 1,25 a 1,5.
- Uma família de display com personalidade, testada com os acentos do português, e uma família de texto confortável. Serifas editoriais são bem-vindas aqui.
- Tracking negativo nos títulos grandes; altura de linha maior no corpo.
- Auto-hospede as fontes, use `font-display: swap` e pré-carregue a fonte do hero.

## 4. Direção de arte

- **Um sistema de imagem**, escolhido na direção: fotografia (própria ou banco gratuito, com tratamento único de cor e enquadramento), ilustração (um estilo só), 3D ou interface real do produto.
- A interface real convence mais que mockup genérico; mostre o produto em uso, com dados verossímeis.
- Texturas, gradientes e shaders entram quando a direção pede e sem esconder o texto. Teste o contraste sobre a imagem na captura.
- Detalhes do domínio (o avião de uma agência, o carimbo num envio) ficam ligados a uma ação ou a um momento, nunca como papel de parede.

## 5. Motion em site

- Movimento conta a história: uma ação e seu resultado, revelação por rolagem com propósito, transição entre rotas (View Transitions).
- Scroll-driven animations em CSS antes de bibliotecas pesadas; GSAP ou Motion quando a coreografia pede.
- Rolagem suave substitui a física nativa: use pouco e nunca em leitura longa.
- `prefers-reduced-motion`: o conteúdo aparece sem deslocamento e a demonstração vira um quadro estático que conta o resultado.
- Animação nunca segura o texto nem a chamada principal.

## 6. Desempenho e técnica

- Orçamento de peso (`perfMaxKB`, requisições, fontes) declarado no manifesto; o auditor mede.
- Imagem do hero otimizada (AVIF/WebP, `fetchpriority="high"`, dimensões declaradas); o resto com `loading="lazy"`.
- HTML semântico: um `h1`, títulos em ordem, landmarks, links com texto que faz sentido fora do contexto.
- Metadados de compartilhamento (título, descrição, imagem) e favicon.
- Formulários curtos, com label visível e mensagem de erro útil.

## 7. Sinais de site genérico

Reprovam como sinal forte (corrija ou justifique):
- gradiente roxo ou azul-neon com blobs desfocados;
- "Transforme seu negócio", "Eleve sua experiência" e similares;
- eyebrow "FEATURES" e numeração decorativa;
- três cartões iguais com ícone em círculo colorido como resposta padrão;
- faixa de logos de clientes inventados, depoimentos fictícios, números arredondados sem fonte;
- mockup de laptop flutuando sobre gradiente;
- emoji como ícone;
- animação em todo elemento ao rolar.

## 8. Componentes e referências

- Seções: `discover_oss_components.py --category marketing --mode persuade` (Tailark, Launch UI, HyperUI, Preline, Magic UI, Animate UI e outros, com licenças marcadas).
- Efeitos: `--category effects` (shaders, 3D, partículas), sempre filtrados pela direção.
- Galerias para estudar estrutura: Godly, Land-book, Lapa Ninja, Siteinspire, Minimal Gallery, One Page Love, Httpster, SaaSFrame.
- Padrões de `recipes.json`: `hero-de-site`, `prova-social`, `precos`.

## 9. Verificação

- Capturas em pelo menos 1440 px, 1024 px e 390 px, Light e Dark se houver os dois.
- Página inteira além da dobra: o ritmo e os vazios aparecem na captura completa.
- Jornada: chegar, entender, agir (clicar na chamada, preencher o formulário, ver a confirmação), também só com teclado.
- Crítico visual com a rubrica de [07](07-auditoria-e-veredito.md), olhando também narrativa e direção de arte.
