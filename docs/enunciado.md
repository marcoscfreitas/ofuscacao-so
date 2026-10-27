# Resumo do enunciado — Trabalho IV (Aula 50)

Fonte: `instrucoes.txt` e slides da aula 50 (Prof. Vinícius Garcia Pinto).

- **Grupo:** até 3 alunos.
- **Prazo:** AVA, até 30/10/2026 23h55. **Peso:** 50% da N4.
- **Apresentação em aula:** todos devem poder apresentar e responder sobre qualquer parte.
- **Sistema alvo:** livre; reportar versão do SO e hardware (processador, memória).

## Entregáveis

- [ ] Código-fonte ofuscado (`ofuscado/`)
- [ ] Instruções de como foi ofuscado (README)
- [ ] Instruções breves de obtenção/instalação da ferramenta de ofuscação (README)
- [ ] Relatório com tabelas e gráficos (`docs/relatorio.md`)

## Requisitos experimentais

- [ ] Uma linguagem (Python) e os **dois** benchmarks (Matrizes, Palavras)
- [ ] ≥ 2 configurações de ofuscação, comparadas ao código **não ofuscado** da mesma linguagem
- [ ] ≥ 3 tamanhos de entrada, com diferença de ≥ 50% entre eles
- [ ] Menor entrada, no código não ofuscado, **não menor que 20 s**
- [ ] 10 repetições por caso
- [ ] Média, mediana, desvio padrão, mínimo e máximo — em tabelas **e** gráficos
- [ ] Plataforma controlada (programas fechados, na tomada)
- [ ] Reportar: dificuldades, decisões, problemas de instalação, o que não funcionou

## Extras (opcionais)

- [ ] Testar em mais de um sistema
- [ ] Mais configurações de ofuscação
- [ ] Mais tamanhos de entrada
- [ ] Identificar regiões equivalentes entre original e ofuscado (função inlined, loop adicionado, constante substituída…)

## Técnicas de ofuscação citadas

Renomeação de identificadores · remoção de metadados · ofuscação de literais ·
transformação de fluxo de controle · indireção de chamadas/dados ·
virtualização de código · empacotamento/compressão.

Ofuscadores sugeridos para Python: PyArmor, pyobfuscate.
