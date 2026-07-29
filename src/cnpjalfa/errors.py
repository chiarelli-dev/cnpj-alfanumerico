"""Exceções do pacote."""

from __future__ import annotations


class ValidationError(ValueError):
    """Entrada estruturalmente inválida para a operação pedida.

    Levantada por :func:`cnpjalfa.calcular_dv`, :func:`cnpjalfa.formatar` e
    :func:`cnpjalfa.limpar` quando a entrada não tem a forma mínima esperada.
    :func:`cnpjalfa.validar` NUNCA levanta: retorna ``False`` para qualquer
    entrada inválida, inclusive ``None`` e tipos que não são ``str``.
    """
