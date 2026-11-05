# Preparação — alex — 05/11/2026

- Ambiente: Ubuntu 26.04.1 LTS, Intel Xeon E-2124 (4 núcleos/4 threads), 30,6 GiB de RAM. Detalhes e perfil de energia em `sistema.md`.
- Python escolhido: CPython 3.13.7, no ambiente `.venv-py313/`. O padrão do sistema é 3.14.4; foi escolhido o 3.13 já disponível por compatibilidade com o runtime do PyArmor. Não foi testada a geração em 3.14.
- Dependências instaladas a partir de `requirements.txt`: PyArmor 9.2.8 trial e python-minifier 3.4.0. Ofuscados próprios gerados em `ofuscado/alex/`, sem falhas.
- Primeira instalação, dentro do ambiente com rede restrita, falhou com `Failed to establish a new connection: [Errno -2] Name or service not known`, seguida de `ERROR: Could not find a version that satisfies the requirement pyarmor==9.2.8 (from versions: none)` e `ERROR: No matching distribution found for pyarmor==9.2.8`. Resolvido instalando com acesso externo autorizado; não se tratava de ausência do pacote no índice.
- A pessoa confirmou tomada, outros programas fechados, suspensão desativada e máquina sem uso durante a rodada.
- Nenhuma alteração de fontes, tamanhos, governor ou limites de CPU. Mantido o perfil observado do sistema (`powersave`, turbo permitido).
- Pré-voo e medições em `verificacao.json`; log em `verificacao-alex.log` na raiz. O aviso de duração de palavras usa exclusivamente a exceção existente no `config.json` (piso de 1 s).
- Rodada concluída em 05/11/2026, das 07:20:52 às 12:13:46 (UTC-03:00): 240 medições, dez repetições por caso, auditoria aprovada sem erros. Tabelas e gráficos gerados automaticamente após o runner e a auditoria terminarem com sucesso.
