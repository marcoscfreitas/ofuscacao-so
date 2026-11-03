# Instruções para assistentes de IA

Este repositório é um trabalho universitário em grupo (Sistemas Operacionais, FURG):
medir o custo de desempenho da ofuscação de código Python. **Três pessoas rodam o mesmo benchmark, cada uma na sua máquina, e comparam os resultados.**
Você provavelmente está ajudando um dos três. Leia primeiro:

1. [docs/GUIA-GRUPO.md](docs/GUIA-GRUPO.md) — procedimento completo, passo a passo.
2. [README.md](README.md) — objetivo, estrutura, metodologia.
3. [docs/enunciado.md](docs/enunciado.md) — exigências do professor e checklist.
4. [docs/DECISOES-EXPERIMENTO.md](docs/DECISOES-EXPERIMENTO.md) — achados, pendências
   dos verificadores e critérios para máquinas/SOs diferentes.
5. [docs/AUDITORIA-REQUISITOS-2026-11-03.md](docs/AUDITORIA-REQUISITOS-2026-11-03.md)
   — conferência do PDF original e fluxo compartilhado revisado.

## Fluxo resumido (id da máquina = primeiro nome da pessoa, minúsculo)

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/info_sistema.py --maquina ID
python scripts/ofuscar.py      --maquina ID
python scripts/verificar.py    --maquina ID          # exija "tudo certo" e confira 20 s nos dois originais
python scripts/rodar_benchmarks.py --maquina ID --confirmar-condicoes  # só após confirmação; horas
python scripts/analisar.py --maquina ID
```

## Regras

- **Use o pré-voo revisado.** Agora ele mede os dois menores originais e a RAM
  do maior palavras; abaixo de 20 s reprova. O resultado fica em `verificacao.json`.
  Para escolher entradas por máquina, `--sugerir-tamanhos` faz somente sondas curtas
  e não aprova nem aplica ajustes. Audite as dez repetições por caso com `auditar.py`.
  Não declarar exceção aceita apenas por estar documentada.
- **Retomada exige a mesma condição.** O runner registra `execucao.json` e bloqueia
  troca de Python, fontes, configuração ou perfil. Dados legados sem manifesto
  só podem ser analisados com `--exploratorio`; não invente metadados para aprová-los.
- **Perfil de CPU é parte do experimento.** A preparação de pedro em 1200 MHz
  é específica de sua máquina e ainda não teve rodada completa. Não aplicar esses
  limites em outras máquinas sem avaliação própria, nem misturar amostras de
  perfis/Pythons diferentes. Preservar os dados e registrar motivos e estado real.
- **Pergunte o id da máquina** à pessoa (o primeiro nome dela em minúsculas, ex.: `marcos`). Não invente
  nem use outro nome. Use sempre o mesmo id em todos os comandos.
- **Não edite `src/`.** São os benchmarks originais do professor.
- **Não rode `rodar_benchmarks.py` sem confirmar com a pessoa** que: a máquina está na
  tomada, os outros programas foram fechados, a suspensão está desativada e o
  `verificar.py` terminou com "tudo certo". A rodada leva horas e usa a CPU inteira; a
  medição só vale se a máquina ficar parada. Rode em segundo plano com log
  (`... | tee resultados-ID.log`) e **não use a máquina para outra coisa nesse período**.
- **Não rode `calibrar.py`** salvo se a pessoa pedir. Os tamanhos já estão definidos em
  `config.json` e são compartilhados para a comparação ser justa. Se `verificar.py` indicar
  que não servem, use o bloco `ajustes_por_maquina` que ele imprime (veja o guia, seção 5)
  e avise a pessoa de que o grupo precisa ser informado.
- **Cada máquina gera o próprio `ofuscado/<id>/`** (o runtime do PyArmor depende de
  SO/arquitetura/versão do Python). Nunca copie o `ofuscado/` de outra pessoa.
- **Commit:** apenas `resultados/<id>/`, `ofuscado/<id>/` e, se necessário, a sua entrada em
  `ajustes_por_maquina` do `config.json`. Nunca `.venv/`, `.pyarmor/` ou logs. Faça
  `git pull --rebase` antes do `push`. Não altere pastas de outras máquinas.
- `rodar_benchmarks.py` recusa rodar se `resultados/<id>/raw.csv` existe, a menos que use
  `--retomar` (continuar) — não apague dados sem a pessoa pedir.
- **Não "conserte" o PyArmor trial.** A licença gratuita recusa `--obf-code 2`,
  `--mix-str`, `--enable rft|bcc` (`out of license`); a config `pyarmor-forte` já usa só
  o que a trial aceita.

## O que devolver à pessoa

Ao terminar `verificar.py` ou a rodada, resuma: SO/CPU/RAM/Python da máquina, resultado
da verificação, e **qualquer problema** (erros de instalação, falhas do PyArmor, RAM,
tamanhos ajustados). Esses itens vão para a seção "Dificuldades e decisões" do relatório
([docs/relatorio.md](docs/relatorio.md)) e valem nota — registre o erro exato.

## Mapa do código

- `scripts/comum.py` — config (com `ajustes_por_maquina`), caminhos, execução de um benchmark.
- `scripts/info_sistema.py`, `ofuscar.py`, `verificar.py`, `rodar_benchmarks.py`,
  `analisar.py`, `calibrar.py` — todos (exceto `calibrar`/`analisar`) exigem `--maquina`.
- `config.json` — tamanhos, repetições, comandos de cada ofuscador, ajustes por máquina.
- Saída do benchmark: o próprio programa imprime `time: X seconds` (só a parte
  computacional) e `... are ok` (verificação); `comum.executar` captura isso.
