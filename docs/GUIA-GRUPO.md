# Guia do grupo — rodar o benchmark em cada máquina

Este guia explica **como os 3 integrantes medem, cada um na
própria máquina, e juntam os resultados**. Serve para pessoas e para assistentes
de IA que estejam ajudando. Leia inteiro antes de rodar qualquer coisa.

Leia também os [achados e decisões entre máquinas](DECISOES-EXPERIMENTO.md).
Eles registram a pendência dos 20 s no `palavras` (resolvida pela exceção de 04/11, descrita abaixo) e explicam por que um perfil de CPU
ou tamanho testado em um computador não deve ser copiado automaticamente.
O fluxo compartilhado foi corrigido na [auditoria do PDF de 03/11](AUDITORIA-REQUISITOS-2026-11-03.md).

**Atualização de 04/11/2026 — exceção do `palavras`:** um integrante consultou o professor, que respondeu que o `palavras` pode ficar abaixo de 20 s: o mínimo existe só para evitar tempos desprezíveis (como 0,0001 s). O repositório registra isso em `excecoes_duracao` do `config.json`, com piso de 1 s para o original no menor tamanho. O `matrizes` continua exigindo 20 s. A resposta chegou por relato; **anexe a mensagem original ao relatório**.

## 1. Ideia geral

- O trabalho mede o custo de tempo da ofuscação de código Python (veja o
  [README](../README.md) para o objetivo e [enunciado.md](enunciado.md) para as exigências).
- Cada integrante roda o **mesmo pipeline** na **sua máquina**, normalmente à noite,
  porque a rodada completa leva horas (estimativa na máquina de referência: ~4 h).
- Cada um grava seus resultados numa pasta própria, identificada pelo seu nome
  (o "id da máquina"). Assim ninguém sobrescreve ninguém e o Git não gera conflito.
- Depois, todos os resultados são juntos e o `analisar.py` gera tabelas e gráficos
  por máquina **e** uma comparação entre máquinas.

**Id da máquina:** use sempre o mesmo, em letras minúsculas: o seu primeiro nome (ex.: `marcos`).
Nos comandos abaixo, troque `SEUNOME` pelo seu id.

## 2. Por que cada um gera o próprio código ofuscado

O PyArmor cria um arquivo de runtime (`pyarmor_runtime.so` no Linux, `.pyd` no Windows)
que depende de **sistema operacional, arquitetura da CPU e versão do Python**. O
código ofuscado de um colega **não roda** na sua máquina se algum desses mudar.
Por isso:

- `ofuscado/<id>/<config>/` é gerado por `scripts/ofuscar.py --maquina <id>` e
  versionado por pessoa. A entrega final contém as três pastas.
- O código ofuscado deve ser gerado **com o mesmo Python** que vai executar os testes
  (use sempre o `.venv` do repositório).

## 3. Estrutura de arquivos por máquina

```
ofuscado/<id>/<config>/     código ofuscado desta máquina (gerado por ofuscar.py)
resultados/<id>/sistema.md  hardware/SO/versões (gerado por info_sistema.py)
resultados/<id>/raw.csv     todas as execuções (gerado por rodar_benchmarks.py)
resultados/<id>/tabelas.md  tabelas desta máquina (gerado por analisar.py)
resultados/<id>/graficos/   gráficos desta máquina (gerado por analisar.py)
resultados/comparacao.md    comparação entre máquinas (analisar.py, com ≥ 2 máquinas)
resultados/graficos/comparacao_*.png
```

`src/` (benchmarks originais do professor) **nunca deve ser alterado**.

## 4. Passo a passo (cada integrante)

Execute tudo a partir da raiz do repositório.

### 4.1 Preparar o ambiente (uma vez)

