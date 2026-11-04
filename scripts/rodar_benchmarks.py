#!/usr/bin/env python3
"""Rodada completa protegida por pré-voo, confirmação e identidade da condição.

Não altera energia. Não mistura CSVs de máquinas, Pythons, fontes ou perfis.
"""
import argparse
import csv
import json
import platform

from auditar import auditar
from comum import (agora, assinatura, carregar_config, contexto_experimento, diretorio_config,
                   duracao_minima, escrever_json, executar_detalhado, hash_csv, memoria_disponivel,
                   nome_maquina, pasta_resultados, resultado_valido, validar_config)

CAMPOS = ["timestamp", "maquina", "python", "config", "benchmark", "tamanho", "rep",
          "tempo_interno_s", "tempo_total_s", "saida_ok", "returncode"]


def ja_feitos(raw):
    if not raw.exists():
        return set()
    with raw.open(newline="", encoding="utf-8") as f:
        return {(r["config"], r["benchmark"], r["tamanho"], r["rep"]) for r in csv.DictReader(f)}


def rodar(maquina, cfg, retomar=False):
    erros = validar_config(cfg)
    if erros:
        raise SystemExit("; ".join(erros))
    pasta = pasta_resultados(maquina)
    raw, manifesto = pasta / "raw.csv", pasta / "execucao.json"
    if raw.exists() and not retomar:
        raise SystemExit("raw.csv já existe. Preserve a rodada; use --retomar somente na mesma condição.")
    if retomar and (not raw.exists() or not manifesto.exists()):
        raise SystemExit("Retomada exige CSV e execucao.json da mesma rodada; dados legados não serão alterados.")
    contexto = contexto_experimento(maquina, cfg)
    chave = assinatura(contexto)
    verificacao = pasta / "verificacao.json"
    if not verificacao.is_file():
        raise SystemExit("Execute verificar.py --maquina " + maquina + " antes da rodada.")
    pre = json.loads(verificacao.read_text(encoding="utf-8"))
    if not pre.get("aprovado") or pre.get("assinatura") != chave:
        raise SystemExit("Pré-voo reprovado ou contexto mudou (config/Python/fontes/perfil). Execute verificar.py novamente.")
    if assinatura(pre.get("contexto")) != chave:
        raise SystemExit("Conteúdo do pré-voo inconsistente com sua assinatura.")
    livre = memoria_disponivel()
    if livre is None or livre < pre["ram_exigida_bytes"]:
        raise SystemExit("RAM livre caiu desde a verificação. Feche programas e repita o pré-voo.")
    if retomar:
        meta = json.loads(manifesto.read_text(encoding="utf-8"))
        if meta.get("assinatura") != chave or assinatura(meta.get("contexto")) != chave:
            raise SystemExit("Contexto diferente do início da rodada. Não é permitido misturar medições.")
        parcial = auditar(maquina, cfg=cfg, parcial=True)
        if parcial["erros"]:
            raise SystemExit("CSV existente inválido; preserve os dados e reveja a rodada: " + "; ".join(parcial["erros"][:5]))
    else:
        if manifesto.exists():
            raise SystemExit("execucao.json já existe sem CSV; preserve o registro antes de uma nova rodada.")
        meta = dict(versao=1, inicio=agora(), contexto=contexto, assinatura=chave,
                    condicoes_confirmadas=True, preflight=pre)
    meta.update(estado="em_andamento", atualizado=agora())
    escrever_json(manifesto, meta)
    feitos = ja_feitos(raw)
    novo = not raw.exists()
    try:
        with raw.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            if novo:
                w.writeheader()
                f.flush()
            for rep in range(1, cfg["repeticoes"] + 1):
                for bench, info in cfg["benchmarks"].items():
                    for n in info["tamanhos"]:
                        for config in cfg["ofuscadores"]:
                            if (config, bench, str(n), str(rep)) in feitos:
                                continue
                            r = executar_detalhado(diretorio_config(config, cfg, maquina), info["arquivo"], n,
                                                 memoria_minima=pre["reserva_memoria_bytes"])
                            t = r["tempo_interno_s"]
                            print(f"[rep {rep}/10] {config} {bench} n={n} interno={t} "
                                  f"total={r['tempo_total_s']:.2f}s ok={r['saida_ok']} rc={r['returncode']}", flush=True)
                            w.writerow(dict(timestamp=agora(), maquina=maquina, python=platform.python_version(),
                                            config=config, benchmark=bench, tamanho=n, rep=rep, tempo_interno_s=t,
                                            tempo_total_s=round(r["tempo_total_s"], 3),
                                            saida_ok=int(r["saida_ok"]), returncode=r["returncode"]))
                            f.flush()
                            if not resultado_valido(r) or (config == "original" and t < duracao_minima(cfg, bench)[0]):
                                escrever_json(pasta / "falha.json", dict(config=config, benchmark=bench, tamanho=n, rep=rep, **r))
                                raise RuntimeError("Caso reprovado: saída/retorno/tempo ou RAM. Rodada interrompida; detalhes em falha.json.")
        if assinatura(contexto_experimento(maquina, cfg)) != chave:
            raise RuntimeError("Contexto mudou durante a rodada; não declarar medições conformes.")
        meta.update(estado="concluido", fim=agora(), csv_sha256=hash_csv(raw))
        escrever_json(manifesto, meta)
        auditoria = auditar(maquina, cfg=cfg)
        escrever_json(pasta / "auditoria.json", auditoria)
        if not auditoria["aprovado"]:
            raise RuntimeError("A auditoria final reprovou a rodada: " + "; ".join(auditoria["erros"]))
    except BaseException as erro:
        meta.update(estado="interrompido", atualizado=agora(), erro=str(erro))
        escrever_json(manifesto, meta)
        raise
    print("Concluído e auditado:", raw)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--maquina", required=True)
    ap.add_argument("--retomar", action="store_true")
    ap.add_argument("--confirmar-condicoes", action="store_true",
                    help="confirma tomada, programas fechados, suspensão desativada e máquina sem uso")
    args = ap.parse_args()
    if not args.confirmar_condicoes:
        raise SystemExit("Confirme com a pessoa as condições exigidas e use --confirmar-condicoes. Nenhuma medição iniciada.")
    maquina = nome_maquina(args.maquina)
    rodar(maquina, carregar_config(maquina), args.retomar)


if __name__ == "__main__":
    main()
