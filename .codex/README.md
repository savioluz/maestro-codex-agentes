# Configuração Codex deste repositório

- `config.toml` ativa subagentes quando o repositório é confiável e limita a simultaneidade a quatro threads secundárias.
- `agents/*.toml` declara nove papéis especializados usando os campos reconhecidos: `name`, `description` e `developer_instructions`.
- O Maestro é um **comportamento da sessão principal** acionado por `$maestro`; subagentes independentes são opcionais, conforme tarefa e disponibilidade.
- Não mudamos modelo, tokens, permissões, autenticação, telemetria nem `~/.codex/config.toml`.
- Documentação oficial: https://learn.chatgpt.com/docs/agent-configuration/subagents

- `.codex/hooks.json` integra o detector de erro em PostToolUse, sujeito a confiança/aprovação; exige SMTP configurado localmente.
- `agents/skills_guardian.toml` é o responsável por evoluir as skills com evidência e testes; nenhuma sugestão vira correção comprovada automaticamente.
