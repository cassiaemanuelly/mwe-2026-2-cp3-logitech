# 5. Implementação em TDD

Implementem a regra de cálculo do crédito (RF02, RF03 e RF04) em **uma** linguagem à
escolha da dupla: Java, C#, Python ou TypeScript. O Codespace deste repositório já traz
as quatro.

## Como trabalhar

1. Escrevam um teste para um caso do plano (`docs/03-testes.md`) e confirmem que ele
   **falha**. Façam o commit: `test: CT01 atraso abaixo da tolerância não gera crédito`.
2. Escrevam o mínimo de código que faz o teste passar. Façam o commit:
   `feat: calcula crédito zero dentro da tolerância`.
3. Se for preciso, refatorem com os testes passando. Façam o commit: `refactor: ...`.
4. Repitam para o próximo caso.

O histórico de commits é a evidência do TDD: o commit de teste vem antes do commit de
código que o faz passar.

## O que registrar aqui

- Linguagem e framework de teste: Python 3 + pytest
- Comando para executar os testes: `cd implementacao/python` e depois `python -m pytest -v`
- Casos do plano implementados (IDs): CT01 a CT12 e CT14, mais um teste para tipo de cliente desconhecido
- Saída da última execução dos testes:

```
collected 14 items

tests/test_credito.py::test_ct01_varejo_atraso_1h59_nao_gera_credito PASSED
tests/test_credito.py::test_ct02_varejo_atraso_exato_de_2h_ainda_e_tolerancia PASSED
tests/test_credito.py::test_ct03_varejo_atraso_2h01_gera_10_por_cento PASSED
tests/test_credito.py::test_ct04_varejo_atraso_exato_de_24h_continua_10_por_cento PASSED
tests/test_credito.py::test_ct05_varejo_atraso_24h01_gera_25_por_cento PASSED
tests/test_credito.py::test_ct06_varejo_atraso_exato_de_72h_continua_25_por_cento PASSED
tests/test_credito.py::test_ct07_varejo_atraso_72h01_gera_50_por_cento PASSED
tests/test_credito.py::test_ct08_varejo_credito_limitado_ao_teto_de_500 PASSED
tests/test_credito.py::test_ct09_corporativo_dobra_os_percentuais_em_cada_faixa PASSED
tests/test_credito.py::test_ct10_corporativo_credito_limitado_ao_teto_de_2000 PASSED
tests/test_credito.py::test_ct11_cortesia_nunca_recebe_credito PASSED
tests/test_credito.py::test_ct12_tipo_novo_entra_por_registro_sem_alterar_os_existentes PASSED
tests/test_credito.py::test_ct14_entrega_adiantada_nao_gera_credito PASSED
tests/test_credito.py::test_tipo_de_cliente_desconhecido_e_recusado PASSED

14 passed in 0.11s
```