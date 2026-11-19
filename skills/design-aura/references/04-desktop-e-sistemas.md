# Guia de Sistemas Web, SaaS, ERPs & Apps Desktop

Interfaces desktop e sistemas operacionais existem para **velocidade de leitura, precisão na tomada de decisão e baixa fadiga em jornadas longas**. A estética nunca pode atrasar ou fantasiar o trabalho diário.

---

## 1. Filosofia `Operate` (Sistemas e Ferramentas de Trabalho)

Em sistemas operacionais (ERPs, CRMs, portais financeiros, painéis de SRE, IDEs e ferramentas B2B):
- **O tema empresta apenas 4 elementos**: Tipografia, Paleta, Densidade e **1 Assinatura Visual** ligada ao domínio.
- **Nunca fantasie os controles**: botões, selects, abas, tabelas ordenáveis, filtros e menus mantêm comportamento 100% padrão e previsível. Nunca transforme uma tabela financeira em "papel pautado" nem um painel web em "terminal retrô com moldura falsa" só por estilo.
- **Hierarquia por urgência real**: organize o espaço por horizonte temporal ou criticidade (**Agora / Atrasado** → **Em Rota / Hoje** → **Radar / Histórico**).

---

## 2. Arquitetura de Composição Desktop (Zero Espaços Mortos)

O erro clássico de sistemas web/desktop é deixar **60–70% do painel direito vazio** ou empurrar a ação principal para o rodapé isolada do contexto. Escolha o arquétipo certo pelo tipo de tarefa:

### A. Cockpit Operacional de 3 Zonas (Triagem e Aprovação)
Ideal para contas a pagar/receber, atendimento/inbox, revisão de pedidos, editais e filas operacionais:
1. **Zona Esquerda (280–340px)**: fila priorizada e filtrável com divisórias nítidas, indicador claro de urgência e seleção por teclado (`↑`/`↓`).
2. **Zona Central (1fr — Documento Vivo)**: detalhe completo do item selecionado + **barra fixa de decisão** visível sem scroll excessivo.
3. **Zona Direita (260–320px — Telemetria & Contexto Imediato)**: saldo/cobertura, histórico do registro, vínculos e risco — tudo visível na mesma leitura para decidir em 1 clique.

### B. Master-Detail com Inspector Lateral
Ideal para catálogos grandes, usuários, contratos, logs e registros administrativos:
- Tabela ou lista densa no corpo principal.
- Inspector lateral direito (drawer não-bloqueante de 380–460px) que abre ao clicar em uma linha **sem tirar o usuário do contexto da tabela**.

### C. Workbench / Split-Pane Redimensionável
Ideal para apps desktop (IDEs, clientes de dados, estúdios, editores, comparação):
- Barra lateral colapsável (`⌘B` / `Ctrl+B`), área de trabalho central limpa e painel auxiliar inferior/direito retrátil.

---

## 3. Tabelas Densas de Alta Legibilidade

- **Alinhamento rígido**: textos e identificadores à esquerda; datas em formato curto uniforme (`18 Nov` ou `18/11/26`); **números, valores monetários, percentuais e contagens sempre à direita com `tabular-nums`**.
- **Controle de badges**: no máximo 1–2 tags/pills semânticas por linha. Evite arco-íris de pílulas competindo pelo olhar.
- **Cabeçalho fixo (`sticky`)** quando a tabela rola, barra de ações em lote flutuante quando >= 1 linha estiver selecionada.
- **Ações por linha**: mantenha no máximo 1 ação rápida visível no hover/foco e o restante em menu contextual (`...` ou clique direito).
- **Ordenação e filtros visíveis**: chip/pílula ativa sempre indica o filtro aplicado e mostra o botão rápido de limpar.

---

## 4. Ergonomia de Apps Desktop (Electron, Tauri, macOS, Windows)

Se o projeto compila para janela desktop nativa (Electron, Tauri, SwiftUI macOS, WinUI 3):

### Anatomia de Janela
- **Titlebar integrada e arrastável (`-webkit-app-region: drag`)**: botões, inputs, buscas e controles dentro da titlebar DEVEM ter `-webkit-app-region: no-drag`.
- **Respeito ao OS host**:
  - **macOS**: reserve `76–84px` à esquerda na titlebar para os *traffic lights* (fechar/minimizar/zoom); use `⌘` para atalhos (`⌘K`, `⌘,`, `⌘W`).
  - **Windows / Linux**: reserve espaço à direita para minimizar/maximizar/fechar com altura confortável (`>= 32–40px`); use `Ctrl` nos atalhos.
- **Estado `window-unfocused`**: atenue sutilmente a barra de título/seleção ativa quando a janela perder foco do SO (detalhe clássico de app nativo).

### Produtividade por Teclado & Command Palette (`⌘K`)
- **Command Palette (`⌘K` / `Ctrl+K`)** obrigatório em sistemas com >= 5 módulos ou ações recorrentes: busca instantânea de telas, registros e ações rápidas, totalmente operável por `↑`/`↓`/`Enter`/`Esc`.
- **Atalhos descobertos**: exiba `<kbd>` discreto nos tooltips ou menus (`G` depois `P` para Portal, `/` para buscar, `Esc` para fechar drawer/modal).
- **Menus contextuais e estado persistente**: salve tema, largura de sidebar e filtros recentes em `localStorage` ou store do app desktop.

---

## 5. Alto Contraste Ótico em Sistemas Corporativos

Para ambientes de escritório iluminados (Light Mode) e operações noturnas (Dark Mode):
- **Light Mode Aterrado**: evite fundo `#FFFFFF` com borda `rgba(0,0,0,0.06)` onde tudo vira um clarão branco. Use canvas areia/pedra suave (`Z1`) com cartões elevados (`Z2`), contorno nítido (`1.25px` com contraste perceptível) e sombra dupla suave.
- **Dark Mode Estruturado**: evite `#000000` absoluto. Use base profunda (`#0B1220` / `#0E1624`), painéis em `+6%` a `+10%` de luminosidade (`#132033`), e borda de destaque superior sutil (`rgba(255,255,255,0.12)`).
- **Semântica antes de texto**: um item vencido ou bloqueado deve comunicar urgência em < 1 segundo por contraste cromático controlado (borda/badge/indicador), nunca escondido num bloco todo azul ou todo cinza.
