"""Regra de calculo do credito da Garantia de Prazo (RF02, RF03, RF04).

Strategy: cada tipo de cliente tem a sua PoliticaDeCredito.
Registro: um tipo novo entra com registrar_politica(), sem alterar as classes existentes (RF04).
As faixas sao dados (tabela), nao classes: so mudam limites e percentuais.
"""
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

CENTAVO = Decimal("0.01")

# (limite superior INCLUSIVO em minutos, percentual base). None = sem limite.
FAIXAS_PADRAO = (
    (2 * 60, Decimal("0.00")),    # tolerancia: ate 2 h
    (24 * 60, Decimal("0.10")),   # acima de 2 h e ate 24 h
    (72 * 60, Decimal("0.25")),   # acima de 24 h e ate 72 h
    (None, Decimal("0.50")),      # acima de 72 h
)


class PoliticaDeCredito(Protocol):
    def calcular(self, frete: Decimal, atraso_minutos: int) -> Decimal: ...


class PoliticaPorFaixas:
    """Percentual da faixa x multiplicador, limitado ao teto."""

    def __init__(self, multiplicador: Decimal, teto: Decimal, faixas=FAIXAS_PADRAO):
        self._multiplicador = multiplicador
        self._teto = teto
        self._faixas = faixas

    def _percentual(self, atraso_minutos: int) -> Decimal:
        for limite, percentual in self._faixas:
            if limite is None or atraso_minutos <= limite:
                return percentual
        raise AssertionError("tabela de faixas sem faixa final")

    def calcular(self, frete: Decimal, atraso_minutos: int) -> Decimal:
        bruto = frete * self._percentual(atraso_minutos) * self._multiplicador
        return min(bruto, self._teto).quantize(CENTAVO, ROUND_HALF_UP)


class PoliticaVarejo(PoliticaPorFaixas):
    def __init__(self):
        super().__init__(multiplicador=Decimal("1"), teto=Decimal("500.00"))


class PoliticaCorporativo(PoliticaPorFaixas):
    def __init__(self):
        super().__init__(multiplicador=Decimal("2"), teto=Decimal("2000.00"))


class PoliticaCortesia:
    """Frete zero: nunca recebe credito (a notificacao do atraso e feita fora da regra)."""

    def calcular(self, frete: Decimal, atraso_minutos: int) -> Decimal:
        return Decimal("0.00")


class TipoDeClienteDesconhecido(LookupError):
    pass


_POLITICAS: dict[str, PoliticaDeCredito] = {}


def registrar_politica(tipo_cliente: str, politica: PoliticaDeCredito) -> None:
    _POLITICAS[tipo_cliente.upper()] = politica


def politica_para(tipo_cliente: str) -> PoliticaDeCredito:
    try:
        return _POLITICAS[tipo_cliente.upper()]
    except KeyError:
        raise TipoDeClienteDesconhecido(tipo_cliente) from None


def calcular_credito(tipo_cliente: str, frete: Decimal, atraso_minutos: int) -> Decimal:
    return politica_para(tipo_cliente).calcular(frete, max(0, atraso_minutos))


registrar_politica("VAREJO", PoliticaVarejo())
registrar_politica("CORPORATIVO", PoliticaCorporativo())
registrar_politica("CORTESIA", PoliticaCortesia())
