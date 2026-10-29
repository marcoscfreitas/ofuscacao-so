# Achados e decisões do experimento em máquinas diferentes

Registro de 29/10/2026, antes da repetição da rodada de pedro.
Este documento orienta os integrantes e deve acompanhar o
[guia de execução](GUIA-GRUPO.md) e o [relatório](relatorio.md).

## 1. O problema identificado

O enunciado exige pelo menos 20 segundos na menor entrada do original, em
**ambos os benchmarks**, três tamanhos com crescimento de pelo menos 50% e dez
repetições por caso. A medida adotada pelo trabalho é `time: X seconds`, impressa
pelo benchmark. O tempo de abrir o processo e construir a entrada fica fora
desse cronômetro e não pode ser somado para fazer um caso atingir 20 segundos.

Os tamanhos globais foram definidos na máquina de referência. Eles não garantem
a mesma duração ou consumo de RAM em outra CPU, SO ou versão do Python.
Na primeira rodada de pedro, os cálculos passaram nas 240 execuções, mas palavras
não cumpriu a duração mínima. **Correção da saída e conformidade experimental
são verificações diferentes.** Registrar a pendência não dispensa o requisito.

### O que os scripts atuais verificam

| Etapa | Verifica | Conferência adicional necessária |
|---|---|---|
| `verificar.py` | Saída de testes curtos, estimativa de RAM e estimativa de duração de matrizes | Medir a menor entrada real dos dois originais; conferir os avisos e o pico real de RAM |
| `rodar_benchmarks.py` | Executa os casos e registra tempos, correção da saída e código de retorno | Auditar falhas, duração, completude e condições constantes da rodada |
| `analisar.py` | Produz estatísticas das linhas com saída correta e retorno zero | Confirmar dez repetições por caso; o script pode gerar tabelas de um conjunto incompleto |

Em `verificar.py`, matrizes abaixo do alvo pode produzir somente um aviso,
seguido de “tudo certo”; palavras não recebe essa checagem de duração.
Portanto, **“RESULTADO: tudo certo” é necessário no fluxo, mas não comprova
sozinho o atendimento ao enunciado**. As proteções adicionais descritas no
protocolo de pedro pertencem ao supervisor local preparado para sua repetição;
elas não foram incorporadas aos scripts compartilhados.

## 2. Evidências e estado de cada etapa de pedro

Ambiente: Windows 10 build 19045, Intel i7-9700, 8 núcleos/8 threads, 31,9 GiB
de RAM, CPython 3.12.15, PyArmor 9.2.8 trial e python-minifier 3.4.0.

| Etapa | O que foi observado | Situação |
|---|---|---|
| Primeira rodada, 28/10 22h36 a 29/10 04h31 | 240 casos únicos com saída correta e retorno zero; dez repetições por caso | Concluída, com pendência de duração em palavras |
| Matrizes original, n=560, primeira rodada | 26,263 a 28,106 s | Menor entrada passou de 20 s |
| Palavras original, primeira rodada | Médias de 4,316 s, 6,980 s e 10,924 s para 50M, 80M e 128M | Nenhuma das três médias atingiu 20 s |
| Sonda sob perfil de CPU de 1200 MHz | Matrizes n=360: 32,112 s; palavras n=96M: 32,874 s | Execuções isoladas corretas, acima de 20 s |
| Sonda de palavras, n=216M, no mesmo perfil | 83,342 s; pico residente 12,63 GiB; mínimo livre 4,02 GiB | Maior entrada testada com saída correta e reserva de RAM |
| Repetição completa no perfil de 1200 MHz | Preparada, estimada em 10–12 h | **Não iniciada: participante pediu deixar para depois** |

As tabelas da primeira rodada estão em
[resultados/pedro/tabelas.md](../resultados/pedro/tabelas.md), com dados em
[raw.csv](../resultados/pedro/raw.csv), registrados no commit `0cea67c`.
As sondas são evidenciadas em
[sondas_correcao.json](../resultados/pedro/sondas_correcao.json).
O [protocolo da repetição](../resultados/pedro/protocolo-correcao.md) contém
as entradas propostas, o perfil de energia, erros exatos e regras de preservação.
Até a nova rodada acontecer, as tabelas existentes continuam sendo as do perfil
anterior. As sondas não foram adicionadas ao CSV estatístico.

## 3. Por que aumentar somente a entrada não bastou

Palavras mantém todas as strings na RAM. No perfil original de pedro, uma
extrapolação linear dos 10,9236 s médios em 128 milhões sugere aproximadamente
234,4 milhões de palavras para chegar a 20 s. Com outros dois tamanhos 50%
maiores, o maior chegaria a aproximadamente 527,3 milhões. Usando os 56 bytes
por palavra estimados pelo projeto, seriam 27,5 GiB; com a folga de 25%,
34,4 GiB livres, acima dos 31,9 GiB totais dessa máquina.

Essa conta é uma estimativa específica desse ambiente. Nas sondas seguintes,
o pico residente por palavra variou e chegou a cerca de 62,8 bytes, mostrando
que os 56 bytes não devem ser tratados como garantia de consumo máximo.
RAM total, RAM livre, pico residente e memória privada também são grandezas
diferentes: é preciso deixar espaço para o SO e evitar paginação/swap.

Uma tentativa de 270 milhões sob perfil de 1800 MHz foi interrompida quando
a RAM livre caiu abaixo da proteção de 3 GiB. Isso reprova aquela tentativa
nas condições em que foi executada; não demonstra que toda máquina de 32 GiB
teria o mesmo limite.

## 4. Por que foi preparado outro perfil de CPU

Foi preparada uma repetição integral em uma condição de plataforma diferente:
CPU limitada a 1200 MHz, estados mínimo/máximo em 40% e Turbo Boost desativado
no Windows de pedro. Essa escolha aumenta a duração do cálculo sem exigir
um corpus que esgote a RAM e mantém os arquivos do professor intactos.
É uma escolha experimental que deve aparecer no relatório; os resultados
representarão **esse perfil de CPU**.

Essa configuração deve permanecer igual no original e em todos os ofuscados,
nos dois benchmarks e durante a rodada inteira. Como a plataforma mudou,
foi preparada a repetição dos dois benchmarks. As amostras da primeira rodada
não serão combinadas com as novas para completar dez repetições.

**1200 MHz e 40% são específicos da preparação de pedro.** A porcentagem não
corresponde à mesma frequência em outra CPU; comandos PowerCfg são do Windows.
Governors do Linux e políticas do macOS têm outros comportamentos e mecanismos.
Até o nome `powersave` de um governor não prova que a frequência esteja fixa.
Não há aqui uma recomendação para todos reduzirem a frequência, nem registro de
aprovação desse protocolo pelo professor. A exigência do enunciado é a duração;
o perfil escolhido precisa ser declarado e avaliado como parte do método.

## 5. O que cada integrante deve verificar na própria máquina

1. Registrar identificação, SO/build, arquitetura, CPU, núcleos, fuso horário, RAM total e
   livre, implementação/versão do Python, versões dos ofuscadores e revisão Git.
   Usar `sistema.md` e complementar manualmente o que o script não coletar.
2. Registrar o perfil de energia/governor, limites solicitados e frequência
   observada quando disponível. Se algum dado não puder ser medido, escrever
   “não medido”. Manter essa condição constante durante toda a rodada.
3. Gerar seu próprio `ofuscado/<id>/` com o Python que executará os testes.
   O runtime depende do SO, da arquitetura e do Python; não copiar de um colega.
4. Executar `verificar.py`, ler os avisos e medir as **menores entradas reais
   dos dois originais**, sob o perfil da futura rodada. Mirar uma margem acima
   de 20 s; no protocolo preparado de pedro, o piloto deve levar pelo menos 22 s.
5. Conferir pelo menos três tamanhos com crescimento de 50% ou mais e testar
   se o maior cabe na RAM, observando o pico e a reserva livre. A margem de 25%
   é uma proteção do projeto, não um número imposto pelo professor. Os 3 GiB
   mínimos livres são uma proteção local de pedro, não um limite universal.
6. Se precisar ajustar tamanhos, usar somente sua entrada em
   `ajustes_por_maquina`, registrar o motivo e comunicar o grupo. Se também
   mudar o perfil, Python ou ofuscado, tratar como outra condição experimental.
   Não rodar `calibrar.py` sem solicitação da pessoa.
7. Confirmar tomada, programas fechados, suspensão desativada e uma janela
   sem uso antes de iniciar a rodada longa com log. Uma estimativa obtida em
   outra máquina não é uma previsão garantida para a sua.
8. Auditar o CSV final: dez repetições únicas de cada caso, saída correta,
   retorno zero e tempos do original de pelo menos 20 s. Com as quatro
   configurações e três tamanhos atuais, são 240 casos no total. Se a duração
   falhar, preservar os dados e preparar uma nova condição; não selecionar
   apenas as repetições mais lentas para parecer que o requisito foi cumprido.

As mesmas regras se aplicam a Windows, Linux e macOS. O procedimento para
configurar e observar o hardware depende do sistema e da máquina. Se não
houver condição que atenda simultaneamente duração, tamanhos e RAM, registrar
o impedimento para decidir outra plataforma/método; não marcar como cumprido.

## 6. Como comparar e escrever o relatório

Usar `slowdown = média ofuscada / média original` para o mesmo tamanho,
na mesma máquina, versão do Python e perfil. Informar também os tempos absolutos
e a dispersão. O slowdown ajuda a comparar, mas pode mudar com tamanho, memória,
frequência e interpretador; ele não elimina essas diferenças de contexto.

Sempre preferir entradas iguais entre máquinas quando forem viáveis. Quando
forem diferentes, identificar cada tamanho. O gráfico consolidado atual usa o
**maior tamanho de cada máquina**, que pode representar cargas diferentes;
não interpretá-lo como comparação da mesma entrada.

O SO, a CPU, o Python e o perfil mudam juntos entre os participantes. Por isso,
uma diferença observada não permite atribuir a causa isoladamente ao SO ou
à arquitetura. Registrar essas variáveis e limitar as conclusões aos casos
efetivamente medidos. Metadados de uma máquina sem seu CSV não provam uma rodada.

O valor `tempo_total_s - tempo_interno_s`, chamado de overhead nas tabelas,
inclui construção da entrada, além de iniciar Python e carregar o runtime.
Em palavras, a montagem do corpus é importante. Não atribuir toda a diferença
ao PyArmor nem usá-la para satisfazer os 20 segundos do cálculo.

Para cada condição do relatório, apresentar: máquina/perfil, tamanhos, dez
repetições, média, mediana, desvio, mínimo e máximo, saída correta, dificuldades,
alterações e estado da validação. Manter separadas as sondas, rodadas completas
com pendências e rodadas que passaram nos critérios experimentais.
Quando uma repetição pendente terminar, atualizar seu estado no relatório e
nas orientações que a mencionam, preservando este registro datado das decisões.
