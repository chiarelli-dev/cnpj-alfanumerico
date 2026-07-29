"""Linha de comando: ``cnpjalfa validar 12.ABC.345/01DE-35``.

Exit code 0 para sucesso (CNPJ válido) e 1 para falha (CNPJ inválido ou
entrada malformada), pensado para uso em shell script:

    cnpjalfa validar "$CNPJ" && echo ok
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import formatar, gerar, validar
from .errors import ValidationError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cnpjalfa",
        description="Validação de CNPJ alfanumérico da Receita Federal (IN RFB 2.229/2024).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_validar = sub.add_parser("validar", help="valida um CNPJ (exit 0 válido, 1 inválido)")
    p_validar.add_argument("cnpj", help="CNPJ com ou sem máscara")

    p_gerar = sub.add_parser("gerar", help="gera CNPJs válidos aleatórios para testes")
    p_gerar.add_argument("n", nargs="?", type=int, default=1, help="quantidade (default 1)")
    p_gerar.add_argument(
        "--numerico",
        action="store_true",
        help="gera apenas dígitos (formato numérico legado)",
    )

    p_formatar = sub.add_parser("formatar", help="aplica a máscara XX.XXX.XXX/XXXX-XX")
    p_formatar.add_argument("cnpj", help="CNPJ com ou sem máscara")

    args = parser.parse_args(argv)

    if args.comando == "validar":
        ok = validar(args.cnpj)
        print("valido" if ok else "invalido")
        return 0 if ok else 1

    if args.comando == "gerar":
        if args.n < 1:
            print("erro: quantidade deve ser >= 1", file=sys.stderr)
            return 1
        for _ in range(args.n):
            print(gerar(alfanumerico=not args.numerico))
        return 0

    # formatar
    try:
        print(formatar(args.cnpj))
    except ValidationError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
