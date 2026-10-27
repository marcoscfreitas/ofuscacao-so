#!/usr/bin/env python3
"""Registra SO, hardware e versões das ferramentas em resultados/<maquina>/sistema.md.

Rode em cada máquina onde os testes serão executados e cole no relatório.

Uso:
    python scripts/info_sistema.py --maquina marcos
"""
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

from comum import FERRAMENTAS, nome_maquina, pasta_resultados


def cpu():
    try:
        for linha in Path("/proc/cpuinfo").read_text().splitlines():
            if linha.startswith("model name"):
                return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    if sys.platform == "darwin":
        r = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                           capture_output=True, text=True)
        if r.stdout.strip():
            return r.stdout.strip()
    return platform.processor() or platform.machine() or "desconhecido"


def nucleos():
    try:
        import psutil
        return f"{psutil.cpu_count(logical=False)} núcleos físicos / {psutil.cpu_count()} threads"
    except ImportError:
        return f"{os.cpu_count()} threads"


def memoria():
    try:
        import psutil
        return f"{psutil.virtual_memory().total / 2**30:.1f} GiB"
    except ImportError:
        pass
    try:
        for linha in Path("/proc/meminfo").read_text().splitlines():
            if linha.startswith("MemTotal"):
                return f"{int(linha.split()[1]) / 1024 / 1024:.1f} GiB"
    except OSError:
        pass
    return "desconhecido"


def governor():
    try:
        return Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read_text().strip()
    except OSError:
        return "n/d (só Linux)"


def energia():
    try:
        import psutil
        bat = psutil.sensors_battery()
    except ImportError:
        return "n/d"
    if bat is None:
        return "sem bateria (desktop)"
    return "na tomada" if bat.power_plugged else "NA BATERIA (conecte na tomada!)"


def versao(nome):
    cmd = FERRAMENTAS[nome] + ["--version"]
    try:
        saida = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()
        return saida[0] if saida else "não instalado"
    except Exception:
        return "não instalado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maquina", required=True, help="identificador do dono da máquina (ex.: marcos)")
    maquina = nome_maquina(ap.parse_args().maquina)

    linhas = [
        f"# Ambiente de teste — {maquina}",
        f"- SO: {platform.platform()}",
        f"- CPU: {cpu()} ({nucleos()})",
        f"- Memória: {memoria()}",
        f"- Governor de CPU: {governor()}",
        f"- Energia: {energia()}",
        f"- Python: {sys.version.split()[0]} ({sys.executable})",
        f"- PyArmor: {versao('pyarmor')}",
        f"- python-minifier: {versao('pyminify')}",
    ]
    pasta = pasta_resultados(maquina)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "sistema.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    print(f"\nescrito: {pasta / 'sistema.md'}")


if __name__ == "__main__":
    main()
