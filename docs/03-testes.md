# 3. Plano de testes

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 17 (CT01 a CT17) | Cálculo do atraso, faixas, percentuais, tetos, tipos de cliente, ausência comprovada, idempotência e colaboração com Faturamento e Notificações, tudo com dublês na fronteira do processo |
| Integração | 3 (CT18 a CT20) | Banco real: unicidade da nota sob concorrência (RNF03), `UNIQUE (entrega_id)` do RF09 e o Adapter contra o contrato da API de WhatsApp |
| Ponta a ponta | 1 (CT21) | Plataforma inteira no `compose`: entrega confirmada → nota emitida → saldo no Portal em até 5 min (RNF02, RF10) |

**Por que essa proporção.** O risco maior da Garantia de Prazo está nas **regras de valor**
(faixas, limites exatos, tetos, tipo de cliente): é dinheiro devolvido ao cliente e um erro de `>`
por `>=` passa despercebido. Essas regras são funções puras e rodam em milissegundos, então cabem
muitos casos na base. Já o que a unidade **não** enxerga, unicidade sob concorrência real e o
contrato SQL, fica em poucos testes de integração com PostgreSQL real. Um único teste de ponta a
ponta prova que as peças conversam; mais do que isso seria lento e frágil.

## Convenções

- Frete de referência: **R$ 300,00** (salvo quando indicado).
- Atraso guardado em **minutos** no código, para os limites serem exatos (2 h = 120 min).
- RF08 interpretado como **1 envio + até 3 retentativas = no máximo 4 tentativas**.
- Valores esperados escritos **à mão** no teste, nunca recalculados com a constante do código.

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 1h59 | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Varejo, frete R$ 300,00 | Atraso de **2h00** exatas | R$ 0,00 (limite "até 2 h" é inclusivo) | Unidade | Nenhum | Regra pura |
| CT03 | RF02 | Varejo, frete R$ 300,00 | Atraso de **2h01** | R$ 30,00 (10%) | Unidade | Nenhum | Regra pura |
| CT04 | RF02 | Varejo, frete R$ 300,00 | Atraso de **24h00** | R$ 30,00 (ainda 10%) | Unidade | Nenhum | Regra pura |
| CT05 | RF02 | Varejo, frete R$ 300,00 | Atraso de **24h01** | R$ 75,00 (25%) | Unidade | Nenhum | Regra pura |
| CT06 | RF02 | Varejo, frete R$ 300,00 | Atraso de **72h00** | R$ 75,00 (ainda 25%) | Unidade | Nenhum | Regra pura |
| CT07 | RF02 | Varejo, frete R$ 300,00 | Atraso de **72h01** | R$ 150,00 (50%) | Unidade | Nenhum | Regra pura |
| CT08 | RF02 | Varejo, frete R$ 1.200,00 | Atraso de 80h | R$ 500,00 (50% = 600, limitado ao teto) | Unidade | Nenhum | Regra pura |
| CT09 | RF03 | Corporativo, frete R$ 300,00 | Atraso de 2h01 / 24h01 / 72h01 | R$ 60,00 (20%) / R$ 150,00 (50%) / R$ 300,00 (100%) | Unidade | Nenhum | Regra pura |
| CT10 | RF03 | Corporativo, frete R$ 2.500,00 | Atraso de 73h | R$ 2.000,00 (100% = 2.500, limitado ao teto) | Unidade | Nenhum | Regra pura |
| CT11 | RF03 | Cliente Cortesia, frete R$ 0,00 | Atraso de 80h | Crédito R$ 0,00, **nenhuma** nota emitida e **uma** notificação de atraso | Unidade | Mock (Faturamento e Notificações) | O resultado (R$ 0) é igual com ou sem notificação: só uma asserção sobre a **chamada** (`assert_called_once` / `assert_not_called`) prova o RF03 |
| CT12 | RF04 | Política de um tipo novo `"PREMIUM"` registrada no teste | Cliente PREMIUM, frete R$ 300, atraso 30h | Crédito calculado pela política nova; CT02 a CT10 continuam verdes sem alterar as classes existentes | Unidade | Stub (política fake) | A política fake responde um valor fixo; o teste prova que o calculador aceita um tipo novo só por registro |
| CT13 | RF01 | Prazo prometido 10/11 10:00 | Confirmação 10/11 12:30 | Atraso = 150 min (2,5 h) | Unidade | Stub (ClienteFrete) | O prazo vem do serviço de Frete, que não está no ar; o Stub devolve o prazo e o teste afirma sobre o **resultado** |
| CT14 | RF01 | Prazo prometido 10/11 10:00 | Confirmação 10/11 09:00 (adiantada) | Atraso = 0 e crédito R$ 0,00 | Unidade | Stub (ClienteFrete) | Idem CT13 |
| CT15 | RF05 | Varejo, atraso 30h; Rastreamento responde ausência comprovada (parado a 150 m por 10 min) | Confirmação com registro de ausência | Crédito R$ 0,00 e **nenhuma** nota emitida | Unidade | Stub (ClienteRastreamento) + Mock (Faturamento) | Stub fornece o veredito; Mock prova que `emitir` **não foi chamado** |
| CT16 | RF09 | Varejo, atraso 30h, repositório Fake em memória | A **mesma** confirmação (`entregaId = E-1`) duas vezes | Um crédito de R$ 75,00; `faturamento.emitir` chamado **uma vez** com `chave_idempotencia="E-1"` | Unidade | Mock (Faturamento) + Fake (Repositório) | O valor devolvido é igual nas duas chamadas; só o Mock pega a segunda emissão |
| CT17 | RF08 | Enviador falha sempre | Notificação de atraso | **4** tentativas (1 + 3) e `registrar_falha_final` chamado uma vez com o pedido | Unidade | Mock (enviador e registro de falhas) | A regra é sobre **quantas vezes** algo foi chamado e se a falha foi registrada, não sobre valor |
| CT18 | RF06, RNF03 | PostgreSQL real com a sequência | 1.000 emissões concorrentes (pool de 50 threads) | 1.000 notas, `COUNT(DISTINCT numero) = 1000`, números crescentes | Integração | Nenhum | Concorrência real e a atomicidade do `nextval` só existem no banco de verdade |
| CT19 | RF09 | PostgreSQL real | Dois `INSERT … ON CONFLICT` concorrentes com o mesmo `entrega_id` | Uma linha em `garantia.creditos` | Integração | Nenhum | O que se testa é a restrição do banco |
| CT20 | RF07 | Servidor fake da API de WhatsApp (contrato do parceiro) | Notificação para cliente com canal WHATSAPP | O parceiro recebe o JSON no formato dele (`to`, `template`, `params`) | Integração | Spy (cliente HTTP real envolvido) | O Adapter precisa falar com o HTTP real; o Spy registra o corpo enviado sem substituir o comportamento |
| CT21 | RNF02, RF10, RNF04 | `docker compose up -d --wait` | Confirmar entrega com 30h de atraso de um pedido Varejo de R$ 300 | Nota emitida e o Portal exibe saldo R$ 75,00 em até 5 min | Ponta a ponta | Nenhum | Prova que o sistema funciona junto |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Trocar `atraso <= 120` por `atraso < 120` na tolerância | **CT02** | Com 2h00 exatas o mutante concede 10% (R$ 30,00) e o esperado é R$ 0,00 |
| Trocar `min(valor, teto)` por `valor` (remover o teto) | **CT08** e **CT10** | O crédito vira R$ 600,00 e R$ 2.500,00 |
| Corporativo usando multiplicador 1 em vez de 2 | **CT09** | 24h01 dá R$ 75,00 em vez de R$ 150,00 |
| Remover a verificação de idempotência por `entregaId` | **CT16** | O valor devolvido não muda, mas `emitir` passa a ser chamado 2 vezes: só o **Mock** pega |
| Retentar 2 vezes em vez de 3 | **CT17** | O Mock registra 3 tentativas em vez de 4 |