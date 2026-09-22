# cnpj-alfanumerico

Biblioteca Python que valida, calcula dígito verificador, formata e gera CNPJs no formato alfanumérico da Receita Federal (IN RFB 2.229/2024), com retrocompatibilidade total com CNPJs numéricos. Zero dependências em runtime, pacote tipado, CLI incluída.

## Stack e estrutura

- Python >= 3.10, build via `hatchling`, layout `src/`.
- `src/cnpjalfa/core.py`: algoritmo (limpar, calcular_dv, validar, formatar, gerar).
- `src/cnpjalfa/errors.py`: `ValidationError` (subclasse de `ValueError`).
- `src/cnpjalfa/__init__.py`: API pública e aliases em inglês (`is_valid`, `calculate_dv`, `format_cnpj`, `clean`, `generate`).
- `src/cnpjalfa/__main__.py`: CLI (`cnpjalfa`), exit code 0/1 para válido/inválido, exit 2 reservado pelo `argparse`.
- `tests/test_cnpjalfa.py`: suíte pytest.
- Sem dependências de runtime (`dependencies = []` no `pyproject.toml`). Dependências de dev: `pytest`, `pytest-cov`, `ruff`.

## Comandos obrigatórios

- Setup: `python -m pip install -e ".[dev]"`
- Lint: `python -m ruff check .`
- Formatação: `python -m ruff format --check .`
- Testes: `python -m pytest -q --cov=cnpjalfa --cov-report=term-missing`
- Build: não há (nenhum workflow ou script do repo empacota o wheel; o backend `hatchling` está declarado em `pyproject.toml` mas não há comando de build documentado nem em CI).
- E2E: não há.

O CI (`.github/workflows/ci.yml`) roda lint, formatação e testes em matriz `ubuntu-latest`/`windows-latest` x Python 3.10 a 3.13. Rode as mesmas verificações localmente antes de qualquer entrega.

## Convenções de arquitetura e segurança

- Algoritmo do DV (módulo 11, conversão ASCII-48, pesos 2-9 recomeçando a cada 8 posições) é a fonte de verdade normativa (PDF técnico do SERPRO e FAQ da RFB, citados no README). Qualquer mudança no cálculo exige conferir o exemplo oficial `12ABC34501DE` -> DV `35` (coberto em teste).
- `limpar()` rejeita entrada não-ASCII antes de `.upper()`: proteção deliberada contra lookalikes Unicode (ex.: `ı` U+0131, `ſ` U+017F) que o `str.upper()` do Python mapeia para caracteres ASCII e furariam o regex `[A-Z0-9]`. Não remover essa checagem ao mexer em `limpar`/`validar`.
- `validar()` nunca levanta exceção, para qualquer entrada (incluindo `None` e tipos não-`str`); `calcular_dv`, `formatar` e `limpar` levantam `ValidationError` para entrada estruturalmente inválida. Preservar essa distinção de contrato ao alterar as funções.
- `validar()` rejeita base com um único caractere repetido (ex.: `000000000000`) mesmo com DV correto: não é uma inscrição real.
- `gerar()` não usa fonte criptográfica (`random`, não `secrets`): é para dados de teste/dev, nunca para inscrições reais. Manter esse aviso se a função for exposta em outro lugar.
- API pública é bilíngue (funções em português + aliases em inglês no `__init__.py`): ao adicionar função nova, adicionar também o alias correspondente e listar em `__all__`.
- Zero dependências de runtime é um requisito do projeto (ver descrição no `pyproject.toml` e comparação no README): qualquer dependência nova em runtime precisa de justificativa explícita do usuário.

## Áreas críticas

- `src/cnpjalfa/core.py`: tabela de pesos, conversão ASCII-48 e regras de validação (checagem ASCII, caractere único repetido) não devem ser simplificadas sem pedido explícito: são requisitos normativos ou de segurança, não estilo.
- `pyproject.toml`: `[project.scripts]`, `dependencies = []` e classifiers de versão do Python refletem o contrato público do pacote publicado no PyPI. Alterar com cautela.

## Regras de trabalho

- Mudanças pequenas e testadas. Sem commit, push ou deploy sem pedido explícito: entregas via `/entrega`.
- Formato de entrega: arquivos alterados, decisões tomadas, comandos de validação executados (com resultado), pendências abertas.

## Decisões do projeto

Ainda não há arquivo de decisões neste repo. Quando existir, será `.claude/memory/decisions.md` (convenção global); não crie um novo local sem necessidade.
