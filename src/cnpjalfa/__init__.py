"""cnpj-alfanumerico: validação do CNPJ alfanumérico da Receita Federal.

A partir de julho de 2026 (IN RFB 2.229/2024), novas inscrições de CNPJ podem
conter letras nas 12 primeiras posições (``AA.AAA.AAA/AAAA-DV``). Os 2 dígitos
verificadores continuam numéricos, calculados por módulo 11 sobre o valor
ASCII de cada caractere menos 48. Este pacote valida, calcula DV, formata e
gera CNPJs nesse formato, com retrocompatibilidade total com os CNPJs
numéricos existentes.

Uso:

    >>> import cnpjalfa
    >>> cnpjalfa.validar("12.ABC.345/01DE-35")
    True
    >>> cnpjalfa.calcular_dv("12ABC34501DE")
    '35'
    >>> cnpjalfa.formatar("12abc34501de35")
    '12.ABC.345/01DE-35'

Aliases em inglês, mesmo comportamento das funções em português:
``is_valid`` (validar), ``calculate_dv`` (calcular_dv), ``format_cnpj``
(formatar), ``clean`` (limpar) e ``generate`` (gerar).

Sem dependência externa: só a biblioteca padrão do Python.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from .core import calcular_dv, formatar, gerar, limpar, validar
from .errors import ValidationError

try:
    __version__ = _version("cnpj-alfanumerico")
except PackageNotFoundError:  # pragma: no cover - checkout sem instalação
    __version__ = "0.0.0+dev"

# Aliases em inglês.
is_valid = validar
calculate_dv = calcular_dv
format_cnpj = formatar
clean = limpar
generate = gerar

__all__ = [
    "validar",
    "calcular_dv",
    "formatar",
    "limpar",
    "gerar",
    "ValidationError",
    "is_valid",
    "calculate_dv",
    "format_cnpj",
    "clean",
    "generate",
    "__version__",
]
