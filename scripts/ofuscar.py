#!/usr/bin/env python3
"""Gera o código ofuscado de cada configuração definida em config.json.

Uso:
    python scripts/ofuscar.py                  # todas as configurações
    python scripts/ofuscar.py pyarmor-basico   # apenas algumas
"""
import shutil
import subprocess
import sys

from comum import RAIZ, carregar_config


def main():
    cfg = carregar_config()
    arquivos = [RAIZ / "src" / b["arquivo"] for b in cfg["benchmarks"].values()]
    alvos = sys.argv[1:] or [n for n, i in cfg["ofuscadores"].items() if "cmd" in i]

    for nome in alvos:
        info = cfg["ofuscadores"][nome]
        if "cmd" not in info:
            continue
        saida = RAIZ / "ofuscado" / nome
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
            print("   $", " ".join(cmd))
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
