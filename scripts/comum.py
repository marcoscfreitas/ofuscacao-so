"""Utilitários compartilhados pelos scripts."""
import copy
from datetime import datetime
import hashlib
import importlib.metadata
import json
import math
import platform
import re
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config.json"
RESULTADOS = RAIZ / "resultados"
OFUSCADO = RAIZ / "ofuscado"

_RE_TEMPO = re.compile(r"time:\s*([0-9.]+)\s*seconds")
_RE_MAQUINA = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# Reserva inicial conservadora; a verificação também mede o pico nesta máquina.
BYTES_POR_PALAVRA = 80
FOLGA_RAM = 1.25

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


def validar_config(cfg):
    erros = []
    if type(cfg.get("repeticoes")) is not int or cfg["repeticoes"] != 10:
        erros.append("o experimento exige 10 repetições por caso")
    alvo = cfg.get("tamanho_minimo_segundos", 0)
    if not isinstance(alvo, (int, float)) or not math.isfinite(alvo) or alvo < 20:
        erros.append("tamanho_minimo_segundos deve ser pelo menos 20")
    fator = cfg.get("fator_entre_tamanhos", 0)
    if not isinstance(fator, (int, float)) or not math.isfinite(fator) or fator < 1.5:
        erros.append("fator_entre_tamanhos deve ser pelo menos 1.5")
        fator = 1.5
    for nome in ("matrizes", "palavras"):
        ns = cfg.get("benchmarks", {}).get(nome, {}).get("tamanhos", [])
        if not isinstance(ns, list) or len(ns) < 3 or any(type(n) is not int or n <= 0 or n % 8 for n in ns):
            erros.append(f"{nome}: pelo menos três tamanhos positivos, múltiplos de 8")
        elif any(b < a * max(1.5, fator) for a, b in zip(ns, ns[1:])):
            erros.append(f"{nome}: cada tamanho deve crescer pelo menos {max(1.5, fator):g} vezes")
    configs = cfg.get("ofuscadores", {})
    if "original" not in configs or len([c for c in configs if c != "original"]) < 2:
        erros.append("são necessários original e pelo menos dois ofuscadores")
    if configs.get("original", {}).get("diretorio") != "src":
        erros.append("o original deve executar os arquivos intactos de src")
    return erros


def multiplo_de_8_acima(n):
    return max(8, math.ceil(n / 8) * 8)


def tamanhos_progressivos(base, fator):
    ns = [multiplo_de_8_acima(base)]
    for _ in range(2):
        ns.append(multiplo_de_8_acima(ns[-1] * fator))
    return ns


def agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def escrever_json(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(caminho)


def assinatura(dados):
    return hashlib.sha256(json.dumps(dados, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def hash_csv(caminho):
    # Normaliza as quebras de linha para permitir analisar clones Windows/Linux.
    return hashlib.sha256(Path(caminho).read_text(encoding="utf-8").encode()).hexdigest()


def perfil_energia():
    """Somente leitura. Nunca altera frequência ou plano de energia."""
    def ler_comando(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=10)
            return r.stdout.strip() if r.returncode == 0 else ""
        except (OSError, subprocess.TimeoutExpired):
            return ""

    if sys.platform == "win32":
        saida = ler_comando(["powercfg", "/getactivescheme"])
        guid = re.search(r"[0-9a-fA-F-]{36}", saida)
        ajustes = {}
        for opcao in ("PROCTHROTTLEMIN", "PROCTHROTTLEMAX", "PROCFREQMAX", "PERFBOOSTMODE"):
            texto = ler_comando(["powercfg", "/qh", "SCHEME_CURRENT", "SUB_PROCESSOR", opcao])
            valores = re.findall(r"0x([0-9a-fA-F]+)", texto)
            ajustes[opcao] = [int(v, 16) for v in valores[-2:]]
        return {"sistema": "Windows", "plano": guid.group() if guid else "não medido", "ajustes_ac_dc": ajustes}
    if sys.platform.startswith("linux"):
        caminhos = [Path("/sys/devices/system/cpu/cpu0/cpufreq") / n for n in
                    ("scaling_governor", "scaling_min_freq", "scaling_max_freq")]
        caminhos += [Path("/sys/devices/system/cpu/intel_pstate/no_turbo"),
                     Path("/sys/devices/system/cpu/cpufreq/boost")]
        dados = {}
        for caminho in caminhos:
            try:
                dados[str(caminho)] = caminho.read_text().strip()
            except OSError:
                pass
        return {"sistema": "Linux", "politica": dados or "não medido"}
    if sys.platform == "darwin":
        return {"sistema": "macOS", "politica": ler_comando(["pmset", "-g", "custom"]) or "não medido"}
    return {"sistema": sys.platform, "politica": "não medido"}


def contexto_experimento(maquina, cfg):
    import psutil
    from info_sistema import cpu
    hashes = {}
    for nome in cfg["ofuscadores"]:
        pasta = diretorio_config(nome, cfg, maquina)
        arquivos = [pasta / b["arquivo"] for b in cfg["benchmarks"].values()]
        if nome != "original" and pasta.exists():
            arquivos += [p for p in pasta.rglob("*") if p.suffix in (".so", ".pyd", ".dll")]
            arquivos += list(pasta.rglob("__init__.py"))
        for p in arquivos:
            hashes[str(p.relative_to(RAIZ))] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "ausente"
    for nome in ("comum.py", "verificar.py", "rodar_benchmarks.py"):
        p = RAIZ / "scripts" / nome
        hashes[str(p.relative_to(RAIZ))] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "ausente"
    ferramentas = {}
    for pacote in ("pyarmor", "python-minifier", "psutil", "matplotlib"):
        try:
            ferramentas[pacote] = importlib.metadata.version(pacote)
        except importlib.metadata.PackageNotFoundError:
            ferramentas[pacote] = "não instalado"
    efetiva = copy.deepcopy(cfg)
    efetiva.pop("ajustes_por_maquina", None)  # alterações de colegas não invalidam esta rodada
    return dict(maquina=maquina, python=platform.python_version(), implementacao=platform.python_implementation(),
                abi=sys.implementation.cache_tag, bits_python=struct.calcsize("P") * 8,
                so=platform.platform(), arquitetura=platform.machine(), cpu=cpu(),
                ram_total_bytes=psutil.virtual_memory().total,
                perfil=perfil_energia(), perfil_declarado=cfg.get("perfil_experimento", "padrão do sistema"),
                ferramentas=ferramentas, config=efetiva, hashes=hashes)


def reserva_memoria():
    try:
        import psutil
        return max(512 * 2**20, int(psutil.virtual_memory().total * 0.1))
    except ImportError:
        return 512 * 2**20


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


def executar_detalhado(diretorio, arquivo, tamanho, *, memoria_minima=None, timeout=3600):
    """Executa com captura de erros e proteção de RAM, inclusive no launcher Windows."""
    import psutil

    inicio = time.perf_counter()
    memoria_minima = reserva_memoria() if memoria_minima is None else memoria_minima
    pico = 0
    motivo = ""
    with tempfile.TemporaryFile() as saida, tempfile.TemporaryFile() as erros:
        proc = subprocess.Popen([sys.executable, arquivo, str(tamanho)], cwd=diretorio, stdout=saida, stderr=erros)
        try:
            while proc.poll() is None:
                try:
                    pai = psutil.Process(proc.pid)
                    arvore = [pai] + pai.children(recursive=True)
                    consumo = 0
                    for p in arvore:
                        try:
                            m = p.memory_info()
                            consumo += max(m.rss, getattr(m, "private", 0))
                        except psutil.NoSuchProcess:
                            pass
                    pico = max(pico, consumo)
                    if psutil.virtual_memory().available < memoria_minima:
                        motivo = "RAM livre abaixo da reserva de segurança"
                    elif timeout is not None and time.perf_counter() - inicio > timeout:
                        motivo = f"tempo total excedeu {timeout} segundos"
                    if motivo:
                        for p in reversed(arvore):
                            try:
                                p.kill()
                            except psutil.NoSuchProcess:
                                pass
                except psutil.NoSuchProcess:
                    pass
                time.sleep(0.05)
        except BaseException:
            try:
                pai = psutil.Process(proc.pid)
                for filho in reversed(pai.children(recursive=True)):
                    try:
                        filho.kill()
                    except psutil.NoSuchProcess:
                        pass
                pai.kill()
            except psutil.NoSuchProcess:
                pass
            proc.wait(timeout=5)
            raise
        proc.wait()
        saida.seek(0)
        erros.seek(0)
        stdout = saida.read().decode("utf-8", errors="replace")
        stderr = erros.read().decode("utf-8", errors="replace")
    total = time.perf_counter() - inicio
    m = _RE_TEMPO.search(stdout)
    interno = float(m.group(1)) if m else None
    ok = "are ok" in stdout and not motivo
    return dict(tempo_interno_s=interno, tempo_total_s=total, saida_ok=ok,
                returncode=proc.returncode if not motivo else -9, stdout=stdout,
                stderr=stderr, motivo=motivo, pico_memoria_bytes=pico)


def resultado_valido(r):
    t = r["tempo_interno_s"]
    return r["returncode"] == 0 and r["saida_ok"] and t is not None and math.isfinite(t) and t > 0


def executar(diretorio, arquivo, tamanho):
    """API dos utilitários: tempo interno, total, saída correta, retorno."""
    r = executar_detalhado(diretorio, arquivo, tamanho)
    return r["tempo_interno_s"], r["tempo_total_s"], r["saida_ok"], r["returncode"]
