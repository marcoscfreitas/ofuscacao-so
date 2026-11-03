#!/usr/bin/env python3
"""Pré-voo por máquina: duração real dos dois originais e RAM do maior palavras.

Grava verificacao.json; não muda config, energia, fontes ou resultados anteriores.
Sugestões são estimativas: só se aprova uma entrada realmente medida >= 20 s.
"""
import argparse
import json
import math

from comum import (BYTES_POR_PALAVRA, FOLGA_RAM, agora, assinatura,
                   carregar_config, contexto_experimento, diretorio_config,
                   escrever_json, executar_detalhado, memoria_disponivel,
                   nome_maquina, pasta_resultados, reserva_memoria,
                   resultado_valido, tamanhos_progressivos, validar_config)

TESTE_CURTO = {"matrizes": 64, "palavras": 1_000_000}
SONDA = {"matrizes": 200, "palavras": 5_000_000}


def verificar(maquina, cfg, somente_sugestoes=False):
    problemas = validar_config(cfg)
    rel = dict(versao=1, maquina=maquina, data=agora(), aprovado=False,
               problemas=problemas, medicoes=[], sugestoes={})
    if problemas:
        return rel
    contexto = contexto_experimento(maquina, cfg)
    rel.update(contexto=contexto, assinatura=assinatura(contexto))
    alvo, fator = cfg["tamanho_minimo_segundos"], cfg["fator_entre_tamanhos"]
    rel["reserva_memoria_bytes"] = reserva_memoria()
    custos = {}

    def medir(config, bench, tamanho, etapa):
        d = diretorio_config(config, cfg, maquina)
        arquivo = cfg["benchmarks"][bench]["arquivo"]
        if not (d / arquivo).is_file():
            problemas.append(f"{config}/{arquivo} ausente; gere o ofuscado desta máquina")
            return None
        r = executar_detalhado(d, arquivo, tamanho, memoria_minima=rel["reserva_memoria_bytes"])
        rel["medicoes"].append(dict(config=config, benchmark=bench, tamanho=tamanho, etapa=etapa, **r))
        print(f"{etapa}: {config}/{bench} n={tamanho} tempo={r['tempo_interno_s']}s "
              f"ok={r['saida_ok']} rc={r['returncode']}", flush=True)
        if not resultado_valido(r):
            erro = r["motivo"] or r["stderr"].strip() or r["stdout"].strip() or "tempo/saída inválidos"
            problemas.append(f"{config}/{bench} falhou (rc={r['returncode']}): {erro}")
            return None
        return r

    print("[1/4] correção das configurações", flush=True)
    for config in cfg["ofuscadores"]:
        for bench in cfg["benchmarks"]:
            medir(config, bench, TESTE_CURTO[bench], "curto")
    if problemas:
        return rel

    print("[2/4] sondas para sugestões e estimativa de RAM", flush=True)
    bytes_palavra = BYTES_POR_PALAVRA
    for bench, info in cfg["benchmarks"].items():
        n = min(SONDA[bench], min(info["tamanhos"]))
        r = medir("original", bench, n, "sonda")
        if r is None:
            continue
        base = n * (alvo * 1.25 / r["tempo_interno_s"]) ** (1 / info["expoente_custo"])
        rel["sugestoes"][bench] = {"tamanhos": tamanhos_progressivos(base, fator)}
        custos[bench] = (n, r)
        if bench == "palavras":
            bytes_palavra = max(bytes_palavra, math.ceil(r["pico_memoria_bytes"] / n))
    if problemas:
        return rel

    livre = memoria_disponivel()
    maior_palavras = max(cfg["benchmarks"]["palavras"]["tamanhos"])
    exigida = math.ceil(maior_palavras * bytes_palavra * FOLGA_RAM)
    rel.update(bytes_por_palavra=bytes_palavra, ram_disponivel_bytes=livre, ram_exigida_bytes=exigida)
    print(f"RAM: exige {exigida / 2**30:.2f} GiB livres, com folga e {bytes_palavra} B/palavra", flush=True)
    ram_ok = livre is not None and livre >= max(exigida, rel["reserva_memoria_bytes"])
    if not ram_ok:
        problemas.append("RAM livre insuficiente ou não medida para o maior palavras; não executar a entrada grande")
    sugerida = rel["sugestoes"]["palavras"]["tamanhos"][-1] * bytes_palavra * FOLGA_RAM
    rel["sugestao_palavras_cabe_ram"] = livre is not None and sugerida <= livre
    if somente_sugestoes:
        rel["somente_sugestoes"] = True
        return rel

    print("[3/4] duração REAL das menores entradas originais", flush=True)
    for bench, info in cfg["benchmarks"].items():
        if bench == "palavras" and not ram_ok:
            continue
        n = min(info["tamanhos"])
        r = medir("original", bench, n, "menor_real")
        if r is None:
            continue
        custos[bench] = (n, r)
        if r["tempo_interno_s"] < alvo:
            problemas.append(f"{bench} n={n}: {r['tempo_interno_s']:.3f} s < {alvo} s exigidos")
            base = n * (alvo * 1.25 / r["tempo_interno_s"]) ** (1 / info["expoente_custo"])
            rel["sugestoes"][bench] = {"tamanhos": tamanhos_progressivos(base, fator)}

    print("[4/4] pico REAL de memória na maior entrada de palavras", flush=True)
    if not problemas:
        r = medir("original", "palavras", maior_palavras, "maior_real")
        if r:
            exigida = max(exigida, math.ceil(r["pico_memoria_bytes"] * FOLGA_RAM))
            rel["ram_exigida_bytes"] = exigida
            if livre < exigida:
                problemas.append("pico real do maior palavras não deixa a folga de RAM exigida")
            custos["palavras"] = (maior_palavras, r)
    segundos = 0
    for bench, (n, r) in custos.items():
        exp = cfg["benchmarks"][bench]["expoente_custo"]
        segundos += sum(r["tempo_total_s"] * (t / n) ** exp for t in cfg["benchmarks"][bench]["tamanhos"])
    rel["estimativa_horas"] = segundos * len(cfg["ofuscadores"]) * cfg["repeticoes"] / 3600
    if "palavras" in rel["sugestoes"]:
        sugerida = rel["sugestoes"]["palavras"]["tamanhos"][-1] * bytes_palavra * FOLGA_RAM
        rel["sugestao_palavras_cabe_ram"] = livre is not None and sugerida <= livre
    if assinatura(contexto_experimento(maquina, cfg)) != rel["assinatura"]:
        problemas.append("contexto mudou durante a verificação; repetir sob condição constante")
    rel["aprovado"] = not problemas
    return rel


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--maquina", required=True)
    ap.add_argument("--sugerir-tamanhos", action="store_true",
                    help="somente sondas curtas; sugere entradas desta máquina sem aprovar nem aplicar ajustes")
    args = ap.parse_args()
    maquina = nome_maquina(args.maquina)
    rel = verificar(maquina, carregar_config(maquina), args.sugerir_tamanhos)
    destino = "sugestoes.json" if args.sugerir_tamanhos else "verificacao.json"
    escrever_json(pasta_resultados(maquina) / destino, rel)
    for erro in rel["problemas"]:
        print("PROBLEMA:", erro)
    if not rel["aprovado"]:
        if rel["sugestoes"]:
            print("Sugestões estimadas, sem aplicar no config e sem aprovação experimental:")
            print(json.dumps({"ajustes_por_maquina": {maquina: {"benchmarks": rel["sugestoes"]}}}, indent=2))
            if not rel.get("sugestao_palavras_cabe_ram", False):
                print("Os tamanhos sugeridos de palavras NÃO cabem com a folga de RAM. Não os execute.")
                print("Reveja máquina/perfil/entradas; o perfil de outro colega não é uma solução automática.")
        if args.sugerir_tamanhos and rel.get("somente_sugestoes"):
            print("RESULTADO: somente sugestões. A verificação completa ainda é obrigatória; nada foi aplicado.")
            return
        raise SystemExit(f"RESULTADO: reprovado. Os detalhes estão em {destino}.")
    print(f"Estimativa de duração: ~{rel['estimativa_horas']:.1f} h, incluindo montar as entradas aproximadamente.")
    print("RESULTADO: tudo certo. Confirme as condições com a pessoa antes da rodada completa.")


if __name__ == "__main__":
    main()
