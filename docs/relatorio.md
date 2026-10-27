# Relatório — Trabalho IV: custo da ofuscação em Python

**Grupo:** _(nomes)_
**Data:** _(data)_

## 1. Ambiente de teste

_Cole aqui o conteúdo de `resultados/sistema.md` (SO + versão, CPU, memória, Python, versões dos ofuscadores).
Informe também: notebook na tomada? programas fechados? governor de CPU?_

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
como a plataforma foi controlada._

## 5. Resultados

_Cole/inclua `resultados/tabelas.md` e os gráficos de `resultados/graficos/`._

![matrizes](../resultados/graficos/matrizes.png)
![palavras](../resultados/graficos/palavras.png)

## 6. Análise

- O custo é linear com a entrada? Por quê?
- Qual técnica teve maior impacto? Em qual benchmark?
- Tempo de inicialização vs. tempo de computação (compare `tempo_interno_s` e `tempo_total_s`).
- Trade-off segurança × desempenho.

## 7. Dificuldades e decisões

- Problemas de instalação:
- O que não funcionou de maneira alguma:
- Decisões tomadas:

## 8. Extras (se feitos)

- Outros sistemas:
- Outras configurações/tamanhos:
- Regiões equivalentes entre original e ofuscado:
