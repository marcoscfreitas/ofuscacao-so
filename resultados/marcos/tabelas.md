# Resultados — marcos

## matrizes

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 608 | original | 10 | 26.175 | 26.045 | 0.244 | 25.986 | 26.584 | 1.000x | 0.063 |
| 608 | minifier-renomear | 10 | 26.676 | 26.242 | 0.680 | 26.053 | 27.786 | 1.019x | 0.078 |
| 608 | pyarmor-basico | 10 | 26.683 | 26.038 | 1.483 | 25.949 | 30.633 | 1.019x | 0.072 |
| 608 | pyarmor-forte | 10 | 26.223 | 26.017 | 0.531 | 25.964 | 27.703 | 1.002x | 0.084 |
| 912 | original | 10 | 88.678 | 88.330 | 0.742 | 88.272 | 90.643 | 1.000x | 0.110 |
| 912 | minifier-renomear | 10 | 89.301 | 88.945 | 1.107 | 88.894 | 92.449 | 1.007x | 0.123 |
| 912 | pyarmor-basico | 10 | 88.256 | 88.060 | 0.459 | 87.949 | 89.323 | 0.995x | 0.112 |
| 912 | pyarmor-forte | 10 | 90.741 | 88.054 | 8.277 | 87.979 | 114.289 | 1.023x | 0.116 |
| 1368 | original | 10 | 317.464 | 315.249 | 6.591 | 312.588 | 333.673 | 1.000x | 0.201 |
| 1368 | minifier-renomear | 10 | 316.474 | 315.683 | 2.624 | 314.218 | 322.920 | 0.997x | 0.202 |
| 1368 | pyarmor-basico | 10 | 321.839 | 311.998 | 20.591 | 311.068 | 366.606 | 1.014x | 0.208 |
| 1368 | pyarmor-forte | 10 | 315.071 | 314.790 | 3.188 | 310.852 | 319.891 | 0.992x | 0.204 |

## palavras

| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original | overhead de inicialização (s) |
|---|---|---|---|---|---|---|---|---|---|
| 50000000 | original | 10 | 3.201 | 3.194 | 0.057 | 3.132 | 3.302 | 1.000x | 6.397 |
| 50000000 | minifier-renomear | 10 | 3.150 | 3.149 | 0.062 | 3.029 | 3.274 | 0.984x | 6.607 |
| 50000000 | pyarmor-basico | 10 | 3.196 | 3.209 | 0.075 | 3.014 | 3.279 | 0.998x | 6.305 |
| 50000000 | pyarmor-forte | 10 | 3.218 | 3.210 | 0.059 | 3.124 | 3.330 | 1.005x | 6.313 |
| 80000000 | original | 10 | 5.069 | 5.093 | 0.126 | 4.851 | 5.255 | 1.000x | 10.161 |
| 80000000 | minifier-renomear | 10 | 5.117 | 5.063 | 0.218 | 4.831 | 5.666 | 1.009x | 10.190 |
| 80000000 | pyarmor-basico | 10 | 5.117 | 5.097 | 0.107 | 4.989 | 5.277 | 1.009x | 10.161 |
| 80000000 | pyarmor-forte | 10 | 5.104 | 5.112 | 0.126 | 4.851 | 5.299 | 1.007x | 10.030 |
| 128000000 | original | 10 | 8.376 | 8.271 | 0.367 | 7.957 | 9.169 | 1.000x | 16.180 |
| 128000000 | minifier-renomear | 10 | 8.059 | 8.095 | 0.147 | 7.813 | 8.245 | 0.962x | 16.292 |
| 128000000 | pyarmor-basico | 10 | 8.109 | 8.102 | 0.216 | 7.862 | 8.551 | 0.968x | 16.039 |
| 128000000 | pyarmor-forte | 10 | 8.149 | 8.152 | 0.160 | 7.906 | 8.421 | 0.973x | 16.197 |

_slowdown = média da config / média do original no mesmo tamanho. overhead = média(tempo total do processo) − média(tempo interno): custo de iniciar o interpretador, carregar o runtime/descriptografar e montar as entradas._