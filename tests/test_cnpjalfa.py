"""Testes de cnpj-alfanumerico.

Vetores oficiais: exemplo 12.ABC.345/01DE-35 do PDF técnico do SERPRO e do
FAQ da Receita Federal (soma1=459, DV1=3; soma2=424, DV2=5), mais CNPJs
numéricos reais recalculados com o algoritmo alfanumérico para provar a
retrocompatibilidade.
"""

from __future__ import annotations

import pytest

import cnpjalfa
from cnpjalfa import ValidationError, calcular_dv, formatar, gerar, limpar, validar
from cnpjalfa.__main__ import main

# (base sem DV, DV esperado) — vetores da especificação oficial.
VETORES = [
    ("12ABC34501DE", "35"),  # exemplo oficial SERPRO / FAQ RFB
    ("112223330001", "81"),  # 11.222.333/0001-81, exemplo clássico numérico
    ("000000000001", "91"),  # Banco do Brasil S.A.
    ("330001670001", "01"),  # Petrobras
    ("336831110001", "07"),  # SERPRO
]

VALIDOS_SEM_MASCARA = [base + dv for base, dv in VETORES]
VALIDOS_COM_MASCARA = [
    "12.ABC.345/01DE-35",
    "11.222.333/0001-81",
    "00.000.000/0001-91",
    "33.000.167/0001-01",
    "33.683.111/0001-07",
]


# --------------------------------------------------------------------------
# calcular_dv
# --------------------------------------------------------------------------


class TestCalcularDv:
    @pytest.mark.parametrize(("base", "dv"), VETORES)
    def test_vetores_oficiais(self, base, dv):
        assert calcular_dv(base) == dv

    def test_aceita_base_com_mascara(self):
        assert calcular_dv("12.ABC.345/01DE") == "35"

    def test_aceita_minusculas(self):
        assert calcular_dv("12abc34501de") == "35"

    def test_aceita_espacos(self):
        assert calcular_dv("  12ABC34501DE  ") == "35"

    @pytest.mark.parametrize(
        "entrada",
        [
            "",
            "12ABC34501D",  # 11 chars
            "12ABC34501DEF",  # 13 chars
            "12ABC34501D*",  # caractere inválido
            "12ábc34501de",  # letra acentuada
            "12abc34501dı",  # U+0131 dotless i: .upper() mapearia para 'I'
            "12abc34501dſ",  # U+017F long s: .upper() mapearia para 'S'
        ],
    )
    def test_rejeita_base_malformada(self, entrada):
        with pytest.raises(ValidationError):
            calcular_dv(entrada)

    @pytest.mark.parametrize("entrada", [None, 12, 12.5, ["12ABC34501DE"]])
    def test_rejeita_nao_string(self, entrada):
        with pytest.raises(ValidationError):
            calcular_dv(entrada)


# --------------------------------------------------------------------------
# validar
# --------------------------------------------------------------------------


class TestValidar:
    @pytest.mark.parametrize("cnpj", VALIDOS_SEM_MASCARA)
    def test_validos_sem_mascara(self, cnpj):
        assert validar(cnpj) is True

    @pytest.mark.parametrize("cnpj", VALIDOS_COM_MASCARA)
    def test_validos_com_mascara(self, cnpj):
        assert validar(cnpj) is True

    @pytest.mark.parametrize("cnpj", ["12abc34501de35", "12.abc.345/01de-35"])
    def test_case_insensitive(self, cnpj):
        assert validar(cnpj) is True

    def test_aceita_espacos_nas_bordas(self):
        assert validar("  12.ABC.345/01DE-35  ") is True

    @pytest.mark.parametrize(
        "cnpj",
        [
            "12ABC34501DE36",  # DV2 errado
            "12ABC34501DE45",  # DV1 errado
            "11222333000182",  # DV errado em CNPJ numérico
            "00000000000192",  # DV errado no Banco do Brasil
        ],
    )
    def test_rejeita_dv_errado(self, cnpj):
        assert validar(cnpj) is False

    @pytest.mark.parametrize(
        "cnpj",
        [
            "",
            "1",
            "12ABC34501DE3",  # 13 chars
            "12ABC34501DE355",  # 15 chars
            "112223330001",  # base sem DV
        ],
    )
    def test_rejeita_tamanho_errado(self, cnpj):
        assert validar(cnpj) is False

    @pytest.mark.parametrize(
        "cnpj",
        [
            "12ABC34501DE3A",  # letra na posição de DV
            "12ABC34501DEAA",  # letras nas duas posições de DV
            "12*BC34501DE35",  # símbolo na base
            "12ÁBC34501DE35",  # letra acentuada
            "12abc34501de3é",  # DV não ASCII
        ],
    )
    def test_rejeita_caractere_invalido(self, cnpj):
        assert validar(cnpj) is False

    def test_rejeita_unicode_lookalike_dotless_i(self):
        # 'ı' (U+0131).upper() == 'I': sem a guarda isascii(), a entrada
        # não-ASCII passaria no regex [A-Z0-9] com o DV do texto mapeado.
        dv = calcular_dv("12abc34501di")
        assert dv == "69"
        assert validar("12abc34501di" + dv) is True
        assert validar("12abc34501dı" + dv) is False

    def test_rejeita_unicode_lookalike_long_s(self):
        # 'ſ' (U+017F).upper() == 'S': mesmo cenário do dotless i.
        dv = calcular_dv("12abc34501ds")
        assert validar("12abc34501ds" + dv) is True
        assert validar("12abc34501dſ" + dv) is False

    @pytest.mark.parametrize("entrada", [None, 12345678000195, 12.34, [], {}, b"12ABC34501DE35"])
    def test_rejeita_nao_string_sem_levantar(self, entrada):
        assert validar(entrada) is False

    def test_rejeita_todos_zeros_mesmo_com_dv_coerente(self):
        # 000000000000 produz DV 00 pelo módulo 11, mas não é inscrição real.
        assert calcular_dv("000000000000") == "00"
        assert validar("00000000000000") is False

    def test_rejeita_base_com_caractere_unico_repetido(self):
        dv = calcular_dv("AAAAAAAAAAAA")
        assert validar("AAAAAAAAAAAA" + dv) is False

    @pytest.mark.parametrize(
        "cnpj",
        [
            "12.ABC.34/501DE-35",  # grupos deslocados
            "12ABC.345/01DE-35",  # mistura parcial de máscara
            "12.ABC.345/01DE35",  # falta o hífen
            "12-ABC-345/01DE-35",  # separadores errados
            "1.2ABC.345/01DE-35",  # ponto na posição errada
        ],
    )
    def test_rejeita_mascara_malformada(self, cnpj):
        assert validar(cnpj) is False


