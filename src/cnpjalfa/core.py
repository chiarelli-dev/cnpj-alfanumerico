"""Núcleo da validação de CNPJ alfanumérico (IN RFB 2.229/2024).

Formato oficial: ``AA.AAA.AAA/AAAA-DV``. As 12 primeiras posições (raiz e
ordem da filial) aceitam numerais 0-9 e letras maiúsculas A-Z; as 2 últimas
(dígitos verificadores) são sempre numéricas.

Cálculo do DV (fontes: PDF técnico do SERPRO e FAQ oficial da RFB):

1. Cada caractere é convertido para o valor decimal ASCII menos 48.
   Dígitos 0-9 mantêm os valores 0-9; letras A-Z valem 17-42 (A=17 ... Z=42).
2. Módulo 11 em duas etapas, com pesos de 2 a 9 distribuídos da direita para
   a esquerda, recomeçando a cada 8 posições. Resto 0 ou 1 resulta em DV 0;
   caso contrário, DV = 11 - resto.

Como os dígitos 0-9 preservam seus valores na conversão, o algoritmo é 100%
retrocompatível com os CNPJs numéricos existentes.
"""

from __future__ import annotations

import random
import re

from .errors import ValidationError

_ALFABETO = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# CNPJ completo sem máscara: 12 posições alfanuméricas + 2 DVs numéricos.
_RE_SEM_MASCARA = re.compile(r"^[A-Z0-9]{12}[0-9]{2}$")

# CNPJ completo com a máscara oficial XX.XXX.XXX/XXXX-XX.
_RE_COM_MASCARA = re.compile(
    r"^([A-Z0-9]{2})\.([A-Z0-9]{3})\.([A-Z0-9]{3})/([A-Z0-9]{4})-([0-9]{2})$"
)

# Base de 12 posições (raiz + ordem), sem os DVs.
_RE_BASE = re.compile(r"^[A-Z0-9]{12}$")

# Caracteres de máscara e espaços em branco, removidos por limpar().
_RE_MASCARA_CHARS = re.compile(r"[./\-\s]")


def _valor(caractere: str) -> int:
    """Valor de cálculo de um caractere: decimal ASCII menos 48."""
    return ord(caractere) - 48


def _dv(valores: list[int]) -> int:
    """Um dígito verificador por módulo 11.

    Pesos de 2 a 9 da direita para a esquerda, recomeçando a cada 8 posições:
    o peso da i-ésima posição a partir da direita é ``(i % 8) + 2``.
    """
    soma = sum(v * ((i % 8) + 2) for i, v in enumerate(reversed(valores)))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def limpar(cnpj: str) -> str:
    """Remove máscara (pontos, barra, hífen e espaços) e converte a maiúsculas.

    Não valida o conteúdo além do charset: apenas normaliza. Levanta
    :class:`ValidationError` se a entrada não for ``str`` ou contiver
    caracteres não-ASCII (``str.upper`` mapearia lookalikes Unicode como
    ``ı`` U+0131 para ``I`` e ``ſ`` U+017F para ``S``, mascarando entrada
    inválida).

    >>> limpar("12.abc.345/01de-35")
    '12ABC34501DE35'
    """
    if not isinstance(cnpj, str):
        raise ValidationError(f"entrada deve ser str, recebeu {type(cnpj).__name__}")
    if not cnpj.isascii():
        raise ValidationError(f"entrada contém caracteres não-ASCII: {cnpj!r}")
    return _RE_MASCARA_CHARS.sub("", cnpj).upper()


def calcular_dv(cnpj_sem_dv: str) -> str:
    """Calcula os 2 dígitos verificadores da base de 12 posições.

    Aceita a base com ou sem máscara, maiúscula ou minúscula. Levanta
    :class:`ValidationError` se, após a limpeza, a base não tiver exatamente
    12 caracteres em ``[A-Z0-9]``.

    >>> calcular_dv("12ABC34501DE")
    '35'
    """
    base = limpar(cnpj_sem_dv)
    if not _RE_BASE.match(base):
        raise ValidationError(
            "base do CNPJ deve ter 12 caracteres alfanuméricos (0-9, A-Z) "
            f"após a limpeza, recebeu {base!r}"
        )
    valores = [_valor(c) for c in base]
    dv1 = _dv(valores)
    dv2 = _dv(valores + [dv1])
    return f"{dv1}{dv2}"


def validar(cnpj: str) -> bool:
    """Valida um CNPJ alfanumérico ou numérico legado.

    Aceita com ou sem a máscara oficial ``XX.XXX.XXX/XXXX-XX``, em qualquer
    caixa (normaliza para maiúsculas). NUNCA levanta exceção: retorna
    ``False`` para qualquer entrada inválida, inclusive ``None``, tipos que
    não são ``str``, máscara malformada, tamanho errado, caracteres fora de
    ``[A-Z0-9]`` nas 12 primeiras posições, DV não numérico, DV incorreto e
    base com um único caractere repetido.

    >>> validar("12.ABC.345/01DE-35")
    True
    >>> validar("11.222.333/0001-81")
    True
    >>> validar(None)
    False
    """
    if not isinstance(cnpj, str):
        return False
    if not cnpj.isascii():
        # Rejeita antes do .upper(): Python mapeia lookalikes Unicode como
        # 'ı' (U+0131) para 'I' e 'ſ' (U+017F) para 'S', o que furaria o
        # regex [A-Z0-9] com entrada que não é ASCII.
        return False
    texto = cnpj.strip().upper()
    com_mascara = _RE_COM_MASCARA.match(texto)
    if com_mascara:
        texto = "".join(com_mascara.groups())
    if not _RE_SEM_MASCARA.match(texto):
        return False
    base, dv = texto[:12], texto[12:]
    if len(set(base)) == 1:
        # Raiz + ordem com um único caractere repetido (ex.: 000000000000)
        # nunca é uma inscrição real, mesmo quando o DV confere.
        return False
    return calcular_dv(base) == dv


def formatar(cnpj: str) -> str:
    """Aplica a máscara oficial ``XX.XXX.XXX/XXXX-XX``.

    Aceita entrada já mascarada ou sem máscara, em qualquer caixa. Valida
    apenas a estrutura (14 posições, DVs numéricos), não o valor do DV.
    Levanta :class:`ValidationError` para estrutura inválida.

    >>> formatar("12abc34501de35")
    '12.ABC.345/01DE-35'
    """
    texto = limpar(cnpj)
    if not _RE_SEM_MASCARA.match(texto):
        raise ValidationError(
            "CNPJ deve ter 12 caracteres alfanuméricos (0-9, A-Z) seguidos de "
            f"2 dígitos verificadores numéricos, recebeu {texto!r}"
        )
    return f"{texto[0:2]}.{texto[2:5]}.{texto[5:8]}/{texto[8:12]}-{texto[12:14]}"


def gerar(alfanumerico: bool = True) -> str:
    """Gera um CNPJ válido aleatório para testes e desenvolvimento.

    Retorna com a máscara oficial aplicada. Com ``alfanumerico=False`` gera
    apenas dígitos (formato numérico legado). Não usa fonte criptográfica:
    é um gerador para dados de teste, não para inscrições reais.

    >>> validar(gerar())
    True
    """
    alfabeto = _ALFABETO if alfanumerico else _ALFABETO[:10]
    while True:
        base = "".join(random.choices(alfabeto, k=12))
        if len(set(base)) > 1:
            break
    return formatar(base + calcular_dv(base))
