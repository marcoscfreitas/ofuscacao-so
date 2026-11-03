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
import math
from collections import defaultdict

from auditar import auditar
from comum import RESULTADOS, carregar_config, maquinas_com_resultados, nome_maquina, pasta_resultados
from comum import escrever_json


def carregar(maquina):
    """Retorna (interno, total): (benchmark, tamanho, config) -> [tempos]."""
    interno, total = defaultdict(list), defaultdict(list)
    descartadas = 0
    with open(pasta_resultados(maquina) / "raw.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t, t_total = float(r["tempo_interno_s"]), float(r["tempo_total_s"])
                chave = (r["benchmark"], int(r["tamanho"]), r["config"])
                valido = math.isfinite(t) and math.isfinite(t_total) and t > 0 and t_total > 0
            except (KeyError, TypeError, ValueError):
                valido = False
            if r.get("returncode") == "0" and r.get("saida_ok") == "1" and valido:
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
    except ImportError as erro:
        raise SystemExit("matplotlib não instalado; instale requirements.txt para produzir os gráficos exigidos") from erro


def graficos(plt, maquina, interno, ordem, exploratorio=False):
    pasta = pasta_resultados(maquina) / "graficos"
    pasta.mkdir(exist_ok=True)
    for bench in sorted({k[0] for k in interno}):
        tamanhos = sorted({k[1] for k in interno if k[0] == bench})
        fig, eixos = plt.subplots(2, 3, figsize=(15, 8))
        estatisticas = [("media", "Média"), ("mediana", "Mediana"), ("desvio", "Desvio padrão amostral"),
                       ("min", "Mínimo"), ("max", "Máximo")]
        larg = 0.8 / len(ordem)
        for ax, (chave, titulo) in zip(eixos.flat, estatisticas):
            for i, cfg in enumerate(ordem):
                xs, valores = [], []
                for j, tam in enumerate(tamanhos):
                    v = interno.get((bench, tam, cfg))
                    if v:
                        xs.append(j + i * larg)
                        valores.append(resumo(v)[chave])
                ax.bar(xs, valores, larg, label=cfg)
            ax.set_xticks([j + 0.4 - larg / 2 for j in range(len(tamanhos))])
            ax.set_xticklabels([f"{t:,}" for t in tamanhos], rotation=15)
            ax.set_xlabel("tamanho da entrada")
            ax.set_ylabel("tempo computacional (s)")
            ax.set_title(titulo)
        eixos.flat[-1].axis("off")
        handles, labels = eixos.flat[0].get_legend_handles_labels()
        eixos.flat[-1].legend(handles, labels, loc="center", frameon=False)
        estado = " — EXPLORATÓRIO: há pendências" if exploratorio else ""
        fig.suptitle(f"{bench} — máquina: {maquina}{estado}", fontsize=14)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(pasta / f"{bench}.png", dpi=150)
        plt.close(fig)


def media(d, chave):
    v = d.get(chave)
    return st.mean(v) if v else None


def comparacao(plt, por_maquina, ordem, exploratorio=False):
    """Tabela e gráficos lado a lado entre máquinas."""
    maquinas = list(por_maquina)
    linhas = ["# Comparação entre máquinas\n"]
    if exploratorio:
        linhas.append("> EXPLORATÓRIO: pelo menos uma rodada tem pendências de validação.\n")
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
        nota = " — EXPLORATÓRIO" if exploratorio else ""
        ax.set_title(f"Benchmark: {bench} — maior tamanho de cada máquina{nota}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(RESULTADOS / "graficos" / f"comparacao_{bench}.png", dpi=150)
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maquina", help="analisa só esta máquina (padrão: todas as encontradas)")
    ap.add_argument("--exploratorio", action="store_true", help="gera saídas marcadas mesmo com pendências")
    args = ap.parse_args()

    maquinas = [nome_maquina(args.maquina)] if args.maquina else maquinas_com_resultados()
    if not maquinas:
        raise SystemExit("nenhum resultados/<maquina>/raw.csv encontrado")

    auditorias = {m: auditar(m) for m in maquinas}
    for m, rel in auditorias.items():
        escrever_json(pasta_resultados(m) / "auditoria.json", rel)
    if not args.exploratorio and any(not a["aprovado"] for a in auditorias.values()):
        raise SystemExit("Rodada reprovada/incompleta ou legada. Consulte auditoria.json; "
                         "use --exploratorio para gerar gráficos identificados com a pendência.")
    ordem = list(dict.fromkeys(c for a in auditorias.values() for c in a["config"]["ofuscadores"]))
    plt = importar_pyplot()
    por_maquina = {}
    for m in maquinas:
        interno, total = carregar(m)
        por_maquina[m] = interno
        aviso = ""
        if not auditorias[m]["aprovado"]:
            aviso = "\n> EXPLORATÓRIO: pendências registradas em auditoria.json; não comprova atendimento ao enunciado.\n"
        (pasta_resultados(m) / "tabelas.md").write_text(
            f"# Resultados — {m}\n" + aviso + tabelas(interno, total, ordem), encoding="utf-8")
        if plt:
            graficos(plt, m, interno, ordem, exploratorio=not auditorias[m]["aprovado"])
        print(f"escrito: resultados/{m}/tabelas.md e resultados/{m}/graficos/")
    if len(maquinas) > 1:
        comparacao(plt, por_maquina, ordem, exploratorio=any(not a["aprovado"] for a in auditorias.values()))
        print("escrito: resultados/comparacao.md e resultados/graficos/comparacao_*.png")


if __name__ == "__main__":
    main()
