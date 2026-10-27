"""Utilitários compartilhados pelos scripts."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config.json"
RESULTADOS = RAIZ / "resultados"
RAW_CSV = RESULTADOS / "raw.csv"

_RE_TEMPO = re.compile(r"time:\s*([0-9.]+)\s*seconds")


def carregar_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def diretorio_config(nome, cfg):
    """Pasta onde estão os .py de uma configuração (original ou ofuscada)."""
    info = cfg["ofuscadores"][nome]
    return RAIZ / info.get("diretorio", f"ofuscado/{nome}")


def executar(diretorio, arquivo, tamanho):
    """Roda um benchmark. Retorna (tempo_interno, tempo_total, ok, returncode)."""
    inicio = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, arquivo, str(tamanho)],
        cwd=diretorio, capture_output=True, text=True,
    )
    total = time.perf_counter() - inicio
    m = _RE_TEMPO.search(proc.stdout)
    interno = float(m.group(1)) if m else None
    ok = "are ok" in proc.stdout or "values are ok" in proc.stdout
    return interno, total, ok, proc.returncode
