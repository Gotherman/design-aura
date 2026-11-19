# Pesquisa de componentes free e open source

A interface nao fica sofisticada porque entrou um componente famoso. Fica sofisticada quando a interacao certa chega pronta, acessivel, e some dentro dos tokens do projeto.

Rode isto na Fase 2, antes de fechar a secao 8 da `DESIGN-BIBLE.md`:

```bash
python3 <skill_dir>/scripts/discover_oss_components.py \
  --need "tabela com edicao inline e colunas fixas" \
  --stack react --platform system --mode operate
```

`--online` consulta a API publica do GitHub e o registry do npm e so devolve licenca **MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause ou ISC**. Sem rede, o modo offline basta: diga que a atualidade nao foi reconfirmada.

## 1. Comece pela interacao

Escreva a necessidade como verbo, nao como "componente bonito":

- comparar muitos registros e editar uma celula
- escolher um intervalo de datas com teclado
- dividir a janela desktop em paineis persistentes
- abrir um sheet arrastavel com o polegar
- mostrar uma lista de milhares de linhas sem perder o scroll

Se a frase servir para qualquer produto, ela ainda nao e uma necessidade.

## 2. O que cada fonte e

| Tipo | Exemplos no catalogo | O que fazer |
|---|---|---|
| Registry copiavel, licenca permissiva | shadcn/ui, coss ui (ex-Origin UI), Kibo UI, Dice UI, HyperUI | Copiar, re-tematizar, assumir a manutencao |
| Dependencia mantida | Base UI, React Aria, TanStack Table, cmdk, Dockview, Mantine, gluestack, Tamagui, Forui | Instalar se o peso couber. Nao embrulhar um segundo kit por cima |
| Primitivo da plataforma | SwiftUI, Material 3 | Preferir ao kit web portado. Nao e pacote para colar |
| Galeria de referencia | Mobbin, Refero, Godly, Page Flows, Screenlane, Component Gallery, 21st.dev | Estudar fluxo e hierarquia. Nao ha codigo com licenca unica |
| Armadilha de licenca | Aceternity UI, React Bits (MIT + Commons Clause), Tailwind Plus | Pode ser bonito e ainda assim nao entrar como open source |

Sites renomados entram nesta skill em dois grupos, de proposito. Mobbin, Refero, Godly, Page Flows e Screenlane ensinam composicao de produto real. HyperUI, Kibo, Dice, coss ui, Magic UI e Cult UI entregam codigo. Misturar os dois grupos e como copiar um print e chamar de componente.

Codigo visivel no browser nao e open source. Preview publico de biblioteca paga tambem nao.

## 3. Filtro pelo modo de superficie

- **Operate** (cockpit, ERP, despacho, backoffice): o script corta pecas `flashy` (glow, marquee, spotlight, partículas). Densidade e estado vencem efeito.
- **Read** (leitura, historico, relatorio): movimento curto de troca de contexto e permitido. Loop decorativo nao.
- **Persuade** (landing, convite, empty de primeiro uso): um gesto de impacto pode entrar, se for o signature move da Biblia e nao a personalidade de toda tela.

## 4. Portao de 8 pontos

Antes de registrar na Biblia, cada candidato responde:

1. **Adequacao.** Resolve a interacao escrita no passo 1?
2. **Stack.** Funciona na versao real do projeto?
3. **Acessibilidade.** Teclado, foco e nome acessivel estao no comportamento, nao so no README?
4. **Adaptacao.** Cor, raio, tipo e icone saem dos tokens, ou a peca traz a paleta dela?
5. **Estados.** Tem loading, vazio, erro, disabled e foco, ou so a demo feliz?
6. **Manutencao.** Ha dono, issues tratadas e uma API estavel? Commit antigo nao e abandono automatico.
7. **Peso.** Quantas dependencias entram para um detalhe que o projeto ja sabe fazer?
8. **Licenca.** O arquivo `LICENSE` do commit copiado e permissivo? Commons Clause, licenca propria e "free para olhar" reprovam.

Declare o uso com uma palavra: **Referencia**, **Dependencia** ou **Codigo copiado via registry**.

## 5. Anti-Frankenstein

Uma tela que junta o card do Magic UI, o input do HeroUI e a tabela do Mantine sem re-tema e uma colcha. Escolha um primitivo de comportamento e pinte com a Biblia.

- Uma familia de icones.
- Os raios concentricos da secao 7.
- As cores semanticas da secao 5, nao as da demo.
- O motion do guia [10-motion-anti-slop.md](10-motion-anti-slop.md), nao o stagger da landing de origem.

Se todos os candidatos levarem ao mesmo dashboard generico, procure outro padrao de interacao (tabela em vez de cards, timeline em vez de feed). Nao responda so trocando a cor.

## 6. Como registrar

Na secao 8 da Biblia, uma linha por peca de fato usada:

| Papel | Fonte | Licenca | Uso | O que foi aproveitado |
|---|---|---|---|---|
| Tabela densa | TanStack Table | MIT | Dependencia | Ordenacao e colunas fixas; visual proprio |
| Sheet mobile | @gorhom/bottom-sheet | MIT | Dependencia | Gesto e detents; cor da superficie Z4 |
| Landing hero | Godly | n/a | Referencia | So a ordem da prova; nenhum codigo |

Nao escreva "a mais atual" ou "a mais bonita" sem a comparacao que sustenta a frase.
