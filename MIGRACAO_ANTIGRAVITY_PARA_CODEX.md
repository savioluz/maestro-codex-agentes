# Mapeamento técnico — Antigravity → OpenAI Codex

Esta versão mantém a autoria e os arquivos-base do projeto original, mas transfere a configuração de execução para recursos suportados pelo Codex.

| Origem | Destino atualizado | Observação |
| --- | --- | --- |
| Regras escritas para Antigravity/Gemini em `AGENTS.md` | `AGENTS.md` reescrito para Codex | Reconhecido automaticamente no projeto |
| Subagentes descritos somente em `.agents/subagents/*.md` | `.codex/agents/*.toml` (8 agentes) | Campos `name`, `description`, `developer_instructions` |
| Skills existentes de Antigravity | `.agents/skills/*/SKILL.md` (9 mantidas) | Compatibilidade estrutural reaproveitada |
| Workflows Antigravity acionados por `/...` | Skills Codex acionadas por `$...` (9 incluindo alias) | Não depende de comandos slash customizados |
| Maestro como persona implícita | `$maestro` + `.agents/orchestrator/MAESTRO.md` | Orquestração sob demanda, sem processo residente |
| Instalação global em `~/.gemini/config` | Instalação opcional em `~/.agents/skills` e `~/.codex/agents` | Sem alterar configurações pessoais |
| Ausência de ajuste do VS Code | `.vscode/extensions.json` e `.vscode/tasks.json` | Extensão recomendada e validador |
| CI verificava skills superficialmente | `scripts/validate_codex_project.py` e CI | Verifica TOML, frontmatter e paths |
| PDF e HTML gerados para Antigravity | `docs/legado-antigravity/` | Preservados para rastreabilidade |
| Guia de uso original | `GUIA_PREMIUM_ECOSSISTEMA.md` e PDF atualizados | Prioridade para o Codex |

## Limites importantes

1. O kit não contém aplicação funcional completa, dependências de backend ou banco configurados.
2. O Codex pode usar os especialistas de forma sequencial ou por subagentes, conforme configuração e suporte do cliente.
3. Instalar globalmente habilidades/agentes **não instala a extensão do VS Code** nem faz login.
4. Não existem garantias automáticas de cobertura, ranking SEO, proteção OWASP ou deploy.
5. Instalação global não copia o `AGENTS.md` raiz para toda a máquina; em outros projetos, invoque `$maestro` explicitamente ou configure instruções próprias.
6. O script `audit_seal.py` foi mantido como checagem heurística, com mensagens ajustadas para não alegar certificação.

## Referências oficiais

- https://learn.chatgpt.com/docs/ide
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/config-file/config-basic


## Aprimoramentos personalizados

- Incluido `skills_guardian`, receita de erros e fila de autoaprendizado sugerido.
- Notificacoes por e-mail SMTP (sem integracoes de WhatsApp).
- Git local de @savioluz; nenhuma operacao remota executada pelo instalador.
- Configuracao SMTP necessaria em `.env` ignorado e secrets CI.
