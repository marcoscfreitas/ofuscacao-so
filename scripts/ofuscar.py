#!/usr/bin/env python3
"""Gera o código ofuscado de cada configuração definida em config.json.

A saída vai para ofuscado/<maquina>/<config>/. O runtime do PyArmor é específico
de SO, arquitetura e versão do Python, então CADA máquina gera o seu próprio.

Uso:
    python scripts/ofuscar.py --maquina marcos                    # todas as configurações
    python scripts/ofuscar.py --maquina marcos pyarmor-basico     # apenas algumas
"""
import argparse
import shutil
import subprocess

from comum import (OFUSCADO, RAIZ, carregar_config, comando_ferramenta, nome_maquina,
                   pasta_resultados, validar_config)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maquina", required=True, help="identificador do dono da máquina (ex.: marcos)")
    ap.add_argument("configs", nargs="*", help="limita às configurações listadas")
    args = ap.parse_args()
    maquina = nome_maquina(args.maquina)

    cfg = carregar_config(maquina)
    if (pasta_resultados(maquina) / "raw.csv").exists():
        raise SystemExit("Esta máquina já tem raw.csv: preserve a rodada e seu ofuscado antes de gerar outra condição.")
    problemas = validar_config(cfg)
    if problemas:
        raise SystemExit("; ".join(problemas))
    arquivos = [RAIZ / "src" / b["arquivo"] for b in cfg["benchmarks"].values()]
    alvos = args.configs or [n for n, i in cfg["ofuscadores"].items() if "cmd" in i]

    for nome in alvos:
        info = cfg["ofuscadores"][nome]
        if "cmd" not in info:
            continue
        saida = OFUSCADO / maquina / nome
        # Verifica o destino absoluto antes de qualquer remoção recursiva.
        saida.resolve().relative_to((OFUSCADO / maquina).resolve())
        if saida.resolve() == (OFUSCADO / maquina).resolve():
            raise SystemExit("Diretório de saída inválido")
        if saida.exists():
            shutil.rmtree(saida)
        saida.mkdir(parents=True)
        print(f"==> {nome}: {info['descricao']}")

        if info["modo"] == "diretorio":
            cmd = []
            for parte in info["cmd"]:
                if parte == "{entradas}":
                    cmd += [str(a) for a in arquivos]
                else:
                    cmd.append(parte.replace("{saida}", str(saida)))
            comandos = [cmd]
        else:  # um comando por arquivo
            comandos = [
                [p.replace("{entrada}", str(a)).replace("{saida}", str(saida / a.name))
                 for p in info["cmd"]]
                for a in arquivos
            ]

        for cmd in comandos:
            cmd = comando_ferramenta(cmd)
            print("   $", " ".join(cmd))
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