# --------------------------------------------------------------------------
# formatar / limpar
# --------------------------------------------------------------------------


class TestFormatar:
    def test_aplica_mascara(self):
        assert formatar("12ABC34501DE35") == "12.ABC.345/01DE-35"

    def test_normaliza_minusculas(self):
        assert formatar("12abc34501de35") == "12.ABC.345/01DE-35"

    def test_entrada_ja_mascarada_e_estavel(self):
        assert formatar("12.ABC.345/01DE-35") == "12.ABC.345/01DE-35"

    @pytest.mark.parametrize("entrada", ["", "12ABC34501DE", "12ABC34501DE3X", "x" * 15])
    def test_rejeita_estrutura_invalida(self, entrada):
        with pytest.raises(ValidationError):
            formatar(entrada)

    def test_rejeita_nao_string(self):
        with pytest.raises(ValidationError):
            formatar(None)


class TestLimpar:
    def test_remove_mascara_e_sobe_caixa(self):
        assert limpar("12.abc.345/01de-35") == "12ABC34501DE35"

    def test_remove_espacos(self):
        assert limpar(" 12 ABC 345 01DE 35 ") == "12ABC34501DE35"

    def test_nao_valida_conteudo(self):
        assert limpar("!!") == "!!"

    def test_rejeita_nao_string(self):
        with pytest.raises(ValidationError):
            limpar(None)

    @pytest.mark.parametrize(
        "entrada",
        [
            "12abc34501dı",  # U+0131 dotless i
            "12abc34501dſ",  # U+017F long s
            "12ábc34501de",  # letra acentuada
        ],
    )
    def test_rejeita_nao_ascii_antes_do_upper(self, entrada):
        with pytest.raises(ValidationError):
            limpar(entrada)


# --------------------------------------------------------------------------
# gerar
# --------------------------------------------------------------------------


class TestGerar:
    def test_propriedade_500_gerados_todos_validos(self):
        for _ in range(500):
            assert validar(gerar()) is True

    def test_numerico_gera_so_digitos_e_valida(self):
        for _ in range(100):
            cnpj = gerar(alfanumerico=False)
            assert limpar(cnpj).isdigit()
            assert validar(cnpj) is True

    def test_retorna_com_mascara_oficial(self):
        cnpj = gerar()
        assert formatar(cnpj) == cnpj


# --------------------------------------------------------------------------
# Aliases em inglês e metadados
# --------------------------------------------------------------------------


class TestAliases:
    def test_aliases_apontam_para_as_mesmas_funcoes(self):
        assert cnpjalfa.is_valid is validar
        assert cnpjalfa.calculate_dv is calcular_dv
        assert cnpjalfa.format_cnpj is formatar
        assert cnpjalfa.clean is limpar
        assert cnpjalfa.generate is gerar

    def test_alias_funciona(self):
        assert cnpjalfa.is_valid("12.ABC.345/01DE-35") is True

    def test_versao_exposta(self):
        assert cnpjalfa.__version__ == "0.1.0"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


class TestCli:
    def test_validar_valido_exit_0(self, capsys):
        assert main(["validar", "12.ABC.345/01DE-35"]) == 0
        assert capsys.readouterr().out.strip() == "valido"

    def test_validar_invalido_exit_1(self, capsys):
        assert main(["validar", "12.ABC.345/01DE-36"]) == 1
        assert capsys.readouterr().out.strip() == "invalido"

    def test_gerar_n(self, capsys):
        assert main(["gerar", "3"]) == 0
        linhas = capsys.readouterr().out.strip().splitlines()
        assert len(linhas) == 3
        assert all(validar(linha) for linha in linhas)

    def test_gerar_numerico(self, capsys):
        assert main(["gerar", "--numerico"]) == 0
        cnpj = capsys.readouterr().out.strip()
        assert limpar(cnpj).isdigit()
        assert validar(cnpj) is True

    def test_gerar_quantidade_invalida_exit_1(self, capsys):
        assert main(["gerar", "0"]) == 1
        assert "erro" in capsys.readouterr().err

    def test_formatar_ok(self, capsys):
        assert main(["formatar", "12abc34501de35"]) == 0
        assert capsys.readouterr().out.strip() == "12.ABC.345/01DE-35"

    def test_formatar_invalido_exit_1(self, capsys):
        assert main(["formatar", "abc"]) == 1
        assert "erro" in capsys.readouterr().err

    def test_dv_ok(self, capsys):
        assert main(["dv", "12ABC34501DE"]) == 0
        assert capsys.readouterr().out.strip() == "35"

    def test_dv_invalido_exit_1(self, capsys):
        assert main(["dv", "abc"]) == 1
        assert "erro" in capsys.readouterr().err