```bash
git clone <url-do-repositorio>
cd ofuscacao-so
python3 -m venv .venv                 # no Windows: python -m venv .venv
source .venv/bin/activate             # Windows (cmd): .venv\Scripts\activate
                                      # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Todos os comandos seguintes assumem o venv ativado (os scripts chamam o PyArmor e o
python-minifier com `python -m`, usando o Python do venv).

### 4.2 Registrar a máquina, gerar o ofuscado e verificar

```bash
python scripts/info_sistema.py --maquina SEUNOME
python scripts/ofuscar.py      --maquina SEUNOME
python scripts/verificar.py    --maquina SEUNOME
```

O `verificar.py` é a **checagem pré-voo**. Ele não altera configuração ou energia e confere:

1. se cada configuração existe e seus testes curtos imprimem "ok";
2. se a menor entrada real do `matrizes` leva pelo menos 20 s; no `palavras` basta o piso da
   exceção (`excecoes_duracao`, 1 s), e a medição aparece como AVISO no resultado;
3. se há reserva de RAM estimada e se o maior palavras passa numa sonda real;
4. se configuração, Python, arquivos e política de energia permanecem constantes;
5. uma estimativa de duração incluindo a montagem das entradas aproximadamente.

Ele grava `resultados/SEUNOME/verificacao.json`, inclusive os erros exatos se
reprovar. O pré-voo completo pode levar alguns minutos. Se faltar RAM estimada
ou a menor entrada falhar, ele não inicia a sonda maior. Só prossiga com o
pré-voo aprovado na condição em que a rodada será executada. O tempo de abrir
o processo e construir a entrada não substitui os 20 s do cálculo.

Em um computador diferente ou com tamanhos inadequados, use primeiro o modo curto:

```bash
python scripts/verificar.py --maquina SEUNOME --sugerir-tamanhos
```

Ele grava `sugestoes.json` e imprime estimativas para `ajustes_por_maquina`.
Não altera a configuração e não aprova a medição. Confira a RAM indicada, aplique
somente o bloco do seu id e rode o pré-voo completo depois. Isso permite entradas
menores em máquinas mais lentas, sem executar primeiro casos muito demorados.
Se a sugestão de palavras não couber na RAM, não a execute. Reavalie a condição
experimental; não copie limites de CPU de pedro e não altere `src/`.

### 4.3 Se o `verificar.py` reclamar

| Mensagem | O que fazer |
|---|---|
| `... não existe -> ofuscar.py` | Rode o `ofuscar.py` do passo 4.2. |
| `<config>/<arquivo> falhou` | Rode o comando manual que ele sugere e leia o erro. Causas prováveis: PyArmor sem suporte ao seu SO/Python (veja 6), ou venv não ativado. **Registre o erro** — é conteúdo do relatório ("o que não funcionou"). |
| `RAM livre insuficiente ...` | Feche programas, examine as sugestões e sua margem de RAM. O fluxo usa pelo menos 80 B/palavra como estimativa conservadora e mede o pico real. Não execute uma sugestão que não caiba. |
| `matrizes ... < 20 s exigidos` | Examine a sugestão e a RAM, aplique apenas o ajuste do seu id e verifique novamente. |
| `palavras ... < 1 s exigidos` | Abaixo do piso da exceção: aumente a entrada dentro da RAM. Acima de 1 s, o `palavras` é aceito mesmo abaixo de 20 s. |

### 4.4 Preparar a noite de medição

A medição só é válida se a máquina estiver quieta e estável:

- **Na tomada** (o `info_sistema.py` avisa se estiver na bateria).
- **Feche tudo** (navegador, IDE, mensageiros, jogos). Não use o computador durante a rodada.
- **Impeça suspensão/hibernação** e proteção de tela:
  - Linux: `systemd-inhibit --what=idle:sleep python scripts/rodar_benchmarks.py --maquina SEUNOME --confirmar-condicoes`
  - macOS: `caffeinate -i python scripts/rodar_benchmarks.py --maquina SEUNOME --confirmar-condicoes`
  - Windows: Configurações → Sistema → Energia → "Nunca" para suspender na tomada.
- Se possível, modo de energia "alto desempenho" (Linux: governor `performance`;
  o `info_sistema.py` registra o governor atual). Não é obrigatório, mas anote.
- Ambiente térmico estável: notebook em superfície dura, ventilação livre.

### 4.5 Rodar a rodada completa

```bash
python scripts/rodar_benchmarks.py --maquina SEUNOME --confirmar-condicoes 2>&1 | tee resultados-SEUNOME.log
```

(No Windows PowerShell, use `| Tee-Object resultados-SEUNOME.log`.)
O argumento `--confirmar-condicoes` registra a confirmação da tomada, programas
fechados, suspensão desativada e ausência de uso. Não o forneça sem combinar a
janela de medição com a pessoa. O script nunca muda a política de energia.

- Grava em `resultados/SEUNOME/raw.csv` a cada execução (linha por linha).
- Se a execução for interrompida (queda de energia, Ctrl+C), continue com
  `--retomar`; ele pula o que já foi gravado:
  `python scripts/rodar_benchmarks.py --maquina SEUNOME --retomar --confirmar-condicoes`.
- Sem `--retomar`, o script **recusa** rodar se o `raw.csv` já existir, para não
  misturar rodadas. Para outra condição, preserve os resultados, metadados e
  ofuscado anteriores em um arquivo histórico identificado antes de recomeçar.
- As 10 repetições são **intercaladas** entre configurações (rodada 1 de tudo,
  depois rodada 2 de tudo...), então uma interrupção ainda deixa dados balanceados.
- Só retome se Python, fontes, ofuscado, tamanhos e perfil de energia forem
  os mesmos. Se mudar a condição, preserve a rodada anterior em uma subpasta
  identificada e produza outro CSV. Não complete dez amostras misturando perfis.
- O fluxo grava `execucao.json` e impede retomada com contexto diferente.
  CSVs legados sem manifesto são legíveis para análise exploratória, mas não
  são retomados ou convertidos retroativamente em uma rodada validada.
- Erro, falta de RAM ou original abaixo de 20 s interrompem a rodada, preservando
  CSV e `falha.json`. Uma hora por caso é o limite de segurança de execução.

### 4.6 Conferir e enviar

```bash
python scripts/analisar.py --maquina SEUNOME      # confere se os dados fazem sentido
git add resultados/SEUNOME ofuscado/SEUNOME
git commit -m "Resultados e ofuscado da máquina SEUNOME"
git pull --rebase
git push
```

Commite **apenas** as pastas com o seu id (e o `config.json` se tiver adicionado o seu
`ajustes_por_maquina`). Não commite `.venv/`, `.pyarmor/` nem o `.log`. Se vierem
execuções com falha, a auditoria reprova a rodada. A análise final exige aprovação;
para estudar dados legados ou incompletos, use `--exploratorio`, que identifica a
pendência nas saídas. Auditoria sem cargas: `python scripts/auditar.py --maquina SEUNOME`.

Antes do commit, confira dez repetições únicas por caso, saída correta, retorno
zero e duração de pelo menos 20 s no original do `matrizes` (e pelo menos o piso da exceção no
`palavras`). Na configuração
atual, a rodada completa tem 240 casos. Gráficos exploratórios não comprovam
uma rodada completa ou conforme.

No Windows, confirme que os dois `pyarmor_runtime.pyd` do seu ofuscado foram
incluídos. O `.gitignore` foi corrigido para permitir esses runtimes em `ofuscado/`,
mantendo caches e venv ignorados. Eles fazem parte da entrega, assim como o `.so`
de Linux. O gerador recusa sobrescrever o ofuscado associado a um CSV existente.

## 5. Ajustes de tamanho por máquina (`ajustes_por_maquina`)

Por padrão **todos usam os mesmos tamanhos** do `config.json` — é o que torna a
comparação entre máquinas justa. Só se o `verificar.py` indicar que os tamanhos não
servem, adicione ao `config.json` (chave de topo) o trecho que ele imprime, por exemplo:

```json
"ajustes_por_maquina": {
  "integrante2": {
    "benchmarks": { "palavras": { "tamanhos": [24000000, 36000000, 54000000] } }
  }
}
```

O bloco da sua máquina é mesclado por cima da configuração global somente quando
você usa `--maquina integrante2`. Os tamanhos diferentes ficam visíveis em `comparacao.md`
(células "-" onde um tamanho não foi medido) e o gráfico de comparação usa o maior
tamanho de cada máquina. **Documente no relatório** quem usou tamanhos diferentes e por quê.

## 6. Problemas esperados e o que registrar

Tudo abaixo é conteúdo do relatório (seção "Dificuldades e decisões"). Anote o erro
exato, o SO/Python e o que tentou:

- **PyArmor trial:** a licença gratuita recusa `--obf-code 2`, `--mix-str`,
  `--enable rft` e `--enable bcc` (erro `out of license`). Por isso a configuração
  `pyarmor-forte` usa só o que a trial aceita. Não tente "consertar" com opções mais fortes.
- **PyArmor em outro SO/Python:** o PyArmor pode não ter runtime para a sua combinação
  (por exemplo, um Python muito novo). Se `pip install` ou `ofuscar.py` falhar, tente
  um Python anterior (3.11–3.13) num venv novo **e anote a versão usada**.
- **Windows/macOS:** comandos de venv diferem (veja 4.1). Se faltar `python3`, use `python`.
- **Memória:** o `palavras` mantém todas as palavras na RAM; se o sistema começar a
  usar swap, o tempo medido deixa de ser confiável. Mantenha os tamanhos dentro da RAM.

## 7. Juntar tudo (depois que os três enviaram)

Uma pessoa (sugestão: marcos) faz:

```bash
git pull
python scripts/analisar.py          # lê todas as pastas resultados/<id>/
git add resultados
git commit -m "Tabelas e gráficos consolidados"
git push
```

Depois o grupo preenche [relatorio.md](relatorio.md) com `resultados/<id>/sistema.md`,
as tabelas e os gráficos (por máquina e `comparacao.md`).

## 8. Como interpretar a comparação

- **slowdown** = tempo médio da configuração ofuscada ÷ tempo médio do original, no
  mesmo tamanho, máquina, Python e perfil de CPU. 1,00× = sem custo; 1,30× = 30% mais lento.
- Compare **slowdowns**, não tempos absolutos, entre máquinas: CPUs diferentes têm
  velocidades diferentes, mas o custo relativo da ofuscação é comparável.
- **Overhead de inicialização** = tempo total do processo − tempo interno do benchmark.
  Inclui iniciar Python, carregar o runtime e construir a entrada. Em palavras,
  construir o corpus é relevante; não atribua toda a diferença ao PyArmor.
- Desvio padrão alto indica ruído (programas abertos, temperatura, energia).
  Considere repetir a rodada naquela máquina.

O gráfico de comparação usa o maior tamanho de cada máquina, que pode ser
diferente. Identifique os tamanhos e os perfis no relatório. Slowdown não elimina
os efeitos de entrada, memória ou interpretador. Como CPU, SO e Python mudam
entre colegas, não atribua uma diferença isoladamente ao SO sem um experimento
que controle as demais variáveis. Veja o [registro metodológico](DECISOES-EXPERIMENTO.md).

## 9. Resumo dos scripts

| Script | O que faz | Precisa de `--maquina` |
|---|---|---|
| `info_sistema.py` | Registra SO, CPU, RAM, energia, versões | sim |
| `ofuscar.py` | Gera `ofuscado/<id>/<config>/` | sim |
| `verificar.py` | Pré-voo real; grava verificacao.json ou sugestoes.json | sim |
| `auditar.py` | Confere CSV e requisitos sem executar benchmarks | opcional |
| `rodar_benchmarks.py` | Rodada completa → `resultados/<id>/raw.csv` | sim |
| `analisar.py` | Tabelas/gráficos por máquina + comparação | opcional |
| `calibrar.py` | Procura tamanhos (uso avançado; normalmente desnecessário) | não |
