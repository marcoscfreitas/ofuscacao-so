#!/usr/bin/env python3
"""Executa todos os benchmarks (configuração x benchmark x tamanho x repetição).

As repetições são intercaladas (rodada 1 de tudo, rodada 2 de tudo, ...) para
que variações do sistema (temperatura, processos em segundo plano) não se
concentrem em uma única configuração.

Resultado: resultados/raw.csv (acrescenta; use --retomar para continuar uma
execução interrompida sem repetir linhas já feitas).

Uso:
    python scripts/rodar_benchmarks.py
    python scripts/rodar_benchmarks.py --retomar
    python scripts/rodar_benchmarks.py --so original pyarmor-basico --reps 1   # teste rápido
"""
import argparse
import csv
from datetime import datetime

from comum import RAW_CSV, RESULTADOS, carregar_config, diretorio_config, executar

CAMPOS = ["timestamp", "config", "benchmark", "tamanho", "rep",
          "tempo_interno_s", "tempo_total_s", "saida_ok", "returncode"]


def ja_feitos():
    if not RAW_CSV.exists():
        return set()
    with open(RAW_CSV, newline="", encoding="utf-8") as f:
        return {(r["config"], r["benchmark"], r["tamanho"], r["rep"]) for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retomar", action="store_true")
    ap.add_argument("--so", nargs="*", help="limita às configurações listadas")
    ap.add_argument("--reps", type=int, help="sobrescreve 'repeticoes' do config.json")
    args = ap.parse_args()

    cfg = carregar_config()
    reps = args.reps or cfg["repeticoes"]
    configs = args.so or list(cfg["ofuscadores"])
    feitos = ja_feitos() if args.retomar else set()

    RESULTADOS.mkdir(exist_ok=True)
    novo = not RAW_CSV.exists()
    with open(RAW_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for rep in range(1, reps + 1):
            for bname, bench in cfg["benchmarks"].items():
                for tamanho in bench["tamanhos"]:
                    for nome in configs:
                        if (nome, bname, str(tamanho), str(rep)) in feitos:
                            continue
                        interno, total, ok, rc = executar(
                            diretorio_config(nome, cfg), bench["arquivo"], tamanho)
                        print(f"[rep {rep}/{reps}] {nome:20s} {bname:9s} n={tamanho:<10d} "
                              f"interno={interno} total={total:.2f}s ok={ok} rc={rc}", flush=True)
                        w.writerow(dict(
                            timestamp=datetime.now().isoformat(timespec="seconds"),
                            config=nome, benchmark=bname, tamanho=tamanho, rep=rep,
                            tempo_interno_s=interno, tempo_total_s=round(total, 3),
                            saida_ok=int(ok), returncode=rc))
                        f.flush()


if __name__ == "__main__":
    main()
