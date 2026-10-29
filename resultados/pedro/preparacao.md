# Preparação e dificuldades — pedro

Preparação realizada em 28/10/2026; resultados e limitações conferidos em
29/10/2026. As sondas de preparação não substituem as dez repetições finais.

- Windows 10, build 19045, x86_64; Intel Core i7-9700, 8 núcleos/8 threads;
  31,9 GiB de RAM; desktop sem bateria.
- Ambiente isolado `.venv` com Python 3.12.15, já disponível na máquina.
  O Python padrão era 3.14; ele não foi usado nem apresentou erro neste trabalho.
- PyArmor 9.2.8 trial e python-minifier 3.4.0 instalados; matplotlib 3.11.2
  e psutil 7.2.2 disponíveis.
- Instalação concluída com sucesso, com o aviso exato:
  `WARNING: Cache entry deserialization failed, entry ignored`.
  O pip ignorou a entrada de cache; a instalação e a verificação subsequente passaram.
- As configurações `minifier-renomear`, `pyarmor-basico` e `pyarmor-forte`
  foram geradas nesta máquina para Windows/Python 3.12, usando os comandos do
  `config.json`, sem mudar as opções da licença trial.
- Os oito testes curtos (quatro configurações × dois benchmarks) passaram.
- `verificar.py --maquina pedro`: **RESULTADO: tudo certo**.
- RAM disponível na verificação: 20,9 GiB; estimativa do maior caso de
  palavras (128.000.000): 6,7 GiB, além da folga exigida pelo verificador.
- Sondas do original: matrizes, n=200, 1,31 s; palavras, n=5.000.000, 0,41 s.
  São medições isoladas de preparação, sem validade de estatística final.
- Menor caso de matrizes, n=560: aproximadamente 28,9 s estimados.
- Duração estimada pelo verificador: 5,3 horas, para 4 configurações,
  2 benchmarks, 3 tamanhos e 10 repetições: 240 execuções.
- Plano de energia consultado: alto desempenho; suspensão automática
  desativada na tomada e na bateria. Antes do início, o participante confirmou
  que a máquina está na tomada, os demais programas foram fechados, a suspensão
  está desativada e ela ficará sem uso durante a medição; autorizou iniciar
  em segundo plano com log.
- Os tamanhos do grupo foram mantidos; `src/` e `config.json` preservados.
  Isso mantém entradas iguais para comparação, mas não resolve a pendência
  de duração mínima do benchmark palavras, detalhada abaixo.

## Pendência do requisito de 20 segundos

O enunciado exige pelo menos 20 segundos no menor tamanho do original.
Em matrizes, as dez execuções de n=560 ficaram entre 26,263 e 28,106 s,
cumprindo esse requisito. Em palavras, as médias foram 4,316 s (50 milhões),
6,980 s (80 milhões) e 10,924 s (128 milhões): **o requisito não foi atendido**.
O tempo total do processo, que inclui montar o corpus, não substitui o tempo
computacional impresso pelo benchmark.

O README e o guia já adotavam os tamanhos menores por limite de memória
da máquina de referência. O `verificar.py` verifica a duração mínima apenas
de matrizes; por isso, seu “tudo certo” não comprova o requisito para palavras.
Essa pendência deveria ter sido destacada antes da autorização da rodada.

Uma extrapolação linear da média final do original em 128 milhões
(10,9236 s, sem arredondar) sugere aproximadamente 234,4 milhões para 20 s.
Três tamanhos com fator 1,5 seriam cerca de 234,4, 351,5 e 527,3 milhões.
Pela estimativa do projeto de 56 bytes/palavra, o maior caso exigiria
27,5 GiB de RAM; com a folga de 25% do verificador, seriam 34,4 GiB livres,
acima dos 31,9 GiB totais desta máquina. Trata-se de estimativa, não de uma
medição desses tamanhos, e não garante 20 s em cada repetição.

Portanto, aumentar apenas os tamanhos não satisfaz simultaneamente a duração,
os três tamanhos e a margem de RAM adotada pelo projeto nesta máquina.
O grupo precisa resolver essa pendência com o professor: obter aceitação
explícita da exceção ou medir em uma máquina com memória suficiente.
Documentar a limitação, por si só, não equivale a obter essa aceitação.
Não houve nova rodada, alteração dos benchmarks ou mudança retroativa dos dados.

**Complemento de 29/10:** essa extrapolação descreve o perfil da primeira rodada.
Depois foram preparadas sondas sob outro perfil de CPU para atingir 20 s com
entradas menores. A repetição completa foi adiada pelo participante. Os achados
e sua aplicação em outras máquinas estão em
[DECISOES-EXPERIMENTO.md](../../docs/DECISOES-EXPERIMENTO.md); os detalhes locais
estão no [protocolo](protocolo-correcao.md). Não houve substituição do CSV anterior.

Logs locais, ignorados pelo Git: `preparacao-pedro.log` e
`verificacao-pedro.log`. Para a seção “Dificuldades e decisões” do relatório,
usar este registro junto com os resultados finais da rodada.
