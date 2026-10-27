#!/usr/bin/env python3
"""Descobre tamanhos de entrada para os quais o código ORIGINAL leva >= 20 s.

Imprime 3 tamanhos (múltiplos de 8) com fator >= fator_entre_tamanhos entre
eles. O tamanho do palavras é limitado pela RAM disponível (o corpus inteiro
fica na memória), então ele pode NÃO alcançar 20 s; o script avisa.

ATENÇÃO: os tamanhos de config.json já estão definidos para o grupo. Só rode
isto se `verificar.py` indicar que os tamanhos não servem nesta máquina, e use
o resultado em "ajustes_por_maquina" (ver README), não no config global.
Feche outros programas antes de rodar.

Uso:
    python scripts/calibrar.py
"""
from comum import BYTES_POR_PALAVRA, RAIZ, carregar_config, executar, memoria_disponivel

CHUTE_INICIAL = {"matrizes": 200, "palavras": 5_000_000}
USO_MAX_RAM = 0.6  # fração da RAM disponível que o palavras pode ocupar


def multiplo_de_8(n):
    return max(8, int(round(n / 8)) * 8)


def limite_palavras():
    livre = memoria_disponivel()
    return None if livre is None else multiplo_de_8(livre * USO_MAX_RAM / BYTES_POR_PALAVRA)


def calibrar(nome, bench, alvo, limite):
    tamanho = CHUTE_INICIAL[nome]
    exp = bench["expoente_custo"]
    for _ in range(6):
        t, _, ok, rc = executar(RAIZ / "src", bench["arquivo"], tamanho)
        print(f"   {nome}: tamanho={tamanho} tempo={t}s ok={ok}")
        if t is None or rc != 0:
            raise SystemExit(f"falha ao rodar {nome} (rc={rc}); veja memória disponível")
        if alvo <= t <= alvo * 1.3:
            return tamanho, True
        proximo = multiplo_de_8(tamanho * (alvo * 1.1 / t) ** (1 / exp))
        if limite and proximo > limite:
            print(f"   limite de memória atingido ({limite}); {nome} NÃO chega a {alvo} s "
                  f"nesta máquina (último tempo: {t:.1f} s)")
            return limite, False
        tamanho = proximo
    return tamanho, True


def main():
    cfg = carregar_config()
    alvo = cfg["tamanho_minimo_segundos"]
    fator = cfg["fator_entre_tamanhos"]
    for nome, bench in cfg["benchmarks"].items():
        print(f"==> calibrando {nome}")
        limite = limite_palavras() if nome == "palavras" else None
        base, atingiu = calibrar(nome, bench, alvo, limite)
        if not atingiu:
            # a base é o MAIOR tamanho que cabe na RAM: os outros vêm dividindo pelo fator
            tamanhos = [multiplo_de_8(base / fator ** i) for i in (2, 1, 0)]
        else:
            tamanhos = [multiplo_de_8(base * fator ** i) for i in range(3)]
        print(f"   sugestão ({nome}): {tamanhos}\n")


if __name__ == "__main__":
    main()
