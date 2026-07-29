# cnpj-alfanumerico

[![CI](https://github.com/chiarelli-dev/cnpj-alfanumerico/actions/workflows/ci.yml/badge.svg)](https://github.com/chiarelli-dev/cnpj-alfanumerico/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cnpj-alfanumerico)](https://pypi.org/project/cnpj-alfanumerico/)
[![Python](https://img.shields.io/pypi/pyversions/cnpj-alfanumerico)](https://pypi.org/project/cnpj-alfanumerico/)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE)

CNPJ alfanumérico é o novo formato de inscrição da Receita Federal do Brasil, em produção a partir de julho de 2026 (IN RFB nº 2.229/2024). CNPJs numéricos existentes permanecem válidos; o formato novo vale para novas inscrições, incluindo novas filiais. Esta biblioteca Python valida, calcula dígito verificador, formata e gera CNPJs alfanuméricos e numéricos, com zero dependências e retrocompatibilidade total.

Última atualização: julho de 2026.

## O que muda no CNPJ alfanumérico

O CNPJ continua com 14 posições, no padrão `AA.AAA.AAA/AAAA-DV`. O que muda:

- **As 12 primeiras posições passam a ser alfanuméricas.** A raiz (posições 1 a 8) e a ordem da filial (posições 9 a 12) podem conter numerais `0-9` e letras maiúsculas `A-Z`, atribuídas aleatoriamente pelo sistema da RFB. Raiz alfanumérica com ordem numérica é possível, e vice-versa.
- **As 2 últimas posições (dígitos verificadores) são SEMPRE numéricas.** Confirmado no FAQ oficial da Receita Federal (pergunta 2: "AA.AAA.AAA/AAAA-DV onde A = alfanumérico, DV = dígito verificador pelo módulo 11") e no documento técnico do SERPRO ("doze caracteres alfanuméricos e dois dígitos verificadores numéricos").
- **A data de início é julho de 2026.** FAQ oficial da RFB, pergunta 4: "A data para início de entrada em produção dos primeiros CNPJ alfanuméricos será a partir de Julho de 2026" (reconfirmado na pergunta 26). Base normativa: Instrução Normativa RFB nº 2.229, de 15 de outubro de 2024.

### Regra de conversão dos caracteres

Cada caractere é convertido para o seu valor decimal na tabela ASCII menos 48:

- Dígitos `0-9` (ASCII 48 a 57) mantêm os valores 0 a 9.
- Letras `A-Z` (ASCII 65 a 90) valem 17 a 42 (A=17, B=18, C=19, D=20, E=21, ..., Z=42).

A regra está literal nas duas fontes oficiais: o SERPRO manda "atribuir o valor da coluna Valor para cálculo do DV ou subtrair 48 do Valor ASCII" (com a tabela completa 0=0 ... 9=9, A=17 ... Z=42) e o FAQ da RFB, pergunta 14, exemplifica: "Tomemos a letra A cujo decimal correspondente, no código ASCII, é 65. Subtraindo 48 temos o valor 17". Como `0-9` preservam seus valores, o algoritmo é 100% retrocompatível com CNPJs numéricos.

### Como calcular o dígito verificador do CNPJ alfanumérico (exemplo passo a passo)

O DV usa módulo 11 em duas etapas, com pesos de 2 a 9 aplicados da direita para a esquerda, recomeçando a cada 8 posições. Resto 0 ou 1 resulta em DV 0; caso contrário, DV = 11 menos o resto.

Exemplo oficial da spec: base `12ABC34501DE`, DV esperado `35` (documento do SERPRO, resultado final `12.ABC.345/01DE-35`; FAQ da RFB, pergunta 14, com as mesmas somas).

**Passo 1: converter cada caractere (ASCII menos 48).**

| Caractere | 1 | 2 | A | B | C | 3 | 4 | 5 | 0 | 1 | D | E |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Valor | 1 | 2 | 17 | 18 | 19 | 3 | 4 | 5 | 0 | 1 | 20 | 21 |

**Passo 2: primeiro DV.** Pesos sobre as 12 posições: `5 4 3 2 9 8 7 6 5 4 3 2`.

```
soma1 = 1*5 + 2*4 + 17*3 + 18*2 + 19*9 + 3*8 + 4*7 + 5*6 + 0*5 + 1*4 + 20*3 + 21*2
      = 5 + 8 + 51 + 36 + 171 + 24 + 28 + 30 + 0 + 4 + 60 + 42
      = 459
459 % 11 = 8  ->  DV1 = 11 - 8 = 3
```

**Passo 3: segundo DV.** Anexa DV1 à base (13 valores), pesos `6 5 4 3 2 9 8 7 6 5 4 3 2`.

```
soma2 = 1*6 + 2*5 + 17*4 + 18*3 + 19*2 + 3*9 + 4*8 + 5*7 + 0*6 + 1*5 + 20*4 + 21*3 + 3*2
      = 6 + 10 + 68 + 54 + 38 + 27 + 32 + 35 + 0 + 5 + 80 + 63 + 6
      = 424
424 % 11 = 6  ->  DV2 = 11 - 6 = 5
```

Resultado: `12.ABC.345/01DE-35`. As somas 459 e 424 batem com o FAQ da RFB e o algoritmo desta biblioteca reproduz o vetor oficial (revalidado computacionalmente na suíte de testes).

### Fontes oficiais

- [SERPRO: Cálculo dos dígitos verificadores de CNPJ alfanumérico (PDF)](https://www.serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf). Documento oficial com a tabela de conversão completa, pesos, regra do resto e o exemplo `12.ABC.345/01DE-35`.
- [Receita Federal: Perguntas e Respostas CNPJ Alfanumérico (PDF, 14 páginas)](https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf). Formato `AA.AAA.AAA/AAAA-DV`, regra ASCII-48, exemplo completo com somas 459/424 e a data de julho de 2026.
- [Receita Federal: notícia oficial sobre a IN RFB 2.229/2024](https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2024/outubro/cnpj-tera-letras-e-numeros-a-partir-de-julho-de-2026).
- [SERPRO: notícia com códigos de validação em Java, Python e TypeScript](https://www.serpro.gov.br/menu/noticias/noticias-2024/cnpj-alfanumerico).

## Como instalar

```bash
pip install cnpj-alfanumerico
```

Requer Python 3.10 ou superior. Zero dependências: só a biblioteca padrão. Pacote tipado (`py.typed`).

## Como usar em Python (API completa)

O módulo importável chama-se `cnpjalfa`. Todas as funções aceitam entrada com ou sem a máscara oficial, em qualquer caixa.

### validar(cnpj) -> bool

Valida CNPJ alfanumérico ou numérico legado. NUNCA levanta exceção: retorna `False` para qualquer entrada inválida, inclusive `None`, tipos que não são `str`, máscara malformada, DV incorreto e base com um único caractere repetido (ex.: `000000000000`).

```python
import cnpjalfa

cnpjalfa.validar("12.ABC.345/01DE-35")   # True (exemplo oficial SERPRO/RFB)
cnpjalfa.validar("12ABC34501DE35")       # True (sem máscara)
cnpjalfa.validar("11.222.333/0001-81")   # True (CNPJ numérico legado)
cnpjalfa.validar("12.ABC.345/01DE-99")   # False (DV errado)
cnpjalfa.validar(None)                   # False (nunca levanta exceção)
```

### calcular_dv(cnpj_sem_dv) -> str

Calcula os 2 dígitos verificadores da base de 12 posições. Levanta `ValidationError` se, após a limpeza, a base não tiver exatamente 12 caracteres em `[A-Z0-9]`.

```python
cnpjalfa.calcular_dv("12ABC34501DE")     # '35'
cnpjalfa.calcular_dv("12.abc.345/01de")  # '35' (aceita máscara e minúsculas)
```

### formatar(cnpj) -> str

Aplica a máscara oficial `XX.XXX.XXX/XXXX-XX`. Valida apenas a estrutura (14 posições, DVs numéricos), não o valor do DV. Levanta `ValidationError` para estrutura inválida.

```python
cnpjalfa.formatar("12abc34501de35")      # '12.ABC.345/01DE-35'
```

### limpar(cnpj) -> str

Remove máscara (pontos, barra, hífen e espaços) e converte a maiúsculas. Só normaliza, não valida o conteúdo além do charset. Levanta `ValidationError` se a entrada não for `str` ou contiver caracteres não-ASCII (proteção contra lookalikes Unicode como `ı` U+0131, que `str.upper` mapearia para `I`).

```python
cnpjalfa.limpar("12.abc.345/01de-35")    # '12ABC34501DE35'
```

### gerar(alfanumerico=True) -> str

Gera um CNPJ válido aleatório para testes e desenvolvimento, já com a máscara aplicada. Com `alfanumerico=False` gera apenas dígitos (formato numérico legado). Não usa fonte criptográfica: é para dados de teste, não para inscrições reais.

```python
cnpjalfa.gerar()                         # ex.: '2D.IYU.IYY/8S80-11'
cnpjalfa.gerar(alfanumerico=False)       # CNPJ numérico legado válido
cnpjalfa.validar(cnpjalfa.gerar())       # True, sempre
```

### ValidationError

Exceção do pacote (subclasse de `ValueError`), levantada por `calcular_dv`, `formatar` e `limpar` para entrada estruturalmente inválida. `validar` nunca a levanta.

```python
from cnpjalfa import ValidationError

try:
    cnpjalfa.formatar("123")
except ValidationError as exc:
    print(exc)
```

### Aliases em inglês

Mesmo comportamento, nomes em inglês: `is_valid` (validar), `calculate_dv` (calcular_dv), `format_cnpj` (formatar), `clean` (limpar), `generate` (gerar).

```python
from cnpjalfa import is_valid, generate

is_valid(generate())                     # True
```

## Como usar a CLI

O pacote instala o comando `cnpjalfa` (também acessível via `python -m cnpjalfa`). Exit code 0 para CNPJ válido e 1 para inválido, pensado para shell script.

```bash
cnpjalfa validar "12.ABC.345/01DE-35"
# valido        (exit code 0)

cnpjalfa validar "12.ABC.345/01DE-99"
# invalido      (exit code 1)

cnpjalfa gerar 2
# 2D.IYU.IYY/8S80-11
# WO.NJE.0UI/26XW-78

cnpjalfa gerar --numerico
# CNPJ numérico legado válido

cnpjalfa formatar 12abc34501de35
# 12.ABC.345/01DE-35

cnpjalfa --version
```

Uso em script:

```bash
cnpjalfa validar "$CNPJ" && echo ok
```

## Comparação com outras bibliotecas de CNPJ

Várias bibliotecas já suportam o formato alfanumérico, e este README diz isso com clareza. O diferencial de `cnpj-alfanumerico` é o foco único no novo formato com zero dependências, tipagem (`py.typed`), CLI incluída e API bilíngue pt/en. Legenda: n/v = não verificado no código-fonte.

| Biblioteca | Linguagem | Suporta alfanumérico | Zero deps | Tipada | CLI | Observação |
|---|---|---|---|---|---|---|
| **cnpj-alfanumerico (esta)** | Python | Sim | Sim | Sim | Sim | Foco único no CNPJ alfanumérico, retrocompatível com o numérico. |
| [brutils](https://pypi.org/project/brutils/) | Python | Sim | n/v | n/v | Não | v2.5.0 (2026-06-30) valida E gera alfanumérico: `is_valid` usa `_is_alphanumeric(cnpj[:12])` + DVs numéricos, `generate(alphanumeric=True)`. Confirmado no código de `brutils/cnpj.py`. A issue #685 foi fechada como stale, mas o suporte entrou por outro caminho. |
| [validate-docbr](https://pypi.org/project/validate-docbr/) | Python | Sim | n/v | n/v | Não | v2.0.0 (2026-04-04) declara suporte a CNPJ numérico e alfanumérico na descrição do PyPI. É a lib de documentos BR mais popular do Python. |
| [brazilnum](https://pypi.org/project/brazilnum/) | Python | Sim | n/v | n/v | Não | v0.10.0 (2026-07-24): o código usa `CNPJ_PATTERN ^[0-9A-Z]{12}[0-9]{2}$` e conversão A-Z para 17-42. O README do PyPI ainda não menciona alfanumérico. |
| [cnpj-cpf-validator](https://pypi.org/project/cnpj-cpf-validator/) | Python | Sim | n/v | n/v | n/v | Lib dedicada de FredericoSFerreira com suporte explícito ao padrão de julho/2026. Tem versão gêmea em TypeScript/npm. |
| [br-cpf-cnpj](https://pypi.org/project/br-cpf-cnpj/) | Python | Sim | n/v | n/v | n/v | Validação e geração de CPF/CNPJ com suporte declarado ao novo padrão. |
| [alfac](https://libraries.io/pypi/alfac) | Python | Sim | n/v | n/v | n/v | Lib pequena dedicada ao CNPJ alfanumérico (norma técnica SERPRO), aceita o formato numérico legado. |
| [robotframework-cnpjalfanum](https://github.com/Srjordao/robotframework-cnpjalfanum) | Python (Robot Framework) | Sim | n/v | n/v | Não | Keywords de Robot Framework para gerar, validar e formatar. Nicho QA. |
| [cpf-cnpj-validator](https://www.npmjs.com/package/cpf-cnpj-validator) | JavaScript/TypeScript | Sim | n/v | n/v | n/v | v2.x (atual 2.1.2) valida ambos os formatos com módulo 11 e conversão ASCII-48 (A=17..Z=42). |
| [validation-br](https://github.com/klawdyo/validation-br) | JavaScript/TypeScript | Sim | n/v | n/v | n/v | Suíte de documentos BR (CPF, CNPJ numérico e alfanumérico, título, PIS, CNH etc.). |
| [gerador-validador-cnpj](https://www.npmjs.com/package/gerador-validador-cnpj) | JavaScript | Sim | n/v | n/v | n/v | Gera e valida CNPJ alfanumérico. |
| [cnpj-universal](https://dev.to/leandrogazoli/validando-cnpj-de-forma-definitiva-conheca-a-cnpj-universal-jsts-2l68) | JavaScript/TypeScript | Sim | n/v | n/v | n/v | Valida formato clássico e alfanumérico seguindo as notas técnicas da RFB. |
| [novo-cnpj (gabrielfroes)](https://github.com/gabrielfroes/novo-cnpj) | TypeScript | Sim | n/v | n/v | n/v | Repo mais estrelado do tema no GitHub (~43 stars). |
| [validador-cnpj-alfanumerico (marcelo-lourenco)](https://github.com/marcelo-lourenco/validador-cnpj-alfanumerico) | Multi (JS, Java, Python, TS, PHP, Laravel) | Sim | n/v | n/v | Não | Coleção de snippets em 6 linguagens com site GitHub Pages, não é pacote publicado em PyPI/npm. |
| [cnpj-alfanumerico (JohnPitter)](https://github.com/JohnPitter/cnpj-alfanumerico) | Java | Sim | n/v | n/v | n/v | Colisão de nome de repo (owner diferente): validação, formatação e geração citando a IN RFB 2.229/2024. |
| [CnpjAlfaNumerico (FRACerqueira)](https://github.com/FRACerqueira/CnpjAlfaNumerico) e CnpjAlfanumerico (NIZZOLA) | C# | Sim | n/v | n/v | n/v | Validadores .NET dedicados ao novo formato. |
| [brado](https://github.com/brenomfviana/brado) | Rust | Sim (declarado) | n/v | n/v | n/v | Validador de documentos BR em Rust; suporte declarado, não verificado no código. |
| [br-validations](https://www.npmjs.com/package/br-validations) | JavaScript (legado AngularJS) | Não | n/v | n/v | n/v | Lib antiga sem manutenção ativa; nenhuma evidência de suporte ao formato alfanumérico. |

## Perguntas frequentes

### Como validar CNPJ alfanumérico em Python?

Instale `pip install cnpj-alfanumerico` e chame `cnpjalfa.validar("12.ABC.345/01DE-35")`, que retorna `True` ou `False` sem nunca levantar exceção. A função aceita entrada com ou sem máscara, em qualquer caixa, e também valida CNPJs numéricos legados com o mesmo algoritmo.

### O que é o novo CNPJ alfanumérico de 2026?

É o formato de inscrição que a Receita Federal passa a emitir a partir de julho de 2026 (IN RFB nº 2.229/2024): as 12 primeiras posições aceitam letras `A-Z` e números `0-9`, e os 2 dígitos verificadores continuam numéricos. Vale só para novas inscrições; os CNPJs numéricos existentes permanecem válidos.

### CNPJ com letras: como validar?

Converta cada um dos 12 primeiros caracteres para o valor ASCII menos 48 (dígitos mantêm 0-9; A=17 até Z=42), aplique módulo 11 com pesos de 2 a 9 da direita para a esquerda e compare com os 2 DVs numéricos. Em Python, `cnpjalfa.validar()` faz tudo isso em uma chamada.

### Qual é o algoritmo do dígito verificador do CNPJ alfanumérico?

Módulo 11 em duas etapas sobre os valores ASCII-48 dos caracteres, com pesos de 2 a 9 distribuídos da direita para a esquerda, recomeçando a cada 8 posições. Resto 0 ou 1 gera DV 0; caso contrário, DV = 11 menos o resto. Exemplo oficial: base `12ABC34501DE` produz somas 459 e 424, DV `35`.

### Qual regex reconhece um CNPJ alfanumérico?

Sem máscara: `^[A-Z0-9]{12}[0-9]{2}$`. Com a máscara oficial: `^[A-Z0-9]{2}\.[A-Z0-9]{3}\.[A-Z0-9]{3}\/[A-Z0-9]{4}-[0-9]{2}$`. Atenção: regex confere só a estrutura, não o dígito verificador. Para validação completa use `cnpjalfa.validar()`, que também rejeita bases com um único caractere repetido.

### Como gerar CNPJ alfanumérico válido para teste?

Em Python, `cnpjalfa.gerar()` retorna um CNPJ alfanumérico válido já formatado. No terminal, `cnpjalfa gerar 10` imprime 10 de uma vez, e `cnpjalfa gerar --numerico` produz o formato numérico legado. O gerador serve para dados de teste e desenvolvimento, nunca para criar inscrições reais.

### Biblioteca Python para validar CNPJ: qual usar?

Se você precisa de vários documentos brasileiros (CPF, CNH, PIS), `brutils` e `validate-docbr` são boas opções e já suportam o alfanumérico. Se quer foco único no CNPJ com zero dependências, pacote tipado, CLI e aliases em inglês (`is_valid`, `generate`), use `cnpj-alfanumerico`.

### O CNPJ numérico atual continua válido depois de julho de 2026?

Sim. A Receita Federal confirma que os CNPJs numéricos existentes permanecem válidos e não serão alterados. O formato alfanumérico se aplica apenas a novas inscrições, incluindo novas filiais de empresas já constituídas. Como os dígitos preservam seus valores no cálculo, o mesmo validador cobre os dois formatos.

## Licença e autoria

Licença [MIT](LICENSE). Criado por Leonardo Chiarelli, [Chiarelli Labs](https://chiarelli.dev).

Biblioteca irmã: [ofx-br](https://github.com/chiarelli-dev/ofx-br), parser de extratos OFX de bancos brasileiros.
