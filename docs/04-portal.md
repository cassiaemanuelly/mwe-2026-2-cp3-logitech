# 4. Tela do Portal do Cliente (RF10)

## Estados da tela

A tela é uma função do estado: `tela = f(carregamento, pedido, conexaoAoVivo, saldo)`.
Nada é "apagado à mão": cada estado tem a sua renderização.

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| `carregando` | apenas o `pedidoId` | `<p role="status">Consultando o pedido…</p>` |
| `erro` | mensagem de erro (404 ou falha de rede/CORS) | `<p role="alert">Pedido PED-9999 não encontrado</p>` ou "Não foi possível falar com o serviço. Tentar de novo" |
| `emTransito` + `aoVivo` | pedido, última posição, previsão de chegada (ETA), saldo | Mapa/posição do veículo, "Chega em ~2 h (14:30)", saldo de créditos, selo "ao vivo" |
| `emTransito` + `reconectando` | último pedido, posição e ETA conhecidos | Os mesmos dados com aviso discreto `role="status"`: "Atualização ao vivo interrompida, reconectando… (última posição às 13:42)" |
| `atrasado` | pedido, ETA já passou do prazo prometido | Destaque "Atrasado em 3 h. Você terá crédito de garantia ao receber" |
| `entregueNoPrazo` | pedido entregue, sem atraso | "Entregue em 10/11 às 09:55" e saldo |
| `entregueComCredito` | pedido entregue com atraso, crédito emitido | "Entregue com 30 h de atraso. Crédito de R$ 75,00 (nota nº 1042)" e saldo atualizado |
| `entregueSemCredito` | entregue com atraso, mas cliente Cortesia ou ausência comprovada | "Entregue com atraso. Motivo de não haver crédito: destinatário ausente" |

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>
  ├── <EstadoCarregando />                                   (carregando)
  ├── <MensagemErro mensagem onTentarDeNovo />                (erro)
  └── <PainelPedido pedido posicao eta saldo conexao credito>
        ├── <IndicadorAoVivo conexao />
        ├── <PosicaoVeiculo posicao />
        ├── <PrevisaoChegada eta prazoPrometido />
        ├── <SituacaoEntrega pedido credito />
        └── <SaldoCreditos saldo />
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| `AcompanhamentoPedido` | `pedidoId: string` | Dono do estado (`useState`: `pedido`, `erro`, `carregando`, `posicao`, `eta`, `saldo`, `conexao`). Faz a carga inicial com `useEffect([pedidoId])` e abre o `EventSource`; a função de limpeza fecha o `EventSource` e descarta respostas velhas |
| `EstadoCarregando` | — | Mostra `role="status"` |
| `MensagemErro` | `mensagem`, `onTentarDeNovo` | Mostra `role="alert"` e o botão para repetir |
| `PainelPedido` | `pedido`, `posicao`, `eta`, `saldo`, `conexao`, `credito` | Layout do pedido; repassa props |
| `IndicadorAoVivo` | `conexao: 'aoVivo' \| 'reconectando'` | Selo "ao vivo" ou aviso de reconexão |
| `PosicaoVeiculo` | `posicao: {lat, lon, em}` | Posição atual e horário da última leitura |
| `PrevisaoChegada` | `eta`, `prazoPrometido` | Previsão e destaque de atraso quando `eta > prazoPrometido` |
| `SituacaoEntrega` | `pedido`, `credito` | Texto de situação em português (`EM_TRANSITO` → "Em trânsito") e o crédito/motivo |
| `SaldoCreditos` | `saldo: number` | Saldo formatado em R$ |

Componentes filhos são funções puras (props entram, árvore sai), testáveis com Vitest + Testing
Library sem rede.

## Origem dos dados

| Dado | Origem | Como chega |
|---|---|---|
| Pedido, situação, prazo prometido | Pedidos (`GET /api/v1/pedidos/{id}`) e Frete | HTTP GET na montagem |
| Saldo de créditos inicial | Faturamento (`GET /api/v1/clientes/{id}/creditos/saldo`) | HTTP GET na montagem |
| Posição do veículo | Rastreamento → painel | **SSE**, evento `posicao` a cada ~30 s |
| Previsão de chegada | painel (calcula a partir da posição e da rota) | **SSE**, evento `previsao` |
| Crédito novo / saldo atualizado | Faturamento → painel | **SSE**, evento `credito` |

**Atualização ao vivo:** o componente abre `new EventSource('http://localhost:3000/api/v1/pedidos/{id}/eventos')`.
O painel envia só o que é desse pedido. O `EventSource` reconecta sozinho; durante a reconexão a tela
fica em `reconectando` com os últimos dados. Ao trocar de pedido ou sair da tela, a função de
limpeza do `useEffect` chama `fonte.close()`, senão o servidor acumula assinantes (vazamento visto na
Aula 11). Os serviços chamados pelo navegador precisam liberar a origem `http://localhost:5173` via
`LOGITECH_CORS_ORIGINS`.