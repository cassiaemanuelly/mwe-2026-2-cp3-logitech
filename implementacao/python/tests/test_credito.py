"""Casos do plano docs/03-testes.md para RF02, RF03 e RF04.

Valores esperados escritos a mao, nunca recalculados com constantes do codigo.
Atraso em minutos: 2h = 120 min, 24h = 1440 min, 72h = 4320 min.
"""
from decimal import Decimal

import pytest

from garantia.credito import (
    TipoDeClienteDesconhecido,
    calcular_credito,
    registrar_politica,
)

FRETE = Decimal("300.00")


def h(horas: int, minutos: int = 0) -> int:
    return horas * 60 + minutos


def test_ct01_varejo_atraso_1h59_nao_gera_credito():
    assert calcular_credito("VAREJO", FRETE, h(1, 59)) == Decimal("0.00")


def test_ct02_varejo_atraso_exato_de_2h_ainda_e_tolerancia():
    assert calcular_credito("VAREJO", FRETE, h(2)) == Decimal("0.00")


def test_ct03_varejo_atraso_2h01_gera_10_por_cento():
    assert calcular_credito("VAREJO", FRETE, h(2, 1)) == Decimal("30.00")


def test_ct04_varejo_atraso_exato_de_24h_continua_10_por_cento():
    assert calcular_credito("VAREJO", FRETE, h(24)) == Decimal("30.00")


def test_ct05_varejo_atraso_24h01_gera_25_por_cento():
    assert calcular_credito("VAREJO", FRETE, h(24, 1)) == Decimal("75.00")


def test_ct06_varejo_atraso_exato_de_72h_continua_25_por_cento():
    assert calcular_credito("VAREJO", FRETE, h(72)) == Decimal("75.00")


def test_ct07_varejo_atraso_72h01_gera_50_por_cento():
    assert calcular_credito("VAREJO", FRETE, h(72, 1)) == Decimal("150.00")


def test_ct08_varejo_credito_limitado_ao_teto_de_500():
    # 50% de 1200 = 600, acima do teto
    assert calcular_credito("VAREJO", Decimal("1200.00"), h(80)) == Decimal("500.00")


def test_ct09_corporativo_dobra_os_percentuais_em_cada_faixa():
    assert calcular_credito("CORPORATIVO", FRETE, h(2)) == Decimal("0.00")
    assert calcular_credito("CORPORATIVO", FRETE, h(2, 1)) == Decimal("60.00")
    assert calcular_credito("CORPORATIVO", FRETE, h(24, 1)) == Decimal("150.00")
    assert calcular_credito("CORPORATIVO", FRETE, h(72, 1)) == Decimal("300.00")


def test_ct10_corporativo_credito_limitado_ao_teto_de_2000():
    # 100% de 2500 = 2500, acima do teto corporativo
    assert calcular_credito("CORPORATIVO", Decimal("2500.00"), h(73)) == Decimal("2000.00")


def test_ct11_cortesia_nunca_recebe_credito():
    assert calcular_credito("CORTESIA", Decimal("0.00"), h(80)) == Decimal("0.00")


def test_ct12_tipo_novo_entra_por_registro_sem_alterar_os_existentes():
    class PoliticaPremiumStub:
        def calcular(self, frete, atraso_minutos):
            return Decimal("42.00")

    registrar_politica("PREMIUM", PoliticaPremiumStub())

    assert calcular_credito("PREMIUM", FRETE, h(30)) == Decimal("42.00")
    assert calcular_credito("VAREJO", FRETE, h(30)) == Decimal("75.00")
    assert calcular_credito("CORPORATIVO", FRETE, h(30)) == Decimal("150.00")


def test_ct14_entrega_adiantada_nao_gera_credito():
    assert calcular_credito("VAREJO", FRETE, -60) == Decimal("0.00")


def test_tipo_de_cliente_desconhecido_e_recusado():
    with pytest.raises(TipoDeClienteDesconhecido):
        calcular_credito("INEXISTENTE", FRETE, h(30))
