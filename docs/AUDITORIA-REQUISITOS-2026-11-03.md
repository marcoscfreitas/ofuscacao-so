# Conferência do trabalho com o PDF original

Data: 03/11/2026. Referência do checkout antes desta revisão: `a692c1f`.

Fonte lida e inspecionada visualmente: `semana-29-aula-50-B-ava-1.pdf`, Aula 50,
Prof. Vinícius Garcia Pinto. São 85 páginas físicas, pois existem sobreposições
dos slides. As regras estão nas páginas físicas 11–18, slides numerados 4/34–11/34.
SHA-256 do arquivo consultado:
`eec41e3a0aabf83961ea2e01978d11cf30216839f01774ce8b825e126e125d9f`.
O PDF permanece fora do repositório; os colegas podem obtê-lo no AVA.

**Atualização de 04/11/2026 — exceção do `palavras`:** um integrante consultou o professor, que respondeu que o `palavras` pode ficar abaixo de 20 s: o mínimo existe só para evitar tempos desprezíveis (como 0,0001 s). O repositório registra isso em `excecoes_duracao` do `config.json`, com piso de 1 s para o original no menor tamanho. O `matrizes` continua exigindo 20 s. A resposta chegou por relato; **anexe a mensagem original ao relatório**.

## Resultado da conferência

**O trabalho ainda não atende integralmente ao enunciado.** Há uma rodada de
pedro com 240 execuções corretas, mas palavras não atinge a duração mínima.
O ambiente de marcos está registrado, mas seu CSV não está neste checkout.
A terceira máquina não está identificada. Não foi iniciada outra rodada nesta
revisão, e nenhuma frequência ou configuração de entradas foi alterada.

| Requisito | Fonte no PDF | Evidência e situação em 03/11 |
|---|---|---|
| Até três integrantes | p. 11, slide 4/34 | Nomes completos do grupo ainda faltam no relatório |
| Uma linguagem e os dois benchmarks | p. 14, slide 7/34 | Python; originais presentes em `src/`, preservados |
| Código ofuscado e instruções de instalação/geração | p. 11, slide 4/34 | Artefatos de pedro e marcos presentes; README e `ofuscar.py`; cada máquina gera o seu runtime |
| Baseline não ofuscado e pelo menos duas configurações | p. 17, slide 10/34 | Original e três ofuscados; oito testes curtos reais passaram no Windows de pedro |
| Três entradas com pelo menos 50% de diferença | p. 17, slide 10/34 | Tamanhos globais cumprem; o código passa a validar também os ajustes de cada máquina |
| Menor entrada original com pelo menos 20 s | p. 17, slide 10/34 | **Pendente:** palavras de pedro ficou abaixo; a repetição em outro perfil permanece adiada |
| Dez repetições por caso | p. 17, slide 10/34 | 240 casos únicos completos no CSV de pedro; dados dos demais ainda pendentes |
| Média, mediana, desvio padrão, mínimo e máximo em tabelas e gráficos | p. 17, slide 10/34 | Tabelas já tinham as cinco; gráficos foram corrigidos para mostrar as cinco. Dados antigos estão marcados como exploratórios |
| Plataforma controlada | p. 17, slide 10/34 | Condições da primeira rodada foram confirmadas; não há manifesto automático histórico. Novo fluxo registra contexto e confirmação |
| Versão do SO, processador e memória | p. 12, slide 5/34 | `sistema.md` de pedro e marcos; terceira máquina pendente. Coleta foi complementada para os próximos participantes |
| Dificuldades, decisões, instalação e falhas | p. 18, slide 11/34 | Registro em DECISOES-EXPERIMENTO, protocolo de pedro e relatório; cada colega deve acrescentar suas ocorrências |
| Apresentação por todos | p. 12, slide 5/34 | Não verificável pelo código; todos devem estudar os programas, o método e os resultados |
| Entrega no AVA | p. 11, slide 4/34 | PDF informa 30/10/2026, 23h55; o repositório não comprova entrega no AVA nem eventual alteração do prazo |

Testar em mais de um sistema é um **extra** no slide 11/34. Rodar em três
máquinas é uma escolha metodológica do grupo, e não uma exigência adicional
inventada a partir do PDF. Metadados de SO não equivalem a uma rodada medida.

## Correções implementadas nesta revisão

