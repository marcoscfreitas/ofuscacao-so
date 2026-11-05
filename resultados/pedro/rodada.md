# Rodada completa — pedro

- Início: 2026-11-04T23:58:14-03:00.
- Conclusão: 2026-11-05T05:48:54-03:00 (análise gerada às 05:48:56).
- Execuções aprovadas: 240/240, em 24 casos, com dez repetições por caso.
- Todas as saídas indicaram correção e código de retorno zero; sem casos faltantes.
- Auditoria aprovada, sem erros ou avisos, registrada em `auditoria.json`.
- Pré-voo: `verificacao.json`; contexto, confirmação das condições e hash normalizado
  do CSV: `execucao.json`. O hash confere com o CSV atual.
- Windows 10 build 19045, Intel Core i7-9700 (8 núcleos/8 threads), 31,9 GiB de RAM;
  CPython 3.12.15, PyArmor 9.2.8 trial e python-minifier 3.4.0.
- Perfil registrado: alto desempenho; estados mínimo/máximo da CPU em 100% na
  tomada, sem teto de frequência solicitado e com boost habilitado. A frequência
  efetiva da CPU não foi monitorada continuamente.
- Tamanhos: matrizes 560, 840 e 1264; palavras 50, 80 e 128 milhões.
- Menor tempo entre os originais: matrizes 26,659 s; palavras 4,157 s.
- Palavras utiliza a exceção de duração registrada no `config.json` em 04/11,
  com piso de 1 s. A mensagem original do professor ainda deve ser anexada ao
  relatório pelo grupo; esta rodada não fornece essa evidência externa.
- Condições de medição confirmadas pelo participante. O executor aguardou o
  fechamento dos aplicativos, repetiu o pré-voo e então iniciou a medição.
- Estatísticas: `tabelas.md`; gráficos: `graficos/matrizes.png` e
  `graficos/palavras.png`.
