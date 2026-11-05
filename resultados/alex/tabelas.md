# Resultados — alex

## matrizes

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 560 | original | 10 | 23.046 | 22.788 | 0.821 | 22.690 | 25.372 | 1.000x | 0.068 |
| 560 | minifier-renomear | 10 | 23.161 | 22.898 | 0.843 | 22.797 | 25.549 | 1.005x | 0.066 |
| 560 | pyarmor-basico | 10 | 22.872 | 22.794 | 0.242 | 22.703 | 23.531 | 0.992x | 0.069 |
| 560 | pyarmor-forte | 10 | 22.805 | 22.814 | 0.081 | 22.688 | 22.963 | 0.990x | 0.063 |
| 840 | original | 10 | 80.475 | 79.916 | 1.848 | 79.653 | 85.718 | 1.000x | 0.096 |
| 840 | minifier-renomear | 10 | 80.132 | 80.135 | 0.134 | 79.879 | 80.342 | 0.996x | 0.107 |
| 840 | pyarmor-basico | 10 | 80.145 | 80.099 | 0.240 | 79.810 | 80.527 | 0.996x | 0.101 |
| 840 | pyarmor-forte | 10 | 80.132 | 80.141 | 0.166 | 79.883 | 80.463 | 0.996x | 0.104 |
| 1264 | original | 10 | 282.548 | 282.243 | 1.830 | 280.048 | 286.012 | 1.000x | 0.190 |
| 1264 | minifier-renomear | 10 | 283.539 | 282.820 | 2.290 | 280.526 | 289.233 | 1.004x | 0.192 |
| 1264 | pyarmor-basico | 10 | 282.185 | 282.116 | 0.176 | 282.023 | 282.613 | 0.999x | 0.193 |
| 1264 | pyarmor-forte | 10 | 282.329 | 282.329 | 0.350 | 281.697 | 282.962 | 0.999x | 0.192 |

## palavras

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 50000000 | original | 10 | 3.974 | 3.990 | 0.043 | 3.900 | 4.013 | 1.000x | 6.392 |
| 50000000 | minifier-renomear | 10 | 3.955 | 3.954 | 0.086 | 3.837 | 4.076 | 0.995x | 6.471 |
| 50000000 | pyarmor-basico | 10 | 3.982 | 3.999 | 0.082 | 3.863 | 4.081 | 1.002x | 6.288 |
| 50000000 | pyarmor-forte | 10 | 4.038 | 4.054 | 0.091 | 3.846 | 4.140 | 1.016x | 6.281 |
| 80000000 | original | 10 | 6.306 | 6.279 | 0.107 | 6.195 | 6.508 | 1.000x | 10.227 |
| 80000000 | minifier-renomear | 10 | 6.177 | 6.191 | 0.136 | 6.005 | 6.383 | 0.979x | 10.297 |
| 80000000 | pyarmor-basico | 10 | 6.472 | 6.434 | 0.117 | 6.339 | 6.725 | 1.026x | 10.006 |
| 80000000 | pyarmor-forte | 10 | 6.509 | 6.528 | 0.180 | 6.202 | 6.856 | 1.032x | 10.155 |
| 128000000 | original | 10 | 10.206 | 10.201 | 0.213 | 9.956 | 10.601 | 1.000x | 16.267 |
| 128000000 | minifier-renomear | 10 | 9.923 | 9.924 | 0.241 | 9.609 | 10.307 | 0.972x | 16.425 |
| 128000000 | pyarmor-basico | 10 | 10.227 | 10.268 | 0.270 | 9.851 | 10.592 | 1.002x | 15.898 |
| 128000000 | pyarmor-forte | 10 | 10.136 | 10.166 | 0.218 | 9.823 | 10.462 | 0.993x | 15.889 |

_slowdown = média da config / média do original no mesmo tamanho. overhead = média(tempo total do processo) − média(tempo interno): custo de iniciar o interpretador, carregar o runtime/descriptografar e montar as entradas._