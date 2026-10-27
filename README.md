# Trabalho IV — Ofuscação de código e custo de desempenho (Python)

Disciplina de Sistemas Operacionais — FURG, Prof. Vinícius Garcia Pinto.
Entrega no AVA até **30/10/2026 23h55** (50% da N4). Haverá apresentação em aula:
todos os integrantes devem saber explicar qualquer parte do trabalho.

**Grupo:** _(nomes dos até 3 integrantes)_

> **Vai rodar o benchmark na sua máquina?** Leia o [guia do grupo](docs/GUIA-GRUPO.md)
> (e, se estiver usando um assistente de IA, o [AGENTS.md](AGENTS.md)).

## Objetivo

Medir quanto custa, em tempo de execução, aplicar diferentes configurações de
ofuscação a dois benchmarks fornecidos (multiplicação de matrizes e contagem de
palavras), usando **Python**. A base de comparação é sempre o código Python
não ofuscado. O experimento é repetido em **três máquinas** (uma por integrante) e
os resultados são comparados.

## Estrutura

```
.
├── README.md
├── AGENTS.md / CLAUDE.md  # instruções para assistentes de IA
├── config.json            # tamanhos, repetições, configs de ofuscação, ajustes por máquina
├── requirements.txt
├── src/                   # benchmarks ORIGINAIS (fornecidos pelo professor, sem alterações)
│   ├── matrizes.py        #   (t4-multi-python.py)
│   └── palavras.py        #   (t4-palavras.py)
├── ofuscado/<maquina>/<config>/   # código ofuscado gerado EM CADA máquina
├── scripts/
│   ├── info_sistema.py    # registra SO, CPU, memória e versões das ferramentas
│   ├── ofuscar.py         # gera ofuscado/<maquina>/<config>/ a partir de src/
│   ├── verificar.py       # checagem pré-voo (ofuscado ok? RAM? tamanhos? tempo estimado)
│   ├── rodar_benchmarks.py# executa tudo e grava resultados/<maquina>/raw.csv
│   ├── analisar.py        # tabelas e gráficos (por máquina e comparação)
│   ├── calibrar.py        # busca de tamanhos (uso avançado, normalmente desnecessário)
│   └── comum.py           # utilitários compartilhados
├── resultados/
│   ├── <maquina>/         # sistema.md, raw.csv, tabelas.md, graficos/
│   ├── comparacao.md      # máquinas lado a lado
│   └── graficos/          # comparacao_<benchmark>.png
└── docs/
    ├── GUIA-GRUPO.md      # como cada integrante roda e como juntamos os resultados
    ├── enunciado.md       # resumo das exigências do trabalho + checklist
    └── relatorio.md       # relatório (modelo a preencher)
```

## Instalação

Requer Python 3 (a versão fica registrada em `resultados/<maquina>/sistema.md`).

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

Ambas entram no `requirements.txt`. Os scripts as chamam via `python -m`, usando o
Python do venv ativo, então não dependem do PATH.

## Como reproduzir (uma máquina)

Todos os scripts que geram dados exigem `--maquina <id>` (o primeiro nome de cada integrante, em minúsculas; ex.: `marcos`),
que separa os resultados de cada integrante. Execute da raiz do repositório, com o
venv ativado:

```bash
# 1. Registrar o ambiente  -> resultados/<id>/sistema.md
python scripts/info_sistema.py --maquina <id>

# 2. Gerar o código ofuscado  -> ofuscado/<id>/<config>/
python scripts/ofuscar.py --maquina <id>

# 3. Checagem pré-voo (testa as configs, confere RAM e tamanhos, estima a duração)
python scripts/verificar.py --maquina <id>

# 4. Rodada completa (10 repetições; horas) — retome com --retomar se interromper
python scripts/rodar_benchmarks.py --maquina <id>

# 5. Tabelas e gráficos
python scripts/analisar.py --maquina <id>     # só esta máquina
python scripts/analisar.py                    # todas + comparação entre máquinas
```

Detalhes (preparar a noite de medição, o que fazer se o `verificar.py` reclamar,
commits, ajustes de tamanho por máquina) estão no [guia do grupo](docs/GUIA-GRUPO.md).

### Como o código foi ofuscado

Cada configuração em `config.json` (`ofuscadores`) define o comando usado.
`scripts/ofuscar.py` executa esses comandos sobre `src/*.py` e grava a saída em
`ofuscado/<id>/<config>/`. Configurações atuais:

| Config | Ferramenta | Técnicas |
|---|---|---|
| `original` | — | baseline |
| `minifier-renomear` | python-minifier | remoção de comentários/docstrings, renomeação de identificadores |
| `pyarmor-basico` | PyArmor | empacotamento/criptografia do bytecode (padrão) |
| `pyarmor-forte` | PyArmor | `--obf-module 1 --obf-code 1 --enable jit --private --assert-call --assert-import` |

> A licença *trial* do PyArmor 9.2.8 recusa (`out of license`) `--obf-code 2`,
> `--mix-str`, `--enable rft` e `--enable bcc`; por isso o `pyarmor-forte` usa
> apenas opções aceitas pela trial.

_Atualize esta tabela se mudar as configurações._ O diretório `ofuscado/<id>/`
é versionado de propósito: faz parte da entrega. Cada integrante gera e commita o
seu, pois o runtime do PyArmor depende de SO, arquitetura e versão do Python.

## Trabalho em grupo: três máquinas

- Cada integrante roda o pipeline na própria máquina e commita **somente** as pastas
  `resultados/<id>/` e `ofuscado/<id>/`. Não há conflito de arquivos.
- Todos usam os **mesmos tamanhos** do `config.json`, para a comparação ser justa.
  Se a máquina não comportar (principalmente RAM no `palavras`) ou for rápida demais
  para o `matrizes`, o `verificar.py` imprime um bloco para a chave `ajustes_por_maquina`
  do `config.json`, aplicado só à máquina em questão. Isso deve ser documentado.
- Depois que os três enviarem, `python scripts/analisar.py` gera as tabelas por
  máquina e `resultados/comparacao.md` com gráficos de slowdown lado a lado.
- A comparação entre máquinas usa **slowdown** (tempo ofuscado ÷ tempo original, na
  mesma máquina), não tempos absolutos.

## Metodologia (exigências do enunciado)

- ≥ 3 tamanhos de entrada, cada um ≥ 50% maior que o anterior; menor entrada do
  original ≥ 20 s (`verificar.py` estima isso; ver `fator_entre_tamanhos` em `config.json`).
- 10 repetições por caso, intercaladas entre configurações.
- Tempo medido é o impresso pelo próprio benchmark (`time: X seconds`, só a
  parte computacional); o tempo total do processo também é gravado, e a diferença
  entre os dois é o overhead de inicialização.
- Estatísticas: média, mediana, desvio padrão, mínimo e máximo.
- Ambiente controlado: fechar outros programas, notebook na tomada, mesma
  máquina e mesmo estado térmico em todas as configurações.

## Tamanhos de entrada

| Benchmark | Tamanhos | Observação |
|---|---|---|
| matrizes | 560, 840, 1264 (fator 1,5) | ~21 s no original no menor tamanho (Ryzen 5 5500) |
| palavras | 50M, 80M, 128M (fator 1,6) | **não chega a 20 s** (≈ 8 s no maior): limitado pela RAM |

**Exceção do `palavras`:** o benchmark mantém todas as palavras na memória
(~56 bytes por palavra) e leva ~61 ns por palavra. Para 20 s seriam ~325 milhões de
palavras (~18 GB), mais do que a RAM da máquina de referência (15,5 GiB). Em vez de
alterar o benchmark do professor, usamos o maior tamanho que cabe e documentamos a
limitação no relatório.

## Observações

- **Custo do matrizes cresce com n³:** aumentar 50% o tamanho multiplica o tempo
  por ~3,4. Planeje o tempo total (10 repetições × configurações × tamanhos): ~4 h na
  máquina de referência.
- Alguns ofuscadores (PyArmor) geram uma pasta de runtime ao lado do script;
  o `rodar_benchmarks.py` já executa cada configuração dentro do seu diretório.
- O diretório `.pyarmor/` (cache/licença local) não é versionado.

## Dificuldades, decisões e extras

Registrados em [docs/relatorio.md](docs/relatorio.md).
