"""Utilitários compartilhados pelos scripts."""
import copy
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config.json"
RESULTADOS = RAIZ / "resultados"
OFUSCADO = RAIZ / "ofuscado"

_RE_TEMPO = re.compile(r"time:\s*([0-9.]+)\s*seconds")
_RE_MAQUINA = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# Consumo medido de RAM do palavras.py (cada palavra é um objeto str separado).
BYTES_POR_PALAVRA = 56

# Ferramentas são chamadas via "python -m" para não depender do PATH (Windows/venv).
FERRAMENTAS = {
    "pyarmor": [sys.executable, "-m", "pyarmor.cli"],
    "pyminify": [sys.executable, "-m", "python_minifier"],
}


def nome_maquina(valor):
    """Valida o identificador da máquina (ex.: marcos)."""
    valor = (valor or "").strip().lower()
    if not _RE_MAQUINA.match(valor):
        raise SystemExit(f"nome de máquina inválido: {valor!r} "
                         "(use letras minúsculas, números, '-' ou '_'; ex.: --maquina marcos)")
    return valor


def pasta_resultados(maquina):
    return RESULTADOS / maquina


def maquinas_com_resultados():
    """Máquinas que já têm resultados/<maquina>/raw.csv."""
    if not RESULTADOS.exists():
        return []
    return sorted(p.name for p in RESULTADOS.iterdir() if (p / "raw.csv").exists())


def _mesclar(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _mesclar(base[k], v)
        else:
            base[k] = v


def carregar_config(maquina=None):
    """Lê config.json; se a máquina tiver entrada em "ajustes_por_maquina", mescla-a."""
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    ajustes = cfg.get("ajustes_por_maquina", {}).get(maquina) if maquina else None
    if ajustes:
        _mesclar(cfg, copy.deepcopy(ajustes))
    return cfg


def diretorio_config(nome, cfg, maquina):
    """Pasta onde estão os .py de uma configuração (original ou ofuscada) nesta máquina."""
    info = cfg["ofuscadores"][nome]
    if "diretorio" in info:
        return RAIZ / info["diretorio"]
    return OFUSCADO / maquina / nome


def comando_ferramenta(cmd):
    """Troca o primeiro item (pyarmor/pyminify) por 'python -m <módulo>'."""
    return FERRAMENTAS.get(cmd[0], [cmd[0]]) + list(cmd[1:])


def memoria_disponivel():
    """Bytes de RAM disponíveis agora (None se não for possível medir)."""
    try:
        import psutil
        return psutil.virtual_memory().available
    except ImportError:
        pass
    try:
        for linha in Path("/proc/meminfo").read_text().splitlines():
            if linha.startswith("MemAvailable"):
                return int(linha.split()[1]) * 1024
    except OSError:
        pass
    return None


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
    ok = "are ok" in proc.stdout
    return interno, total, ok, proc.returncode
