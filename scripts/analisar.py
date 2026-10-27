#!/usr/bin/env python3
"""Gera tabelas (média, mediana, desvio padrão, mínimo, máximo) e gráficos.

Lê resultados/<maquina>/raw.csv de cada máquina e escreve:
    resultados/<maquina>/tabelas.md
    resultados/<maquina>/graficos/<benchmark>.png
    resultados/comparacao.md                       (todas as máquinas lado a lado)
    resultados/graficos/comparacao_<benchmark>.png (slowdown por máquina)

Uso:
    python scripts/analisar.py                  # todas as máquinas encontradas
    python scripts/analisar.py --maquina marcos   # só uma (a comparação é pulada)
"""
import argparse
import csv
import statistics as st
from collections import defaultdict

from comum import RESULTADOS, carregar_config, maquinas_com_resultados, nome_maquina, pasta_resultados


def carregar(maquina):
    """Retorna (interno, total): (benchmark, tamanho, config) -> [tempos]."""
    interno, total = defaultdict(list), defaultdict(list)
    descartadas = 0
    with open(pasta_resultados(maquina) / "raw.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["returncode"] == "0" and r["saida_ok"] == "1" and r["tempo_interno_s"]:
                chave = (r["benchmark"], int(r["tamanho"]), r["config"])
                interno[chave].append(float(r["tempo_interno_s"]))
                total[chave].append(float(r["tempo_total_s"]))
            else:
                descartadas += 1
    if descartadas:
        print(f"AVISO [{maquina}]: {descartadas} execuções com falha/saída incorreta foram ignoradas")
    return interno, total


def resumo(v):
    return dict(n=len(v), media=st.mean(v), mediana=st.median(v),
                desvio=st.stdev(v) if len(v) > 1 else 0.0, min=min(v), max=max(v))


def tabelas(interno, total, ordem):
    linhas = []
    for bench in sorted({k[0] for k in interno}):
        linhas.append(f"\n## {bench}\n")
        linhas.append("| tamanho | config | n | média (s) | mediana (s) | desvio (s) | mín (s) | máx (s) "
                      "| slowdown vs original | overhead de inicialização (s) |")
        linhas.append("|---|---|---|---|---|---|---|---|---|---|")
        for tam in sorted({k[1] for k in interno if k[0] == bench}):
            base = interno.get((bench, tam, "original"))
            base_med = st.mean(base) if base else None
            for cfg in ordem:
                v = interno.get((bench, tam, cfg))
                if not v:
                    continue
                s = resumo(v)
                slow = f"{s['media'] / base_med:.3f}x" if base_med else "-"
                overhead = st.mean(total[(bench, tam, cfg)]) - s["media"]
                linhas.append(f"| {tam} | {cfg} | {s['n']} | {s['media']:.3f} | {s['mediana']:.3f} "
                              f"| {s['desvio']:.3f} | {s['min']:.3f} | {s['max']:.3f} | {slow} "
                              f"| {overhead:.3f} |")
    linhas.append("\n_slowdown = média da config / média do original no mesmo tamanho. "
                  "overhead = média(tempo total do processo) − média(tempo interno): custo de "
                  "iniciar o interpretador, carregar o runtime/descriptografar e montar as entradas._")
    return "\n".join(linhas)


def importar_pyplot():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("matplotlib não instalado; pulando gráficos")
        return None


def graficos(plt, maquina, interno, ordem):
    pasta = pasta_resultados(maquina) / "graficos"
    pasta.mkdir(exist_ok=True)
    for bench in sorted({k[0] for k in interno}):
        tamanhos = sorted({k[1] for k in interno if k[0] == bench})
        fig, ax = plt.subplots(figsize=(8, 5))
        larg = 0.8 / len(ordem)
        for i, cfg in enumerate(ordem):
            xs, medias, erros = [], [], []
            for j, tam in enumerate(tamanhos):
                v = interno.get((bench, tam, cfg))
                if v:
                    xs.append(j + i * larg)
                    medias.append(st.mean(v))
                    erros.append(st.stdev(v) if len(v) > 1 else 0)
            ax.bar(xs, medias, larg, yerr=erros, capsize=3, label=cfg)
        ax.set_xticks([j + 0.4 - larg / 2 for j in range(len(tamanhos))])
        ax.set_xticklabels([f"{t:,}" for t in tamanhos])
        ax.set_xlabel("tamanho da entrada")
        ax.set_ylabel("tempo (s) — média ± desvio padrão")
        ax.set_title(f"Benchmark: {bench} — máquina: {maquina}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pasta / f"{bench}.png", dpi=150)
        plt.close(fig)


def media(d, chave):
    v = d.get(chave)
    return st.mean(v) if v else None


def comparacao(plt, por_maquina, ordem):
    """Tabela e gráficos lado a lado entre máquinas."""
    maquinas = list(por_maquina)
    linhas = ["# Comparação entre máquinas\n"]
    benchs = sorted({k[0] for m in maquinas for k in por_maquina[m]})
    for bench in benchs:
        linhas.append(f"\n## {bench}\n")
        linhas.append("| tamanho | config | " + " | ".join(f"{m} média (s)" for m in maquinas)
                      + " | " + " | ".join(f"{m} slowdown" for m in maquinas) + " |")
        linhas.append("|---|---|" + "---|" * (2 * len(maquinas)))
        tamanhos = sorted({k[1] for m in maquinas for k in por_maquina[m] if k[0] == bench})
        for tam in tamanhos:
            for cfg in ordem:
                tempos, slows = [], []
                for m in maquinas:
                    t = media(por_maquina[m], (bench, tam, cfg))
                    b = media(por_maquina[m], (bench, tam, "original"))
                    tempos.append(f"{t:.3f}" if t is not None else "-")
                    slows.append(f"{t / b:.3f}x" if t is not None and b else "-")
                if any(x != "-" for x in tempos):
                    linhas.append(f"| {tam} | {cfg} | " + " | ".join(tempos) + " | "
                                  + " | ".join(slows) + " |")
    linhas.append("\n_Células com \"-\" = esse tamanho não foi medido naquela máquina._")
    (RESULTADOS / "comparacao.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    if plt is None:
        return
    (RESULTADOS / "graficos").mkdir(exist_ok=True)
    ofuscadas = [c for c in ordem if c != "original"]
    for bench in benchs:
        fig, ax = plt.subplots(figsize=(8, 5))
        larg = 0.8 / len(maquinas)
        for i, m in enumerate(maquinas):
            tams = sorted({k[1] for k in por_maquina[m] if k[0] == bench})
            if not tams:
                continue
            tam = tams[-1]  # maior tamanho medido naquela máquina
            ys = []
            for cfg in ofuscadas:
                t, b = media(por_maquina[m], (bench, tam, cfg)), media(por_maquina[m], (bench, tam, "original"))
                ys.append(t / b if t is not None and b else 0)
            ax.bar([j + i * larg for j in range(len(ofuscadas))], ys, larg, label=f"{m} (n={tam:,})")
        ax.axhline(1.0, color="gray", linewidth=1, linestyle="--")
        ax.set_xticks([j + 0.4 - larg / 2 for j in range(len(ofuscadas))])
        ax.set_xticklabels(ofuscadas)
        ax.set_ylabel("slowdown (tempo ofuscado / tempo original)")
        ax.set_title(f"Benchmark: {bench} — maior tamanho de cada máquina")
        ax.legend()
        fig.tight_layout()
        fig.savefig(RESULTADOS / "graficos" / f"comparacao_{bench}.png", dpi=150)
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maquina", help="analisa só esta máquina (padrão: todas as encontradas)")
    args = ap.parse_args()

    maquinas = [nome_maquina(args.maquina)] if args.maquina else maquinas_com_resultados()
    if not maquinas:
        raise SystemExit("nenhum resultados/<maquina>/raw.csv encontrado")

    ordem = list(carregar_config()["ofuscadores"])
    plt = importar_pyplot()
    por_maquina = {}
    for m in maquinas:
        interno, total = carregar(m)
        por_maquina[m] = interno
        (pasta_resultados(m) / "tabelas.md").write_text(
            f"# Resultados — {m}\n" + tabelas(interno, total, ordem), encoding="utf-8")
        if plt:
            graficos(plt, m, interno, ordem)
        print(f"escrito: resultados/{m}/tabelas.md e resultados/{m}/graficos/")
    if len(maquinas) > 1:
        comparacao(plt, por_maquina, ordem)
        print("escrito: resultados/comparacao.md e resultados/graficos/comparacao_*.png")


if __name__ == "__main__":
    main()
