#!/usr/bin/env python3
"""Registra SO, hardware e versões das ferramentas em resultados/sistema.md.

Rode na(s) máquina(s) onde os testes foram executados e cole no relatório.
"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from comum import RESULTADOS


def cpu():
    try:
        for linha in Path("/proc/cpuinfo").read_text().splitlines():
            if linha.startswith("model name"):
                return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconhecido"


def memoria():
    try:
        for linha in Path("/proc/meminfo").read_text().splitlines():
            if linha.startswith("MemTotal"):
                return f"{int(linha.split()[1]) / 1024 / 1024:.1f} GiB"
    except OSError:
        pass
    try:
        return f"{os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2**30:.1f} GiB"
    except (ValueError, OSError, AttributeError):
        return "desconhecido"


def versao(cmd):
    if not shutil.which(cmd[0]):
        return "não instalado"
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()[0]
    except Exception:
        return "?"


def main():
    linhas = [
        "# Ambiente de teste",
        f"- SO: {platform.platform()}",
        f"- CPU: {cpu()} ({os.cpu_count()} threads)",
        f"- Memória: {memoria()}",
        f"- Python: {sys.version.split()[0]} ({sys.executable})",
        f"- PyArmor: {versao(['pyarmor', '--version'])}",
        f"- python-minifier: {versao(['pyminify', '--version'])}",
    ]
    RESULTADOS.mkdir(exist_ok=True)
    (RESULTADOS / "sistema.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
