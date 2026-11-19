# Protocolo Obrigatório de Sincronização e Retomada

Este projeto é desenvolvido em regime híbrido (Antigravity + edição manual assistida por outra IA durante pausas de cota).

Antes de executar QUALQUER tarefa, planejar ou modificar arquivos:
1. Leia integralmente os arquivos `ARCHITECTURE.md` e `HANDOFF.md` na raiz do projeto.
2. Execute `git status` e `git log -n 5` no terminal para verificar quais arquivos foram criados ou alterados manualmente fora da sua última sessão.
3. Respeite todas as alterações manuais recentes. Nunca sobrescreva ou reverta código alterado manualmente sem antes verificar o motivo no `HANDOFF.md`.
4. Ao concluir uma etapa (ou sempre que finalizar um bloco de alterações), atualize a seção de estado atual e próximos passos no arquivo `HANDOFF.md` e sugira um `git commit` descritivo.