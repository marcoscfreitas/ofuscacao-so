"""Regressões do protocolo: sem executar os benchmarks grandes ou alterar dados reais."""
import copy
import csv
import io
import json
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import comum
import verificar
import rodar_benchmarks as runner
import auditar
import analisar


class ProtocoloTest(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".venv" / "testes"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="case-", dir=base)
        self.root = Path(self.temp.name).resolve()
        self.root.relative_to(base.resolve())  # confere o alvo antes da limpeza recursiva
        self.addCleanup(self.temp.cleanup)
        self.cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        self.cfg["benchmarks"]["matrizes"]["tamanhos"] = [8, 16, 24]
        self.cfg["benchmarks"]["palavras"]["tamanhos"] = [800, 1200, 1800]
        for name, value in [("RAIZ", self.root), ("CONFIG", self.root/"config.json"),
                            ("RESULTADOS", self.root/"resultados"), ("OFUSCADO", self.root/"ofuscado")]:
            p = patch.object(comum, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(comum, "perfil_energia", return_value={"sistema":"teste", "plano":"fixo"})
        p.start()
        self.addCleanup(p.stop)
        self.gravar_config()
        for config in self.cfg["ofuscadores"]:
            d = comum.diretorio_config(config, self.cfg, "teste")
            d.mkdir(parents=True, exist_ok=True)
            for b in self.cfg["benchmarks"].values():
                (d/b["arquivo"]).write_text("print('values are ok\\ntime: 21.0 seconds')\n", encoding="utf-8")
        self.pasta = comum.pasta_resultados("teste")
        self.pasta.mkdir(parents=True)

    def gravar_config(self):
        comum.CONFIG.write_text(json.dumps(self.cfg), encoding="utf-8")

    def preflight(self):
        c = comum.contexto_experimento("teste", self.cfg)
        pre = dict(aprovado=True, contexto=c, assinatura=comum.assinatura(c),
                   ram_exigida_bytes=1, reserva_memoria_bytes=1)
        comum.escrever_json(self.pasta/"verificacao.json", pre)
        return pre

    @staticmethod
    def resultado(t=21, n=1000):
        return dict(tempo_interno_s=t, tempo_total_s=t+0.2, saida_ok=True, returncode=0,
                    stdout=f"values are ok\ntime: {t} seconds\n", stderr="", motivo="",
                    pico_memoria_bytes=n*80)

    def falso_preflight(self, minimo_m=21, minimo_p=21, maior_ram=None):
        chamadas = []
        def fake(d, f, n, **kwargs):
            indice = len(chamadas)
            chamadas.append((str(d), f, n))
            t = minimo_m if indice == 10 else minimo_p if indice == 11 else 1
            r = self.resultado(t, n)
            if indice == 12 and maior_ram is not None:
                r["pico_memoria_bytes"] = maior_ram
            return r
        with patch.object(verificar, "executar_detalhado", side_effect=fake), \
             patch.object(verificar, "memoria_disponivel", return_value=20*2**30), \
             patch("sys.stdout", new_callable=io.StringIO):
            rel = verificar.verificar("teste", self.cfg)
        return rel, chamadas

    def rodada(self, limite=None):
        self.preflight()
        contador = 0
        def fake(d, f, n, **kwargs):
            nonlocal contador
            contador += 1
            if limite and contador > limite:
                raise KeyboardInterrupt("interrupção simulada")
            return self.resultado()
        with patch.object(runner, "executar_detalhado", side_effect=fake), \
             patch("sys.stdout", new_callable=io.StringIO):
            runner.rodar("teste", self.cfg)
        return contador

    def test_config_valida_e_progressao_sem_arredondar_para_baixo(self):
        self.assertEqual(comum.validar_config(self.cfg), [])
        ns = comum.tamanhos_progressivos(17, 1.6)
        self.assertTrue(all(b >= a*1.6 for a,b in zip(ns, ns[1:])))
        self.assertTrue(all(n % 8 == 0 for n in ns))

    def test_config_reprova_nove_repeticoes_e_tamanhos_proximos(self):
        self.cfg["repeticoes"] = 9
        self.cfg["benchmarks"]["matrizes"]["tamanhos"] = [8, 16, 16]
        self.assertEqual(len(comum.validar_config(self.cfg)), 2)

    def test_config_reprova_fator_invalido_sem_crash(self):
        self.cfg["fator_entre_tamanhos"] = "ruim"
        self.assertTrue(comum.validar_config(self.cfg))

    def test_ajuste_so_da_propria_maquina(self):
        self.cfg["ajustes_por_maquina"] = {"colega":{"benchmarks":{"matrizes":{"tamanhos":[16,24,40]}}}}
        self.gravar_config()
        self.assertEqual(comum.carregar_config("teste")["benchmarks"]["matrizes"]["tamanhos"], [8,16,24])
        self.assertEqual(comum.carregar_config("colega")["benchmarks"]["matrizes"]["tamanhos"], [16,24,40])

    def test_contexto_nao_muda_com_ajuste_de_colega(self):
        c1 = comum.contexto_experimento("teste", self.cfg)
        self.cfg["ajustes_por_maquina"]["colega"] = {"perfil_experimento":"outro"}
        c2 = comum.contexto_experimento("teste", self.cfg)
        self.assertEqual(comum.assinatura(c1), comum.assinatura(c2))

    def test_contexto_detecta_fonte_modificada(self):
        c1 = comum.contexto_experimento("teste", self.cfg)
        (self.root/"src/matrizes.py").write_text("# mudança\n", encoding="utf-8")
        self.assertNotEqual(comum.assinatura(c1), comum.assinatura(comum.contexto_experimento("teste", self.cfg)))

    def test_preflight_aprova_somente_com_dois_menores_e_maior_real(self):
        rel, chamadas = self.falso_preflight()
        self.assertTrue(rel["aprovado"], rel["problemas"])
        self.assertEqual(len(chamadas), 13)
        self.assertEqual({m["benchmark"] for m in rel["medicoes"] if m["etapa"]=="menor_real"}, {"matrizes","palavras"})
        self.assertEqual(rel["medicoes"][-1]["tamanho"], 1800)

    def test_preflight_reprova_palavras_abaixo_20(self):
        rel, _ = self.falso_preflight(minimo_p=19.999)
        self.assertFalse(rel["aprovado"])
        self.assertTrue(any("palavras" in e and "< 20" in e for e in rel["problemas"]))
        self.assertFalse(any(m["etapa"]=="maior_real" for m in rel["medicoes"]))

    def test_preflight_reprova_matrizes_abaixo_20(self):
        rel, _ = self.falso_preflight(minimo_m=19.999)
        self.assertFalse(rel["aprovado"])

    def test_preflight_aceita_limite_exato_20(self):
        rel, _ = self.falso_preflight(20, 20)
        self.assertTrue(rel["aprovado"])

    def test_preflight_ram_real_maior_que_estimativa_reprova(self):
        rel, _ = self.falso_preflight(maior_ram=20*2**30)
        self.assertFalse(rel["aprovado"])
        self.assertTrue(any("pico real" in e for e in rel["problemas"]))

    def test_preflight_nao_testa_entrada_grande_sem_ram(self):
        with patch.object(verificar, "executar_detalhado", return_value=self.resultado()), \
             patch.object(verificar, "memoria_disponivel", return_value=1), \
             patch("sys.stdout", new_callable=io.StringIO):
            rel = verificar.verificar("teste", self.cfg)
        self.assertFalse(rel["aprovado"])
        self.assertFalse(any(m["etapa"]=="maior_real" for m in rel["medicoes"]))

    def test_sugestoes_sao_curtas_e_nao_aprovam_experimento(self):
        with patch.object(verificar,"executar_detalhado",return_value=self.resultado()), \
             patch.object(verificar,"memoria_disponivel",return_value=20*2**30), \
             patch("sys.stdout",new_callable=io.StringIO):
            rel=verificar.verificar("teste",self.cfg,somente_sugestoes=True)
        self.assertFalse(rel["aprovado"])
        self.assertTrue(rel["somente_sugestoes"])
        self.assertEqual(len(rel["medicoes"]),10)
        self.assertEqual(set(rel["sugestoes"]),{"matrizes","palavras"})

    def test_preflight_registra_erro_exato_do_runtime(self):
        r = self.resultado()
        r.update(returncode=1, saida_ok=False, stderr="RuntimeError: unsupported Python")
        with patch.object(verificar, "executar_detalhado", return_value=r), patch("sys.stdout", new_callable=io.StringIO):
            rel = verificar.verificar("teste", self.cfg)
        self.assertFalse(rel["aprovado"])
        self.assertIn("unsupported Python", rel["problemas"][0])

    def test_runner_sem_confirmacao_nao_inicia_nem_grava(self):
        with patch.object(sys, "argv", ["rodar_benchmarks.py", "--maquina","teste"]), \
             patch.object(runner, "rodar") as rodar:
            with self.assertRaises(SystemExit):
                runner.main()
            rodar.assert_not_called()
        self.assertFalse((self.pasta/"raw.csv").exists())

    def test_runner_sem_preflight_nao_cria_csv(self):
        with self.assertRaises(SystemExit):
            runner.rodar("teste", self.cfg)
        self.assertFalse((self.pasta/"raw.csv").exists())

    def test_rodada_completa_240_casos_e_auditoria(self):
        self.assertEqual(self.rodada(), 240)
        rel = auditar.auditar("teste")
        self.assertTrue(rel["aprovado"], rel)
        self.assertEqual(rel["faltantes"], 0)

    def test_retoma_interrupcao_sem_duplicar(self):
        with self.assertRaises(KeyboardInterrupt):
            self.rodada(limite=7)
        with patch.object(runner, "executar_detalhado", return_value=self.resultado()) as executar, \
             patch("sys.stdout", new_callable=io.StringIO):
            runner.rodar("teste", self.cfg, retomar=True)
        self.assertEqual(executar.call_count, 233)
        self.assertTrue(auditar.auditar("teste")["aprovado"])

    def test_retoma_perfil_diferente_bloqueado(self):
        with self.assertRaises(KeyboardInterrupt):
            self.rodada(limite=2)
        with patch.object(comum, "perfil_energia", return_value={"sistema":"teste","plano":"outro"}):
            self.preflight()
            with self.assertRaisesRegex(SystemExit, "Contexto diferente"):
                runner.rodar("teste", self.cfg, retomar=True)

    def test_csv_existente_nunca_sobrescrito(self):
        self.rodada()
        antes = (self.pasta/"raw.csv").read_bytes()
        with self.assertRaises(SystemExit):
            runner.rodar("teste", self.cfg)
        self.assertEqual((self.pasta/"raw.csv").read_bytes(), antes)

    def test_original_abaixo_20_interrompe_e_preserva_linha(self):
        self.preflight()
        with patch.object(runner, "executar_detalhado", return_value=self.resultado(19)), \
             patch("sys.stdout", new_callable=io.StringIO):
            with self.assertRaises(RuntimeError):
                runner.rodar("teste", self.cfg)
        with (self.pasta/"raw.csv").open(encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 1)
        self.assertTrue((self.pasta/"falha.json").exists())

    def test_auditoria_reprova_csv_legado_sem_inventar_proveniencia(self):
        self.rodada()
        (self.pasta/"execucao.json").unlink()
        rel = auditar.auditar("teste")
        self.assertFalse(rel["aprovado"])
        self.assertTrue(any("legada" in a for a in rel["avisos"]))

    def test_auditoria_detecta_duplicata_e_nan(self):
        self.rodada()
        p = self.pasta/"raw.csv"
        with p.open(encoding="utf-8",newline="") as f:
            rows = list(csv.DictReader(f))
        rows[0]["tempo_interno_s"] = "nan"
        rows.append(rows[1].copy())
        with p.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=runner.CAMPOS)
            w.writeheader()
            w.writerows(rows)
        rel = auditar.auditar("teste")
        self.assertTrue(any("duplicada" in e for e in rel["erros"]))
        self.assertTrue(any("não finito" in e for e in rel["erros"]))
        self.assertFalse(rel["aprovado"])

    def test_auditoria_detecta_falta_repeticao(self):
        self.rodada()
        p=self.pasta/"raw.csv"
        lines=p.read_text(encoding="utf-8").splitlines()
        p.write_text("\n".join(lines[:-1])+"\n",encoding="utf-8")
        self.assertEqual(auditar.auditar("teste")["faltantes"], 1)

    def test_manifesto_corrompido_nao_aprova(self):
        self.rodada()
        (self.pasta/"execucao.json").write_text("{", encoding="utf-8")
        rel=auditar.auditar("teste")
        self.assertFalse(rel["aprovado"])
        self.assertTrue(any("manifesto inválido" in e for e in rel["erros"]))

    def test_graficos_contem_as_cinco_estatisticas(self):
        plt=analisar.importar_pyplot()
        interno={("matrizes",n,c):list(range(20,30)) for n in [8,16,24] for c in self.cfg["ofuscadores"]}
        figuras=[]
        original=plt.subplots
        def capturar(*args,**kwargs):
            fig,axs=original(*args,**kwargs)
            figuras.append(fig)
            return fig,axs
        with patch.object(plt, "subplots", side_effect=capturar):
            analisar.graficos(plt, "teste", interno, list(self.cfg["ofuscadores"]))
        self.assertEqual([a.get_title() for a in figuras[0].axes[:5]],
                         ["Média","Mediana","Desvio padrão amostral","Mínimo","Máximo"])
        esperados=[24.5,24.5,math.sqrt(82.5/9),20,29]
        for ax,esperado in zip(figuras[0].axes,esperados):
            self.assertAlmostEqual(ax.patches[0].get_height(),esperado)
        self.assertTrue((self.pasta/"graficos/matrizes.png").is_file())

    def test_executor_captura_saida_e_memoria_de_processo_real_pequeno(self):
        d=self.root/"src"
        (d/"mini.py").write_text("import time\ntime.sleep(.15)\nprint('values are ok\\ntime: 0.1 seconds')",encoding="utf-8")
        r=comum.executar_detalhado(d,"mini.py",1,memoria_minima=0,timeout=5)
        self.assertTrue(comum.resultado_valido(r),r)
        self.assertGreater(r["pico_memoria_bytes"],0)

    def test_executor_preserva_stderr(self):
        d=self.root/"src"
        (d/"erro.py").write_text("raise RuntimeError('erro exato de teste')",encoding="utf-8")
        r=comum.executar_detalhado(d,"erro.py",1,memoria_minima=0,timeout=5)
        self.assertFalse(comum.resultado_valido(r))
        self.assertIn("erro exato de teste",r["stderr"])

    def test_executor_timeout_interrompe_carga(self):
        d=self.root/"src"
        (d/"lento.py").write_text("import time\ntime.sleep(30)",encoding="utf-8")
        r=comum.executar_detalhado(d,"lento.py",1,memoria_minima=0,timeout=.2)
        self.assertIn("tempo total excedeu",r["motivo"])
        self.assertFalse(comum.resultado_valido(r))

    def test_executor_interrupcao_tambem_encerra_processo(self):
        d=self.root/"src"
        (d/"interromper.py").write_text("import time\ntime.sleep(30)",encoding="utf-8")
        with patch.object(comum.time,"sleep",side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                comum.executar_detalhado(d,"interromper.py",1,memoria_minima=0,timeout=5)

    def test_leitura_perfil_windows_nao_altera_energia(self):
        # Usa a implementação real, preservada antes do patch do setUp.
        def resposta(cmd, **kwargs):
            if "/getactivescheme" in cmd:
                return SimpleNamespace(returncode=0,stdout="GUID: 12345678-1234-1234-1234-123456789012")
            return SimpleNamespace(returncode=0,stdout="AC: 0x00000028\nDC: 0x00000005")
        with patch.object(sys, "platform", "win32"), patch.object(comum.subprocess,"run",side_effect=resposta) as run:
            perfil = PERFIL_REAL()
        self.assertEqual(perfil["ajustes_ac_dc"]["PROCTHROTTLEMAX"], [40,5])
        self.assertTrue(all(c.args[0][1] in ("/qh","/getactivescheme") for c in run.call_args_list))

    def test_leitura_perfil_linux_somente_sysfs(self):
        with patch.object(sys,"platform","linux"), patch.object(Path,"read_text",return_value="performance\n"), \
             patch.object(comum.subprocess,"run") as run:
            perfil=PERFIL_REAL()
        self.assertEqual(perfil["sistema"],"Linux")
        self.assertTrue(perfil["politica"])
        run.assert_not_called()

    def test_leitura_perfil_macos_somente_consulta(self):
        with patch.object(sys,"platform","darwin"), \
             patch.object(comum.subprocess,"run",return_value=SimpleNamespace(returncode=0,stdout="AC Power: lowpowermode 0")) as run:
            perfil=PERFIL_REAL()
        self.assertEqual(perfil["sistema"],"macOS")
        self.assertEqual(run.call_args.args[0],["pmset","-g","custom"])


PERFIL_REAL = comum.perfil_energia


if __name__ == "__main__":
    unittest.main()
