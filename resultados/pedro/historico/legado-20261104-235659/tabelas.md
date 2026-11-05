# Resultados — pedro

> EXPLORATÓRIO: pendências registradas em auditoria.json; não comprova atendimento ao enunciado.

## matrizes

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 560 | original | 10 | 27.126 | 27.112 | 0.544 | 26.263 | 28.106 | 1.000x | 0.061 |
| 560 | minifier-renomear | 10 | 27.457 | 27.309 | 0.596 | 26.858 | 28.520 | 1.012x | 0.059 |
| 560 | pyarmor-basico | 10 | 28.177 | 27.993 | 0.380 | 27.901 | 28.934 | 1.039x | 0.065 |
| 560 | pyarmor-forte | 10 | 28.297 | 28.223 | 0.322 | 27.935 | 28.957 | 1.043x | 0.065 |
| 840 | original | 10 | 95.295 | 95.308 | 1.690 | 91.901 | 98.341 | 1.000x | 0.097 |
| 840 | minifier-renomear | 10 | 94.793 | 94.439 | 2.709 | 90.937 | 99.305 | 0.995x | 0.097 |
| 840 | pyarmor-basico | 10 | 98.742 | 98.254 | 1.517 | 97.033 | 101.954 | 1.036x | 0.102 |
| 840 | pyarmor-forte | 10 | 97.891 | 97.788 | 1.021 | 96.387 | 99.442 | 1.027x | 0.103 |
| 1264 | original | 10 | 341.637 | 339.964 | 11.996 | 328.607 | 364.692 | 1.000x | 0.179 |
| 1264 | minifier-renomear | 10 | 339.828 | 338.538 | 7.541 | 326.939 | 350.857 | 0.995x | 0.179 |
| 1264 | pyarmor-basico | 10 | 350.175 | 350.034 | 3.522 | 344.751 | 357.272 | 1.025x | 0.187 |
| 1264 | pyarmor-forte | 10 | 351.624 | 350.633 | 6.543 | 345.721 | 367.223 | 1.029x | 0.187 |

## palavras

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 50000000 | original | 10 | 4.316 | 4.271 | 0.140 | 4.147 | 4.514 | 1.000x | 7.312 |
| 50000000 | minifier-renomear | 10 | 4.298 | 4.321 | 0.128 | 4.052 | 4.466 | 0.996x | 7.358 |
| 50000000 | pyarmor-basico | 10 | 4.581 | 4.620 | 0.133 | 4.327 | 4.749 | 1.061x | 7.447 |
| 50000000 | pyarmor-forte | 10 | 4.465 | 4.441 | 0.136 | 4.290 | 4.643 | 1.035x | 7.474 |
| 80000000 | original | 10 | 6.980 | 6.997 | 0.185 | 6.744 | 7.279 | 1.000x | 11.736 |
| 80000000 | minifier-renomear | 10 | 6.893 | 6.858 | 0.251 | 6.536 | 7.339 | 0.987x | 11.729 |
| 80000000 | pyarmor-basico | 10 | 7.399 | 7.321 | 0.179 | 7.217 | 7.696 | 1.060x | 11.991 |
| 80000000 | pyarmor-forte | 10 | 7.358 | 7.359 | 0.116 | 7.174 | 7.580 | 1.054x | 12.001 |
| 128000000 | original | 10 | 10.924 | 10.780 | 0.398 | 10.462 | 11.655 | 1.000x | 18.777 |
| 128000000 | minifier-renomear | 10 | 11.270 | 11.277 | 0.262 | 10.916 | 11.645 | 1.032x | 18.763 |
| 128000000 | pyarmor-basico | 10 | 11.749 | 11.770 | 0.342 | 11.198 | 12.343 | 1.076x | 19.024 |
| 128000000 | pyarmor-forte | 10 | 11.585 | 11.570 | 0.235 | 11.254 | 12.017 | 1.061x | 19.071 |

_slowdown = média da config / média do original no mesmo tamanho. overhead = média(tempo total do processo) − média(tempo interno): custo de iniciar o interpretador, carregar o runtime/descriptografar e montar as entradas._