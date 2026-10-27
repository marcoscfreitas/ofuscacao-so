#!/usr/bin/env python3
"""Gera tabelas (média, mediana, desvio padrão, mínimo, máximo) e gráficos.

Lê resultados/raw.csv e escreve:
    resultados/tabelas.md
    resultados/graficos/<benchmark>.png

Uso:
    python scripts/analisar.py
"""
import csv
import statistics as st
from collections import defaultdict

from comum import RAW_CSV, RESULTADOS, carregar_config


def carregar():
    dados = defaultdict(list)  # (benchmark, tamanho, config) -> [tempos]
    with open(RAW_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["returncode"] == "0" and r["tempo_interno_s"]:
                dados[(r["benchmark"], int(r["tamanho"]), r["config"])].append(
                    float(r["tempo_interno_s"]))
    return dados


def resumo(v):
    return dict(n=len(v), media=st.mean(v), mediana=st.median(v),
                desvio=st.stdev(v) if len(v) > 1 else 0.0, min=min(v), max=max(v))


def tabelas(dados, ordem):
    linhas = []
    for bench in sorted({k[0] for k in dados}):
        linhas.append(f"\n## {bench}\n")
        linhas.append("| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) | slowdown vs original |")
        linhas.append("|---|---|---|---|---|---|---|---|---|")
        for tam in sorted({k[1] for k in dados if k[0] == bench}):
            base = dados.get((bench, tam, "original"))
            base_med = st.mean(base) if base else None
            for cfg in ordem:
                v = dados.get((bench, tam, cfg))
                if not v:
                    continue
                s = resumo(v)
                slow = f"{s['media'] / base_med:.2f}x" if base_med else "-"
                linhas.append(f"| {tam} | {cfg} | {s['n']} | {s['media']:.3f} | {s['mediana']:.3f} "
                              f"| {s['desvio']:.3f} | {s['min']:.3f} | {s['max']:.3f} | {slow} |")
    return "\n".join(linhas)


def graficos(dados, ordem):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado; pulando gráficos")
        return
    for bench in sorted({k[0] for k in dados}):
        tamanhos = sorted({k[1] for k in dados if k[0] == bench})
        fig, ax = plt.subplots(figsize=(8, 5))
        larg = 0.8 / len(ordem)
        for i, cfg in enumerate(ordem):
            xs, medias, erros = [], [], []
            for j, tam in enumerate(tamanhos):
                v = dados.get((bench, tam, cfg))
                if v:
                    xs.append(j + i * larg)
                    medias.append(st.mean(v))
                    erros.append(st.stdev(v) if len(v) > 1 else 0)
            ax.bar(xs, medias, larg, yerr=erros, capsize=3, label=cfg)
        ax.set_xticks([j + 0.4 - larg / 2 for j in range(len(tamanhos))])
        ax.set_xticklabels([str(t) for t in tamanhos])
        ax.set_xlabel("tamanho da entrada")
        ax.set_ylabel("tempo (s) — média ± desvio padrão")
        ax.set_title(f"Benchmark: {bench}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(RESULTADOS / "graficos" / f"{bench}.png", dpi=150)
        plt.close(fig)


def main():
    cfg = carregar_config()
    ordem = list(cfg["ofuscadores"])
    dados = carregar()
    (RESULTADOS / "tabelas.md").write_text("# Resultados\n" + tabelas(dados, ordem), encoding="utf-8")
    graficos(dados, ordem)
    print("escrito: resultados/tabelas.md e resultados/graficos/")


if __name__ == "__main__":
    main()
