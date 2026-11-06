"""Gera relatorio/tabelas_geradas.tex (tabelas completas) e relatorio/tabela_resumo.tex
a partir dos raw.csv. Requer relatorio/slowdown_ic.json (analise_extra.py).
Uso (raiz do repo): python relatorio/gerar_tabelas.py"""
import csv
import json
import statistics as st
from collections import defaultdict

MAQ = {"pedro": "Pedro", "alex": "Alex", "marcos": "Marcos"}
CFG = ["original", "minifier-renomear", "pyarmor-basico", "pyarmor-forte"]
IC = json.load(open("relatorio/slowdown_ic.json"))
BS = "\\"  # barra invertida


def num(x, p=3):
    return f"{x:.{p}f}".replace(".", ",")


def L(*partes):
    return "".join(partes)


out = []
for m in MAQ:
    d = defaultdict(list)
    for r in csv.DictReader(open(f"resultados/{m}/raw.csv", encoding="utf-8")):
        d[(r["benchmark"], int(r["tamanho"]), r["config"])].append(float(r["tempo_interno_s"]))
    for b in ["matrizes", "palavras"]:
        out.append(BS + "begin{table}[ht]" + BS + "centering" + BS + "footnotesize\n")
        out.append(f"{BS}caption{{{b.capitalize()} --- máquina {MAQ[m]} (10 repetições por linha; tempos em s).}}"
                   f"{BS}label{{tab:{m}-{b}}}\n")
        out.append(f"{BS}begin{{tabular}}{{rlrrrrrr}}{BS}hline\n")
        out.append(f"$n$ & configuração & média & mediana & desvio & mín & máx & slowdown {BS}{BS}{BS}hline\n")
        for t in sorted({k[1] for k in d if k[0] == b}):
            base = st.mean(d[(b, t, "original")])
            for c in CFG:
                v = d[(b, t, c)]
                nome = (str(t) if b == "matrizes" else f"{t // 10**6}M") if c == "original" else ""
                out.append(f"{nome} & {c} & {num(st.mean(v))} & {num(st.median(v))} & {num(st.stdev(v))} & "
                           f"{num(min(v))} & {num(max(v))} & {num(st.mean(v) / base)} {BS}{BS}\n")
            out.append(BS + "hline\n")
        out.append(f"{BS}end{{tabular}}{BS}end{{table}}\n\n")
open("relatorio/tabelas_geradas.tex", "w", encoding="utf-8").write("".join(out))

res = [f"{BS}begin{{table}}[ht]{BS}centering{BS}footnotesize\n",
       f"{BS}caption{{Slowdown (média ofuscada / média original) no maior tamanho, com IC 95{BS}% por bootstrap. "
       f"Negrito: IC não contém 1,0.}}{BS}label{{tab:resumo}}\n",
       f"{BS}begin{{tabular}}{{llccc}}{BS}hline\n",
       f"benchmark & máquina (tamanho) & minifier-renomear & pyarmor-basico & pyarmor-forte {BS}{BS}{BS}hline\n"]
for b, tam in [("matrizes", {"pedro": 1264, "alex": 1264, "marcos": 1368}),
               ("palavras", {m: 128000000 for m in MAQ})]:
    for m in MAQ:
        cel = []
        for c in CFG[1:]:
            v = IC[f"{m}|{b}|{tam[m]}|{c}"]
            s = f"{num(v['slow'])} [{num(v['lo'])}; {num(v['hi'])}]"
            cel.append(f"{BS}textbf{{{s}}}" if (v["lo"] > 1 or v["hi"] < 1) else s)
        rot = tam[m] if b == "matrizes" else "128M"
        res.append(f"{b} & {MAQ[m]} ({rot}) & " + " & ".join(cel) + f" {BS}{BS}\n")
res.append(f"{BS}hline{BS}end{{tabular}}{BS}end{{table}}\n")
open("relatorio/tabela_resumo.tex", "w", encoding="utf-8").write("".join(res))
print("ok")
