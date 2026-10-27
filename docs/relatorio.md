# Relatório — Trabalho IV: custo da ofuscação em Python

**Grupo:** _(nomes dos integrantes)_
**Data:** _(data)_

## 1. Ambiente de teste

_Uma subseção por máquina: cole o conteúdo de `resultados/<id>/sistema.md` (SO + versão, CPU, memória,
governor, energia, Python, versões dos ofuscadores) de cada integrante.
Informe também: programas fechados? suspensão desativada? tamanhos ajustados (`ajustes_por_maquina`)?_

### marcos
### _(id do integrante 2)_
### _(id do integrante 3)_

## 2. Benchmarks

- **Matrizes:** multiplicação n×n com 3 laços aninhados; custo O(n³).
- **Palavras:** contagem de frequência em dicionário; custo O(n).

## 3. Configurações de ofuscação

| Config | Ferramenta/versão | Comando | Técnicas aplicadas |
|---|---|---|---|
| original | — | — | — |
| | | | |

## 4. Metodologia

_Tamanhos escolhidos e por quê, número de repetições, como o tempo foi medido,
como a plataforma foi controlada, como os resultados de três máquinas foram combinados
(ver [GUIA-GRUPO.md](GUIA-GRUPO.md)). Lembre-se de justificar que o `palavras` não chega a
20 s: o benchmark guarda o corpus inteiro na RAM (~56 B/palavra), então 20 s exigiria ~18 GB._

## 5. Resultados

_Para cada máquina, inclua `resultados/<id>/tabelas.md` e os gráficos de
`resultados/<id>/graficos/`. Depois inclua a comparação (`resultados/comparacao.md`)._

![matrizes — marcos](../resultados/marcos/graficos/matrizes.png)
![palavras — marcos](../resultados/marcos/graficos/palavras.png)
![comparação matrizes](../resultados/graficos/comparacao_matrizes.png)
![comparação palavras](../resultados/graficos/comparacao_palavras.png)

## 6. Análise

- O custo é linear com a entrada? Por quê?
- Qual técnica teve maior impacto? Em qual benchmark?
- Tempo de inicialização vs. tempo de computação (compare `tempo_interno_s` e `tempo_total_s`).
- Trade-off segurança × desempenho.
- O custo relativo (slowdown) é parecido entre as três máquinas? O que explicaria diferenças (CPU, SO, versão do Python)?

## 7. Dificuldades e decisões

- Problemas de instalação (por máquina):
- O que não funcionou de maneira alguma: PyArmor trial recusa `--obf-code 2`, `--mix-str`,
  `--enable rft|bcc` (`out of license`); `pyarmor-forte` usa só opções aceitas pela trial.
- Tamanhos do `palavras` limitados pela RAM (< 20 s no original):
- Decisões tomadas:

## 8. Extras (se feitos)

- Outros sistemas (as três máquinas):
- Outras configurações/tamanhos:
- Regiões equivalentes entre original e ofuscado:
