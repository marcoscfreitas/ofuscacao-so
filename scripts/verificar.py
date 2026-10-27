#!/usr/bin/env python3
"""Checagem pré-voo: rode ANTES de deixar o benchmark completo rodando.

Verifica, nesta máquina:
  1. ferramentas instaladas e código ofuscado gerado (ofuscado/<maquina>/);
  2. cada configuração roda e imprime "ok" (testes curtos);
  3. a RAM disponível comporta o maior tamanho do palavras;
  4. o menor tamanho do matrizes leva >= 20 s no original (estimativa);
  5. quanto tempo a rodada completa deve levar (estimativa).

Se algum tamanho não servir, imprime um trecho de "ajustes_por_maquina" para
colar no config.json (ver README). Não altera nenhum arquivo.

Uso:
    python scripts/verificar.py --maquina marcos
"""
import argparse
import sys

from comum import (BYTES_POR_PALAVRA, RAIZ, carregar_config, diretorio_config, executar,
                   memoria_disponivel, nome_maquina)

TESTE_CURTO = {"matrizes": 64, "palavras": 1_000_000}
SONDA = {"matrizes": 200, "palavras": 5_000_000}  # tamanhos usados para estimar tempos
FOLGA_RAM = 1.25  # exige 25% a mais de RAM livre do que o estimado


def multiplo_de_8(n):
    return max(8, int(round(n / 8)) * 8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maquina", required=True, help="identificador do dono da máquina (ex.: marcos)")
    maquina = nome_maquina(ap.parse_args().maquina)
    cfg = carregar_config(maquina)
    alvo = cfg["tamanho_minimo_segundos"]
    fator = cfg["fator_entre_tamanhos"]
    problemas, avisos, ajustes = [], [], {}

    print(f"== verificando máquina '{maquina}' (Python {sys.version.split()[0]}) ==\n")

    # 1 + 2. ofuscado existe e roda
    print("[1/4] código ofuscado e teste curto")
    for nome in cfg["ofuscadores"]:
        d = diretorio_config(nome, cfg, maquina)
        if not d.exists():
            problemas.append(f"{d.relative_to(RAIZ)} não existe -> "
                             f"python scripts/ofuscar.py --maquina {maquina}")
            print(f"   {nome:20s} AUSENTE")
            continue
        status = []
        for bname, bench in cfg["benchmarks"].items():
            _, _, ok, rc = executar(d, bench["arquivo"], TESTE_CURTO[bname])
            status.append(f"{bname}={'ok' if ok and rc == 0 else 'FALHOU'}")
            if not (ok and rc == 0):
                problemas.append(f"{nome}/{bench['arquivo']} falhou (rc={rc}); rode manualmente: "
                                 f"cd {d.relative_to(RAIZ)} && python {bench['arquivo']} "
                                 f"{TESTE_CURTO[bname]}")
        print(f"   {nome:20s} {'  '.join(status)}")

    # 3. sonda do original -> estimativas
    print("\n[2/4] medindo o original para estimar tempos (alguns segundos)")
    original = RAIZ / "src"
    t_sonda = {}
    for bname, bench in cfg["benchmarks"].items():
        t, _, ok, rc = executar(original, bench["arquivo"], SONDA[bname])
        if t is None or not ok:
            problemas.append(f"original/{bench['arquivo']} falhou na sonda (rc={rc})")
            continue
        t_sonda[bname] = t
        print(f"   {bname}: n={SONDA[bname]} -> {t:.2f} s")

    def estimar(bname, n):
        exp = cfg["benchmarks"][bname]["expoente_custo"]
        return t_sonda[bname] * (n / SONDA[bname]) ** exp

    # 4. memória do palavras
    print("\n[3/4] memória (palavras)")
    livre = memoria_disponivel()
    pal = cfg["benchmarks"]["palavras"]["tamanhos"]
    precisa = max(pal) * BYTES_POR_PALAVRA
    if livre is None:
        avisos.append("não consegui medir a RAM disponível (instale psutil: pip install psutil)")
    else:
        print(f"   disponível: {livre / 2**30:.1f} GiB | maior tamanho ({max(pal):,}) "
              f"precisa de ~{precisa / 2**30:.1f} GiB")
        if livre < precisa * FOLGA_RAM:
            teto = multiplo_de_8(livre / FOLGA_RAM / BYTES_POR_PALAVRA)
            novo = [multiplo_de_8(teto / fator ** i) for i in (2, 1, 0)]
            problemas.append("RAM insuficiente para os tamanhos do palavras no config.json "
                             "(feche programas e rode de novo; se persistir, use o ajuste abaixo)")
            ajustes.setdefault("benchmarks", {})["palavras"] = {"tamanhos": novo}

    # 5. matrizes >= 20 s
    print("\n[4/4] menor tamanho do matrizes no original")
    mat = cfg["benchmarks"]["matrizes"]["tamanhos"]
    if "matrizes" in t_sonda:
        est = estimar("matrizes", min(mat))
        print(f"   n={min(mat)} -> ~{est:.1f} s estimados (mínimo exigido: {alvo} s)")
        if est < alvo * 0.95:
            n0 = multiplo_de_8(SONDA["matrizes"] * (alvo * 1.1 / t_sonda["matrizes"]) ** (1 / 3))
            novo = [n0, multiplo_de_8(n0 * fator), multiplo_de_8(n0 * fator ** 2)]
            avisos.append(f"matrizes n={min(mat)} deve levar < {alvo} s nesta máquina "
                          "(esta máquina é mais rápida que a de referência)")
            ajustes.setdefault("benchmarks", {})["matrizes"] = {"tamanhos": novo}

    # tempo total estimado
    if len(t_sonda) == len(cfg["benchmarks"]):
        por_rodada = sum(estimar(b, n) for b, bench in cfg["benchmarks"].items()
                         for n in bench["tamanhos"])
        total = por_rodada * len(cfg["ofuscadores"]) * cfg["repeticoes"]
        print(f"\nTempo estimado da rodada completa: ~{total / 3600:.1f} h "
              f"({len(cfg['ofuscadores'])} configs x {cfg['repeticoes']} repetições; "
              "inclui o tempo de montar as entradas só aproximadamente)")

    print()
    for a in avisos:
        print("AVISO:", a)
    for p in problemas:
        print("PROBLEMA:", p)
    if ajustes:
        import json
        print("\nSe os tamanhos não servirem, adicione em config.json (chave de topo):")
        print(json.dumps({"ajustes_por_maquina": {maquina: ajustes}}, indent=2))
        print("Avise o grupo: tamanhos diferentes entre máquinas reduzem a comparabilidade.")
    if problemas:
        print("\nRESULTADO: corrija os problemas acima antes de rodar o benchmark completo.")
        sys.exit(1)
    print("RESULTADO: tudo certo. Pode rodar: "
          f"python scripts/rodar_benchmarks.py --maquina {maquina}")


if __name__ == "__main__":
    main()
