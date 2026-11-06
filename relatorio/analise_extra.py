"""Calcula slowdown com IC 95% (bootstrap) a partir dos raw.csv. Uso: python relatorio/analise_extra.py"""
import csv, random, statistics as st, json
from collections import defaultdict
random.seed(42)
MAQ = ["pedro", "alex", "marcos"]
def carregar(m):
    d = defaultdict(list); tot = defaultdict(list)
    for r in csv.DictReader(open(f"resultados/{m}/raw.csv", encoding="utf-8")):
        assert r["returncode"] == "0" and r["saida_ok"] == "1"
        k = (r["benchmark"], int(r["tamanho"]), r["config"])
        d[k].append(float(r["tempo_interno_s"])); tot[k].append(float(r["tempo_total_s"]))
    return d, tot
def boot(a, b, n=5000):
    rs = []
    for _ in range(n):
        ma = st.mean(random.choices(a, k=len(a))); mb = st.mean(random.choices(b, k=len(b)))
        rs.append(mb / ma)
    rs.sort(); return rs[int(.025 * n)], rs[int(.975 * n)]
out = {}
for m in MAQ:
    d, tot = carregar(m)
    for (b, t, c), v in sorted(d.items()):
        if c == "original": continue
        base = d[(b, t, "original")]
        lo, hi = boot(base, v)
        out[f"{m}|{b}|{t}|{c}"] = dict(slow=st.mean(v) / st.mean(base), lo=lo, hi=hi,
                                       med=st.median(v) / st.median(base))
json.dump(out, open("relatorio/slowdown_ic.json", "w"), indent=1)
for k, v in out.items():
    sig = "*" if (v["lo"] > 1 or v["hi"] < 1) else " "
    print(f"{k:45s} {v['slow']:.3f} [{v['lo']:.3f},{v['hi']:.3f}] med {v['med']:.3f} {sig}")
