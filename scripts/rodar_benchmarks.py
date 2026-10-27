#!/usr/bin/env python3
"""Executa todos os benchmarks (configuração x benchmark x tamanho x repetição).

As repetições são intercaladas (rodada 1 de tudo, rodada 2 de tudo, ...) para
que variações do sistema (temperatura, processos em segundo plano) não se
concentrem em uma única configuração.

Resultado: resultados/<maquina>/raw.csv (acrescenta; use --retomar para
continuar uma execução interrompida sem repetir linhas já feitas).

Uso:
    python scripts/rodar_benchmarks.py --maquina marcos
    python scripts/rodar_benchmarks.py --maquina marcos --retomar
"""
import argparse
import csv
import platform
from datetime import datetime

from comum import carregar_config, diretorio_config, executar, nome_maquina, pasta_resultados

CAMPOS = ["timestamp", "maquina", "python", "config", "benchmark", "tamanho", "rep",
          "tempo_interno_s", "tempo_total_s", "saida_ok", "returncode"]


def ja_feitos(raw):
    if not raw.exists():
        return set()
    with open(raw, newline="", encoding="utf-8") as f:
        return {(r["config"], r["benchmark"], r["tamanho"], r["rep"]) for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maquina", required=True, help="identificador do dono da máquina (ex.: marcos)")
    ap.add_argument("--retomar", action="store_true",
                    help="continua uma execução interrompida (não repete linhas já gravadas)")
    ap.add_argument("--so", nargs="*", help="limita às configurações listadas")
    ap.add_argument("--reps", type=int, help="sobrescreve 'repeticoes' do config.json (só para testes)")
    args = ap.parse_args()
    maquina = nome_maquina(args.maquina)

    cfg = carregar_config(maquina)
    reps = args.reps or cfg["repeticoes"]
    configs = args.so or list(cfg["ofuscadores"])

    pasta = pasta_resultados(maquina)
    raw = pasta / "raw.csv"
    if raw.exists() and not args.retomar:
        raise SystemExit(f"{raw} já existe. Use --retomar para continuar, ou apague/renomeie o "
                         "arquivo para recomeçar do zero.")
    feitos = ja_feitos(raw) if args.retomar else set()
    for nome in configs:
        d = diretorio_config(nome, cfg, maquina)
        if not d.exists():
            raise SystemExit(f"{d} não existe. Rode: python scripts/ofuscar.py --maquina {maquina}")

    pasta.mkdir(parents=True, exist_ok=True)
    novo = not raw.exists()
    with open(raw, "a", newline="", encoding="utf-8") as f:
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
                            diretorio_config(nome, cfg, maquina), bench["arquivo"], tamanho)
                        print(f"[rep {rep}/{reps}] {nome:20s} {bname:9s} n={tamanho:<10d} "
                              f"interno={interno} total={total:.2f}s ok={ok} rc={rc}", flush=True)
                        w.writerow(dict(
                            timestamp=datetime.now().isoformat(timespec="seconds"),
                            maquina=maquina, python=platform.python_version(),
                            config=nome, benchmark=bname, tamanho=tamanho, rep=rep,
                            tempo_interno_s=interno, tempo_total_s=round(total, 3),
                            saida_ok=int(ok), returncode=rc))
                        f.flush()
    print(f"\nconcluído: {raw}")


if __name__ == "__main__":
    main()
