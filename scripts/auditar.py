#!/usr/bin/env python3
"""Audita CSV sem executar benchmarks. Só grava com --salvar."""
import argparse
import csv
import json
import math

from comum import (agora, assinatura, carregar_config, escrever_json, hash_csv,
                   maquinas_com_resultados, nome_maquina, pasta_resultados, validar_config)


def auditar(maquina, cfg=None, parcial=False):
    pasta = pasta_resultados(maquina)
    meta_path = pasta / "execucao.json"
    meta, erro_meta = None, None
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict) or not isinstance(meta.get("contexto", {}).get("config"), dict):
                raise ValueError("contexto/config ausentes")
        except (ValueError, AttributeError, TypeError) as erro:
            meta, erro_meta = None, f"manifesto inválido: {erro}"
    cfg = cfg or (meta["contexto"]["config"] if meta else carregar_config(maquina))
    erros = validar_config(cfg)
    if erro_meta:
        erros.append(erro_meta)
    avisos = []
    if not meta:
        avisos.append("rodada legada: sem manifesto de Python/fontes/perfil; proveniência não verificável")
    raw = pasta / "raw.csv"
    if not raw.is_file():
        return dict(maquina=maquina, aprovado=False, erros=erros + ["raw.csv ausente"], avisos=avisos,
                    linhas=0, faltantes=0, config=cfg)
    esperado = {(c,b,str(n),str(r)) for c in cfg["ofuscadores"] for b,bench in cfg["benchmarks"].items()
                for n in bench["tamanhos"] for r in range(1,cfg["repeticoes"]+1)} if not erros else set()
    vistos, minimos = set(), {}
    with raw.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    for i, r in enumerate(linhas, 2):
        try:
            chave = (r["config"], r["benchmark"], r["tamanho"], r["rep"])
            if chave in vistos:
                erros.append(f"linha {i}: repetição duplicada {chave}")
            vistos.add(chave)
            if chave not in esperado:
                erros.append(f"linha {i}: caso fora da configuração registrada")
            interno, total = float(r["tempo_interno_s"]), float(r["tempo_total_s"])
            if not math.isfinite(interno) or not math.isfinite(total) or interno <= 0 or total <= 0:
                erros.append(f"linha {i}: tempo não positivo ou não finito")
            if r["maquina"] != maquina or r["returncode"] != "0" or r["saida_ok"] != "1":
                erros.append(f"linha {i}: identificação, saída ou retorno inválidos")
            if meta and r["python"] != meta["contexto"]["python"]:
                erros.append(f"linha {i}: Python diferente do manifesto")
            if r["config"] == "original" and math.isfinite(interno) and interno > 0:
                bench = r["benchmark"]
                minimos[bench] = min(minimos.get(bench, float("inf")), interno)
                if interno < cfg["tamanho_minimo_segundos"]:
                    erros.append(f"linha {i}: {bench} original abaixo de {cfg['tamanho_minimo_segundos']} s")
        except (KeyError, TypeError, ValueError):
            erros.append(f"linha {i}: registro incompleto ou inválido")
    faltantes = len(esperado - vistos)
    if faltantes and not parcial:
        erros.append(f"faltam {faltantes} casos/repetições")
    if meta:
        if meta.get("assinatura") != assinatura(meta["contexto"]):
            erros.append("assinatura do manifesto inválida")
        if not meta.get("condicoes_confirmadas"):
            erros.append("condições de medição não confirmadas")
        pre = meta.get("preflight", {})
        if (not pre.get("aprovado") or pre.get("assinatura") != meta.get("assinatura")
                or assinatura(pre.get("contexto")) != meta.get("assinatura")):
            erros.append("pré-voo aprovado não registrado no manifesto")
        if not parcial and meta.get("estado") != "concluido":
            erros.append("rodada sem conclusão registrada")
        if not parcial and not meta.get("csv_sha256"):
            erros.append("hash de conclusão do CSV ausente")
        if meta.get("csv_sha256") and hash_csv(raw) != meta["csv_sha256"]:
            erros.append("CSV mudou após a conclusão registrada")
    return dict(versao=1, data=agora(), maquina=maquina, aprovado=not erros and not avisos,
                erros=erros, avisos=avisos, linhas=len(linhas), esperadas=len(esperado),
                faltantes=faltantes, minimos_originais_s=minimos, config=cfg)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--maquina")
    ap.add_argument("--salvar", action="store_true", help="grava auditoria.json na pasta da máquina")
    args = ap.parse_args()
    maquinas = [nome_maquina(args.maquina)] if args.maquina else maquinas_com_resultados()
    if not maquinas:
        raise SystemExit("nenhuma rodada encontrada")
    aprovado = True
    for maquina in maquinas:
        rel = auditar(maquina)
        print(f"{maquina}: {'APROVADO' if rel['aprovado'] else 'PENDÊNCIAS'}; {rel['linhas']} linhas")
        for erro in rel["erros"] + rel["avisos"]:
            print(" -", erro)
        if args.salvar:
            escrever_json(pasta_resultados(maquina) / "auditoria.json", rel)
        aprovado &= rel["aprovado"]
    raise SystemExit(0 if aprovado else 1)


if __name__ == "__main__":
    main()
