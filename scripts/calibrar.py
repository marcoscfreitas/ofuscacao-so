#!/usr/bin/env python3
"""Descobre tamanhos de entrada para os quais o código ORIGINAL leva >= 20 s.

Imprime 3 tamanhos (múltiplos de 8) com fator >= fator_entre_tamanhos entre
eles, para colar em config.json. Feche outros programas antes de rodar.

Uso:
    python scripts/calibrar.py
"""
from comum import RAIZ, carregar_config, executar

CHUTE_INICIAL = {"matrizes": 200, "palavras": 5_000_000}


def multiplo_de_8(n):
    return max(8, int(round(n / 8)) * 8)


def calibrar(nome, bench, alvo):
    tamanho = CHUTE_INICIAL[nome]
    exp = bench["expoente_custo"]
    for _ in range(6):
        t, _, ok, rc = executar(RAIZ / "src", bench["arquivo"], tamanho)
        print(f"   {nome}: tamanho={tamanho} tempo={t}s ok={ok}")
        if t is None or rc != 0:
            raise SystemExit(f"falha ao rodar {nome} (rc={rc}); veja memória disponível")
        if alvo <= t <= alvo * 1.3:
            return tamanho
        # custo ~ tamanho**exp  ->  corrige proporcionalmente (margem de 10%)
        tamanho = multiplo_de_8(tamanho * (alvo * 1.1 / t) ** (1 / exp))
    return tamanho


def main():
    cfg = carregar_config()
    alvo = cfg["tamanho_minimo_segundos"]
    fator = cfg["fator_entre_tamanhos"]
    for nome, bench in cfg["benchmarks"].items():
        print(f"==> calibrando {nome}")
        base = calibrar(nome, bench, alvo)
        tamanhos = [multiplo_de_8(base * fator ** i) for i in range(3)]
        print(f"   sugestão para config.json ({nome}): {tamanhos}\n")


if __name__ == "__main__":
    main()
