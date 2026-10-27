# 5. Uso de assistentes de IA

Assistente usado: Claude (Anthropic).

| Entrega | O que foi pedido | O que o assistente sugeriu | Decisão da dupla | Motivo |
|---|---|---|---|---|
| 1. Domínio | Rascunho da modelagem do domínio | 7 bounded contexts, com a Garantia de Prazo como contexto novo e o RF05 no Rastreamento; mapa de contexto, agregados e linguagem ubíqua | Aceito | Concordo porque cada serviço mantém sua responsabilidade e cada requisito fica com um único contexto. |
| 2. Arquitetura | Protocolos, padrões de projeto, onde não aplicar padrão, RF09 e RNF03 | UDP na telemetria, HTTP com reenvio na confirmação, SSE no Portal; Strategy, Adapter, Decorator e Observer; não usar Singleton na numeração; UNIQUE (entrega_id) e SEQUENCE no banco | Aceito | Concordo com as escolhas porque cada protocolo atende à necessidade da comunicação e os padrões facilitam a manutenção e a expansão do sistema. Também considero essencial garantir no banco que não haja créditos duplicados nem números de notas repetidos. Assim, a arquitetura fica mais segura, organizada e alinhada aos requisitos do projeto. |