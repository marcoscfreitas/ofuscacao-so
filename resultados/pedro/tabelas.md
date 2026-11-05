# Resultados — pedro

## matrizes

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 560 | original | 10 | 27.464 | 27.275 | 0.653 | 26.659 | 28.993 | 1.000x | 0.084 |
| 560 | minifier-renomear | 10 | 27.553 | 27.663 | 0.331 | 26.933 | 28.023 | 1.003x | 0.088 |
| 560 | pyarmor-basico | 10 | 28.506 | 28.310 | 0.483 | 27.913 | 29.376 | 1.038x | 0.085 |
| 560 | pyarmor-forte | 10 | 28.620 | 28.590 | 0.709 | 27.902 | 30.295 | 1.042x | 0.091 |
| 840 | original | 10 | 97.074 | 96.422 | 2.795 | 92.210 | 100.738 | 1.000x | 0.125 |
| 840 | minifier-renomear | 10 | 94.498 | 94.102 | 2.047 | 92.161 | 97.957 | 0.973x | 0.116 |
| 840 | pyarmor-basico | 10 | 98.980 | 98.979 | 1.864 | 96.846 | 103.543 | 1.020x | 0.136 |
| 840 | pyarmor-forte | 10 | 98.861 | 98.909 | 1.503 | 96.778 | 102.081 | 1.018x | 0.121 |
| 1264 | original | 10 | 333.784 | 335.045 | 5.784 | 323.321 | 342.395 | 1.000x | 0.209 |
| 1264 | minifier-renomear | 10 | 334.618 | 335.580 | 6.919 | 325.628 | 342.407 | 1.002x | 0.200 |
| 1264 | pyarmor-basico | 10 | 344.935 | 346.204 | 3.600 | 339.523 | 350.544 | 1.033x | 0.214 |
| 1264 | pyarmor-forte | 10 | 343.321 | 343.697 | 2.021 | 340.873 | 346.338 | 1.029x | 0.220 |

## palavras

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 50000000 | original | 10 | 4.314 | 4.292 | 0.161 | 4.157 | 4.713 | 1.000x | 7.341 |
| 50000000 | minifier-renomear | 10 | 4.269 | 4.255 | 0.196 | 4.063 | 4.594 | 0.990x | 7.330 |
| 50000000 | pyarmor-basico | 10 | 4.633 | 4.640 | 0.118 | 4.469 | 4.858 | 1.074x | 7.448 |
| 50000000 | pyarmor-forte | 10 | 4.610 | 4.600 | 0.158 | 4.364 | 4.859 | 1.069x | 7.478 |
| 80000000 | original | 10 | 6.833 | 6.809 | 0.185 | 6.660 | 7.272 | 1.000x | 11.721 |
| 80000000 | minifier-renomear | 10 | 6.900 | 6.913 | 0.147 | 6.720 | 7.189 | 1.010x | 11.686 |
| 80000000 | pyarmor-basico | 10 | 7.401 | 7.378 | 0.265 | 7.030 | 7.939 | 1.083x | 11.861 |
| 80000000 | pyarmor-forte | 10 | 7.317 | 7.250 | 0.231 | 7.020 | 7.641 | 1.071x | 11.933 |
| 128000000 | original | 10 | 11.068 | 11.020 | 0.422 | 10.369 | 11.758 | 1.000x | 18.765 |
| 128000000 | minifier-renomear | 10 | 11.073 | 11.095 | 0.370 | 10.392 | 11.574 | 1.001x | 18.693 |
| 128000000 | pyarmor-basico | 10 | 11.604 | 11.524 | 0.345 | 11.234 | 12.175 | 1.048x | 19.094 |
| 128000000 | pyarmor-forte | 10 | 11.619 | 11.634 | 0.424 | 11.019 | 12.369 | 1.050x | 19.012 |

_slowdown = média da config / média do original no mesmo tamanho. overhead = média(tempo total do processo) − média(tempo interno): custo de iniciar o interpretador, carregar o runtime/descriptografar e montar as entradas._