---
name: skills-guardian
description: Diagnosticar erros do Codex, revisar sugestoes de correcao, melhorar skills com testes de regressao e curadoria segura da base de conhecimento Maestro.
---

# Maestro Skills Guardian - agente de evolucao continua

Use `$skills-guardian` quando surgirem erros repetidos, quando uma skill falhar, ou em manutencao preventiva.

1. Rode `python scripts/skills_curator.py --report` para abrir `.maestro/knowledge/SKILLS_REVIEW_QUEUE.md`.
2. Compare o erro com `.agents/knowledge/ERROR_CATALOG.json`. Verifique a **causa raiz** por meio de evidencias reais; o catalogo gera apenas hipoteses.
3. Reproduza de forma minima. Proponha patch pequeno na skill apropriada, com caso de regressao e rollback claro.
4. **Antes** de alterar instrucoes permanentes, mostre a prova do erro, resultado do teste, escopo, risco e solicite aprovacao se houver alteracao de permissoes, infraestrutura, dependencias ou codigo sensivel.
5. Atualize instrucoes e catalogo somente com correcao confirmada. Nao insira stack traces completos, PII, comandos com token ou senhas no Git.
6. Rerode `python scripts/validate_codex_project.py` e o teste que identificou a falha.

Se esta skill for usada globalmente fora do kit, os scripts e o catalogo podem estar em `~/.codex/maestro/` (ou `$CODEX_HOME/maestro/`); execute o curador desse local.

O hook `.codex/hooks.json` registra automaticamente falhas **observadas** por PostToolUse, alimenta a fila de sugestoes e tenta notificacao SMTP. Nao presume que o hook capture todos os erros internos do Codex, nem que uma proposta nao testada seja uma solucao real.

Para simular um erro sem API: `python scripts/skills_curator.py --ingest --title "teste" --detail "ModuleNotFoundError: No module named fastapi"`.
