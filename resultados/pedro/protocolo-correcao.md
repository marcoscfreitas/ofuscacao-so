# Protocolo da repetição — pedro

**Atualização de 05/11/2026:** a nova rodada foi concluída e aprovada, com 240
execuções, no perfil de alto desempenho registrado em `sistema.md` e
`execucao.json`. O perfil de 1200 MHz descrito abaixo **não foi utilizado**.
Palavras foi aceito pela exceção de duração do `config.json` (piso de 1 s).
O estado atual está em [rodada.md](rodada.md). O restante deste documento é o
registro histórico da preparação de 29/10 e da revisão de 03/11.

## Registro histórico da preparação

**Atualização de 03/11/2026:** este é o registro da preparação local de 29/10.
O fluxo compartilhado foi revisado na [auditoria do PDF](../../docs/AUDITORIA-REQUISITOS-2026-11-03.md).
Usar os scripts de `scripts/` e o guia atualizado; não depender do antigo supervisor
privado em `.venv`. Os parâmetros de CPU abaixo continuam específicos de pedro e
não foram ativados nesta revisão. A repetição completa permanece adiada.

Estado: preparação e sondas; a rodada final depende da confirmação de máquina
parada e da aprovação da verificação antes do início. O atendimento ao requisito
de duração será determinado pelos dados da nova rodada.

Em 29/10/2026, após essas sondas, o participante pediu **deixar a nova rodada
preparada para depois**. Ao encerrar essa preparação, a repetição completa não
havia sido iniciada, o plano de energia original havia sido restaurado e os
resultados anteriores permaneciam nas pastas originais. O `config.json`
compartilhado ainda não tinha o ajuste proposto de pedro.

Para o restante do grupo, consultar também os
[achados e critérios entre máquinas](../../docs/DECISOES-EXPERIMENTO.md).

## Objetivo e ambiente

Repetir integralmente os dois benchmarks, com dez repetições por caso, fazendo
o menor tamanho do original levar pelo menos 20 segundos. Os scripts originais
do professor e as opções dos ofuscadores permanecem iguais às da rodada anterior.
O interpretador permanece CPython 3.12.15, com PyArmor 9.2.8 trial e
python-minifier 3.4.0, na mesma máquina Windows 10/i7-9700/31,9 GiB.

A plataforma desta repetição terá um perfil de energia temporário com limite de
CPU de **1200 MHz**, estados mínimo/máximo em **40%** e Turbo Boost desativado.
O mesmo perfil será usado em todos os casos de ambos os benchmarks. Ele permite
atingir a duração com entradas que cabem na memória. Os resultados deverão ser
apresentados como medições nesse perfil de CPU. O perfil anterior será restaurado
ao concluir ou em uma interrupção tratada pelo supervisor.