- `verificar.py`: duração real da menor entrada dos dois originais; erro abaixo
  de 20 s; teste do maior palavras com medição de memória e margem. Gera
  `verificacao.json`, inclusive quando reprova, para preservar os erros exatos.
- `verificar.py --sugerir-tamanhos`: somente testes curtos e sondas pequenas;
  estima três entradas para aquela máquina, verifica espaçamento e informa
  se a sugestão de palavras cabe na RAM. Não aprova nem altera o experimento.
- `rodar_benchmarks.py`: exige pré-voo aprovado e confirmação das condições;
  registra `execucao.json`; bloqueia retomada se mudarem Python, ABI, SO,
  ferramentas, arquivos, tamanhos ou perfil de energia. Alterações de ajustes
  dos outros integrantes não invalidam uma rodada em andamento desta máquina.
- A execução monitora a reserva de RAM e interrompe casos inválidos ou originais
  abaixo de 20 s, preservando o CSV e os detalhes da falha. A reserva automática
  é de 10% da RAM total, com mínimo de 512 MiB. Há limite de uma hora por caso;
  as sugestões de tamanhos evitam iniciar com entradas desnecessariamente grandes.
- `auditar.py`: verifica os casos e as repetições, duplicatas, números não
  finitos, correção das saídas, duração e manifesto. Audita sem executar cargas.
  Dados legados continuam legíveis, mas não recebem proveniência inventada.
- `analisar.py`: só gera resultados finais com auditoria aprovada. Para estudar
  dados antigos ou incompletos, exige `--exploratorio` e identifica a pendência
  nas tabelas e nos gráficos. Os gráficos agora mostram as cinco estatísticas.
- `info_sistema.py`: inclui arquitetura, data/fuso e política de energia;
  melhora a identificação da CPU no Windows. Se já há CSV, preserva o ambiente
  histórico e escreve `sistema-atual.md`.
- `ofuscar.py`: protege o ofuscado associado a um CSV existente; o runtime `.pyd`
  de Windows deixa de ser ignorado pelo Git. Versões dos dois ofuscadores foram
  fixadas nas versões usadas no experimento para evitar atualização acidental.

Nenhum script compartilhado troca plano de energia, governor, frequência ou
Turbo Boost. O perfil de 1200 MHz preparado em 29/10 continua sendo uma opção
específica de pedro; seu uso não foi estendido às máquinas dos colegas.

## Procedimento por computador

Seguir o [guia atualizado](GUIA-GRUPO.md): informar o próprio id, criar seu venv,
instalar os mesmos ofuscadores e gerar seus próprios artefatos. Usar as sugestões
curtas para escolher entradas próprias quando necessário; aplicar somente sua
entrada de `ajustes_por_maquina` e executar depois a verificação completa.

Uma CPU considerada mais fraca pode precisar de entradas menores para chegar
a 20 s; isso não permite deduzir RAM ou duração sem medir. SO, interpretador,
clock e disponibilidade de RAM também importam. Quando não houver combinação
que cumpra duração, crescimento das entradas e memória, o pré-voo deve reprovar.
Não aceitar uma exceção silenciosa nem executar um tamanho que a sugestão
identifica como incompatível com a RAM.

Os colegas usam os mesmos scripts, sem compartilhar o binário do PyArmor entre
sistemas. A compatibilidade de um ambiente específico depende também dos runtimes
disponíveis para a combinação de Python, SO e arquitetura; os testes curtos devem
passar antes da medição. Referência: [ambientes do PyArmor](https://pyarmor.readthedocs.io/en/stable/reference/environments.html).

## Validação e pendências restantes

Os **33 testes automatizados** usam dados sintéticos e diretórios temporários isolados;
não substituem os resultados do trabalho. Eles verificam reprovação dos dois
benchmarks abaixo de 20 s, memória, retomada, integridade e gráficos. As consultas
de energia de Windows, Linux e macOS são cobertas por testes sem modificar o SO.
Também foram executados oito casos reais pequenos dos artefatos de pedro,
com saídas corretas. **Execução real foi validada apenas no Windows disponível;
Linux/macOS precisam da verificação feita pelos próprios colegas.**

Para encerrar o trabalho faltam: medir uma rodada conforme de pedro, obter e
auditar as rodadas dos colegas, completar os nomes/ambientes e as conclusões do
relatório com as condições realmente medidas e conferir apresentação/entrega.
Os arquivos e o CSV anteriores de cada máquina foram preservados.
