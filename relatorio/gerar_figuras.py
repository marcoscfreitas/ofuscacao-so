"""Gera as figuras do relatório/slides a partir de resultados/<id>/raw.csv.
Uso (raiz do repo): .venv/Scripts/python.exe relatorio/gerar_figuras.py"""
import csv, json, math, statistics as st
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MAQ = ["pedro", "alex", "marcos"]
CFG = ["original", "minifier-renomear", "pyarmor-basico", "pyarmor-forte"]
COR = {"original": "#4c72b0", "minifier-renomear": "#dd8452", "pyarmor-basico": "#55a868", "pyarmor-forte": "#c44e52"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

def carregar(m):
    d = defaultdict(list)
    for r in csv.DictReader(open(f"resultados/{m}/raw.csv", encoding="utf-8")):
        d[(r["benchmark"], int(r["tamanho"]), r["config"])].append(float(r["tempo_interno_s"]))
    return d
D = {m: carregar(m) for m in MAQ}
IC = json.load(open("relatorio/slowdown_ic.json"))
def tam(m, b): return sorted({k[1] for k in D[m] if k[0] == b})
def fmt(b, t): return str(t) if b == "matrizes" else f"{t//10**6}M"

# --- Fig 1: slowdown com IC95 (2 linhas x 3 maquinas) ---
fig, axs = plt.subplots(2, 3, figsize=(10, 5.2), sharey="row")
for i, b in enumerate(["matrizes", "palavras"]):
    for j, m in enumerate(MAQ):
        ax = axs[i][j]; ts = tam(m, b); w = 0.26
        for c, cfg in enumerate(CFG[1:]):
            xs = [x + (c - 1) * w for x in range(len(ts))]
            vs = [IC[f"{m}|{b}|{t}|{cfg}"] for t in ts]
            ax.bar(xs, [v["slow"] for v in vs], w, color=COR[cfg], label=cfg,
                   yerr=[[v["slow"] - v["lo"] for v in vs], [v["hi"] - v["slow"] for v in vs]],
                   capsize=2, error_kw=dict(lw=.8))
        ax.axhline(1, color="k", lw=.8, ls="--")
        ax.set_ylim(0.9, 1.13); ax.set_xticks(range(len(ts))); ax.set_xticklabels([fmt(b, t) for t in ts])
        ax.set_title(f"{b} — {m}");
        if j == 0: ax.set_ylabel("slowdown (× original)")
        ax.set_xlabel("tamanho da entrada")
axs[0][0].legend(loc="upper left", fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig("relatorio/fig/slowdown.png", dpi=200); plt.close(fig)

# --- Fig 2: escalonamento do original (log-log) ---
fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
simb = {"pedro": "o", "alex": "s", "marcos": "^"}
for ax, b, exp in [(axs[0], "matrizes", 3), (axs[1], "palavras", 1)]:
    for m in MAQ:
        ts = tam(m, b); ys = [st.mean(D[m][(b, t, "original")]) for t in ts]
        sl = (math.log(ys[-1]) - math.log(ys[0])) / (math.log(ts[-1]) - math.log(ts[0]))
        ax.loglog(ts, ys, simb[m] + "-", label=f"{m} (expoente {sl:.2f})")
    t0 = tam("pedro", b); y0 = st.mean(D["pedro"][(b, t0[0], "original")])
    ax.loglog(t0, [y0 * (t / t0[0]) ** exp for t in t0], "k:", lw=1, label=f"referência $n^{exp}$" if exp > 1 else "referência $n$")
    ax.set_title(b); ax.set_xlabel("tamanho da entrada"); ax.set_ylabel("tempo do original (s)"); ax.legend(fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig("relatorio/fig/escalonamento.png", dpi=200); plt.close(fig)

# --- Fig 3: as 5 estatisticas por maquina (media±desvio, mediana, min-max) ---
for m in MAQ:
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.0))
    for ax, b in zip(axs, ["matrizes", "palavras"]):
        ts = tam(m, b); w = 0.2
        for c, cfg in enumerate(CFG):
            xs = [x + (c - 1.5) * w for x in range(len(ts))]
            vs = [D[m][(b, t, cfg)] for t in ts]
            ax.bar(xs, [st.mean(v) for v in vs], w, color=COR[cfg], alpha=.85, label=cfg,
                   yerr=[st.stdev(v) for v in vs], capsize=2, error_kw=dict(lw=.9))
            ax.scatter(xs, [st.median(v) for v in vs], marker="D", s=10, color="white", edgecolor="k", lw=.5, zorder=4)
            ax.vlines(xs, [min(v) for v in vs], [max(v) for v in vs], color="k", lw=.6, zorder=3)
        ax.set_yscale("log"); ax.set_xticks(range(len(ts))); ax.set_xticklabels([fmt(b, t) for t in ts])
        ax.set_title(f"{b} — {m}"); ax.set_xlabel("tamanho da entrada"); ax.set_ylabel("tempo computacional (s, log)")
    axs[0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.text(0.99, 0.01, "barra = média ± desvio; ◇ = mediana; linha fina = mín–máx", ha="right", fontsize=7)
    fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(f"relatorio/fig/stats_{m}.png", dpi=200); plt.close(fig)
print("ok")
