# Trabalho IV — Ofuscação de código e custo de desempenho (Python)

Disciplina de Sistemas Operacionais — FURG, Prof. Vinícius Garcia Pinto.
Entrega no AVA até **30/10/2026 23h55** (50% da N4). Haverá apresentação em aula:
todos os integrantes devem saber explicar qualquer parte do trabalho.

**Grupo:** _(nomes dos até 3 integrantes)_

## Objetivo

Medir quanto custa, em tempo de execução, aplicar diferentes configurações de
ofuscação a dois benchmarks fornecidos (multiplicação de matrizes e contagem de
palavras), usando **Python**. A base de comparação é sempre o código Python
não ofuscado.

## Estrutura

```
.
├── README.md
├── config.json            # tamanhos de entrada, repetições e configurações de ofuscação
├── requirements.txt
├── src/                   # benchmarks ORIGINAIS (fornecidos pelo professor, sem alterações)
│   ├── matrizes.py        #   (t4-multi-python.py)
│   └── palavras.py        #   (t4-palavras.py)
├── ofuscado/              # código ofuscado gerado (um subdiretório por configuração)
├── scripts/
│   ├── info_sistema.py    # registra SO, CPU, memória e versões das ferramentas
│   ├── calibrar.py        # acha tamanhos de entrada com original >= 20 s
│   ├── ofuscar.py         # gera ofuscado/<config>/ a partir de src/
│   ├── rodar_benchmarks.py# executa tudo e grava resultados/raw.csv
│   └── analisar.py        # tabelas e gráficos
├── resultados/
│   ├── raw.csv            # todas as execuções
│   ├── tabelas.md         # média, mediana, desvio, mín, máx
│   ├── sistema.md         # ambiente de teste
│   └── graficos/
└── docs/
    ├── enunciado.md       # resumo das exigências do trabalho + checklist
    └── relatorio.md       # relatório (modelo a preencher)
```

## Instalação

Requer Python 3 (testado com a versão registrada em `resultados/sistema.md`).

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Ferramentas de ofuscação usadas:

| Ferramenta | Instalação | Site |
|---|---|---|
| PyArmor | `pip install pyarmor` | https://github.com/dashingsoft/pyarmor |
| python-minifier | `pip install python-minifier` | https://github.com/dflook/python-minifier |

> Confira as opções disponíveis na sua versão com `pyarmor gen --help`; os
> comandos exatos de cada configuração ficam em `config.json`.

## Como reproduzir

Fluxo completo (execute da raiz do repositório):

```bash
# 1. Registrar o ambiente
python scripts/info_sistema.py

# 2. Calibrar tamanhos (original >= 20 s) e atualizar "tamanhos" em config.json
python scripts/calibrar.py

# 3. Gerar o código ofuscado -> ofuscado/<config>/
python scripts/ofuscar.py

# 4. Conferir que o ofuscado roda e dá "ok" (teste rápido)
python scripts/rodar_benchmarks.py --reps 1 --so original pyarmor-basico   # (ajuste tamanhos para um teste curto)

# 5. Rodar tudo (10 repetições; pode levar horas) — retome com --retomar
python scripts/rodar_benchmarks.py

# 6. Tabelas e gráficos
python scripts/analisar.py
```

### Como o código foi ofuscado

Cada configuração em `config.json` (`ofuscadores`) define o comando usado.
`scripts/ofuscar.py` executa esses comandos sobre `src/*.py` e grava a saída em
`ofuscado/<config>/`. Configurações atuais:

| Config | Ferramenta | Técnicas |
|---|---|---|
| `original` | — | baseline |
| `minifier-renomear` | python-minifier | remoção de comentários/docstrings, renomeação de identificadores |
| `pyarmor-basico` | PyArmor | empacotamento/criptografia do bytecode (padrão) |
| `pyarmor-forte` | PyArmor | `--obf-module 1 --obf-code 2 --mix-str` (ofusca strings e código) |

_Atualize esta tabela se mudar as configurações._ O diretório `ofuscado/`
é versionado de propósito: faz parte da entrega.

## Metodologia (exigências do enunciado)

- ≥ 3 tamanhos de entrada, cada um ≥ 50% maior que o anterior; menor entrada do
  original ≥ 20 s (`calibrar.py`; ver `fator_entre_tamanhos` em `config.json`).
- 10 repetições por caso, intercaladas entre configurações.
- Tempo medido é o impresso pelo próprio benchmark (`time: X seconds`, só a
  parte computacional); o tempo total do processo também é gravado.
- Estatísticas: média, mediana, desvio padrão, mínimo e máximo.
- Ambiente controlado: fechar outros programas, notebook na tomada, mesma
  máquina e mesmo estado térmico em todas as configurações.

## Observações

- **Tamanhos em `config.json` são valores iniciais.** Rode `calibrar.py` na
  máquina que fará as medições.
- **Memória:** `palavras.py` cria a lista inteira de palavras antes de medir
  (cada string é um objeto separado). Entradas na casa de centenas de milhões
  podem esgotar a RAM — acompanhe o uso durante a calibração.
- **Custo do matrizes cresce com n³:** aumentar 60% o tamanho multiplica o tempo
  por ~4. Planeje o tempo total (10 repetições × configurações × tamanhos).
- Alguns ofuscadores (PyArmor) geram uma pasta de runtime ao lado do script;
  o `rodar_benchmarks.py` já executa cada configuração dentro do seu diretório.

## Dificuldades, decisões e extras

Registrados em [docs/relatorio.md](docs/relatorio.md).