O Windows permite configurar o limite de frequência com
[`PROCFREQMAX`](https://learn.microsoft.com/en-us/windows-hardware/customize/power-settings/options-for-perf-state-engine-maxfrequency).
O limite solicitado foi conferido nas sondas também pelo contador
`\Processor Information(_Total)\% Processor Performance`.

## Entradas propostas somente para pedro

| Benchmark | Tamanhos | Fator entre entradas |
|---|---|---|
| matrizes | 360, 544, 816 | 1,511 e 1,500 |
| palavras | 96.000.000, 144.000.000, 216.000.000 | 1,500 e 1,500 |

Os ajustes serão aplicados apenas em `ajustes_por_maquina.pedro` do `config.json`.
As entradas e os arquivos das demais máquinas serão preservados. Como os tamanhos
e o perfil mudam, a comparação do grupo deverá identificar essa escolha e
comparar o custo relativo dentro de cada máquina/perfil.

## Sondas e decisões

- As sondas dos originais em CPython 3.10, 3.13 e 3.14 não indicaram uma solução
  de tempo e memória superior ao ambiente 3.12 já utilizado.
- Em perfil de 1800 MHz, 80 milhões de palavras levaram 18,145 s e 120 milhões
  levaram 29,937 s, com saída correta. O pico de RAM da sonda de 120 milhões
  foi aproximadamente 7,02 GiB.
- A tentativa de 270 milhões foi interrompida pela proteção de RAM livre
  mínima de 3 GiB. Portanto, esse maior tamanho não foi aprovado nessa condição.
- Em perfil de 1200 MHz, as sondas reais concluíram com saída correta:
  matrizes n=360, **32,112 s**; palavras n=96.000.000, **32,874 s**;
  palavras n=216.000.000, **83,342 s**.
- O pico de RAM residente da sonda de 216 milhões foi **12,63 GiB**;
  a memória privada chegou a **12,88 GiB** e a RAM livre mínima foi **4,02 GiB**.
  A proteção de 3 GiB de RAM livre permaneceu atendida. Esses valores são de
  uma sonda de preparação e não substituem as dez repetições estatísticas.
- Nas amostras do contador durante as sondas de palavras, o desempenho ficou
  entre aproximadamente 39,71% e 39,78% da frequência nominal de 3000 MHz
  (cerca de 1191–1193 MHz), consistente com o perfil solicitado de 1200 MHz.
- O `verificar.py` foi executado com uma cópia local da configuração proposta,
  sob esse perfil, e terminou com **RESULTADO: tudo certo**: oito testes curtos
  aprovados, 17,7 GiB livres e menor tamanho de matrizes estimado em 30,5 s.
  O `config.json` compartilhado ainda não foi alterado nesta preparação.
- A estimativa interna do verificador foi de 7,2 horas. Para a janela de máquina
  parada, a previsão usada é de **10–12 horas**, incluindo a montagem das grandes
  entradas observada nas sondas e a variação dos tempos.
- Houve uma interrupção inicial da sonda por um limite conservador do monitor
  sobre memória privada/residente; a checagem foi ajustada para exigir divergência
  sustentada, pois a realocação do corpus pode produzir um pico transitório.
- Um erro transitório do contador de desempenho do Windows também interrompeu
  uma sonda inicial. Essas tentativas não integram o conjunto estatístico.

Mensagens exatas das interrupções de preparação:

```text
Sonda interrompida: menos de 3 GiB de RAM livre
Sonda interrompida: memoria privada excede residente em mais de 512 MiB
Internal performance counter API call failed. Error: 800007d6.
```

## Reprodução do perfil

Duplicar o plano de energia atual, guardar seu GUID e configurar somente a cópia
temporária. Com o GUID da cópia no lugar de `<temporario>`:

```powershell
powercfg /setacvalueindex <temporario> SUB_PROCESSOR PROCTHROTTLEMIN 40
powercfg /setacvalueindex <temporario> SUB_PROCESSOR PROCTHROTTLEMAX 40
powercfg /setacvalueindex <temporario> SUB_PROCESSOR PROCFREQMAX 1200
powercfg /setacvalueindex <temporario> SUB_PROCESSOR PERFBOOSTMODE 0
powercfg /setactive <temporario>
```

Executar os scripts do guia com o Python 3.12.15 e os ajustes de pedro descritos
acima. Restaurar o GUID do plano anterior ao concluir ou interromper o processo,
com `powercfg /setactive <anterior>`, e remover somente a cópia temporária com
`powercfg /delete <temporario>`. Em uma interrupção abrupta que impeça a restauração
automática, o GUID anterior fica registrado no status local do supervisor.

## Preservação e critérios da rodada

A rodada de 28–29/10/2026 será preservada em
`rodadas/2026-10-28-alto-desempenho/`, incluindo CSV, tabelas, gráficos, ambiente
e observações. A nova rodada produzirá um CSV separado na pasta principal.
Os dados dos dois perfis serão analisados separadamente.

Antes da medição, são exigidos: confirmação de tomada/programas fechados/suspensão
desativada, `verificar.py` aprovado, RAM disponível com 25% de folga e uma execução
real de cada menor entrada do original com pelo menos 22 s como margem inicial.

Durante a medição, RAM livre abaixo de 3 GiB ou qualquer execução do original
abaixo de 20 s interrompem a rodada, preservando os dados coletados. No final,
a auditoria exige exatamente 240 casos únicos, dez repetições por caso, saídas
corretas, retorno zero e todos os tempos do original de pelo menos 20 s.
Só após aprovação serão geradas as tabelas e os gráficos finais.

Essas verificações adicionais estão preparadas no supervisor local de pedro,
em `.venv`, que não é versionado. Elas não são proteções já implementadas em
`scripts/rodar_benchmarks.py` ou `scripts/verificar.py`. Para repetir o método
em outro computador, seguir o protocolo e conferir os critérios nesse ambiente;
os limites de 1200 MHz, 40% e 3 GiB não são uma configuração universal.
